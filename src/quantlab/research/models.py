"""Generic research interfaces: no asset class, order book or trading-policy dependency."""

import math
from dataclasses import dataclass, field
from typing import Any, Protocol

from quantlab.research.codec import plain
from quantlab.research.seeds import SeedPlan


@dataclass(frozen=True, slots=True)
class Variant:
    name: str
    configuration: dict

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("variant name must be nonempty")
        if not isinstance(self.configuration, dict):
            raise ValueError("variant configuration must be a JSON object")
        object.__setattr__(self, "configuration", plain(self.configuration))


@dataclass(frozen=True, slots=True)
class ExperimentSpec:
    question: str
    hypothesis: str
    seeds: SeedPlan
    variants: tuple[Variant, ...]
    adapter: str
    paired: bool = True
    primary_metric: str = "net_pnl"
    bootstrap_resamples: int = 2000
    practical_threshold: float = 0.05
    relationships: tuple[tuple[str, str], ...] = ()
    limitations: tuple[str, ...] = (
        "Synthetic performance is not evidence of real-world alpha.",
        "Independent sessions conditional on one model; uncertainty excludes model error.",
        "Exploratory metrics/intervals are not corrected for multiple testing.",
        "Missing metrics are reported with coverage, not replaced by zero.",
    )

    def __post_init__(self):
        for text in (self.question, self.hypothesis, self.adapter, self.primary_metric):
            if not isinstance(text, str) or not text.strip():
                raise ValueError("question, prior hypothesis, adapter and metric are required")
        if not isinstance(self.seeds, SeedPlan):
            raise TypeError("seeds must be a SeedPlan")
        if not self.variants or not all(isinstance(v, Variant) for v in self.variants):
            raise ValueError("at least one valid variant is required")
        if len({v.name for v in self.variants}) != len(self.variants):
            raise ValueError("variant names must be unique")
        if type(self.paired) is not bool:
            raise TypeError("paired must be a boolean")
        if type(self.bootstrap_resamples) is not int or self.bootstrap_resamples < 2:
            raise ValueError("need at least two bootstrap resamples")
        if (
            isinstance(self.practical_threshold, bool)
            or not math.isfinite(self.practical_threshold)
            or self.practical_threshold < 0
        ):
            raise ValueError("practical threshold must be finite and nonnegative")
        if not self.limitations or any(not isinstance(x, str) for x in self.limitations):
            raise ValueError("explicit limitations are required")
        if any(
            len(pair) != 2 or any(not isinstance(x, str) or not x for x in pair)
            for pair in self.relationships
        ):
            raise ValueError("relationships must name pairs of metrics")


@dataclass(frozen=True, slots=True)
class SimulationOutcome:
    metrics: dict[str, float | int | None]
    environment_fingerprint: str
    trajectory_fingerprint: str
    coverage: dict = field(default_factory=dict)
    journal: Any = field(default=None, repr=False, compare=False)

    def __post_init__(self):
        if not self.metrics:
            raise ValueError("simulation must report metrics")
        for name, value in self.metrics.items():
            if not isinstance(name, str) or not name:
                raise ValueError("invalid metric name")
            if value is not None and (
                type(value) not in (int, float) or not math.isfinite(value)
            ):
                raise ValueError(f"metric {name} must be finite or explicitly missing")
        for value in (self.environment_fingerprint, self.trajectory_fingerprint):
            if not isinstance(value, str) or len(value) != 64:
                raise ValueError("fingerprints must be SHA-256 hex strings")
            int(value, 16)
        plain(self.coverage)


class SimulationAdapter(Protocol):
    name: str

    def validate(self, configuration: dict) -> None: ...

    def environment_key(self, configuration: dict) -> dict:
        """Equality means identical exogenous paths are expected for a shared seed."""
        ...

    def run(
        self, seed: int, configuration: dict, *, full: bool = False
    ) -> SimulationOutcome: ...

    def metric_units(self, configuration: dict) -> dict[str, str]: ...


def spec_from_dict(raw: dict) -> ExperimentSpec:
    return ExperimentSpec(
        **{
            **raw,
            "seeds": SeedPlan(**raw["seeds"]),
            "variants": tuple(Variant(**v) for v in raw["variants"]),
            "limitations": tuple(raw["limitations"]),
            "relationships": tuple(tuple(p) for p in raw.get("relationships", ())),
        }
    )
