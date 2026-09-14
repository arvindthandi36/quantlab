"""Explicit units and validated configuration for the first autonomous market."""

import math
from dataclasses import dataclass
from decimal import Decimal

from quantlab.domain import PriceGrid, positive_integer
from quantlab.randomness import RandomStreams

MICROSECONDS_PER_SECOND = 1_000_000


def finite_nonnegative(value: float, name: str) -> None:
    if type(value) not in (int, float):
        raise TypeError(f"{name} must be a real number")
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    """Rates are arrivals/second; latent sigma is ticks/sqrt(second).

    The opening public reference is separate from hidden initial value. Normal
    traders never receive latent values; informed flow receives noisy measurements.
    Zero arrival rates disable a flow, including Phase 3 informed flow by default.
    """

    seed: int = 42
    duration_us: int = 5_000_000
    tick_size: str = "0.01"
    opening_reference_ticks: int = 10000
    initial_latent_ticks: int = 10000
    latent_step_us: int = 1_000_000
    latent_sigma_ticks: float = 2.0
    noise_rate_per_second: float = 1.0
    liquidity_rate_per_second: float = 0.6
    noise_price_radius_ticks: int = 2
    noise_max_quantity: int = 4
    liquidity_max_quantity: int = 3
    max_events: int = 10_000
    informed_rate_per_second: float = 0.0
    signal_noise_ticks: float = 2.0
    informed_prior_sd_ticks: float = 8.0
    informed_cost_ticks: float = 0.25
    informed_minimum_edge_ticks: float = 0.25
    informed_uncertainty_multiplier: float = 0.5
    markout_horizons_events: tuple[int, ...] = (1, 5, 20)

    def __post_init__(self) -> None:
        RandomStreams(self.seed)
        for name in (
            "duration_us",
            "opening_reference_ticks",
            "initial_latent_ticks",
            "latent_step_us",
            "noise_max_quantity",
            "liquidity_max_quantity",
            "max_events",
        ):
            positive_integer(getattr(self, name), name)
        if type(self.noise_price_radius_ticks) is not int:
            raise TypeError("noise_price_radius_ticks must be an integer")
        if self.noise_price_radius_ticks < 0:
            raise ValueError("noise_price_radius_ticks must be nonnegative")
        for name in (
            "latent_sigma_ticks",
            "noise_rate_per_second",
            "liquidity_rate_per_second",
            "informed_rate_per_second",
            "signal_noise_ticks",
            "informed_prior_sd_ticks",
            "informed_cost_ticks",
            "informed_minimum_edge_ticks",
            "informed_uncertainty_multiplier",
        ):
            finite_nonnegative(getattr(self, name), name)
        if self.signal_noise_ticks == 0 or self.informed_prior_sd_ticks == 0:
            raise ValueError("signal noise and prior uncertainty must be strictly positive")
        if (
            not isinstance(self.markout_horizons_events, tuple)
            or not self.markout_horizons_events
        ):
            raise ValueError("markout_horizons_events must be a nonempty tuple")
        for horizon in self.markout_horizons_events:
            positive_integer(horizon, "markout horizon")
        if tuple(sorted(set(self.markout_horizons_events))) != self.markout_horizons_events:
            raise ValueError("markout horizons must be unique and increasing")
        if not isinstance(self.tick_size, str):
            raise TypeError("tick_size must be an exact decimal string")
        PriceGrid(Decimal(self.tick_size))
