"""Durable pre-access audit for evaluation seeds, including failed experiments."""

import fcntl
import json
import os
import warnings
from datetime import UTC, datetime
from pathlib import Path

from quantlab.research.codec import canonical


class EvaluationReuseWarning(UserWarning):
    pass


def claim_evaluation(
    path: str | Path, *, design_digest: str, seeds: tuple[int, ...]
) -> list[str]:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        handle.seek(0)
        claims = [json.loads(line) for line in handle if line.strip()]
        previous = {seed for claim in claims for seed in claim["seeds"]}
        overlap = len(previous.intersection(seeds))
        messages = []
        if overlap:
            message = (
                f"EVALUATION REUSE: {overlap} seeds were already exposed. Repeated inspection "
                "turns evaluation data into development data; this is not a fresh holdout."
            )
            warnings.warn(message, EvaluationReuseWarning, stacklevel=2)
            messages.append(message)
        handle.write(
            canonical(
                {
                    "design_digest": design_digest,
                    "seeds": seeds,
                    "claimed_at": datetime.now(UTC).isoformat(),
                }
            )
        )
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    return messages
