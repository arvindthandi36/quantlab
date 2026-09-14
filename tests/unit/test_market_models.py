from dataclasses import replace
from random import Random
from unittest.mock import Mock

import pytest

from quantlab.market.config import SimulationConfig
from quantlab.market.processes import exponential_wait_us, fundamental_step


@pytest.mark.parametrize(("dt_us", "expected"), [(250000, 101), (1000000, 102), (4000000, 104)])
def test_latent_step_uses_seconds_and_square_root_time(dt_us, expected):
    rng = Mock(spec=Random)
    rng.gauss.return_value = 1.0
    assert fundamental_step(100, 2, dt_us, rng) == expected
    assert fundamental_step(100, 0, dt_us, rng) == 100


@pytest.mark.parametrize("shock", [-1000, float("nan"), float("inf")])
def test_invalid_latent_results_fail_instead_of_clipping(shock):
    rng = Mock(spec=Random)
    rng.gauss.return_value = shock
    with pytest.raises(ValueError, match="no clipping"):
        fundamental_step(1, 1, 1000000, rng)


@pytest.mark.parametrize(
    ("seconds", "expected_us"), [(0, 1), (1.0000001, 1000001), (0.5, 500000)]
)
def test_arrival_gaps_round_up_and_never_form_zero_time_chains(seconds, expected_us):
    rng = Mock(spec=Random)
    rng.expovariate.return_value = seconds
    assert exponential_wait_us(2, rng) == expected_us
    rng.expovariate.assert_called_once_with(2)


def test_overflowing_arrival_gap_and_zero_rate_are_explicit():
    rng = Mock(spec=Random)
    rng.expovariate.return_value = float("inf")
    with pytest.raises(ValueError, match="overflowed"):
        exponential_wait_us(1, rng)
    with pytest.raises(ValueError, match="disables"):
        exponential_wait_us(0, rng)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("seed", -1),
        ("seed", True),
        ("duration_us", 0),
        ("duration_us", 1.5),
        ("latent_step_us", 0),
        ("initial_latent_ticks", 0),
        ("opening_reference_ticks", 0),
        ("latent_sigma_ticks", -1),
        ("latent_sigma_ticks", float("nan")),
        ("noise_rate_per_second", float("inf")),
        ("liquidity_rate_per_second", -1),
        ("noise_rate_per_second", True),
        ("noise_price_radius_ticks", -1),
        ("noise_price_radius_ticks", 0.5),
        ("noise_max_quantity", 0),
        ("liquidity_max_quantity", False),
        ("max_events", 0),
        ("tick_size", "NaN"),
        ("tick_size", "0"),
        ("tick_size", 0.01),
    ],
)
def test_invalid_market_config_is_rejected(field, value):
    with pytest.raises((ValueError, TypeError)):
        replace(SimulationConfig(), **{field: value})
