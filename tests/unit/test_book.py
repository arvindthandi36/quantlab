from dataclasses import FrozenInstanceError
from fractions import Fraction

import pytest

from quantlab import LimitOrder, MarketOrder, OrderBook, Side


def test_empty_and_one_sided_book_have_no_synthetic_quote():
    book = OrderBook()
    assert book.best_bid is book.best_ask is None
    assert book.spread_ticks is book.mid_price_ticks is None
    report = book.submit(LimitOrder("b", Side.BUY, 5, 100))
    assert report.executed_quantity == report.cancelled_quantity == 0
    assert report.resting_quantity == 5
    assert report.vwap_ticks is None
    assert book.best_bid == 100
    assert book.best_ask is book.spread_ticks is book.mid_price_ticks is None
    book.check_invariants()


def test_depth_spread_midpoint_and_immutable_snapshots():
    book = OrderBook()
    for order in (
        LimitOrder("b1", Side.BUY, 2, 99),
        LimitOrder("b2", Side.BUY, 3, 100),
        LimitOrder("b3", Side.BUY, 4, 100),
        LimitOrder("s", Side.SELL, 5, 103),
    ):
        book.submit(order)
    snapshot = book.snapshot()
    assert [(p.price_ticks, p.quantity) for p in snapshot.bids] == [(100, 7), (99, 2)]
    assert [o.order_id for o in snapshot.bids[0].orders] == ["b2", "b3"]
    assert book.spread_ticks == snapshot.spread_ticks == 3
    assert book.mid_price_ticks == snapshot.mid_price_ticks == Fraction(203, 2)
    with pytest.raises(FrozenInstanceError):
        snapshot.bids[0].orders[0].remaining_quantity = 1000
    book.submit(MarketOrder("m", Side.SELL, 2))
    assert snapshot.bids[0].quantity == 7
    assert book.depth(Side.BUY)[0].quantity == 5
    book.check_invariants()


@pytest.mark.parametrize("taker_side", list(Side))
def test_price_then_time_priority_for_both_sides(taker_side):
    book = OrderBook()
    maker_side = taker_side.opposite
    best = 100
    worse = 102 if taker_side is Side.BUY else 98
    for order in (
        LimitOrder("worse-but-older", maker_side, 5, worse),
        LimitOrder("first", maker_side, 3, best),
        LimitOrder("second", maker_side, 4, best),
    ):
        book.submit(order)
    report = book.submit(MarketOrder("taker", taker_side, 9))
    assert [(t.maker_order_id, t.quantity, t.price_ticks) for t in report.trades] == [
        ("first", 3, best),
        ("second", 4, best),
        ("worse-but-older", 2, worse),
    ]
    assert [t.trade_id for t in report.trades] == [1, 2, 3]
    assert report.executed_quantity == book.traded_volume == 9
    assert book.trade_count == 3
    assert report.vwap_ticks == Fraction(7 * best + 2 * worse, 9)
    assert book.get_order("worse-but-older").remaining_quantity == 3
    for trade in report.trades:
        assert (
            trade.buy_order_id if taker_side is Side.BUY else trade.sell_order_id
        ) == "taker"
    book.check_invariants()


@pytest.mark.parametrize("taker_side", list(Side))
def test_marketable_limit_executes_at_resting_price_and_respects_bound(taker_side):
    book = OrderBook()
    maker_side = taker_side.opposite
    limit = 101 if taker_side is Side.BUY else 99
    outside = 102 if taker_side is Side.BUY else 98
    book.submit(LimitOrder("better", maker_side, 2, 100))
    book.submit(LimitOrder("at-bound", maker_side, 3, limit))
    book.submit(LimitOrder("outside", maker_side, 5, outside))
    report = book.submit(LimitOrder("taker", taker_side, 8, limit))
    assert [(t.price_ticks, t.quantity) for t in report.trades] == [(100, 2), (limit, 3)]
    assert report.resting_quantity == 3
    assert report.cancelled_quantity == 0
    assert book.get_order("taker").remaining_quantity == 3
    assert book.get_order("outside").remaining_quantity == 5
    book.check_invariants()


@pytest.mark.parametrize("taker_side", list(Side))
def test_equal_price_cross_executes_and_removes_empty_level(taker_side):
    book = OrderBook()
    book.submit(LimitOrder("maker", taker_side.opposite, 4, 100))
    report = book.submit(LimitOrder("taker", taker_side, 4, 100))
    assert report.executed_quantity == 4
    assert report.resting_quantity == 0
    assert book.snapshot().bids == book.snapshot().asks == ()
    assert book.get_order("maker") is book.get_order("taker") is None
    book.check_invariants()


