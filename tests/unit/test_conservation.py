from dataclasses import replace

import pytest

import quantlab.orderbook.book as book_module
from quantlab import LimitOrder, MarketOrder, OrderBook, Side
from quantlab.orderbook.conservation import verify_conservation


@pytest.mark.parametrize("side", list(Side))
@pytest.mark.parametrize(
    ("makers", "requested"),
    [
        ([(100, 4)], 4),  # Single complete fill.
        ([(100, 7)], 3),  # Partial resting fill.
        ([(100, 2), (100, 3)], 4),  # Multiple FIFO orders at one price.
        ([(98, 2), (100, 3), (102, 4)], 7),  # Sweep across price levels.
        ([(100, 2), (101, 3)], 10),  # Unfilled market remainder.
        ([], 3),  # No liquidity, no invented fills.
    ],
)
def test_both_fill_totals_reconcile_to_actual_book_reductions(side, makers, requested):
    book = OrderBook()
    for i, (price, size) in enumerate(makers):
        book.submit(LimitOrder(f"m{i}", side.opposite, size, price))
    before = {
        order.order_id: order.remaining_quantity
        for level in book.depth(side.opposite)
        for order in level.orders
    }
    report = book.submit(MarketOrder("taker", side, requested))
    observed_maker_fills = 0
    for trade in report.trades:
        remaining = book.get_order(trade.maker_order_id)
        reduction = before[trade.maker_order_id] - (
            0 if remaining is None else remaining.remaining_quantity
        )
        assert reduction == trade.quantity
        observed_maker_fills += reduction
    observed_taker_fills = requested - report.cancelled_quantity - report.resting_quantity
    assert (
        observed_maker_fills == observed_taker_fills == sum(t.quantity for t in report.trades)
    )
    assert report.buyer_filled_quantity == report.seller_filled_quantity == observed_maker_fills
    assert book.traded_volume == observed_maker_fills


def test_cancelled_quantity_does_not_become_a_later_fill():
    book = OrderBook()
    book.submit(LimitOrder("cancelled", Side.SELL, 5, 100))
    book.submit(LimitOrder("survivor", Side.SELL, 4, 100))
    first = book.submit(MarketOrder("first", Side.BUY, 2))
    cancelled = book.cancel("cancelled")
    assert cancelled.remaining_quantity == 3
    second = book.submit(MarketOrder("second", Side.BUY, 9))
    assert [(t.maker_order_id, t.quantity) for t in second.trades] == [("survivor", 4)]
    assert second.cancelled_quantity == 5
    assert first.buyer_filled_quantity == first.seller_filled_quantity == 2
    assert second.buyer_filled_quantity == second.seller_filled_quantity == 4
    assert book.traded_volume == 6


@pytest.mark.parametrize(
    "quantities", [(2, 1, 2), (1, 2, 2), (2, 2, 1), (-1, -1, -1), (True, 1, 1)]
)
def test_discrepancies_fail_loudly(quantities):
    with pytest.raises(AssertionError, match="fill conservation failed"):
        verify_conservation(*quantities, "test execution")


def test_corrupted_trade_is_detected_and_book_cannot_continue(monkeypatch):
    book = OrderBook()
    book.submit(LimitOrder("maker", Side.SELL, 5, 100))
    real_trade = book_module.Trade

    def corrupt_trade(*args):
        trade = real_trade(*args)
        return replace(trade, quantity=trade.quantity + 1)

    monkeypatch.setattr(book_module, "Trade", corrupt_trade)
    with pytest.raises(AssertionError, match="buyer=2, seller=2, recorded=3"):
        book.submit(MarketOrder("bad", Side.BUY, 2))
    with pytest.raises(RuntimeError, match="discard"):
        book.submit(MarketOrder("later", Side.BUY, 1))
    with pytest.raises(RuntimeError, match="discard"):
        book.cancel("maker")


def test_whole_operation_detects_recorded_trade_sum_corruption(monkeypatch):
    book = OrderBook()
    book.submit(LimitOrder("maker", Side.SELL, 5, 100))
    real_verify = book_module.verify_conservation

    def corrupt_volume_after_verified_fill(buyer, seller, recorded, context):
        real_verify(buyer, seller, recorded, context)
        if context.startswith("trade "):
            book._traded_volume += 1

    monkeypatch.setattr(book_module, "verify_conservation", corrupt_volume_after_verified_fill)
    with pytest.raises(AssertionError, match="order bad totals"):
        book.submit(MarketOrder("bad", Side.BUY, 2))
