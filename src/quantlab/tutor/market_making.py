"""Prediction, hint, retry and delayed explanation for the manual maker loop."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Lesson:
    question: str
    accepted: tuple[str, ...]
    hint: str
    explanation: str


LESSONS = (
    Lesson(
        "Scenario: you are long 5 units. To reduce inventory, "
        "should the quote centre move up or down?",
        ("down", "downward", "lower"),
        "Think about which change discourages another purchase "
        "while encouraging someone to buy from you.",
        "Down: a lower bid discourages more buying; "
        "a lower ask makes selling existing inventory easier.",
    ),
    Lesson(
        "Scenario: tight spreads, many fills, consistently negative provider markouts. "
        "Could better-informed takers be picking off your quotes? Answer yes or no.",
        ("yes", "y"),
        "A fill only tells you someone accepted your price. "
        "Consider why they wanted that trade.",
        "Yes: informed selection is one possible cause. High fill rate alone is not success; "
        "unrelated price moves can also produce negative markouts.",
    ),
    Lesson(
        "Scenario: volatility rises while you carry large inventory. "
        "Does valuation risk rise or fall?",
        ("rise", "rises", "up", "increase", "increases"),
        "Imagine the same price move with one unit versus many units still held.",
        "It rises: a larger position multiplies the effect of price changes; higher volatility "
        "makes larger changes more likely. This strategy does not yet estimate volatility.",
    ),
)


class Prediction:
    """Keep the answer hidden until the caller reaches RESULT → EXPLAIN."""

    def __init__(self, lesson: Lesson) -> None:
        self.lesson = lesson
        self.attempts = 0
        self.ready = False
        self.correct = False

    def answer(self, text: str) -> str:
        if self.ready:
            raise ValueError("prediction already recorded")
        self.attempts += 1
        self.correct = text.strip().lower() in self.lesson.accepted
        if not self.correct and self.attempts == 1:
            return "Hint: " + self.lesson.hint
        self.ready = True
        return "Prediction recorded. Choose your quotes; explanation follows the result."

    def explain(self) -> str:
        if not self.ready:
            raise ValueError(
                "make a prediction and use the retry before revealing the explanation"
            )
        return (
            "Your prediction was correct. " if self.correct else "Reconsider this: "
        ) + self.lesson.explanation
