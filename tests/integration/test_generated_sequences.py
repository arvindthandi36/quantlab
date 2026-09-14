from collections import defaultdict

from hypothesis import given, settings
from hypothesis import strategies as st

from quantlab import LimitOrder, MarketOrder, OrderBook, Side
from tests.reference_book import ReferenceBook

actions = st.lists(
    st.tuples(
        st.sampled_from(["limit", "limit", "market", "cancel"]),
        st.sampled_from(list(Side)),
        st.integers(min_value=1, max_value=20),
        st.integers(min_value=95, max_value=105),
        st.integers(min_value=0, max_value=120),
    ),
    min_size=1,
    max_size=100,
)


@settings(max_examples=200, derandomize=True, database=None, deadline=None)
@given(actions)
def test_mixed_sequences_match_reference_and_conserve_every_order(sequence):
    """Check both a different algorithm and independent accounting after each action.

    Derandomization makes the search reproducible with the locked tool versions.
    Hypothesis still generates and shrinks varied sequences; no sample outcome
    or stochastic market distribution is being asserted.
    """
    book, reference = OrderBook(), ReferenceBook()
    submitted = {}
    submitted_sides = {}
    executed = defaultdict(int)
    cancelled = defaultdict(int)
    for i, (operation, side, quantity, price, target) in enumerate(sequence):
        order_id = f"order-{i}"
        if operation == "cancel":
            ids = list(submitted)
            cancel_id = ids[target % len(ids)] if ids and target % 3 else "unknown"
            actual = book.cancel(cancel_id)
            expected = reference.cancel(cancel_id)
            assert (None if actual is None else actual.remaining_quantity) == expected
            if actual:
                cancelled[cancel_id] += actual.remaining_quantity
        else:
            order = (
                LimitOrder(order_id, side, quantity, price)
                if operation == "limit"
                else MarketOrder(order_id, side, quantity)
            )
            maker_before = {
                o.order_id: o.remaining_quantity
                for level in book.depth(side.opposite)
                for o in level.orders
            }
            report = book.submit(order)
            expected_trades, expected_resting, expected_cancelled = reference.submit(
                order_id, side.value, quantity, price if operation == "limit" else None
            )
            actual_trades = [
                (
                    t.trade_id,
                    t.maker_order_id,
                    t.taker_order_id,
                    t.price_ticks,
                    t.quantity,
                    t.aggressor_side.value,
                )
                for t in report.trades
            ]
            assert actual_trades == expected_trades
            assert report.resting_quantity == expected_resting
            assert report.cancelled_quantity == expected_cancelled
            assert report.arrival_sequence == reference.sequence
            assert quantity == (
                report.executed_quantity + report.resting_quantity + report.cancelled_quantity
            )
            submitted[order_id] = quantity
            submitted_sides[order_id] = side
            cancelled[order_id] += report.cancelled_quantity
            maker_total = 0
            for trade in report.trades:
                assert trade.quantity > 0 and trade.price_ticks > 0
                assert trade.buy_order_id != trade.sell_order_id
                assert submitted_sides[trade.buy_order_id] is Side.BUY
                assert submitted_sides[trade.sell_order_id] is Side.SELL
                maker_after = book.get_order(trade.maker_order_id)
                maker_reduction = maker_before[trade.maker_order_id] - (
                    0 if maker_after is None else maker_after.remaining_quantity
                )
                assert maker_reduction == trade.quantity
                maker_total += maker_reduction
                executed[trade.buy_order_id] += trade.quantity
                executed[trade.sell_order_id] += trade.quantity
            assert report.buyer_filled_quantity == report.seller_filled_quantity == maker_total
            assert maker_total == report.executed_quantity
            assert maker_total == quantity - report.resting_quantity - report.cancelled_quantity
        book.check_invariants()
        snapshot = book.snapshot()
        orders = [order for level in snapshot.bids + snapshot.asks for order in level.orders]
        actual_state = sorted(
            (o.order_id, o.side.value, o.price_ticks, o.remaining_quantity, o.arrival_sequence)
            for o in orders
        )
        assert actual_state == reference.state()
        assert book.traded_volume == reference.volume
        assert book.trade_count == reference.trade_count
        active = {o.order_id: o.remaining_quantity for o in orders}
        for admitted_id, initial_quantity in submitted.items():
            assert initial_quantity == (
                executed[admitted_id] + cancelled[admitted_id] + active.get(admitted_id, 0)
            )
        assert sum(submitted.values()) == (
            2 * book.traded_volume + sum(cancelled.values()) + sum(active.values())
        )
