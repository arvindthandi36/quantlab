"""Private storage for one side; economic matching rules live in book.py."""

from bisect import bisect_left, insort
from collections import OrderedDict
from dataclasses import dataclass

from quantlab.domain import LimitOrder, Side
from quantlab.orderbook.models import OrderView, PriceLevel


@dataclass(slots=True)
class RestingOrder:
    instruction: LimitOrder
    remaining: int
    sequence: int

    def view(self) -> OrderView:
        order = self.instruction
        return OrderView(
            order.order_id, order.side, order.price_ticks, self.remaining, self.sequence
        )


class SideBook:
    """Ascending prices plus FIFO levels; buys access prices from the end."""

    def __init__(self, side: Side) -> None:
        self.side = side
        self.prices: list[int] = []
        self.levels: dict[int, OrderedDict[str, RestingOrder]] = {}

    @property
    def best_price(self) -> int | None:
        if not self.prices:
            return None
        return self.prices[-1] if self.side is Side.BUY else self.prices[0]

    def first(self) -> RestingOrder | None:
        price = self.best_price
        return None if price is None else next(iter(self.levels[price].values()))

    def add(self, resting: RestingOrder) -> None:
        order = resting.instruction
        if order.price_ticks not in self.levels:
            insort(self.prices, order.price_ticks)
            self.levels[order.price_ticks] = OrderedDict()
        self.levels[order.price_ticks][order.order_id] = resting

    def remove(self, resting: RestingOrder) -> None:
        order = resting.instruction
        level = self.levels[order.price_ticks]
        del level[order.order_id]
        if not level:
            del self.levels[order.price_ticks]
            self.prices.pop(bisect_left(self.prices, order.price_ticks))

    def snapshot(self) -> tuple[PriceLevel, ...]:
        prices = reversed(self.prices) if self.side is Side.BUY else iter(self.prices)
        return tuple(
            PriceLevel(price, tuple(order.view() for order in self.levels[price].values()))
            for price in prices
        )

    def check_invariants(self) -> None:
        if self.prices != sorted(self.levels):
            raise AssertionError("price index and levels disagree")
        for price, level in self.levels.items():
            if not level or price <= 0:
                raise AssertionError("empty or invalid price level")
            last_sequence = 0
            for order_id, resting in level.items():
                order = resting.instruction
                if (order.order_id, order.side, order.price_ticks) != (
                    order_id,
                    self.side,
                    price,
                ):
                    raise AssertionError("order stored at incorrect side, price or ID")
                if not 0 < resting.remaining <= order.quantity:
                    raise AssertionError("invalid remaining quantity")
                if resting.sequence <= last_sequence:
                    raise AssertionError("FIFO sequence is not strictly increasing")
                last_sequence = resting.sequence
