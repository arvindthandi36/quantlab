from dataclasses import fields
from random import Random
from unittest.mock import Mock

import pytest

from quantlab import Side
from quantlab.agents.basic import LiquidityTrader, NoiseTrader, PublicObservation


@pytest.mark.parametrize(
    ("public", "expected", "source"),
    [
        (PublicObservation(99, 102, 90, 80), 101, "midpoint"),
        (PublicObservation(99, None, 90, 80), 90, "transaction"),
        (PublicObservation(None, 102, None, 80), 80, "opening"),
        (PublicObservation(None, None, None, 80), 80, "opening"),
    ],
)
def test_noise_reference_uses_only_public_information(public, expected, source):
    price, explanation = public.reference()
    assert price == expected
    assert source in explanation
    assert {f.name for f in fields(PublicObservation)} == {
        "best_bid",
        "best_ask",
        "last_trade_ticks",
        "opening_reference_ticks",
    }


@pytest.mark.parametrize(("coin", "side"), [(0.1, Side.BUY), (0.9, Side.SELL)])
def test_noise_decision_explains_a_random_limit_and_can_cross(coin, side):
    rng = Mock(spec=Random)
    rng.random.return_value = coin
    rng.randint.side_effect = [3, 2]
    decision = NoiseTrader(2, 4).decide("n", PublicObservation(99, 101, None, 100), rng)
    assert (decision.order.side, decision.order.quantity, decision.order.price_ticks) == (
        side,
        3,
        102,
    )
    assert "random" in decision.reason and "midpoint" in decision.reason


def test_invalid_sampled_limit_is_skipped_with_a_reason_not_clamped():
    rng = Mock(spec=Random)
    rng.random.return_value = 0.1
    rng.randint.side_effect = [1, -2]
    decision = NoiseTrader(2, 4).decide("n", PublicObservation(None, None, None, 1), rng)
    assert decision.order is None
    assert "skipped" in decision.reason


def test_liquidity_trader_has_no_price_observation_and_explains_external_need():
    rng = Mock(spec=Random)
    rng.random.return_value = 0.9
    rng.randint.return_value = 3
    decision = LiquidityTrader(3).decide("l", rng)
    assert decision.order.side is Side.SELL and decision.order.quantity == 3
    assert "external sell need" in decision.reason
    assert not hasattr(decision.order, "price_ticks")
