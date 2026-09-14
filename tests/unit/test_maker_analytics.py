from dataclasses import replace
from fractions import Fraction as F

import pytest

from quantlab import LimitOrder, MarketOrder, Side
from quantlab.analytics.markouts import MarkoutStatus
from quantlab.market_making.analytics import diagnostics, lab_markouts, summarise_markouts
from quantlab.market_making.config import MakerConfig, Strategy
from quantlab.market_making.quotes import QuoteRequest
from quantlab.market_making.views import render_observation
from tests.lab_helpers import finish_manual, scripted_lab


def analytic_path(side=Side.BUY):
    # Maker buys at 98 or sells at 102; later a genuine two-sided external book
    # establishes reference 110 or 90. No markout values are assigned to trades.
    sign = 1 if side is Side.BUY else -1
    instructions = [
        (1, MarketOrder("take", side.opposite, 1)),
        (3, LimitOrder("bid", Side.BUY, 1, 100 + 10 * sign - 1)),
        (4, LimitOrder("ask", Side.SELL, 1, 100 + 10 * sign + 1)),
    ]
    lab = scripted_lab(instructions)
    lab.advance_to_decision()
    lab.decide(QuoteRequest(bid_size=1, ask_size=1))
    lab.advance_to_decision()
    lab.decide(QuoteRequest(bid_size=0, ask_size=0))
    return lab, finish_manual(lab, QuoteRequest(bid_size=0, ask_size=0))


@pytest.mark.parametrize("side", list(Side))
def test_markout_sign_and_decomposition_with_real_reference_changes(side):
    _, result = analytic_path(side)
    marks = lab_markouts(result.records, (1, 4))
    early = marks[0]
    assert early.horizon_events == 1
    assert early.status is MarkoutStatus.MISSING  # cancellation leaves missing midpoint
    later = marks[1]
    # Initial quote, fill, cancellation, bid, ask have public indices 1..5.
    # h4 from the fill targets index 6, which has not occurred.
    assert later.status is MarkoutStatus.PENDING
    h3 = lab_markouts(result.records, (3,))[0]
    assert h3.provider_markout_ticks == 12
    assert h3.initial_edge_ticks == 2
    assert h3.reference_move_ticks == 10


def test_markouts_cannot_change_cash_realised_pnl_or_account_state():
    _, result = analytic_path()
    before = result.final_account
    marks = lab_markouts(result.records, (1, 3, 20), debug=True)
    assert len(marks) == 6
    assert result.final_account == before
    assert (
        before.total_pnl_ticks
        == before.spread_capture_ticks + before.inventory_movement_ticks - before.fees_ticks
    )


def test_pending_markouts_have_no_future_values_and_cutoff_excludes_future_records():
    _, result = analytic_path()
    fill_index = next(i for i, r in enumerate(result.records) if r.fills)
    pending = lab_markouts(result.records, (1, 3), as_of_records=fill_index + 1)
    assert all(m.status is MarkoutStatus.PENDING for m in pending)
    assert all(
        m.maturity_time_us is m.reference_after_ticks is m.provider_markout_ticks is None
        for m in pending
    )
    altered = list(result.records)
    for i in range(fill_index + 1, len(altered)):
        altered[i] = replace(altered[i], public_event_number=99999)
    assert lab_markouts(tuple(altered), (1, 3), as_of_records=fill_index + 1) == pending


def test_time_weighted_inventory_and_drawdown_are_hand_calculable():
    # One unit is held from t1 through t5. End marking uses last transaction=98;
    # the opening spread proxy is offset by immediate reference movement.
    result = finish_manual(
        scripted_lab([(1, MarketOrder("sell", Side.SELL, 1))]),
        QuoteRequest(bid_size=1, ask_size=1),
    )
    stats = diagnostics(result.records)
    assert stats.average_inventory == stats.average_absolute_inventory == F(4, 5)
    assert stats.rms_inventory == pytest.approx((4 / 5) ** 0.5)
    assert stats.maximum_absolute_inventory == 1
    assert stats.buy_fills == 1 and stats.sell_fills == 0
    assert stats.buy_units == 1 and stats.sell_units == 0
    assert stats.posted_units == 6
    assert stats.fill_rate == F(1, 6)
    assert stats.turnover_ticks == 98
    assert stats.average_effective_spread_ticks == 4
    assert stats.maximum_drawdown_ticks == F(1, 10)


