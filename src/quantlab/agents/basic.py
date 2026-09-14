"""Small trader rules that receive public information only."""

from dataclasses import dataclass
from random import Random

from quantlab.domain import LimitOrder, MarketOrder, Order, Side, positive_integer


@dataclass(frozen=True, slots=True)
class PublicObservation:
    """The information boundary: no latent value, future events or RNG state."""

    best_bid: int | None
    best_ask: int | None
    last_trade_ticks: int | None
    opening_reference_ticks: int

    def reference(self) -> tuple[int, str]:
        """Midpoint rounded half-up to a tick, else last trade, else opening reference."""
        if self.best_bid is not None and self.best_ask is not None:
            return (self.best_bid + self.best_ask + 1) // 2, "public midpoint, rounded half-up"
        if self.last_trade_ticks is not None:
            return self.last_trade_ticks, "last transaction"
        return self.opening_reference_ticks, "configured opening reference"


@dataclass(frozen=True, slots=True)
class Decision:
    order: Order | None
    reason: str


@dataclass(frozen=True, slots=True)
class NoiseTrader:
    """Non-informational, one-sided limit instructions around public reference prices."""

    price_radius_ticks: int
    max_quantity: int

    def __post_init__(self) -> None:
        positive_integer(self.max_quantity, "max_quantity")
        if type(self.price_radius_ticks) is not int:
            raise TypeError("price_radius_ticks must be an integer")
        if self.price_radius_ticks < 0:
            raise ValueError("price_radius_ticks must be nonnegative")

    def decide(self, order_id: str, public: PublicObservation, rng: Random) -> Decision:
        """Flip a fair direction coin, draw a size and a uniform signed tick offset."""
        side = Side.BUY if rng.random() < 0.5 else Side.SELL
        quantity = rng.randint(1, self.max_quantity)
        offset = rng.randint(-self.price_radius_ticks, self.price_radius_ticks)
        anchor, source = public.reference()
        price = anchor + offset
        reason = f"random {side.value}/size; {source} {anchor} ticks {offset:+d}"
        if price <= 0:
            return Decision(None, reason + "; skipped: sampled limit is not positive")
        return Decision(LimitOrder(order_id, side, quantity, price), reason)


@dataclass(frozen=True, slots=True)
class LiquidityTrader:
    """An external need for immediate execution, independent of prices and value."""

    max_quantity: int

    def __post_init__(self) -> None:
        positive_integer(self.max_quantity, "max_quantity")

    def decide(self, order_id: str, rng: Random) -> Decision:
        """Draw a fair buy/sell need and size; submit a market instruction."""
        side = Side.BUY if rng.random() < 0.5 else Side.SELL
        quantity = rng.randint(1, self.max_quantity)
        return Decision(
            MarketOrder(order_id, side, quantity),
            f"external {side.value} need for {quantity}; "
            "requests immediate execution, no price signal",
        )
