"""Immutable observations returned by the engine; quantities are in units."""

from dataclasses import dataclass
from fractions import Fraction

from quantlab.domain import Side
from quantlab.execution import vwap


@dataclass(frozen=True, slots=True)
class Trade:
    """One maker/taker match, priced at the resting maker's limit."""

    trade_id: int
    price_ticks: int
    quantity: int
    maker_order_id: str
    taker_order_id: str
    aggressor_side: Side

    @property
    def buy_order_id(self) -> str:
        return self.taker_order_id if self.aggressor_side is Side.BUY else self.maker_order_id

    @property
    def sell_order_id(self) -> str:
        return self.taker_order_id if self.aggressor_side is Side.SELL else self.maker_order_id


@dataclass(frozen=True, slots=True)
class OrderView:
    """A detached view of a resting order, or its remainder at cancellation."""

    order_id: str
    side: Side
    price_ticks: int
    remaining_quantity: int
    arrival_sequence: int


@dataclass(frozen=True, slots=True)
class PriceLevel:
    price_ticks: int
    orders: tuple[OrderView, ...]

    @property
    def quantity(self) -> int:
        return sum(order.remaining_quantity for order in self.orders)

    @property
    def order_count(self) -> int:
        return len(self.orders)


@dataclass(frozen=True, slots=True)
class BookSnapshot:
    """Depth from best to worst price on each side, FIFO within each level."""

    bids: tuple[PriceLevel, ...]
    asks: tuple[PriceLevel, ...]

    @property
    def best_bid(self) -> int | None:
        return self.bids[0].price_ticks if self.bids else None

    @property
    def best_ask(self) -> int | None:
        return self.asks[0].price_ticks if self.asks else None

    @property
    def spread_ticks(self) -> int | None:
        bid, ask = self.best_bid, self.best_ask
        return None if bid is None or ask is None else ask - bid

    @property
    def mid_price_ticks(self) -> Fraction | None:
        bid, ask = self.best_bid, self.best_ask
        return None if bid is None or ask is None else Fraction(bid + ask, 2)


@dataclass(frozen=True, slots=True)
class ExecutionReport:
    """Quantity accounting for an incoming order, at the instant of submission.

    requested = executed + resting + cancelled. Resting quantity can change
    later; this report remains a historical observation.
    """

    order_id: str
    arrival_sequence: int
    requested_quantity: int
    trades: tuple[Trade, ...]
    resting_quantity: int
    cancelled_quantity: int
    buyer_filled_quantity: int
    seller_filled_quantity: int

    @property
    def executed_quantity(self) -> int:
        return sum(trade.quantity for trade in self.trades)

    @property
    def vwap_ticks(self) -> Fraction | None:
        """Exact volume-weighted execution price; None means no executions."""
        return vwap((t.price_ticks, t.quantity) for t in self.trades)
