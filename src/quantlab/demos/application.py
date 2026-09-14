"""Guided presentation state; no financial formula, market RNG or personal trade mutation."""

import copy

from quantlab.demos import SCHEMA
from quantlab.demos.annotations import CLASSIFICATIONS, PROCESS_NOTE, summary, teach
from quantlab.demos.builders import build
from quantlab.demos.progress import DemoProgress
from quantlab.demos.projections import explain, journey
from quantlab.demos.registry import REGISTRY, catalogue
from quantlab.explainability.registry import CONCEPTS
from quantlab.research.codec import digest
from quantlab.trading.replay import journal as trading_journal

MODES = ("quick", "learn", "quant", "interview")
DEPTH = {"quick": "beginner", "learn": "beginner", "quant": "quant", "interview": "interview"}


class DemoHub:
    def __init__(self, controller):
        self.controller = controller
        path = controller.learning.tutor.progress.path
        self.progress = DemoProgress(
            path.with_name(path.stem + "-demos.json") if path else None
        )
        self.evidence = None
        self.mode = "quick"
        self.recording = False
        self.large_text = False
        self.index = 0
        self.revealed = False
        self.completed = False
        self.hindsight = False
        self.showcase = False
        self.branch = "full"
        self.questions = {}
        self.path = []
        self.reflections = {}
        self.loaded_source = None

    @property
    def moment(self):
        if not self.evidence:
            raise ValueError("Start a demo or load a completed session")
        return self.evidence.moments[self.index]

    def fingerprint(self, m):
        # Question addresses contain only public before-state and question text.
        return digest(
            {
                "demo": self.evidence.spec.id,
                "moment": m.id,
                "question": m.question.public() if m.question else None,
                "before": m.before,
            }
        )

    def qstate(self):
        m = self.moment
        key = self.fingerprint(m)
        return self.questions.setdefault(
            key,
            dict(
                id="demo-q-" + key[:20],
                fingerprint=key,
                attempt=0,
                hints=0,
                revealed=False,
                previously_seen=key in self.progress.data["exposed_questions"],
                feedback=None,
                closed=False,
                answer=None,
            ),
        )

    def start(self, demo_id, mode="quick", branch="full"):
        if mode not in MODES:
            raise ValueError("Choose Quick, Learn, Quant or Interview")
        e = build(demo_id, branch)  # Commit presentation only after successful engine build.
        self._install(e, mode, branch)

    def _install(self, e, mode, branch="full"):
        self.evidence = e
        self.mode = mode
        self.branch = branch
        self.index = 0
        self.revealed = False
        self.completed = False
        self.hindsight = False
        self.showcase = False
        self.questions = {}
        self.path = []
        self.reflections = {}
        self.progress.count(e.spec.id, "viewed")

    def source_journal(self, lab):
        c = self.controller
        if lab == "environment":
            return c.environments.journal()
        if lab == "trading":
            if c._risk_lab is not None:
                raise ValueError(
                    "This account belongs to Risk; teach the completed Risk journal"
                )
            s = c.replay_session if c.frames is not None else c.session
            return trading_journal(s)
        if lab in ("options", "risk", "statarb"):
            obj = getattr(c, "_" + lab + "_lab")
            if obj is None:
                raise ValueError("Open and complete that lab first")
            return obj.journal()
        raise ValueError("Choose a compatible session source")

    def available_sessions(self):
        c = self.controller
        out = []
        if c.environments.active is not None:
            if c.environments.active.status == "ended":
                out.append({"id": "environment", "title": "Completed market environment"})
        else:
            if (
                c._risk_lab is None
                and (c.replay_session if c.frames is not None else c.session).status == "ended"
            ):
                out.append({"id": "trading", "title": "Completed trading session"})
            for lab in ("options", "risk", "statarb"):
                obj = getattr(c, "_" + lab + "_lab")
                if obj is not None and obj.session.status == "ended":
                    out.append({"id": lab, "title": "Completed " + lab + " session"})
        return out

    def _public_question(self):
        m = self.moment
        if not m.question:
            return None
        a = self.qstate()
        eligible = (
            self.controller.learning.tutor.progress.data["settings"]["enabled"]
            and self.mode == "learn"
            and not (
                self.showcase
                or a["closed"]
                or self.hindsight
                or a["revealed"]
                or a["previously_seen"]
                or self.revealed
                or self.evidence.origin == "saved_replay"
            )
        )
        return {
            "id": a["id"],
            "question": m.question.public(),
            "attempts": a["attempt"],
            "hints_used": a["hints"],
            "hint": m.question.hints[a["hints"] - 1] if a["hints"] else None,
            "feedback": a["feedback"],
            "closed": a["closed"],
            "mastery_eligible": eligible,
            ("note"): (
                "Only eligible Learn answers follow Phase 7 grading. Showcase, "
                "replay practice and previously revealed answers do not earn "
                "mastery."
            ),
            "solution": m.question.public(True) if self.revealed or a["revealed"] else None,
        }

    def state(self, include_catalogue=False):
        out = {
            "schema": SCHEMA,
            "active": None,
            "progress": self.progress.public(),
            "recording": self.recording,
            "large_text": self.large_text,
            "available_sessions": self.available_sessions(),
        }
        if include_catalogue:
            out.update(
                catalogue=catalogue(),
                domains=list(dict.fromkeys(s.domain for s in REGISTRY.values())),
            )
        if not self.evidence:
            return out
        e = self.evidence
        m = self.moment
        snapshot = m.after if self.revealed else m.before
        # An outcome-derived concept is itself information; withhold it before reveal.
        concept = m.concept if self.revealed or e.origin == "built_in" else "model_risk"
        dto = explain(
            snapshot,
            concept,
            previous=m.before
            if self.revealed and m.before["engine"] == snapshot["engine"]
            else None,
            depth=DEPTH[self.mode],
        )
        spec = e.spec.public()
        if e.origin == "saved_replay" and not self.completed:
            spec["concepts"] = []  # selection of future concepts/tags can signal what happened
        active = {
            "spec": spec,
            "mode": self.mode,
            "index": self.index,
            "count": len(e.moments),
            "phase": "RECAP" if self.completed else "RESULT" if self.revealed else "PREDICT",
            "completed": self.completed,
            "showcase": self.showcase,
            "hindsight": self.hindsight,
            "branch": self.branch,
            "moment": {
                "id": m.id,
                "title": m.title,
                "action": m.action,
                "observation": m.observation,
                "result_note": m.result_note if self.revealed else None,
                "concept": concept,
                "tags": m.tags if self.revealed else [],
                "expected_engine_event": m.expected_event if e.origin == "built_in" else None,
            },
            "point": copy.deepcopy(snapshot),
            "question": self._public_question(),
            "explanation": dto,
            "journey": journey(e.spec.concepts)
            if e.origin == "built_in" or self.completed
            else None,
            "limitations": e.limitations,
            "configuration": copy.deepcopy(e.configuration),
            "branch_available": m.branch and not self.revealed and not self.completed,
            "process_assessment": PROCESS_NOTE,
            "reflection": self.reflections.get(m.id),
            "classifications": CLASSIFICATIONS,
            "captures": self.capture_names() if e.origin == "built_in" else [],
            "verification": copy.deepcopy(e.verification)
            if self.completed or self.showcase
            else {"note": "Result fingerprint becomes available in the completed recap."},
            "summary": summary(e) if self.completed and e.origin == "saved_replay" else None,
            "takeaways": [
                {
                    "concept": c,
                    **{k: dto2[k] for k in ("name", "definition", "uses", "limitation")},
                }
                for c in e.spec.concepts
                for dto2 in [CONCEPTS[c].public()]
            ]
            if self.completed
            else [],
            "observer": copy.deepcopy(e.private) if self.hindsight else None,
        }
        out["active"] = active
        return out

    def capture_names(self):
        return [
            {"name": name, "index": i, "result": result}
            for i, m in enumerate(self.evidence.moments)
            for name, result in ((m.capture_before, False), (m.capture_after, True))
            if name
        ]

    def command(self, raw):
        if not isinstance(raw, dict) or set(raw) - {"kind", "payload"}:
            raise ValueError("Invalid demo command")
        kind = raw.get("kind")
        p = raw.get("payload", {})
        allowed = {
            "start": {"id", "mode"},
            "mode": {"mode"},
            "next": set(),
            "restart": set(),
            "branch": {"choice"},
            "answer": {"question_id", "answer"},
            "hint": set(),
            "retry": set(),
            "explain_answer": set(),
            "recording": {"enabled", "large_text"},
            "capture": {"name", "showcase"},
            "hindsight": {"reveal"},
            "explain": {"concept", "depth", "selector"},
            "teach_current": {"lab"},
            "load_journal": {"journal", "journal_text"},
            "reflect": {"classification", "reason"},
            "leave": set(),
        }
        if kind not in allowed or not isinstance(p, dict) or set(p) - allowed[kind]:
            raise ValueError("Unknown demo command or fields")
        if kind == "start":
            self.start(p.get("id"), p.get("mode", "quick"))
            self.loaded_source = None
        elif kind == "leave":
            self.evidence = None
        elif kind in ("teach_current", "load_journal"):
            if kind == "load_journal" and set(p) not in ({"journal"}, {"journal_text"}):
                raise ValueError("Supply one saved journal")
            raw_source = (
                self.source_journal(p.get("lab"))
                if kind == "teach_current"
                else p.get("journal", p.get("journal_text"))
            )
            e = teach(raw_source, self.controller.environments.datasets.values())
            self._install(e, "learn")
            self.loaded_source = copy.deepcopy(raw_source)
        elif kind == "recording":
            if (
                type(p.get("enabled")) is not bool
                or type(p.get("large_text", False)) is not bool
            ):
                raise ValueError("Recording controls require booleans")
            self.recording = p["enabled"]
            self.large_text = p.get("large_text", False)
        else:
            m = self.moment
            if kind == "mode":
                if p.get("mode") not in MODES:
                    raise ValueError("Unknown demo depth")
                self.mode = p["mode"]
            elif kind == "next":
                if self.completed:
                    raise ValueError("Demo completed; restart to repeat")
                if not self.revealed:
                    self.revealed = True
                    if m.question:
                        self.qstate()["revealed"] = True
                        self.progress.expose(self.fingerprint(m))
                elif self.index + 1 < len(self.evidence.moments):
                    self.index += 1
                    self.revealed = False
                else:
                    self.completed = True
                    self.progress.count(self.evidence.spec.id, "completed")
            elif kind == "restart":
                if self.evidence.origin == "saved_replay":
                    self._install(
                        teach(
                            self.loaded_source, self.controller.environments.datasets.values()
                        ),
                        self.mode,
                    )
                else:
                    self.start(self.evidence.spec.id, self.mode, self.branch)
            elif kind == "branch":
                if not m.branch or self.revealed or self.completed:
                    raise ValueError("Choose a branch before revealing the first hedge")
                branch = p.get("choice")
                e = build(self.evidence.spec.id, branch)
                self.evidence = e
                self.branch = branch
            elif kind == "hindsight":
                if not self.completed or p != {"reveal": True}:
                    raise ValueError(
                        "Complete the walkthrough, then explicitly reveal hindsight"
                    )
                self.hindsight = True
            elif kind == "capture":
                if self.evidence.origin != "built_in" or p.get("showcase") is not True:
                    raise ValueError(
                        "Named captures require explicit showcase mode; learning credit "
                        "is disabled"
                    )
                capture = next(
                    (c for c in self.capture_names() if c["name"] == p.get("name")), None
                )
                if not capture:
                    raise ValueError("Unknown named capture state")
                self.showcase = True
                self.index = capture["index"]
                self.revealed = capture["result"]
                self.completed = False
                self.hindsight = False
                for item in self.evidence.moments:
                    if item.question:
                        self.progress.expose(self.fingerprint(item))
            elif kind == "explain":
                snapshot = m.after if self.revealed else m.before
                return explain(
                    snapshot,
                    p.get("concept", m.concept if self.revealed else "model_risk"),
                    depth=p.get("depth", DEPTH[self.mode]),
                    selector=p.get("selector"),
                    previous=m.before
                    if self.revealed and snapshot["engine"] == m.before["engine"]
                    else None,
                )
            elif kind == "reflect":
                if not self.revealed:
                    raise ValueError(
                        "Reveal the outcome before classifying your own process and outcome"
                    )
                if (
                    p.get("classification") not in CLASSIFICATIONS
                    or not isinstance(p.get("reason"), str)
                    or not 1 <= len(p["reason"]) <= 1000
                ):
                    raise ValueError(
                        "Choose a quadrant and add a short reason (1–1000 characters)"
                    )
                self.reflections[m.id] = {
                    "classification": p["classification"],
                    "reason": p["reason"],
                    "label": "YOUR REFLECTION · not an automatic process grade",
                }
            else:
                if not m.question:
                    raise ValueError("This point has no prediction checkpoint")
                a = self.qstate()
                if self.completed or self.revealed or self.hindsight:
                    raise ValueError("This prediction has already been revealed")
                if kind == "hint":
                    if a["hints"] >= 2:
                        raise ValueError("Both hints have been shown")
                    a["hints"] += 1
                elif kind == "retry":
                    if not a["attempt"] or a["feedback"] == "Correct for this question.":
                        raise ValueError("Retry follows an incorrect answer")
                    a["closed"] = False
                elif kind == "explain_answer":
                    a["revealed"] = True
                    self.progress.expose(a["fingerprint"])
                elif kind == "answer":
                    if p.get("question_id") != a["id"] or a["closed"]:
                        raise ValueError("Answer the current open question")
                    correct = m.question.validate(p.get("answer"))
                    a["attempt"] += 1
                    a["closed"] = True
                    a["answer"] = p["answer"]
                    a["feedback"] = (
                        "Correct for this question."
                        if correct
                        else "Not yet. Use a hint, retry, or reveal the explanation."
                    )
                    self.progress.count(self.evidence.spec.id, "checkpoints_attempted")
                    prog = self.controller.learning.tutor.progress
                    if (
                        self.mode == "learn"
                        and not self.showcase
                        and self.evidence.origin != "saved_replay"
                        and not a["revealed"]
                        and not a["previously_seen"]
                        and prog.data["settings"]["enabled"]
                    ):
                        prog.grade(
                            concept=m.question.concept,
                            question_id=a["id"],
                            fingerprint=a["fingerprint"],
                            correct=correct,
                            assisted=a["hints"] > 0,
                            attempt=a["attempt"],
                            misconception=m.question.misconception,
                            evidence="Demo checkpoint answer: " + str(p["answer"]),
                            level=m.question.difficulty,
                            revealed=False,
                            source="demo:" + self.evidence.spec.id,
                            mode="learn",
                        )
                    # A fresh run cannot turn prior practice into first-attempt credit.
                    self.progress.expose(a["fingerprint"])
                else:
                    raise ValueError("Unsupported prediction operation")
        if self.evidence and kind not in ("explain", "recording"):
            self.path.append(
                {
                    "kind": kind,
                    "payload": {"source": "verified journal"}
                    if kind == "load_journal"
                    else copy.deepcopy(p),
                    "index": self.index,
                    "revealed": self.revealed,
                }
            )
        return self.state()

    def export(self):
        if not self.evidence or not (self.completed or self.showcase):
            raise ValueError(
                "Complete the demo or explicitly enter capture/showcase mode "
                "before exporting its full script"
            )
        from quantlab.demos.exports import script

        return script(self.evidence, self.branch)

    def path_journal(self):
        if not self.evidence or not (self.completed or self.showcase):
            raise ValueError("Complete the walkthrough before exporting its path")
        body = {
            "schema": SCHEMA,
            "demo": self.evidence.spec.id,
            "branch": self.branch,
            "configuration": self.evidence.configuration,
            "actions": copy.deepcopy(self.path),
            "reflections": copy.deepcopy(self.reflections),
            "verification": self.evidence.verification,
        }
        return body | {"digest": digest(body)}
