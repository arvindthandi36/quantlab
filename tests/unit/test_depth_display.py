from quantlab import LimitOrder, MarketOrder, OrderBook, PriceGrid, Side
from quantlab.orderbook.display import render_depth


def test_aggregated_display_counts_actual_orders_and_expands_fifo_only_on_request():
    book = OrderBook()
    book.submit(LimitOrder("A", Side.SELL, 3, 10002))
    book.submit(LimitOrder("B", Side.SELL, 4, 10002))
    book.submit(LimitOrder("C", Side.SELL, 5, 10005))
    book.submit(LimitOrder("bid", Side.BUY, 10, 9999))
    snapshot = book.snapshot()
    depth = render_depth(snapshot, PriceGrid())
    assert "Price | Total Quantity | Order Count" in depth
    assert "£100.02 | 7 | 2 orders" in depth
    assert "£100.05 | 5 | 1 order" in depth
    assert "£99.99 | 10 | 1 order" in depth
    assert depth.index("£100.05") < depth.index("£100.02") < depth.index("BIDS")
    assert "FIFO" not in depth
    expanded = render_depth(snapshot, PriceGrid(), expand_orders=True)
    assert "FIFO oldest first: A: 3, B: 4" in expanded
    assert book.snapshot() == snapshot
    assert book.depth(Side.SELL)[0].price_ticks == 10002  # Engine remains best-first.


def test_depth_totals_and_counts_follow_fills_and_cancels_without_mutating_old_view():
    book = OrderBook()
    book.submit(LimitOrder("A", Side.SELL, 3, 10002))
    book.submit(LimitOrder("B", Side.SELL, 4, 10002))
    before = book.snapshot()
    book.submit(MarketOrder("buy", Side.BUY, 5))
    assert "£100.02 | 2 | 1 order" in render_depth(book.snapshot(), PriceGrid())
    assert before.asks[0].quantity == 7
    assert before.asks[0].order_count == 2
    book.cancel("B")
    assert render_depth(book.snapshot(), PriceGrid()).count("(empty)") == 2
