"""Small data records. Narratives are instructions; results come from engine adapters."""

from dataclasses import asdict, dataclass, field

from quantlab.tutor.questions import Question


@dataclass(frozen=True)
class Spec:
    id: str
    title: str
    description: str
    domain: str
    concepts: tuple[str, ...]
    builder: str
    difficulty: str = "First principles"
    duration_minutes: int = 4
    prerequisites: tuple[str, ...] = ()
    environment: str = "SYNTHETIC"
    flagship: bool = False

    def public(self):
        return asdict(self)


@dataclass
class Moment:
    id: str
    title: str  # Neutral before-result label: never selected outcome or private cause.
    action: str
    concept: str
    before: dict
    after: dict
    question: Question | None = None
    observation: str = "Read the available prices, quantities and evidence labels."
    result_note: str = (
        "Compare the recorded result with the inputs available before the action."
    )
    expected_event: str = "Existing engine calculation"
    capture_before: str | None = None
    capture_after: str | None = None
    branch: bool = False
    rank: float = 0
    tags: tuple[str, ...] = ()


@dataclass
class Evidence:
    spec: Spec
    moments: list[Moment]
    configuration: dict
    limitations: tuple[str, ...]
    journal: dict | None = None
    private: dict = field(default_factory=dict)
    origin: str = "built_in"
    verification: dict = field(default_factory=dict)


def choice(concept, prompt, *, correct="no", options=None, context="", hints=None):
    from quantlab.explainability.registry import CONCEPTS
    from quantlab.tutor.catalog import ACTIVE_CONCEPTS

    meta = CONCEPTS[concept].public()
    aliases = {
        "delta": "greeks",
        "gamma": "greeks",
        "vega": "greeks",
        "theta": "greeks",
        "delta_hedging": "hedging",
        "black_scholes": "option_pricing",
        "model_risk": "model_criticism",
        "historical_replay": "decision_quality",
        "market_environments": "decision_quality",
        "current_price": "market_orders",
        "integer_ticks": "numerical_correctness",
        "position": "inventory",
        "residual": "regression",
        "z_score": "regression",
        "leg_risk": "decision_quality",
    }
    tutor_id = (
        concept if concept in ACTIVE_CONCEPTS else aliases.get(concept, "decision_quality")
    )
    return Question(
        tutor_id,
        1,
        prompt,
        "choice",
        correct,
        options or (("yes", "Yes"), ("no", "No")),
        hints
        or (
            "Separate the observed result from a guarantee about what comes next.",
            "Look at the stated assumptions and the evidence available at this point.",
        ),
        meta["definition"],
        meta["maths"]["equation"],
        context,
        meta["interview"],
        "Treating an assumption or outcome as a guarantee.",
    )
