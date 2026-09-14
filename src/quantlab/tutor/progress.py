"""Transparent answer evidence and atomic local storage, independent of market time/RNG."""

import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

from quantlab.research.codec import plain
from quantlab.tutor.catalog import ACTIVE_CONCEPTS as CONCEPTS
from quantlab.tutor.catalog import DOMAINS
from quantlab.tutor.context import context_from_dict


def now_utc():
    return datetime.now(UTC)


def blank():
    return {
        "schema": 1,
        "concepts": {},
        "mistakes": {},
        "recent": [],
        "next_question": 1,
        "contexts": {},
        "active": None,
        "settings": {"enabled": True, "event_gap": 8, "max_attempts": 3},
    }


class Progress:
    def __init__(self, path=None, *, clock=now_utc):
        self.path = Path(path) if path is not None else None
        self.clock = clock
        self.data = blank()
        if self.path is not None and self.path.exists():
            try:
                data = json.loads(self.path.read_text())
                self._validate(data)
                self.data = data
            except (ValueError, KeyError, TypeError, AttributeError, OverflowError) as exc:
                raise ValueError(
                    "Learning progress is corrupt; preserve it and use explicit reset"
                ) from exc

    @staticmethod
    def _validate(data):
        if not isinstance(data, dict) or data.get("schema") != 1 or set(data) != set(blank()):
            raise ValueError("Unknown progress schema")
        for field in ("concepts", "contexts", "mistakes", "settings"):
            if not isinstance(data[field], dict):
                raise ValueError("Invalid saved learning collection")
        if not isinstance(data["recent"], list):
            raise ValueError("Invalid saved answer history")

        def entry_check(entry, *, summary):
            expected = {
                "question_id",
                "concept",
                "correct",
                "result",
                "credited",
                "credit",
                "level",
                "at",
                "evidence",
                "source",
                "mode",
            }
            if summary:
                expected |= {"before", "after"}
            if not isinstance(entry, dict) or set(entry) != expected:
                raise ValueError("Unexpected answer-history fields")
            if entry["concept"] not in CONCEPTS or type(entry["correct"]) is not bool:
                raise ValueError("Invalid answer evidence")
            if entry["mode"] not in ("learn", "interview", "defence") or entry["level"] not in (
                1,
                2,
                3,
                4,
            ):
                raise ValueError("Invalid answer mode or level")
            if summary:
                for key in ("before", "after"):
                    if set(entry[key]) != {"category", "score"}:
                        raise ValueError("Unexpected score fields")

        for entry in data["recent"]:
            entry_check(entry, summary=True)
        for mistake in data["mistakes"].values():
            if set(mistake) != {"concept", "questions", "evidence", "last_seen"}:
                raise ValueError("Unexpected misconception fields")
            if mistake["concept"] not in CONCEPTS:
                raise ValueError("Invalid misconception concept")
        if not set(data["contexts"]) <= set(CONCEPTS):
            raise ValueError("Unknown saved context concept")
        for context in data["contexts"].values():
            context_from_dict(context)
        settings = data["settings"]
        if (
            set(settings) != {"enabled", "event_gap", "max_attempts"}
            or type(settings["enabled"]) is not bool
        ):
            raise ValueError("Invalid tutor settings")
        for key, maximum in (("event_gap", 100), ("max_attempts", 5)):
            if type(settings[key]) is not int or not 1 <= settings[key] <= maximum:
                raise ValueError("Invalid tutor frequency or attempts")
        if data["active"] is not None:
            active = data["active"]
            allowed = {
                "id",
                "concept",
                "level",
                "context",
                "mode",
                "prediction",
                "stage",
                "attempts",
                "hints",
                "revealed",
                "closed",
                "feedback",
                "learning_update",
                "started",
                "result",
                "deeper",
            }
            if set(active) - allowed or active["concept"] not in CONCEPTS:
                raise ValueError("Invalid active question")
            context_from_dict(active["context"])
            if active["learning_update"] is not None:
                entry_check(active["learning_update"], summary=True)
        if not set(data["concepts"]) <= set(CONCEPTS):
            raise ValueError("Unknown learning concept")
        if type(data["next_question"]) is not int or data["next_question"] < 1:
            raise ValueError("Invalid question sequence")
        for item in data["concepts"].values():
            expected = {
                "attempts",
                "correct_first",
                "correct_after_hint",
                "incorrect",
                "last_encountered",
                "last_answered",
                "due",
                "credits",
                "success_streak",
                "level",
                "level_successes",
                "recent",
                "credited_keys",
                "encounters",
            }
            if set(item) != expected:
                raise ValueError("Unexpected concept-record fields")
            for entry in item["recent"]:
                entry_check(entry, summary=False)
            if item["level"] not in (1, 2, 3, 4):
                raise ValueError("Invalid difficulty")
            for key in ("attempts", "correct_first", "correct_after_hint", "incorrect"):
                if type(item[key]) is not int or item[key] < 0:
                    raise ValueError("Invalid answer counts")
            if (
                item["attempts"]
                != item["correct_first"] + item["correct_after_hint"] + item["incorrect"]
            ):
                raise ValueError("Answer counts do not reconcile")
            if len(item["credits"]) > 10 or any(
                type(x) not in (int, float) or x not in (0, 0.5, 1) for x in item["credits"]
            ):
                raise ValueError("Invalid mastery credit")

    def save(self):
        self._validate(self.data)
        if self.path is None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(self.path.suffix + ".tmp")
        with temp.open("w", encoding="utf-8") as output:
            json.dump(self.data, output, indent=2, sort_keys=True, allow_nan=False)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        temp.replace(self.path)

    def record_for(self, concept):
        if concept not in CONCEPTS:
            raise ValueError("Unknown concept")
        return self.data["concepts"].setdefault(
            concept,
            {
                "attempts": 0,
                "correct_first": 0,
                "correct_after_hint": 0,
                "incorrect": 0,
                "last_encountered": None,
                "last_answered": None,
                "due": None,
                "credits": [],
                "success_streak": 0,
                "level": 1,
                "level_successes": 0,
                "recent": [],
                "credited_keys": [],
                "encounters": 0,
            },
        )

    def encounter(self, concept):
        item = self.record_for(concept)
        item["last_encountered"] = self.clock().isoformat()
        item["encounters"] += 1

    def grade(
        self,
        *,
        concept,
        question_id,
        fingerprint,
        correct,
        assisted,
        attempt,
        misconception,
        evidence,
        level,
        revealed=False,
        source="",
        mode="learn",
    ):
        item = self.record_for(concept)
        now = self.clock()
        before = self.status(concept)
        item["attempts"] += 1
        result = (
            "correct_first"
            if correct and not assisted and attempt == 1 and not revealed
            else ("correct_after_hint" if correct else "incorrect")
        )
        item[result] += 1
        item["last_answered"] = now.isoformat()
        key = now.date().isoformat() + ":" + fingerprint
        # Repeated practice after completion/reveal gives counts but no extra score.
        eligible = key not in item["credited_keys"] and not revealed
        credit = (1 if result == "correct_first" else 0.5) if correct else 0
        if eligible:
            item["credits"] = (item["credits"] + [credit])[-10:]
        if correct or revealed:
            item["credited_keys"] = (item["credited_keys"] + [key])[-200:]
        if not correct:
            item["success_streak"] = item["level_successes"] = 0
            days = 1
            if misconception:
                error = self.data["mistakes"].setdefault(
                    misconception,
                    {"concept": concept, "questions": [], "evidence": [], "last_seen": None},
                )
                if question_id not in error["questions"]:
                    error["questions"].append(question_id)
                    error["evidence"] = (error["evidence"] + [evidence])[-5:]
                error["last_seen"] = now.isoformat()
            if len(item["recent"]) >= 1 and not item["recent"][-1]["correct"]:
                item["level"] = max(1, item["level"] - 1)
        elif result == "correct_first" and eligible:
            item["success_streak"] += 1
            item["level_successes"] += 1
            days = (3, 7, 14, 30)[min(item["success_streak"] - 1, 3)]
            assessed = all(
                self.record_for(p)["attempts"] > 0 for p in CONCEPTS[concept].prerequisites
            )
            if level == item["level"] and item["level_successes"] >= 3 and assessed:
                item["level"] = min(4, item["level"] + 1)
                item["level_successes"] = 0
        else:
            item["success_streak"] = 0
            days = 2 if not revealed else 1
        item["due"] = (now + timedelta(days=days)).isoformat()
        entry = {
            "question_id": question_id,
            "concept": concept,
            "correct": correct,
            "result": result,
            "credited": eligible,
            "credit": credit if eligible else None,
            "level": level,
            "at": now.isoformat(),
            "evidence": evidence,
            "source": source,
            "mode": mode,
        }
        item["recent"] = (item["recent"] + [entry])[-10:]
        after = self.status(concept)
        entry = entry | {"before": before, "after": after}
        self.data["recent"] = (self.data["recent"] + [entry])[-200:]
        self.save()
        return entry

    def status(self, concept):
        item = self.data["concepts"].get(concept)
        if item is None or not item["credits"]:
            return {"category": "Not assessed", "score": None}
        n = len(item["credits"])
        score = 100 * (1 + sum(item["credits"])) / (2 + n)
        category = "Beginning"
        if n >= 3 and score >= 40:
            category = "Developing"
        if n >= 6 and score >= 70:
            category = "Comfortable"
        if n >= 10 and score >= 85:
            category = "Strong"
        return {"category": category, "score": 5 * round(score / 5)}

    def due(self):
        now = self.clock()
        rows = []
        for key, item in self.data["concepts"].items():
            if item["due"] and datetime.fromisoformat(item["due"]) <= now:
                repeated = sum(
                    len(m["questions"]) >= 2 and m["concept"] == key
                    for m in self.data["mistakes"].values()
                )
                foundations = sum(key in c.prerequisites for c in CONCEPTS.values())
                overdue = (now - datetime.fromisoformat(item["due"])).days
                rows.append(
                    {
                        "concept": key,
                        "due": item["due"],
                        "priority": 4 * repeated + min(overdue, 30) + foundations,
                        "reason": f"{overdue} days overdue; "
                        f"{repeated} repeated misconceptions; "
                        f"prerequisite for {foundations} concepts",
                    }
                )
        return sorted(rows, key=lambda r: (-r["priority"], r["concept"]))

    def dashboard(self):
        domains = []
        concepts = []
        due = {r["concept"]: r for r in self.due()}
        for key, concept in CONCEPTS.items():
            item = self.data["concepts"].get(key, {})
            concepts.append(
                {
                    "id": key,
                    "title": concept.title,
                    "domain": concept.domain,
                    "implemented": concept.implemented,
                    "prerequisites": concept.prerequisites,
                    **self.status(key),
                    "attempts": item.get("attempts", 0),
                    "correct_first": item.get("correct_first", 0),
                    "correct_after_hint": item.get("correct_after_hint", 0),
                    "incorrect": item.get("incorrect", 0),
                    "level": item.get("level", 1),
                    "last_encountered": item.get("last_encountered"),
                    "last_answered": item.get("last_answered"),
                    "review_at": item.get("due"),
                    "due": due.get(key),
                    "recent_performance": [r["result"] for r in item.get("recent", [])],
                }
            )
        for name in DOMAINS:
            members = [c for c in concepts if c["domain"] == name]
            assessed = [c for c in members if c["score"] is not None]
            domains.append(
                {
                    "domain": name,
                    "assessed": len(assessed),
                    "total": len(members),
                    "attempts": sum(c["attempts"] for c in members),
                    "status": "Not assessed"
                    if not assessed
                    else "Evidence in " + str(len(assessed)) + " concepts",
                    "weak": [
                        c["title"]
                        for c in assessed
                        if c["category"] in ("Beginning", "Developing")
                    ],
                }
            )
        mistakes = [
            {
                "id": key,
                **value,
                "classification": "Repeated misconception"
                if len(value["questions"]) >= 2
                else "One-off error",
            }
            for key, value in self.data["mistakes"].items()
        ]
        return {
            "domains": domains,
            "concepts": concepts,
            "mistakes": mistakes,
            "due": self.due(),
            "recent": self.data["recent"],
            "strong": [c["id"] for c in concepts if c["category"] in ("Comfortable", "Strong")],
            "weak": [c["id"] for c in concepts if c["category"] in ("Beginning", "Developing")],
            "settings": dict(self.data["settings"]),
            "note": (
                "Practice categories describe answer evidence, not calibrated "
                "mastery probabilities."
            ),
        }

    def export(self, markdown=False):
        view = self.dashboard()
        if not markdown:
            return plain({"schema": 1, "learning": view})
        lines = ["# QuantLab learning revision", "", view["note"], "", "## Concepts"]
        for item in view["concepts"]:
            if item["attempts"]:
                lines.append(
                    f"- {item['title']}: {item['category']}; {item['attempts']} answers, "
                    f"{item['correct_first']} first-attempt successes, "
                    f"{item['incorrect']} incorrect."
                )
        lines += [
            "",
            "## Strong concepts",
            ", ".join(view["strong"]) or "Not enough evidence yet.",
            "",
            "## Weak concepts",
            ", ".join(view["weak"]) or "None assessed as weak yet.",
        ]
        lines += ["", "## Common mistakes"] + [
            f"- {m['classification']}: {m['id']} — " + "; ".join(m["evidence"])
            for m in view["mistakes"]
        ]
        lines += ["", "## Recommended review"] + [
            f"- {r['concept']}: {r['reason']}" for r in view["due"]
        ]
        lines += ["", "## Recent questions"] + [
            f"- {r['question_id']}: {r['concept']} — {r['result']}"
            for r in view["recent"][-20:]
        ]
        return "\n".join(lines) + "\n"

    def reset(self):
        self.data = blank()
        self.save()
