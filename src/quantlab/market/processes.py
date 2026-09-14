"""The two stochastic building blocks, with explicit units and failure behaviour."""

import math
from random import Random

from quantlab.domain import positive_integer
from quantlab.market.config import MICROSECONDS_PER_SECOND, finite_nonnegative


def exponential_wait_us(rate_per_second: float, rng: Random) -> int:
    """Sample an exponential gap and round up to our microsecond clock.

    Positive gaps prevent infinite same-time arrival chains. Rounding adds at
    most one microsecond per arrival, making this a discretised Poisson model.
    """
    finite_nonnegative(rate_per_second, "rate_per_second")
    if rate_per_second == 0:
        raise ValueError("zero rate disables a source; it has no finite waiting time")
    scaled_wait = rng.expovariate(rate_per_second) * MICROSECONDS_PER_SECOND
    if not math.isfinite(scaled_wait):
        raise ValueError("arrival gap overflowed; choose a representable arrival rate")
    return max(1, math.ceil(scaled_wait))


def fundamental_step(value_ticks: float, sigma_ticks: float, dt_us: int, rng: Random) -> float:
    """X_next = X + sigma * sqrt(dt_seconds) * Z, with Z standard normal.

    This zero-drift arithmetic random walk is observed at fixed intervals and
    held between updates. A nonpositive/nonfinite result raises, never clips.
    It is research state, not an order price or an input to the Phase 2 traders.
    """
    finite_nonnegative(value_ticks, "value_ticks")
    finite_nonnegative(sigma_ticks, "sigma_ticks")
    positive_integer(dt_us, "dt_us")
    if value_ticks == 0:
        raise ValueError("value_ticks must be positive")
    shock = rng.gauss(0.0, 1.0)
    result = value_ticks + sigma_ticks * math.sqrt(dt_us / MICROSECONDS_PER_SECOND) * shock
    if not math.isfinite(result) or result <= 0:
        raise ValueError(
            "latent process left its positive finite domain; run aborted, no clipping"
        )
    return result
