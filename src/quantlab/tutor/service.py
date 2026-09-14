"""Adaptive teaching coordinator. It can observe public facts, never trade or draw RNG."""

from datetime import timedelta
from fractions import Fraction
from typing import Protocol

from quantlab.research.codec import digest
from quantlab.tutor.catalog import ACTIVE_CONCEPTS as CONCEPTS
from quantlab.tutor.context import context_from_dict, trading_contexts
from quantlab.tutor.progress import Progress
from quantlab.tutor.questions import describe, question_for, relevant


class OptionalLanguageLayer(Protocol):
    """Future adapter only. No implementation, API key, network or automatic invocation."""

    def discuss(self, public_context: dict, ungraded_text: str) -> str: ...


class Tutor:
    def __init__(self, progress=None):
        self.progress = progress or Progress()
        self.active = self.progress.data["active"]
        self.contexts = {
            k: context_from_dict(v) for k, v in self.progress.data["contexts"].items()
        }
        self.seen = set()
        self.asked = set()
        self.last_question_event = {}
        self.events = []
        self.revision = 0
        self.last_source = None
        self._latest_book = None

    def observe(self, snapshot, source):
        candidates = []
        changed = False

        # Rewinding playback must not retain a question or context from a later frame.
        def ahead(context):
            return context.source == source and (
                context.event > snapshot["public_event"]
                or context.time_us > snapshot["time_us"]
            )

        future = [key for key, context in self.contexts.items() if ahead(context)]
        if future or (self.active and ahead(context_from_dict(self.active["context"]))):
            self.active = None
            for key in future:
                self.contexts.pop(key)
                self.progress.data["contexts"].pop(key, None)
            self.seen.clear()
            self.last_question_event[source] = snapshot["public_event"]
            self._latest_book = None
            changed = True
        if not self.progress.data["settings"]["enabled"]:
            if changed:
                self.revision += 1
                self._persist()
            return
        for context in trading_contexts(snapshot, source):
            facts = dict(context.facts)
            # An unchanged order/position isn't a new educational event on every clock tick.
            signature_facts = context.public()["facts"]
            if context.kind == "execution":
                signature_facts = {
                    k: v
                    for k, v in signature_facts.items()
                    if k not in ("position", "limit", "reference")
                }
            signature = digest(
                {"source": source, "kind": context.kind, "facts": signature_facts}
            )
            if signature in self.seen:
                continue
            self.seen.add(signature)
            changed = True
            pairs = relevant(context)
            if (
                context.kind == "book"
                and self._latest_book
                and self._latest_book.source == source
            ):
                old = self._latest_book.facts["spread"]
                if (
                    old is not None
                    and facts["spread"] is not None
                    and Fraction(facts["spread"]) > Fraction(old)
                ):
                    pairs += [("liquidity", 70)]
            if context.kind == "book":
                self._latest_book = context
            for concept, relevance in pairs:
                self.contexts[concept] = context
                self.progress.data["contexts"][concept] = context.public()
                self.progress.encounter(concept)
                self.events.append(
                    {
                        "source": source,
                        "event": context.event,
                        "concept": concept,
                        "context": context.public(),
                        "relevance": relevance,
                    }
                )
                candidates.append((relevance, concept, context))
        self.last_source = source
        settings = self.progress.data["settings"]
        gap = snapshot["public_event"] - self.last_question_event.get(
            source, -settings["event_gap"]
        )
        if candidates and snapshot["public_event"] > 0 and gap >= settings["event_gap"]:
            if self.active is None or (
                self.active["closed"] and self.active["stage"] != "decide"
            ):
                # Weak/repeated concepts can beat a similarly relevant novelty, but not flood.
                def rank(item):
                    score, concept, _ = item
                    errors = self.progress.data["concepts"].get(concept, {}).get("incorrect", 0)
                    return score + min(errors, 3) * 3

                due = [
                    row["concept"]
                    for row in self.progress.due()
                    if row["concept"] in self.contexts
                ]
                if due:
                    self.ask(due[0])
                for _, concept, context in (
                    [] if due else sorted(candidates, key=rank, reverse=True)
                ):
                    fingerprint = self._fingerprint(concept, context)
                    if fingerprint not in self.asked:
                        self.ask(concept, context=context)
                        self.last_question_event[source] = snapshot["public_event"]
                        break
        self.events = self.events[-2000:]
        if changed:
            self.revision += 1
            self._persist()

    def _persist(self):
        self.progress.data["active"] = self.active
        self.progress.save()

    def study(self, contexts, concept=None):
        "Register verified research or public Phase 4 observations, never raw observer data."
        if not self.progress.data["settings"]["enabled"]:
            raise ValueError("Tutor is disabled")
        candidates = []
        for context in contexts:
            for key, relevance in relevant(context):
                self.contexts[key] = context
                self.progress.data["contexts"][key] = context.public()
                self.progress.encounter(key)
                candidates.append((relevance, key, context))
        if not candidates:
            raise ValueError("No supported teaching event in those observations")
        selected = next((row for row in candidates if row[1] == concept), None)
        if concept and selected is None:
            raise ValueError("Concept did not occur in those observations")
        _, key, context = selected or max(candidates, key=lambda row: row[0])
        return self.ask(key, context=context)

    def observe_derivative(self, context):
        """Passive contextual integration; obey the same learner settings and cadence."""
        if context.kind not in ("derivatives", "risk", "statarb"):
            raise ValueError("Expected public derivative facts")
        source = context.source
        future = [
            k
            for k, c in self.contexts.items()
            if c.source == source and (c.event > context.event or c.time_us > context.time_us)
        ]
        active_future = (
            self.active
            and self.active["context"]["source"] == source
            and (
                self.active["context"]["event"] > context.event
                or self.active["context"]["time_us"] > context.time_us
            )
        )
        if future or active_future:
            self.active = None
            for key in future:
                self.contexts.pop(key)
                self.progress.data["contexts"].pop(key, None)
            self.seen.clear()
        if not self.progress.data["settings"]["enabled"]:
            if future or active_future:
                self._persist()
            return
        signature = digest({"source": source, "facts": context.public()["facts"]})
        if signature in self.seen:
            return
        self.seen.add(signature)
        candidates = relevant(context)
        for key, _ in candidates:
            self.contexts[key] = context
            self.progress.data["contexts"][key] = context.public()
            self.progress.encounter(key)
        gap = self.progress.data["settings"]["event_gap"]
        ready = self.active is None or (
            self.active["closed"] and self.active["stage"] != "decide"
        )
        if (
            candidates
            and context.event > 0
            and ready
            and context.event - self.last_question_event.get(source, -gap) >= gap
        ):
            self.ask(max(candidates, key=lambda row: row[1])[0], context=context)
            self.last_question_event[source] = context.event
        self.revision += 1
        self._persist()

    def _fingerprint(self, concept, context, level=None):
        return digest(
            {
                "concept": concept,
                "level": level,
                "kind": context.kind,
                "source": context.source,
                "facts": context.public()["facts"],
            }
        )

    def ask(self, concept=None, *, context=None, mode="learn", prediction=False):
        if not self.progress.data["settings"]["enabled"]:
            raise ValueError("Tutor is disabled; trading remains available")
        if mode not in ("learn", "interview", "defence"):
            raise ValueError("Unknown tutor mode")
        if concept is None:
            due = [r["concept"] for r in self.progress.due() if r["concept"] in self.contexts]
            concept = due[0] if due else next(reversed(self.contexts), None)
        if (
            mode in ("interview", "defence")
            and context is None
            and concept not in self.contexts
        ):
            # Project defence still points at this real implemented public session.
            context = self._latest_book or next(iter(self.contexts.values()), None)
        context = context or self.contexts.get(concept)
        if context is None or concept not in CONCEPTS or not CONCEPTS[concept].implemented:
            raise ValueError("No encountered context for that concept yet")
        item = self.progress.record_for(concept)
        assessed = all(
            self.progress.record_for(p)["attempts"] > 0 for p in CONCEPTS[concept].prerequisites
        )
        level = item["level"] if assessed else 1
        if mode != "learn" and assessed:
            level = min(4, level + 1)
        actual_level = question_for(concept, context, level, prediction=prediction).difficulty
        if (
            level == 2
            and actual_level == 1
            and (item["level"] >= 2 or (mode != "learn" and item["attempts"] > 0))
        ):
            # Qualitative concepts do not get artificial arithmetic exercises.
            actual_level = 3
            if mode == "learn":
                item["level"] = 3
        level = actual_level
        identifier = self.progress.data["next_question"]
        self.progress.data["next_question"] += 1
        self.active = {
            "id": f"q-{identifier}",
            "concept": concept,
            "level": level,
            "context": context.public(),
            "mode": mode,
            "prediction": prediction,
            "stage": "predict" if prediction else "test",
            "attempts": 0,
            "hints": 0,
            "revealed": False,
            "closed": False,
            "feedback": None,
            "learning_update": None,
            "started": self.progress.clock().isoformat(),
            "result": None,
        }
        self.asked.add(self._fingerprint(concept, context))
        self.last_question_event[context.source] = context.event
        self.progress.encounter(concept)
        self.revision += 1
        self._persist()
        return self.view()

    def _question(self):
        if self.active is None:
            raise ValueError("No current question")
        return question_for(
            self.active["concept"],
            context_from_dict(self.active["context"]),
            self.active["level"],
            prediction=self.active["prediction"],
        )

    def _require_enabled(self):
        if not self.progress.data["settings"]["enabled"]:
            raise ValueError("Tutor is disabled; trading remains available")

    def answer(self, question_id, answer):
        self._require_enabled()
        q = self._question()
        current = self.active
        if current["id"] != question_id or current["closed"]:
            raise ValueError("That question has already finished or changed")
        correct = q.validate(answer)  # Invalid types/nonsense are not graded conceptual errors.
        current["attempts"] += 1
        helped = current["hints"] > 0 or current["attempts"] > 1
        # Record selected claims, never arbitrary free text or full snapshots.
        selected = (
            dict(q.options).get(answer, str(answer))
            if isinstance(answer, str)
            else "; ".join(dict(q.options)[a] for a in answer)
            if isinstance(answer, list)
            else str(answer)
        )
        evidence = f"{q.concept}, {current['id']}: selected {selected[:300]}"
        current["learning_update"] = self.progress.grade(
            concept=q.concept,
            question_id=current["id"],
            fingerprint=self._fingerprint(
                q.concept, context_from_dict(current["context"]), q.difficulty
            ),
            correct=correct,
            assisted=helped,
            attempt=current["attempts"],
            misconception=(
                f"{q.concept}:{answer}"
                if q.answer_type == "choice"
                else f"{q.concept}:reasoning"
                if q.answer_type == "choices"
                else f"{q.concept}:calculation"
            ),
            evidence=evidence,
            level=q.difficulty,
            revealed=current["revealed"],
            source=current["context"]["source"],
            mode=current["mode"],
        )
        if current["mode"] != "learn":
            current["closed"] = True
            current["stage"] = "debrief"
            current["feedback"] = (
                "Answer recorded. Request the debrief when ready; no immediate explanation."
            )
        elif correct:
            current["closed"] = True
            current["stage"] = "decide" if current["prediction"] else "explain"
            current["revealed"] = not current["prediction"]
            current["feedback"] = "Correct for the recorded context." + (
                " Choose your trade freely; the market may have changed."
                if current["prediction"]
                else ""
            )
        elif current["attempts"] >= self.progress.data["settings"]["max_attempts"]:
            current["closed"] = True
            current["revealed"] = True
            current["stage"] = "explain"
            current["feedback"] = (
                "This answer did not match the rule. Review the worked explanation."
            )
        else:
            current["hints"] = min(2, max(current["hints"], current["attempts"]))
            current["feedback"] = "Not yet. " + q.hints[current["hints"] - 1]
        if current["revealed"]:
            self._block_revealed_credit(q.difficulty)
        self.revision += 1
        self._persist()
        return self.view()

    def _block_revealed_credit(self, level):
        item = self.progress.record_for(self.active["concept"])
        key = (
            self.progress.clock().date().isoformat()
            + ":"
            + self._fingerprint(
                self.active["concept"], context_from_dict(self.active["context"]), level
            )
        )
        if key not in item["credited_keys"]:
            item["credited_keys"] = (item["credited_keys"] + [key])[-200:]

    def hint(self):
        self._require_enabled()
        q = self._question()
        if self.active["closed"]:
            raise ValueError("This question has finished")
        maximum = 2 if self.active["mode"] == "learn" else 1
        if self.active["hints"] >= maximum:
            raise ValueError(
                "No more hints in this mode; submit an answer or request explanation"
            )
        self.active["hints"] += 1
        self.active["feedback"] = q.hints[self.active["hints"] - 1]
        self.revision += 1
        self._persist()
        return self.view()

    def explain(self, deeper=False):
        self._require_enabled()
        self._question()
        self.active["revealed"] = True
        self.active["closed"] = True
        self.active["stage"] = "explain"
        self.active["feedback"] = "Explanation requested; viewing earns no mastery credit."
        self.active["deeper"] = deeper
        item = self.progress.record_for(self.active["concept"])
        self._block_revealed_credit(self.active["level"])
        if deeper:
            self._block_revealed_credit(self._deeper_question().difficulty)
        if item["due"] is None:
            item["due"] = (self.progress.clock() + timedelta(days=1)).isoformat()
        self.revision += 1
        self._persist()
        return self.view()

    def trading_result(self, snapshot, source):
        if (
            self.active
            and self.active["stage"] == "decide"
            and self.active["context"]["source"] == source
        ):
            if (
                snapshot["orders"]
                and snapshot["public_event"] > self.active["context"]["event"]
            ):
                context = next(
                    c
                    for c in reversed(trading_contexts(snapshot, source))
                    if c.kind == "execution"
                )
                self.active.update(result=describe(context), revealed=True, stage="explain")
                self.last_question_event[source] = snapshot["public_event"]
                self.revision += 1
                self._persist()

    def _deeper_question(self):
        q = self._question()
        context = context_from_dict(self.active["context"])
        deeper = question_for(q.concept, context, min(4, q.difficulty + 1))
        if deeper.difficulty <= q.difficulty and q.difficulty < 3:
            deeper = question_for(q.concept, context, 3)
        return deeper

    def view(self):
        active = None
        if self.active:
            q = self._question()
            current = self.active
            active = {
                k: current[k]
                for k in (
                    "id",
                    "mode",
                    "stage",
                    "attempts",
                    "hints",
                    "closed",
                    "feedback",
                    "learning_update",
                    "result",
                    "started",
                )
            }
            if current["mode"] != "learn" and not current["revealed"]:
                active["learning_update"] = None
            active["question"] = q.public(current["revealed"])
            active["why"] = (
                f"Use {CONCEPTS[q.concept].title.lower()} to explain this recorded "
                f"{current['context']['kind']} context and defend the assumptions "
                "behind your reasoning."
            )
            if current.get("deeper"):
                active["deeper"] = self._deeper_question().public(True)
        return {
            "revision": self.revision,
            "enabled": self.progress.data["settings"]["enabled"],
            "current": active if self.progress.data["settings"]["enabled"] else None,
            "due_count": len(self.progress.due()),
            "encountered": sorted(self.contexts),
        }

    def configure(self, **settings):
        if set(settings) - {"enabled", "event_gap", "max_attempts"}:
            raise ValueError("Unknown tutor setting")
        for name, value in settings.items():
            if name == "enabled":
                if type(value) is not bool:
                    raise ValueError("enabled must be true/false")
            elif type(value) is not int or not (
                1 <= value <= (100 if name == "event_gap" else 5)
            ):
                raise ValueError("Tutor setting outside range")
        self.progress.data["settings"].update(settings)
        self.revision += 1
        self._persist()
        return self.view()

    def review(self, snapshot, source):
        if snapshot["status"] != "ended":
            raise ValueError("End the session before requesting post-session review")
        contexts = trading_contexts(snapshot, source)
        encountered = {concept: c for c in contexts for concept, _ in relevant(c)}
        actions = snapshot["report"]["decisions"]
        well = []
        for action in actions:
            if action["message"].startswith("You cancel"):
                well.append(
                    f"At {action['time_us'] / 1e6:.6f}s you removed outstanding orders. "
                    "That released their reserved capacity; intent is not inferred."
                )
        updates = [r for r in self.progress.data["recent"] if r["source"] == source]
        ranked = sorted(
            encountered.items(),
            key=lambda pair: max(score for key, score in relevant(pair[1]) if key == pair[0]),
            reverse=True,
        )
        for r in updates:
            if r["correct"] and r["credited"] and r["result"] == "correct_first":
                well.append(
                    f"On {r['question_id']}, your first answer applied "
                    f"{r['concept']} correctly "
                    "to its recorded public context; this assesses that answer, "
                    "not the trade's quality."
                )
        questions = [question_for(k, c).public(False) for k, c in ranked[:3]]
        while len(questions) < 3:
            concept = ("decision_quality", "architecture", "research_integrity")[len(questions)]
            questions.append(question_for(concept, contexts[0]).public(False))
        improvements = []
        for c in contexts:
            if c.kind == "position" and abs(c.facts["position"]) >= c.facts["limit"] * 0.7:
                improvements.append(
                    "The recorded position uses at least 70% of the limit; review "
                    "directional exposure."
                )
        wrong = [r for r in updates if not r["correct"]]
        improvements += [r["evidence"] for r in wrong[-3:]]
        return {
            "what_happened": {
                k: snapshot["report"][k]
                for k in ("final_pnl", "trade_count", "fees", "maximum_drawdown")
            },
            "what_you_did_well": well
            or [
                (
                    "No reasoning-based assessment is available; actions alone do not "
                    "establish a good decision."
                )
            ],
            "what_to_improve": improvements
            or [
                (
                    "No specific misconception or limit behaviour was recorded. This is "
                    "not a claim of mastery."
                )
            ],
            "concepts_encountered": sorted(encountered),
            "mastery_updates": updates,
            "three_questions": questions,
            "interview": question_for("decision_quality", contexts[0], 3).public(False),
            "known_then": [
                {
                    "time_us": a["time_us"],
                    "order": "Order submission (pre-match public view)",
                    "observed": a["observed_before"],
                }
                for a in actions
                if "observed_before" in a
            ],
            "later_public": [
                {
                    "time_us": a["time_us"],
                    "reference": a["reference"],
                    "position": a["position"],
                }
                for a in actions
            ],
            "decision_vs_outcome": [
                "Good decision + good outcome",
                "Good decision + bad outcome",
                "Bad decision + good outcome",
                "Bad decision + bad outcome",
            ],
            "assessment": (
                "Financial outcomes do not identify which "
                "decision-quality quadrant applies without "
                "contemporaneous reasoning."
            ),
        }

    def reset(self):
        self.progress.reset()
        self.active = None
        self.contexts.clear()
        self.seen.clear()
        self.asked.clear()
        self.events.clear()
        self.last_question_event.clear()
        self._latest_book = self.last_source = None
        self.revision += 1
