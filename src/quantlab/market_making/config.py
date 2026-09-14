"""Validated, exact maker controls; no hidden market parameters in strategy inputs."""

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction

from quantlab.domain import positive_integer


def exact(value: Fraction | int | str, name: str, *, positive: bool = False) -> Fraction:
    """Reject floats/bools; money and quote distances must have explicit exact input."""
    if type(value) not in (Fraction, int, str):
        raise TypeError(f"{name} must be an exact integer, decimal string or Fraction")
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"invalid exact {name}") from exc
    if result < 0 or (positive and result == 0):
        raise ValueError(f"{name} must be {'positive' if positive else 'nonnegative'}")
    return result


class Strategy(Enum):
    FIXED = "fixed"
    INVENTORY = "inventory"
    MANUAL = "manual"


@dataclass(frozen=True, slots=True)
class MakerConfig:
    strategy: Strategy = Strategy.FIXED
    half_spread_ticks: Fraction = Fraction(2)
    quote_size: int = 2
    inventory_skew_ticks: Fraction = Fraction(1, 2)
    soft_limit: int = 4
    hard_limit: int = 8
    refresh_us: int = 1_000_000
    fee_ticks: Fraction = Fraction(1, 10)
    initial_cash_ticks: Fraction = Fraction(1_000_000)
    max_decisions: int = 10_000

    def __post_init__(self) -> None:
        if not isinstance(self.strategy, Strategy):
            raise TypeError("strategy must be Strategy")
        for name in ("quote_size", "soft_limit", "hard_limit", "refresh_us", "max_decisions"):
            positive_integer(getattr(self, name), name)
        if self.soft_limit >= self.hard_limit:
            raise ValueError("soft_limit must be below hard_limit")
        for name in (
            "half_spread_ticks",
            "inventory_skew_ticks",
            "fee_ticks",
            "initial_cash_ticks",
        ):
            object.__setattr__(
                self,
                name,
                exact(getattr(self, name), name, positive=name == "half_spread_ticks"),
            )
