"""Validated order instructions and exact price units for one instrument."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import Enum
from fractions import Fraction


def positive_integer(value: int, name: str) -> None:
    """Reject floats and bools as well as nonpositive financial quantities."""
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer, not {type(value).__name__}")
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def nonempty_identifier(value: str, name: str = "order_id") -> None:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if not value or value.strip() != value:
        raise ValueError(f"{name} must be nonempty with no surrounding whitespace")


class Side(Enum):
    BUY = "buy"
    SELL = "sell"

    @property
    def opposite(self) -> "Side":
        return Side.SELL if self is Side.BUY else Side.BUY


def validate_order(order_id: str, side: Side, quantity: int) -> None:
    nonempty_identifier(order_id)
    if not isinstance(side, Side):
        raise TypeError("side must be Side.BUY or Side.SELL")
    positive_integer(quantity, "quantity")


@dataclass(frozen=True, slots=True)
class LimitOrder:
    """An instruction to trade at the limit or better; any remainder rests."""

    order_id: str
    side: Side
    quantity: int
    price_ticks: int

    def __post_init__(self) -> None:
        validate_order(self.order_id, self.side, self.quantity)
        positive_integer(self.price_ticks, "price_ticks")


@dataclass(frozen=True, slots=True)
class MarketOrder:
    """An instruction to consume available opposite liquidity, then cancel the rest."""

    order_id: str
    side: Side
    quantity: int

    def __post_init__(self) -> None:
        validate_order(self.order_id, self.side, self.quantity)


Order = LimitOrder | MarketOrder


@dataclass(frozen=True, slots=True)
class PriceGrid:
    """Convert exact decimal prices to integer ticks without rounding.

    Pass prices as strings or Decimal values, never binary floats. The grid
    belongs to the caller's instrument configuration; the matching engine
    operates entirely in ticks. A different grid requires a separate book.
    """

    tick_size: Decimal = Decimal("0.01")

    def __post_init__(self) -> None:
        if not isinstance(self.tick_size, Decimal):
            raise TypeError("tick_size must be a Decimal")
        if not self.tick_size.is_finite() or self.tick_size <= 0:
            raise ValueError("tick_size must be finite and positive")

    def to_ticks(self, price: str | Decimal) -> int:
        """Reject nonpositive, nonfinite, and off-grid prices explicitly."""
        if not isinstance(price, (str, Decimal)):
            raise TypeError("price must be a string or Decimal; floats are not accepted")
        try:
            value = Decimal(price)
        except InvalidOperation as exc:
            raise ValueError("price must be a valid decimal") from exc
        if not value.is_finite() or value <= 0:
            raise ValueError("price must be finite and positive")
        # Rational arithmetic prevents Decimal context precision from silently
        # rounding an off-grid price onto the grid.
        ticks = Fraction(value) / Fraction(self.tick_size)
        if ticks.denominator != 1:
            raise ValueError(f"price {value} is not a multiple of tick_size {self.tick_size}")
        return ticks.numerator

    def to_price(self, ticks: int | Fraction) -> Decimal:
        """Convert ticks, including half-tick mid-prices, exactly to decimal.

        A rational with a nonterminating decimal representation is rejected.
        """
        if type(ticks) is not int and not isinstance(ticks, Fraction):
            raise TypeError("ticks must be an integer or Fraction")
        if ticks <= 0:
            raise ValueError("ticks must be positive")
        value = Fraction(ticks) * Fraction(self.tick_size)
        denominator = value.denominator
        twos = fives = 0
        while denominator % 2 == 0:
            denominator //= 2
            twos += 1
        while denominator % 5 == 0:
            denominator //= 5
            fives += 1
        if denominator != 1:
            raise ValueError("price does not have an exact finite decimal representation")
        scale = max(twos, fives)
        coefficient = value.numerator * 2 ** (scale - twos) * 5 ** (scale - fives)
        digits = tuple(int(digit) for digit in str(coefficient))
        return Decimal((0, digits, -scale))