def test_profit_from_inventory_rally_is_not_labelled_successful_market_making():
    _, result = analytic_path()
    stats = diagnostics(result.records)
    assert result.final_account.spread_capture_ticks == 2
    assert result.final_account.inventory_movement_ticks == 10
    assert result.final_account.total_pnl_ticks == F(119, 10)
    assert "dominated by inventory/reference movement" in stats.attribution_comment


def test_missing_quotes_and_zero_posted_units_have_explicit_missing_statistics():
    result = finish_manual(scripted_lab([]), QuoteRequest(bid_size=0, ask_size=0))
    stats = diagnostics(result.records)
    assert (
        stats.fill_rate
        is stats.average_effective_spread_ticks
        is stats.average_quoted_spread_ticks
        is None
    )
    assert stats.two_sided_quote_time_fraction == 0
    assert stats.average_inventory == stats.average_absolute_inventory == 0
    assert lab_markouts(result.records) == ()


def test_normal_manual_view_rejects_private_markout_reference():
    lab, result = analytic_path()
    public_lab = scripted_lab([])
    observation = public_lab.advance_to_decision()
    with pytest.raises(ValueError, match="private-reference"):
        render_observation(observation, lab_markouts(result.records, debug=True))


@pytest.mark.parametrize("cutoff", [-1, True, 0.5, 10000])
def test_invalid_markout_cutoff_is_rejected(cutoff):
    _, result = analytic_path()
    with pytest.raises(ValueError, match="prefix"):
        lab_markouts(result.records, as_of_records=cutoff)


@pytest.mark.parametrize("horizons", [(), (0,), (True,), (2, 1), (1, 1)])
def test_invalid_markout_horizons_are_rejected(horizons):
    _, result = analytic_path()
    with pytest.raises(ValueError, match="horizons"):
        lab_markouts(result.records, horizons)


def test_soft_limit_partial_quotes_have_time_weighted_two_sided_coverage():
    maker = MakerConfig(strategy=Strategy.MANUAL, refresh_us=2, soft_limit=1, hard_limit=2)
    result = finish_manual(
        scripted_lab([(1, MarketOrder("sell", Side.SELL, 10))], maker=maker),
        QuoteRequest(bid_size=2, ask_size=2),
    )
    stats = diagnostics(result.records)
    assert stats.maximum_absolute_inventory == 2
    assert stats.two_sided_quote_time_fraction == F(1, 5)
    assert stats.average_quoted_spread_ticks == 4


def test_tighter_quotes_can_fill_more_but_have_an_adverse_markout():
    instructions = [
        (1, LimitOrder("seller", Side.SELL, 1, 99)),
        (3, LimitOrder("later-bid", Side.BUY, 1, 95)),
        (4, LimitOrder("later-ask", Side.SELL, 1, 97)),
    ]
    config = MakerConfig(strategy=Strategy.MANUAL, refresh_us=10)
    tight = finish_manual(scripted_lab(instructions, maker=config), QuoteRequest(1, 1, 1, 1))
    wide = finish_manual(scripted_lab(instructions, maker=config), QuoteRequest(10, 10, 1, 1))
    assert len(tight.fills) == 1 and wide.fills == ()
    assert lab_markouts(tight.records, (2,))[0].provider_markout_ticks == -3
    assert tight.final_account.total_pnl_ticks == -F(31, 10)
    assert wide.final_account.total_pnl_ticks == 0


def test_markout_summary_is_volume_weighted_and_excludes_missing_and_pending_units():
    _, result = analytic_path()
    mark = lab_markouts(result.records, (3,))[0]
    group = (
        replace(mark, quantity=1, provider_markout_ticks=F(12)),
        replace(mark, trade_id=2, quantity=3, provider_markout_ticks=F(-2)),
        replace(
            mark,
            trade_id=3,
            quantity=2,
            provider_markout_ticks=None,
            status=MarkoutStatus.MISSING,
        ),
        replace(
            mark,
            trade_id=4,
            quantity=4,
            provider_markout_ticks=None,
            status=MarkoutStatus.PENDING,
        ),
    )
    summary = summarise_markouts(group)[0]
    assert summary.mean_ticks == F(3, 2)  # (1*12 + 3*(-2)) / 4
    assert (summary.available_units, summary.missing_units, summary.pending_units) == (4, 2, 4)
