"""Synchronous price-time matching; each method completes one book operation."""

from dataclasses import dataclass
from fractions import Fraction

from quantlab.domain import LimitOrder, MarketOrder, Order, Side, nonempty_identifier
from quantlab.orderbook._side import RestingOrder, SideBook
from quantlab.orderbook.conservation import verify_conservation
from quantlab.orderbook.models import (
    BookSnapshot,
    ExecutionReport,
    OrderView,
    PriceLevel,
    Trade,
)


@dataclass(slots=True)
class _MatchOutcome:
    remaining: int
    trades: list[Trade]
    buyer_filled: int
    seller_filled: int


class OrderBook:
    """A single-instrument book with positive integer prices and quantities.

    Calls must be serial. Limit orders are good until cancelled; market orders
    cancel any unfilled remainder immediately. IDs cannot be reused for this
    book's lifetime, including after fill, cancellation or zero execution.
    Phase 1 has no accounts, fees, wall clock or self-trade prevention.
    """

    def __init__(self) -> None:
        self._sides = {side: SideBook(side) for side in Side}
        self._active: dict[str, RestingOrder] = {}
        self._seen_ids: set[str] = set()
        self._sequence = 0
        self._trade_count = 0
        self._traded_volume = 0
        self._failed = False

    def _require_healthy(self) -> None:
        if self._failed:
            raise RuntimeError("book failed a conservation check; discard this instance")

    @property
    def best_bid(self) -> int | None:
        return self._sides[Side.BUY].best_price

    @property
    def best_ask(self) -> int | None:
        return self._sides[Side.SELL].best_price

    @property
    def spread_ticks(self) -> int | None:
        bid, ask = self.best_bid, self.best_ask
        return None if bid is None or ask is None else ask - bid

    @property
    def mid_price_ticks(self) -> Fraction | None:
        bid, ask = self.best_bid, self.best_ask
        return None if bid is None or ask is None else Fraction(bid + ask, 2)

    @property
    def traded_volume(self) -> int:
        """Cumulative executed units, counted once per trade (not per side)."""
        return self._traded_volume

    @property
    def trade_count(self) -> int:
        return self._trade_count

    def depth(self, side: Side) -> tuple[PriceLevel, ...]:
        """Return real outstanding orders, aggregated by price, best price first."""
        if not isinstance(side, Side):
            raise TypeError("side must be Side.BUY or Side.SELL")
        return self._sides[side].snapshot()

    def snapshot(self) -> BookSnapshot:
        """Return a detached, immutable snapshot; future fills cannot change it."""
        return BookSnapshot(self.depth(Side.BUY), self.depth(Side.SELL))

    def get_order(self, order_id: str) -> OrderView | None:
        """Look up an active remainder. None means this ID is not resting."""
        nonempty_identifier(order_id)
        resting = self._active.get(order_id)
        return None if resting is None else resting.view()

    def submit(self, order: Order) -> ExecutionReport:
        """Process a validated instruction and report every disposition of its size.

        Reject an unsupported instruction or reused ID before changing state.
        Matching prioritises the best eligible price, then the oldest order at
        that price. The incoming limit is a bound, not the execution price.
        """
        self._require_healthy()
        if not isinstance(order, (LimitOrder, MarketOrder)):
            raise TypeError("order must be a LimitOrder or MarketOrder")
        if order.order_id in self._seen_ids:
            raise ValueError(f"order_id {order.order_id!r} has already been used")
        self._seen_ids.add(order.order_id)
        self._sequence += 1
        try:
            outcome = self._match(order)
        except AssertionError:
            self._failed = True
            raise
        remaining, trades = outcome.remaining, outcome.trades
        resting_quantity = cancelled_quantity = 0
        if remaining:
            if isinstance(order, LimitOrder):
                resting = RestingOrder(order, remaining, self._sequence)
                self._sides[order.side].add(resting)
                self._active[order.order_id] = resting
                resting_quantity = remaining
            else:
                cancelled_quantity = remaining
        return ExecutionReport(
            order.order_id,
            self._sequence,
            order.quantity,
            tuple(trades),
            resting_quantity,
            cancelled_quantity,
            outcome.buyer_filled,
            outcome.seller_filled,
        )

    def cancel(self, order_id: str) -> OrderView | None:
        """Cancel an active remainder, returning its size; otherwise return None.

        Repeated/unknown cancellations are explicit no-ops. A cancellation does
        not consume an arrival sequence or permit reuse of the order ID.
        """
        self._require_healthy()
        nonempty_identifier(order_id)
        resting = self._active.get(order_id)
        if resting is None:
            return None
        cancelled = resting.view()
        self._remove(resting)
        return cancelled

    def _match(self, order: Order) -> _MatchOutcome:
        opposite = self._sides[order.side.opposite]
        remaining = order.quantity
        trades: list[Trade] = []
        buyer_total = seller_total = 0
        volume_before = self._traded_volume
        while remaining:
            maker = opposite.first()
            if maker is None or not self._eligible(order, maker.instruction.price_ticks):
                break
            incoming_before, maker_before = remaining, maker.remaining
            quantity = min(incoming_before, maker_before)
            trade = Trade(
                self._trade_count + 1,
                maker.instruction.price_ticks,
                quantity,
                maker.instruction.order_id,
                order.order_id,
                order.side,
            )
            remaining -= quantity
            maker.remaining -= quantity
            # Measure actual changes on each side, independently of the recorded trade.
            incoming_filled = incoming_before - remaining
            maker_filled = maker_before - maker.remaining
            buyer_filled, seller_filled = (
                (incoming_filled, maker_filled)
                if order.side is Side.BUY
                else (maker_filled, incoming_filled)
            )
            verify_conservation(
                buyer_filled, seller_filled, trade.quantity, f"trade {trade.trade_id}"
            )
            buyer_total += buyer_filled
            seller_total += seller_filled
            trades.append(trade)
            self._trade_count += 1
            self._traded_volume += quantity
            if maker.remaining == 0:
                self._remove(maker)
        recorded = sum(trade.quantity for trade in trades)
        verify_conservation(buyer_total, seller_total, recorded, f"order {order.order_id}")
        verify_conservation(
            order.quantity - remaining,
            self._traded_volume - volume_before,
            recorded,
            f"order {order.order_id} totals",
        )
        return _MatchOutcome(remaining, trades, buyer_total, seller_total)

    @staticmethod
    def _eligible(order: Order, maker_price: int) -> bool:
        if isinstance(order, MarketOrder):
            return True
        if order.side is Side.BUY:
            return maker_price <= order.price_ticks
        return maker_price >= order.price_ticks

    def _remove(self, resting: RestingOrder) -> None:
        self._sides[resting.instruction.side].remove(resting)
        del self._active[resting.instruction.order_id]

    def check_invariants(self) -> None:
        """Raise AssertionError if storage integrity or uncrossedness fails.

        This explicit O(N + L log L) diagnostic is intended for tests and demos,
        rather than imposing a full scan on every future simulation event.
        Quantity conservation is additionally verified by external test ledgers.
        """
        if self._failed:
            raise AssertionError("book failed conservation; state is diagnostic only")
        observed: dict[str, RestingOrder] = {}
        for side in self._sides.values():
            side.check_invariants()
            for level in side.levels.values():
                for order_id, resting in level.items():
                    if order_id in observed:
                        raise AssertionError("order appears more than once")
                    observed[order_id] = resting
        if observed.keys() != self._active.keys():
            raise AssertionError("active order index disagrees with levels")
        for order_id, resting in self._active.items():
            if observed[order_id] is not resting:
                raise AssertionError("active index points to a different order")
            if order_id not in self._seen_ids or not 0 < resting.sequence <= self._sequence:
                raise AssertionError("active order was not admitted")
        if self._sequence != len(self._seen_ids):
            raise AssertionError("admission sequence disagrees with used IDs")
        if self.best_bid is not None and self.best_ask is not None:
            if self.best_bid >= self.best_ask:
                raise AssertionError("book is locked or crossed")
