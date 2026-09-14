"""Trusted signal service; agents never receive this function's latent input."""

import math
from dataclasses import dataclass
from random import Random

from quantlab.agents.informed import InformedDecision, PrivateSignal
from quantlab.market.config import finite_nonnegative


def sample_signal(
    latent_ticks: float, time_us: int, noise_sd_ticks: float, rng: Random
) -> PrivateSignal:
    """Measure current X plus independent normal error; do not draw or inspect future X."""
    finite_nonnegative(latent_ticks, "latent_ticks")
    finite_nonnegative(noise_sd_ticks, "noise_sd_ticks")
    if latent_ticks == 0 or noise_sd_ticks == 0:
        raise ValueError("latent value and signal noise must be positive")
    value = latent_ticks + noise_sd_ticks * rng.gauss(0.0, 1.0)
    if not math.isfinite(value):
        raise ValueError("signal measurement overflowed")
    return PrivateSignal(time_us, value, noise_sd_ticks)


@dataclass(frozen=True, slots=True)
class InformedAudit:
    """Observer-only facts: realised error is never passed back to an agent."""

    signal: PrivateSignal
    error_ticks: float
    decision: InformedDecision
