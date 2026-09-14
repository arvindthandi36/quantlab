from dataclasses import replace
from fractions import Fraction as F

import pytest

from quantlab.market_making.config import MakerConfig, Strategy
from quantlab.market_making.quotes import MakerObservation, QuoteRequest, plan_quotes
from quantlab.portfolio.accounting import MakerAccount
from quantlab.strategies.market_making import quote_request


def observation(q=0, reference=F(100), bid=None, ask=None):
    account = MakerAccount(1000, reference, hard_limit=8).snapshot()
    return MakerObservation(
        0,
        bid,
        ask,
        bid,
        ask,
        reference,
        "test public reference",
        replace(account, inventory=q),
        (),
        (),
    )


@pytest.mark.parametrize("q", [-8, -4, 0, 4, 8])
def test_fixed_quote_centre_ignores_inventory(q):
    config = MakerConfig()
    obs = observation(q)
    request = quote_request(obs, config)
    assert request.centre_shift_ticks == 0
    plan = plan_quotes(obs, request, config)
    assert plan.centre_ticks == 100
    if plan.bid_size:
        assert plan.bid_ticks == 98
    if plan.ask_size:
        assert plan.ask_ticks == 102


@pytest.mark.parametrize(
    "q,centre,bid,ask", [(4, 98, 96, 100), (-4, 102, 100, 104), (0, 100, 98, 102)]
)
def test_inventory_skew_direction_and_hand_calculated_prices(q, centre, bid, ask):
    config = MakerConfig(strategy=Strategy.INVENTORY)
    obs = observation(q)
    plan = plan_quotes(obs, quote_request(obs, config), config)
    assert (plan.centre_ticks, plan.bid_ticks, plan.ask_ticks) == (centre, bid, ask)


@pytest.mark.parametrize("q", [5, -5, 6, -6, 7, -7])
def test_soft_limit_increases_skew_and_reduces_only_exposure_increasing_size(q):
    config = MakerConfig(strategy=Strategy.INVENTORY, quote_size=4)
    obs = observation(q)
    request = quote_request(obs, config)
    assert abs(request.centre_shift_ticks) > F(1, 2) * abs(q)
    assert request.centre_shift_ticks * q < 0
    plan = plan_quotes(obs, request, config)
    if q > 0:
        assert plan.bid_size == 8 - q and plan.ask_size == 4
    else:
        assert plan.ask_size == 8 + q and plan.bid_size == 4


@pytest.mark.parametrize(
    "q,buys,sells", [(0, 8, 8), (4, 4, 12), (-4, 12, 4), (8, 0, 16), (-8, 16, 0)]
)
def test_hard_limit_reserves_both_sides_without_netting(q, buys, sells):
    plan = plan_quotes(observation(q), QuoteRequest(bid_size=100, ask_size=100), MakerConfig())
    assert (plan.bid_size, plan.ask_size) == (buys, sells)
    assert q + plan.bid_size <= 8
    assert q - plan.ask_size >= -8


def test_fractional_reference_distances_and_skew_round_outward():
    obs = observation(reference=F(201, 2))
    request = QuoteRequest(F(1, 3), F(2, 3), centre_shift_ticks=F(-1, 4))
    plan = plan_quotes(obs, request, MakerConfig())
    assert plan.centre_ticks == F(401, 4)
    assert plan.bid_ticks == 99 and plan.ask_ticks == 101


@pytest.mark.parametrize("shift,bid,ask", [(10, 100, 112), (-10, 88, 100)])
def test_marketable_proposals_are_moved_outward_and_reported(shift, bid, ask):
    plan = plan_quotes(
        observation(bid=99, ask=101), QuoteRequest(centre_shift_ticks=shift), MakerConfig()
    )
    assert (plan.bid_ticks, plan.ask_ticks) == (bid, ask)
    assert any("passive" in reason for reason in plan.adjustments)


def test_zero_size_withdraws_and_nonpositive_prices_are_not_fabricated():
    plan = plan_quotes(observation(reference=F(1)), QuoteRequest(ask_size=0), MakerConfig())
    assert plan.bid_ticks is plan.ask_ticks is None
    assert plan.bid_size == plan.ask_size == 0
    assert "nonpositive" in plan.adjustments[0]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"soft_limit": 8},
        {"hard_limit": 0},
        {"refresh_us": True},
        {"half_spread_ticks": 0},
        {"inventory_skew_ticks": -1},
        {"fee_ticks": 0.1},
        {"fee_ticks": "nan"},
        {"strategy": "fixed"},
    ],
)
def test_invalid_maker_configuration(kwargs):
    with pytest.raises((ValueError, TypeError)):
        MakerConfig(**kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"bid_distance_ticks": 0},
        {"ask_distance_ticks": 0.5},
        {"bid_size": -1},
        {"ask_size": True},
        {"centre_shift_ticks": 0.25},
    ],
)
def test_invalid_manual_instructions(kwargs):
    with pytest.raises((ValueError, TypeError)):
        QuoteRequest(**kwargs)