def test_partial_fill_preserves_original_time_priority():
    book = OrderBook()
    original = LimitOrder("first", Side.SELL, 5, 100)
    book.submit(original)
    before = book.get_order("first")
    book.submit(MarketOrder("m1", Side.BUY, 2))
    book.submit(LimitOrder("second", Side.SELL, 5, 100))
    assert book.get_order("first").arrival_sequence == before.arrival_sequence
    report = book.submit(MarketOrder("m2", Side.BUY, 4))
    assert [(t.maker_order_id, t.quantity) for t in report.trades] == [
        ("first", 3),
        ("second", 1),
    ]
    assert original.quantity == before.remaining_quantity == 5
    book.check_invariants()


@pytest.mark.parametrize("side", list(Side))
@pytest.mark.parametrize("available", [0, 3])
def test_market_remainder_is_cancelled_never_rests(side, available):
    book = OrderBook()
    if available:
        book.submit(LimitOrder("maker", side.opposite, available, 100))
    report = book.submit(MarketOrder("market", side, 5))
    assert report.executed_quantity == available
    assert report.cancelled_quantity == 5 - available
    assert report.resting_quantity == 0
    assert book.get_order("market") is None
    assert book.best_bid is book.best_ask is None
    book.check_invariants()


@pytest.mark.parametrize("cancel_id", ["first", "middle", "last"])
def test_cancel_any_queue_position_and_refill_level(cancel_id):
    book = OrderBook()
    ids = ["first", "middle", "last"]
    for order_id in ids:
        book.submit(LimitOrder(order_id, Side.SELL, 2, 100))
    cancelled = book.cancel(cancel_id)
    assert cancelled.order_id == cancel_id
    assert cancelled.remaining_quantity == 2
    assert book.cancel(cancel_id) is None
    assert book.cancel("unknown") is None
    report = book.submit(MarketOrder("taker", Side.BUY, 10))
    assert [t.maker_order_id for t in report.trades] == [i for i in ids if i != cancel_id]
    book.submit(LimitOrder("fresh", Side.SELL, 1, 100))
    assert book.depth(Side.SELL)[0].quantity == 1
    book.check_invariants()


def test_cancellation_returns_only_unfilled_quantity():
    book = OrderBook()
    book.submit(LimitOrder("maker", Side.SELL, 5, 100))
    book.submit(MarketOrder("m", Side.BUY, 3))
    assert book.cancel("maker").remaining_quantity == 2
    assert book.best_ask is None
    assert book.submit(MarketOrder("next", Side.BUY, 2)).executed_quantity == 0
    book.check_invariants()


@pytest.mark.parametrize("state", ["active", "cancelled", "filled", "market_unfilled"])
def test_reused_ids_rejected_without_state_or_sequence_change(state):
    book = OrderBook()
    if state == "market_unfilled":
        book.submit(MarketOrder("used", Side.SELL, 1))
    else:
        book.submit(LimitOrder("used", Side.SELL, 1, 100))
        if state == "cancelled":
            book.cancel("used")
        if state == "filled":
            book.submit(MarketOrder("fill", Side.BUY, 1))
    before = book.snapshot(), book.traded_volume, book.trade_count
    for duplicate in (LimitOrder("used", Side.BUY, 2, 200), MarketOrder("used", Side.BUY, 2)):
        with pytest.raises(ValueError, match="already been used"):
            book.submit(duplicate)
        assert (book.snapshot(), book.traded_volume, book.trade_count) == before
    next_report = book.submit(LimitOrder("new", Side.BUY, 1, 50))
    assert next_report.arrival_sequence == (3 if state == "filled" else 2)
    book.check_invariants()


def test_invalid_operations_and_missing_cancellations_do_not_consume_sequence():
    book = OrderBook()
    with pytest.raises(TypeError):
        book.submit({"side": "buy"})
    with pytest.raises(TypeError):
        book.depth("buy")
    with pytest.raises(ValueError):
        book.cancel("")
    with pytest.raises(TypeError):
        book.get_order(1)
    assert book.cancel("unknown") is None
    assert book.submit(LimitOrder("x", Side.BUY, 1, 100)).arrival_sequence == 1


def test_check_invariants_is_an_effective_diagnostic():
    book = OrderBook()
    book.submit(LimitOrder("x", Side.BUY, 1, 100))
    book._active["x"].remaining = 0
    with pytest.raises(AssertionError, match="remaining"):
        book.check_invariants()
