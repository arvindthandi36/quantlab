"""Contracts use GBP per underlying unit, annual decimals and exact ACT/365 time."""

import math
from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction

from quantlab.domain import positive_integer


def number(value, name, low=None, high=None):
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite number")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    if (
        not math.isfinite(result)
        or (low is not None and result < low)
        or (high is not None and result > high)
    ):
        raise ValueError(f"{name} must be finite and in [{low}, {high}]")
    return result


def exact(value, name="amount"):
    number(value, name)
    try:
        return Fraction(str(value))
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"Invalid {name}") from exc


def years_from_days(days):
    number(days, "ACT/365 calendar days", 0, 18_250)
    return exact(days, "calendar days") / 365


class OptionType(StrEnum):
    CALL = "call"
    PUT = "put"


@dataclass(frozen=True)
class OptionContract:
    option_type: OptionType
    strike_gbp: Fraction
    expiry_years: Fraction
    multiplier: int = 100
    underlying: str = "QL-STOCK"

    def __post_init__(self):
        object.__setattr__(self, "option_type", OptionType(self.option_type))
        number(self.strike_gbp, "strike GBP per underlying unit", 1e-8, 1e12)
        number(self.expiry_years, "expiry model years", 0, 50)
        object.__setattr__(self, "strike_gbp", exact(self.strike_gbp, "strike"))
        object.__setattr__(self, "expiry_years", exact(self.expiry_years, "expiry"))
        positive_integer(self.multiplier, "contract multiplier")
        if self.multiplier > 10_000:
            raise ValueError("contract multiplier is limited to 10,000")
        if not isinstance(self.underlying, str) or not self.underlying.strip():
            raise ValueError("underlying identifier is required")

    @property
    def id(self):
        return (
            f"{self.underlying}:{self.option_type}:{self.strike_gbp}:"
            f"{self.expiry_years}:x{self.multiplier}"
        )

    def remaining(self, elapsed_years=0):
        number(elapsed_years, "elapsed model years", 0, 50)
        return max(Fraction(0), self.expiry_years - exact(elapsed_years))

    def public(self, elapsed_years=0):
        return {
            "id": self.id,
            "underlying": self.underlying,
            "type": self.option_type.value,
            "strike": float(self.strike_gbp),
            "expiry_years": str(self.expiry_years),
            "expiry_days": float(self.expiry_years * 365),
            "remaining_years": float(self.remaining(elapsed_years)),
            "remaining_days": float(self.remaining(elapsed_years) * 365),
            "multiplier": self.multiplier,
            "settlement": "European cash settlement",
        }


@dataclass(frozen=True)
class PricingInputs:
    spot: float
    strike: float
    time_years: float
    volatility: float
    rate: float = 0.0
    dividend_yield: float = 0.0

    def __post_init__(self):
        limits = {
            "spot": (1e-8, 1e12),
            "strike": (1e-8, 1e12),
            "time_years": (0, 50),
            "volatility": (0, 5),
            "rate": (-1, 1),
            "dividend_yield": (-1, 1),
        }
        for key, (lo, hi) in limits.items():
            label = key + (" (annual decimal: 20% = 0.20)" if key == "volatility" else "")
            object.__setattr__(self, key, number(getattr(self, key), label, lo, hi))

    @classmethod
    def for_contract(cls, contract, spot, elapsed_years, volatility, rate=0, dividend_yield=0):
        return cls(
            spot,
            float(contract.strike_gbp),
            float(contract.remaining(elapsed_years)),
            volatility,
            rate,
            dividend_yield,
        )
