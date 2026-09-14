"""Local read-only boundary; capabilities are kept outside the financial sessions."""

import copy
import json

from quantlab.explainability import SCHEMA
from quantlab.explainability.evidence import changes, fields, ground
from quantlab.explainability.registry import (
    ASSUMPTIONS,
    CONCEPTS,
    DEPTHS,
    LAB_CONCEPTS,
    graph,
    resolve,
)
from quantlab.research.codec import digest

MODES = ("live", "post_session", "observer")


class Explainer:
    """At most two projected observations per lab; no persistent learner/session writes."""

    def __init__(self, controller):
        self.controller = controller
        self.observed = {}
        self.quote_actions = {}
        self.max_bytes_per_lab = 2_000_000

    def _lab(self, lab):
        if lab not in LAB_CONCEPTS:
            raise ValueError("Choose an available lab")
        return "trading" if lab == "maker" else lab

    def _source(self, lab):
        c = self.controller
        if lab == "trading":
            return c
        return getattr(c, "_" + lab + "_lab", None)

    def _research(self, selector=None):
        # Only already-verified contexts or a completed server-owned study; never a client path.
        c = self.controller
        contexts = (
            [v for v in c.learning.tutor.contexts.values() if v.kind == "research"]
            if c.learning.tutor
            else []
        )
        for name in ("options", "risk", "statarb"):
            lab = getattr(c, "_" + name + "_lab", None)
            if (
                lab is not None
                and lab.research.get("status") == "complete"
                and lab.research.get("analysis")
            ):
                from quantlab.tutor.adapters import research_contexts

                contexts = list(research_contexts(lab.research["path"]))
                break
        if selector:
            contexts = [v for v in contexts if v.facts.get("variant") == selector]
        if not contexts:
            return {"status": "unavailable", "facts": {}}
        return {"status": "ended", **contexts[-1].public()}

    def snapshot(self, lab, selector=None):
        lab = self._lab(lab)
        if lab == "research":
            return self._research(selector)
        if lab == "learning":
            tutor = self.controller.learning.tutor
            return (
                {
                    "status": "active",
                    "attempts": sum(
                        v.get("attempts", 0) for v in tutor.progress.data["concepts"].values()
                    ),
                }
                if tutor
                else {"status": "unavailable"}
            )
        source = self._source(lab)
        if source is None:
            raise ValueError(
                f"Open the {lab.title()} Lab first to display an actual session. "
                "Reading an explanation does not create financial accounts."
            )
        return source.state()

    def observe(self, lab, snapshot):
        lab = self._lab(lab)
        if lab in ("research", "learning"):
            return
        source = self._source(lab)
        if source is None or snapshot.get("replay"):
            return
        # Project each concept before retention; never retain raw private objects or journals.
        ids = set(LAB_CONCEPTS[lab]) | (
            set(LAB_CONCEPTS["maker"]) if lab == "trading" else set()
        )
        values = {key: ground(key, snapshot, lab) for key in ids}
        if lab == "trading":
            for order in snapshot.get("orders", [])[-20:]:
                for key in (
                    "vwap",
                    "market_orders",
                    "limit_orders",
                    "partial_fills",
                    "order_size",
                ):
                    values[key + ":" + order["order_id"]] = ground(
                        key, snapshot, lab, order["order_id"]
                    )
            action = self.quote_actions.get(id(source.session))
            if action:
                values["quote_skew"]["inputs"]["last_actual_manual_quote_request"] = (
                    copy.deepcopy(action)
                )
        if lab == "options":
            for key in ("delta", "gamma", "vega", "theta", "rho"):
                values[key + ":portfolio"] = ground(key, snapshot, lab, "portfolio")
        if lab == "risk":
            for key in ("var", "expected_shortfall"):
                for method in ("monte_carlo", "historical", "parametric"):
                    values[key + ":" + method] = ground(key, snapshot, lab, method)
        point = fields(snapshot, "revision time_us public_event step t status")
        identity = id(source.session)
        row = dict(identity=identity, point=point, values=values)
        serial = json.dumps(row, allow_nan=False, sort_keys=True)
        if len(serial.encode()) > self.max_bytes_per_lab:
            self.observed.pop(lab, None)
            return  # Skip observation retention, never truncate financial evidence.
        row["digest"] = digest(row)
        current = self.observed.get(lab, [])
        if current and current[-1]["identity"] != identity:
            current = []
        if not current or current[-1]["digest"] != row["digest"]:
            self.observed[lab] = (current + [row])[-2:]

    def record_response(self, path, response):
        lab = {
            "/api/state": "trading",
            "/api/command": "trading",
            "/api/options": "options",
            "/api/risk": "risk",
            "/api/statarb": "statarb",
        }.get(path)
        if lab and isinstance(response, dict):
            snapshot = response.get("state", response)
            if "status" in snapshot:
                self.observe(lab, snapshot)

    def record_action(self, path, raw, before, response):
        if (
            path == "/api/command"
            and raw.get("kind") == "quotes"
            and response.get("result", {}).get("ok")
        ):
            s = response["state"]
            self.quote_actions[id(self.controller.session)] = dict(
                request=fields(
                    raw.get("payload", {}), "bid_distance ask_distance bid_size ask_size shift"
                ),
                before=fields(before, "reference reference_source best_bid best_ask"),
                inventory=before.get("account", {}).get("position"),
                adjustments=response["result"].get("adjustments", []),
                point=fields(s, "revision time_us public_event"),
            )
            self.quote_actions = {
                id(self.controller.session): self.quote_actions[id(self.controller.session)]
            }

    def explain(
        self,
        concept,
        *,
        lab="trading",
        depth="beginner",
        mode="live",
        selector=None,
        reveal=False,
        source=None,
    ):
        hub = getattr(self.controller, "environments", None)
        if hub is not None and hub.active is not None:
            return hub.explain(
                concept,
                lab=lab,
                depth=depth,
                mode=mode,
                selector=selector,
                reveal=reveal,
                source=source,
            )
        key = resolve(concept)
        if depth not in DEPTHS:
            raise ValueError("Choose Beginner, Maths, Quant or Interview depth")
        if mode not in MODES:
            raise ValueError("Unknown explanation mode")
        # Future environment metadata has an explicit vocabulary, never invented observations.
        if source not in (None, "synthetic"):
            raise ValueError(
                "Only the current synthetic environment is available; historical "
                "ingestion is not implemented"
            )
        actual_lab = self._lab(lab)
        s = self.snapshot(actual_lab, selector if actual_lab == "research" else None)
        if mode in ("post_session", "observer") and s.get("status") != "ended":
            raise ValueError(
                "Post-session and observer explanations require the ended session or "
                "ended replay frame"
            )
        if mode == "observer":
            if reveal is not True or actual_lab != "trading":
                raise ValueError(
                    "Explicit reveal is required; synthetic observer evidence is "
                    "supported for the ended trading desk only"
                )
            observer = self.controller.tutor_command(
                {"kind": "observer", "payload": {"reveal": True}}
            )
            return dict(
                schema=SCHEMA,
                mode=mode,
                label=(
                    "OBSERVER / MODEL EXPLANATION — hidden synthetic truth, unavailable "
                    "at decision time"
                ),
                observer=observer,
                quiz_allowed=False,
                concept=CONCEPTS[key].public(),
            )
        meta = CONCEPTS[key].public()
        current = ground(key, s, actual_lab, selector)
        if key == "quote_skew" and not s.get("replay"):
            action = self.quote_actions.get(id(self.controller.session))
            if action:
                current["inputs"]["last_actual_manual_quote_request"] = copy.deepcopy(action)
        previous = None
        previous_point = None
        source_object = self._source(actual_lab)
        if s.get("replay"):
            i = source_object.frame_index
            if i > 0:
                predecessor = source_object.frames[i - 1]
                previous = ground(key, predecessor, actual_lab, selector)
                previous_point = fields(predecessor, "revision time_us public_event step t") | {
                    "frame_index": i - 1
                }
        else:
            self.observe(actual_lab, s)
            rows = self.observed.get(actual_lab, [])
            if len(rows) == 2:
                previous = rows[0]["values"].get(key + ":" + selector if selector else key)
                previous_point = rows[0]["point"]
        change = dict(
            available=previous is not None,
            label=(
                "Main changed inputs between observed public snapshots; not causal percentages"
            ),
            previous_point=previous_point,
            before=None if previous is None else previous["value"],
            after=current["value"],
            inputs=[],
        )
        if previous is not None:
            change["inputs"] = changes(previous["inputs"], current["inputs"])
            change["output"] = changes(
                {"value": previous["value"]}, {"value": current["value"]}
            )
        if key == "quote_skew" and not s.get("replay"):
            action = self.quote_actions.get(id(self.controller.session))
            if action:
                current["inputs"]["last_actual_manual_quote_request"] = copy.deepcopy(action)
        if key == "quote_skew" and s.get("replay"):
            current["note"] += (
                " This legacy public replay frame retains placed prices but not its "
                "full manual quote request; no missing sensitivity or shift is "
                "inferred."
            )
        assumptions = [dict(id=k, **ASSUMPTIONS[k]) for k in meta["assumptions"]]
        return dict(
            schema=SCHEMA,
            concept=meta,
            depth=depth,
            mode=mode,
            label="POST-SESSION PUBLIC REVIEW"
            if mode == "post_session"
            else "SELECTED REPLAY POINT — PUBLIC INFORMATION"
            if s.get("replay")
            else "ACTUAL SESSION — LIVE PUBLIC INFORMATION",
            source=dict(
                environment="synthetic",
                relation="calculated from / model-dependent contributor",
                point=fields(s, "revision time_us public_event step t frame_index status"),
            ),
            current=current,
            change=change,
            assumptions=assumptions,
            dependency_trace=[
                dict(id=x, name=CONCEPTS[x].name, relation="prerequisite / model dependency")
                for x in dict.fromkeys(meta["prerequisites"] + meta["affected_by"])
            ],
            quiz_allowed=actual_lab not in ("learning",) and key in self._quiz_map(),
            statements=[
                dict(type="CALCULATION", text=current["note"]),
                dict(type="MODEL ASSUMPTION", text=meta["limitation"]),
                dict(type="REAL-FINANCE CONTEXT", text=meta["uses"]),
            ],
            selectors=self.selectors(actual_lab, s),
        )

    @staticmethod
    def _quiz_map():
        from quantlab.tutor.catalog import ACTIVE_CONCEPTS

        mapping = {
            k: k for k in CONCEPTS if k in ACTIVE_CONCEPTS and ACTIVE_CONCEPTS[k].implemented
        }
        mapping.update(regression_beta="beta", lookahead_bias="look_ahead")
        return mapping

    def selectors(self, lab, s):
        if lab == "trading":
            return [
                dict(
                    id=o["order_id"],
                    label=o["order_id"]
                    + " · "
                    + o["side"]
                    + " · "
                    + str(o["original"])
                    + " units",
                )
                for o in s.get("orders", [])
            ][-100:]
        if lab == "risk":
            return [
                dict(id=k, label=k.replace("_", " "))
                for k in ("monte_carlo", "historical", "parametric")
            ]
        return []

    def quiz(self, concept, *, lab="trading", mode="learn", selector=None):
        hub = getattr(self.controller, "environments", None)
        if hub is not None and hub.active is not None:
            return hub.tutor.ask(hub.state(), concept, mode)
        from quantlab.tutor.context import trading_contexts
        from quantlab.tutor.derivatives import derivative_context
        from quantlab.tutor.questions import relevant
        from quantlab.tutor.risk import risk_context
        from quantlab.tutor.statarb import statarb_context

        key = resolve(concept)
        if key not in self._quiz_map():
            raise ValueError(
                "This concept has an interview prompt but no scored tutor question yet"
            )
        mapped = self._quiz_map()[key]
        actual = self._lab(lab)
        s = self.snapshot(actual, selector if actual == "research" else None)
        source = "explanation-" + actual
        if actual == "trading":
            contexts = trading_contexts(s, source)
        elif actual == "options":
            contexts = (derivative_context(s, source, "explanation"),)
        elif actual == "risk":
            contexts = (risk_context(s, source),)
        elif actual == "statarb":
            contexts = (statarb_context(s, source),)
        elif actual == "research":
            from quantlab.tutor.context import context_from_dict

            if not s.get("facts"):
                raise ValueError("Complete and select a verified research result first")
            contexts = (
                context_from_dict(
                    {k: s[k] for k in ("source", "kind", "event", "time_us", "facts")}
                ),
            )
        else:
            raise ValueError("Choose a financial lab with an observed context")
        if selector and actual == "trading":
            contexts = tuple(c for c in contexts if c.facts.get("order_id") == selector)
        contexts = [c for c in contexts if mapped in {x[0] for x in relevant(c)}]
        if not contexts:
            raise ValueError(
                "No relevant current public evidence for a scored question on this "
                "concept. Use its Interview prompt or create the relevant event "
                "first."
            )
        learning = self.controller.learning
        with learning.lock:
            learning._healthy()
            return learning.tutor.ask(mapped, context=contexts[-1], mode=mode)

    def what_if(self, kind, *, lab="trading", inputs=None):
        hub = getattr(self.controller, "environments", None)
        if hub is not None and hub.active is not None:
            from quantlab.environments.explanation import what_if

            return what_if(hub.state(), kind, inputs)
        from quantlab.explainability import sandbox

        if not isinstance(inputs, dict):
            raise ValueError("Hypothetical inputs must be an object")
        if len(json.dumps(inputs)) > 4096:
            raise ValueError("Hypothetical input budget exceeded")
        expected = {
            "volatility": "options",
            "correlation": "risk",
            "order_size": "trading",
            "inventory": "trading",
            "entry_threshold": "statarb",
        }
        if kind not in expected:
            raise ValueError("Choose an available hypothetical")
        actual = self._lab(lab)
        if actual != expected[kind]:
            raise ValueError(f"This hypothetical uses the {expected[kind]} lab")
        s = self.snapshot(actual)
        fn = {
            "volatility": sandbox.volatility,
            "correlation": sandbox.correlation,
            "order_size": sandbox.order_size,
            "inventory": sandbox.inventory,
            "entry_threshold": sandbox.threshold,
        }[kind]
        # No access to live engine RNG/account capabilities is passed to any sandbox function.
        risk = None
        if (
            kind == "volatility"
            and not s.get("replay")
            and self.controller._risk_lab is not None
            and self.controller._risk_lab.frames is None
        ):
            risk = self.snapshot("risk")
        out = (
            fn(copy.deepcopy(s), copy.deepcopy(inputs), copy.deepcopy(risk))
            if kind == "volatility"
            else fn(copy.deepcopy(s), copy.deepcopy(inputs))
        )
        return dict(
            schema=SCHEMA,
            label="HYPOTHETICAL SNAPSHOT ANALYSIS",
            kind=kind,
            source_point=fields(s, "revision time_us public_event step t frame_index"),
            isolation=(
                "No live orders, P&L, risk limits, replay actions, research records, "
                "market RNG or learning evidence are changed."
            ),
            result=out,
        )

    def replay_hook(self, lab):
        hub = getattr(self.controller, "environments", None)
        if hub is not None and hub.active is not None:
            return hub.hook()
        actual = self._lab(lab)
        s = self.snapshot(actual)
        source = self._source(actual)
        if not s.get("replay"):
            raise ValueError("Load a verified replay first")
        i = source.frame_index
        previous = source.frames[i - 1] if i else None
        # Compact annotated hook: public pre/post evidence only, never raw command journals.
        concepts = {
            "trading": ("vwap", "pnl_attribution", "markouts"),
            "options": ("delta", "pnl_attribution"),
            "risk": ("var", "pnl_attribution"),
            "statarb": ("z_score", "pnl_attribution"),
        }[actual]
        return dict(
            schema=SCHEMA,
            event_type="public replay transition",
            frame_index=i,
            concept_ids=concepts,
            pre=None
            if previous is None
            else {k: ground(k, previous, actual) for k in concepts},
            post={k: ground(k, s, actual) for k in concepts},
            note=(
                "Only this frame and its predecessor are exposed; action evidence is "
                "the recorded public execution/metric trace. Later frames are "
                "excluded."
            ),
        )

    def command(self, raw):
        kind, p = raw.get("kind"), raw.get("payload", {})
        if not isinstance(p, dict):
            raise ValueError("Explanation payload must be an object")
        allowed = {
            "explain": {"concept", "lab", "depth", "mode", "selector", "reveal", "source"},
            "what_if": {"kind", "lab", "inputs"},
            "quiz": {"concept", "lab", "mode", "selector"},
            "replay_hook": {"lab"},
            "example": {"id"},
        }
        if kind not in allowed or set(p) - allowed[kind]:
            raise ValueError("Unknown explanation command or fields")
        if kind == "explain":
            return self.explain(**p)
        if kind == "what_if":
            return self.what_if(**p)
        if kind == "quiz":
            return self.quiz(**p)
        if kind == "replay_hook":
            return self.replay_hook(**p)
        from quantlab.explainability.examples import example

        return example(p["id"])

    def catalog(self):
        return dict(
            schema=SCHEMA,
            concepts=[c.public() for c in CONCEPTS.values()],
            labs=LAB_CONCEPTS,
            assumptions=ASSUMPTIONS,
            depths=DEPTHS,
            graphs=[graph(i) for i in range(6)],
            search_note=(
                "Local keyword and alias matching; no external language model or "
                "semantic-search claim."
            ),
        )
