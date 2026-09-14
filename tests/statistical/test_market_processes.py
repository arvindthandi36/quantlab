import math
import statistics

import pytest

from quantlab.market.processes import exponential_wait_us, fundamental_step
from quantlab.randomness import RandomStreams


@pytest.mark.parametrize("rate", [0.5, 3.0])
def test_arrival_counts_agree_with_configured_poisson_rate(rate):
    """Independent sessions: total count has Poisson mean/variance rate*T*n.

    Six theoretical standard deviations allow sampling variation, plus a small
    conservative allowance for rounding gaps up by at most one microsecond.
    This tests the generator, not a financial calibration claim.
    """
    sessions, horizon_seconds = 200, 20
    total = 0
    for seed in range(sessions):
        rng = RandomStreams(seed).create("statistical.arrivals")
        time_us = 0
        while True:
            time_us += exponential_wait_us(rate, rng)
            if time_us > horizon_seconds * 1000000:
                break
            total += 1
    expected = sessions * horizon_seconds * rate
    rounding_allowance = expected * rate / 1000000 + 1
    assert abs(total - expected) < 6 * math.sqrt(expected) + rounding_allowance


@pytest.mark.parametrize("dt_us", [250000, 1000000, 4000000])
def test_latent_increments_have_zero_mean_and_sigma_squared_dt_variance(dt_us):
    """Gaussian increment mean SE=sqrt(v/n); sample variance SE≈v*sqrt(2/(n-1)).

    Six-standard-error bands avoid requiring one exact random sample. Values
    are far from the model's positivity boundary, so no boundary conditioning
    contaminates this test of the unrestricted Gaussian increment equation.
    """
    n, sigma, initial = 20000, 2.0, 10000.0
    rng = RandomStreams(2026).create("statistical.latent")
    increments = [fundamental_step(initial, sigma, dt_us, rng) - initial for _ in range(n)]
    expected_variance = sigma**2 * dt_us / 1000000
    mean_se = math.sqrt(expected_variance / n)
    variance_se = expected_variance * math.sqrt(2 / (n - 1))
    assert abs(statistics.mean(increments)) < 6 * mean_se
    assert abs(statistics.variance(increments) - expected_variance) < 6 * variance_se
