"""Stable run addresses; disjoint development/evaluation namespaces."""

import hashlib
from dataclasses import dataclass

from quantlab.randomness import RandomStreams
from quantlab.research.codec import canonical


def derived_seed(root: int, name: str, index: int = 0) -> int:
    RandomStreams(root)
    if not isinstance(name, str) or not name.strip():
        raise ValueError("seed namespace must be nonempty")
    if type(index) is not int or index < 0:
        raise ValueError("seed index must be a nonnegative integer")
    payload = canonical(["quantlab-research-seeds-v1", root, name, index])
    return int.from_bytes(hashlib.sha256(payload.encode()).digest(), "big")


@dataclass(frozen=True, slots=True)
class SeedPlan:
    root: int
    pool: str
    runs: int
    start: int = 0

    def __post_init__(self):
        RandomStreams(self.root)
        if self.pool not in ("development", "evaluation"):
            raise ValueError("seed pool must be development or evaluation")
        if type(self.runs) is not int or self.runs < 1:
            raise ValueError("runs must be a positive integer")
        if type(self.start) is not int or self.start < 0:
            raise ValueError("start must be a nonnegative integer")

    def seeds(self) -> tuple[int, ...]:
        # Parity makes the two pools disjoint even in the event of a digest collision.
        bit = int(self.pool == "evaluation")
        result = tuple(
            2 * derived_seed(self.root, "sessions", i) + bit
            for i in range(self.start, self.start + self.runs)
        )
        if len(set(result)) != len(result):
            raise ValueError("duplicate Monte Carlo seeds; experiment cannot run")
        return result
