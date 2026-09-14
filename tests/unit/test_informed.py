import random
from dataclasses import fields, replace
from random import Random
from unittest.mock import Mock

import pytest

from quantlab import Side
from quantlab.agents.basic import PublicObservation
from quantlab.agents.informed import InformedTrader, PrivateSignal
from quantlab.market.config import SimulationConfig
from quantlab.market.signals import sample_signal
from quantlab.randomness import RandomStreams


@pytest.mark.parametrize("shock", [-1.5, 0, 1.5])
def test_signal_is_current_value_plus_scaled_measurement_error(shock):
    rng = Mock(spec=Random)
    rng.gauss.return_value = shock
    signal = sample_signal(10000, 7, 2, rng)
    assert signal.value_ticks == 10000 + 2 * shock
    assert signal.time_us == 7 and signal.noise_sd_ticks == 2
    assert {f.name for f in fields(PrivateSignal)} == {
        "time_us",
        "value_ticks",
        "noise_sd_ticks",
    }


def test_signals_reproduce_without_global_state_changes():
    before = random.getstate()
    first, second = RandomStreams(42).create("signals"), RandomStreams(42).create("signals")
    assert [sample_signal(10000, t, 2, first) for t in range(10)] == [
        sample_signal(10000, t, 2, second) for t in range(10)
    ]
    assert random.getstate() == before


@pytest.mark.parametrize("noise", [0, -1, float("nan"), float("inf"), True])
def test_perfect_or_invalid_signal_noise_is_rejected(noise):
    with pytest.raises((ValueError, TypeError)):
        sample_signal(100, 1, noise, Random(1))


def test_posterior_matches_normal_normal_formula_and_hurdle_in_tick_units():
    trader = InformedTrader(
        prior_sd_ticks=4, cost_ticks=0.25, minimum_edge_ticks=0.5, uncertainty_multiplier=1
    )
    decision = trader.decide(
        "i", PublicObservation(99, 101, None, 100), PrivateSignal(1, 110, 3), now_us=1
    )
    assert decision.signal_weight == pytest.approx(16 / 25)
    assert decision.estimated_value_ticks == pytest.approx(106.4)
    assert decision.posterior_sd_ticks == pytest.approx(12 / 5)
    assert decision.threshold_ticks == pytest.approx(0.25 + 0.5 + 2.4)
    assert decision.buy_edge_ticks == pytest.approx(5.4)
    assert decision.order.side is Side.BUY and decision.order.price_ticks == 101
    assert decision.order.quantity == 1


@pytest.mark.parametrize(
    ("signal", "expected"), [(110, Side.BUY), (90, Side.SELL), (100, None)]
)
def test_buy_sell_and_abstain_depend_on_executable_edge(signal, expected):
    decision = InformedTrader().decide(
        "i", PublicObservation(99, 101, None, 100), PrivateSignal(5, signal, 2), now_us=5
    )
    assert (None if decision.order is None else decision.order.side) is expected


def test_exact_hurdle_is_not_enough_and_larger_costs_can_prevent_trade():
    public, signal = PublicObservation(99, 101, None, 100), PrivateSignal(1, 110, 2)
    base = InformedTrader(cost_ticks=0, minimum_edge_ticks=0, uncertainty_multiplier=0)
    edge = base.decide("i", public, signal, now_us=1).buy_edge_ticks
    assert base.decide("i", public, signal, now_us=1).order is not None
    assert replace(base, cost_ticks=edge).decide("i", public, signal, now_us=1).order is None
    assert (
        replace(base, cost_ticks=edge + 1).decide("i", public, signal, now_us=1).order is None
    )


@pytest.mark.parametrize("timestamp", [0, 2])
def test_stale_and_future_signals_are_rejected(timestamp):
    with pytest.raises(ValueError, match="fresh signal"):
        InformedTrader().decide(
            "i",
            PublicObservation(99, 101, None, 100),
            PrivateSignal(timestamp, 110, 2),
            now_us=1,
        )


@pytest.mark.parametrize(
    ("bid", "ask", "signal", "side"),
    [
        (None, None, 110, None),
        (99, None, 110, None),
        (None, 101, 90, None),
        (99, None, 90, Side.SELL),
        (None, 101, 110, Side.BUY),
    ],
)
def test_only_available_opposite_quotes_are_actionable(bid, ask, signal, side):
    result = InformedTrader().decide(
        "i", PublicObservation(bid, ask, None, 100), PrivateSignal(1, signal, 2), now_us=1
    )
    assert (None if result.order is None else result.order.side) is side


def test_cleaner_or_stronger_signal_increases_conviction_under_fixed_public_setup():
    trader, public = InformedTrader(), PublicObservation(99, 101, None, 100)
    clean = trader.decide("i", public, PrivateSignal(1, 104, 1), now_us=1)
    noisy = trader.decide("i", public, PrivateSignal(1, 104, 30), now_us=1)
    strong = trader.decide("i", public, PrivateSignal(1, 108, 1), now_us=1)
    assert clean.signal_weight > noisy.signal_weight
    assert clean.posterior_sd_ticks < noisy.posterior_sd_ticks
    assert clean.threshold_ticks < noisy.threshold_ticks
    assert clean.order is not None and noisy.order is None
    assert strong.buy_edge_ticks > clean.buy_edge_ticks


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("informed_rate_per_second", -1),
        ("signal_noise_ticks", 0),
        ("informed_prior_sd_ticks", 0),
        ("informed_cost_ticks", -1),
        ("informed_minimum_edge_ticks", float("nan")),
        ("informed_uncertainty_multiplier", True),
        ("markout_horizons_events", ()),
        ("markout_horizons_events", (1, 1)),
        ("markout_horizons_events", (5, 1)),
        ("markout_horizons_events", (0,)),
        ("markout_horizons_events", (True,)),
    ],
)
def test_invalid_phase3_configuration_fails_before_running(field, value):
    with pytest.raises((ValueError, TypeError)):
        replace(SimulationConfig(), **{field: value})
