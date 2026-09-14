"""Current public-environment questions with the existing tutor validator and grader."""

from quantlab.research.codec import digest
from quantlab.tutor.questions import Question


class EnvironmentTutor:
    def __init__(self, learning):
        self.learning = learning
        self.active = None

    def ask(self, snapshot, concept=None, mode="learn"):
        progress = self.learning.tutor.progress
        if not progress.data["settings"]["enabled"]:
            raise ValueError("Tutor is disabled; trading remains available")
        if mode not in ("learn", "interview", "defence"):
            raise ValueError("Unknown tutor mode")
        env = snapshot["environment"]
        hist = env["type"] == "HISTORICAL"
        hidden = env.get("hidden", False)
        if hist:
            prompt = (
                "These revealed recorded prices changed. Can prices alone "
                "establish why the real market moved?"
            )
            if env.get("data_kind") == "artificial_fixture":
                prompt = (
                    "These artificial test bars changed. Would a real recorded price "
                    "path alone establish why a market moved?"
                )
            options = (
                ("supported", "No. They record movement; causal claims need further evidence."),
                ("cause", "Yes. A falling price proves a hidden true value fell."),
            )
            text = f"Observation {snapshot['index']}, {snapshot['timestamp']}. " + "; ".join(
                f"{k} current close £{v[-1]['close']:.4f}"
                for k, v in snapshot["observations"].items()
            )
        elif hidden:
            prompt = (
                "What would support a claim that displayed liquidity is "
                "deteriorating in this session?"
            )
            options = (
                (
                    "supported",
                    (
                        "Observe reduced displayed quantity, wider quotes or poorer "
                        "actual fills; the hidden regime remains unproven."
                    ),
                ),
                ("cause", "The hidden scenario must be toxic, regardless of the public book."),
            )
            text = (
                f"Scenario Session, public observation {snapshot['index']}. "
                "Only displayed prices, quantities and your executions are evidence."
            )
        else:
            prompt = (
                "A parameter was explicitly configured in this synthetic "
                "experiment. What does the result establish?"
            )
            options = (
                (
                    "supported",
                    (
                        "Evidence conditional on this controlled model; it is not a "
                        "real-market forecast."
                    ),
                ),
                ("cause", "The same outcome must occur in a real market."),
            )
            text = (
                snapshot["environment"]["title"]
                + f", public observation {snapshot['index']}. "
                + snapshot["configuration"]["mechanism"]
            )
        q = Question(
            "decision_quality",
            1,
            prompt,
            "choice",
            "supported",
            options,
            (
                "Separate observation from inference.",
                "A model and a real market are different sources of evidence.",
            ),
            "Distinguish what was observed from what is assumed.",
            "No formula establishes real-world causation from prices alone.",
            text,
            "What additional evidence would change your conclusion?",
            "Treating a precise result as causal proof.",
        )
        if concept == "vwap" and snapshot["engine"] == "historical":
            orders = [o for o in snapshot["orders"] if o["filled"]]
            if orders:
                from quantlab.execution import vwap

                order = orders[-1]
                fills = order["fills"]
                expected = str(vwap((f["exact_price"], f["quantity"]) for f in fills))
                q = Question(
                    "vwap",
                    1,
                    "What is this paper order's executed VWAP in pounds?",
                    "number",
                    expected,
                    (),
                    (
                        "Weight each execution price by its quantity.",
                        "Divide by total executed units.",
                    ),
                    "Larger fills contribute more to the average.",
                    "VWAP = sum(price times quantity) / sum(quantity)",
                    "SIMULATED HISTORICAL EXECUTION: "
                    + "; ".join(f"{f['quantity']} units at £{f['exact_price']}" for f in fills),
                    "Why does unfilled quantity not enter VWAP?",
                    "Including unfilled units.",
                    tolerance="0.00001",
                )
                prompt, text = q.prompt, q.quantlab
        n = progress.data["next_question"]
        progress.data["next_question"] += 1
        progress.encounter(q.concept)
        progress.save()
        self.active = {
            "id": f"env-q-{n}",
            "question": q,
            "point": digest(snapshot),
            "closed": False,
            "mode": mode,
            "source": "environment-public",
            "fingerprint": digest({"prompt": prompt, "context": text}),
            "feedback": None,
        }
        return self.view()

    def view(self):
        if not self.active:
            return {"current": None}
        a = self.active
        return {
            "current": {
                "id": a["id"],
                "question": a["question"].public(),
                "closed": a["closed"],
                "feedback": a["feedback"],
                "mode": a["mode"],
            },
            "note": (
                "Only submitted answer evidence is graded; reading does not increase mastery."
            ),
        }

    def answer(self, snapshot, question_id, answer):
        a = self.active
        if not a or a["closed"] or a["id"] != question_id:
            raise ValueError("Choose the current unanswered question")
        if digest(snapshot) != a["point"]:
            raise ValueError("The public context changed; ask a question at the current point")
        correct = a["question"].validate(answer)
        p = self.learning.tutor.progress
        if not p.data["settings"]["enabled"]:
            raise ValueError("Tutor is disabled")
        result = p.grade(
            concept=a["question"].concept,
            question_id=a["id"],
            fingerprint=a["fingerprint"],
            correct=correct,
            assisted=False,
            attempt=1,
            misconception="decision_quality:environment",
            evidence="Environment question: " + str(answer),
            level=1,
            revealed=False,
            source=a["source"],
            mode=a["mode"],
        )
        p.save()
        a["closed"] = True
        a["feedback"] = (
            "Correct for the public evidence."
            if correct
            else (
                "The observations do not establish the proposed cause. Review the "
                "environment assumptions."
            )
        )
        return self.view() | {"learning_update": result}
