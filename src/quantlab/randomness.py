"""Independent, reproducible named random streams; never global random state."""

import hashlib
import json
from dataclasses import dataclass
from random import Random

from quantlab.domain import nonempty_identifier


@dataclass(frozen=True, slots=True)
class RandomStreams:
    """Derive streams from a root seed and stable names.

    create(name) returns a NEW generator at its starting state. Keep that
    generator to advance it. Creating one stream cannot advance another.
    Reproduction of future distribution draws also requires the Python version.
    """

    seed: int

    def __post_init__(self) -> None:
        if type(self.seed) is not int:
            raise TypeError("seed must be an integer")
        if self.seed < 0:
            raise ValueError("seed must be nonnegative")

    def create(self, name: str) -> Random:
        """Create a stream without relying on Python's process-salted hash()."""
        nonempty_identifier(name, "stream name")
        payload = json.dumps(["quantlab-rng-v1", self.seed, name], ensure_ascii=True)
        digest = hashlib.sha256(payload.encode("utf-8")).digest()
        return Random(int.from_bytes(digest, "big"))
