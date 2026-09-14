"""Authoritative execution statistics; prices stay in the caller's explicit unit."""

from fractions import Fraction

from quantlab.domain import positive_integer


def vwap(fills):
    """Exact volume-weighted price from (price, whole positive quantity) pairs.

    Use integer ticks or decimal GBP strings/Fractions, never mix their units.
    No fills means unavailable, not zero. Fees are separate.
    """
    turnover, quantity = Fraction(0), 0
    for price, size in fills:
        positive_integer(size, "executed quantity")
        value = Fraction(str(price))
        if value <= 0:
            raise ValueError("Execution price must be positive")
        turnover += value * size
        quantity += size
    return turnover / quantity if quantity else None
