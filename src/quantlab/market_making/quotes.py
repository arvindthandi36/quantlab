"""Public quote instructions and a shared passive/exposure safety layer."""

import math
from dataclasses import dataclass
from fractions import Fraction

from quantlab.domain import Side
from quantlab.market_making.config import MakerConfig, exact
from quantlab.orderbook import OrderView
from quantlab.portfolio.accounting import AccountSnapshot, MakerFill


@dataclass(frozen=True, slots=True)
class MakerObservation:
    time_us: int
    best_bid: int | None
    best_ask: int | None
    external_bid: int | None
    external_ask: int | None
    reference_ticks: Fraction
    reference_source: str
    account: AccountSnapshot
    quotes: tuple[OrderView, ...]
    recent_fills: tuple[MakerFill, ...]


@dataclass(frozen=True, slots=True)
class QuoteRequest:
    bid_distance_ticks: Fraction = Fraction(2)
    ask_distance_ticks: Fraction = Fraction(2)
    bid_size: int = 2
    ask_size: int = 2
    centre_shift_ticks: Fraction = Fraction(0)

    def __post_init__(self) -> None:
        for name in ("bid_distance_ticks", "ask_distance_ticks"):
            object.__setattr__(self, name, exact(getattr(self, name), name, positive=True))
        for name in ("bid_size", "ask_size"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer")
        if type(self.centre_shift_ticks) not in (Fraction, int, str):
            raise TypeError("centre shift must be exact")
        object.__setattr__(self, "centre_shift_ticks", Fraction(self.centre_shift_ticks))


@dataclass(frozen=True, slots=True)
class QuotePlan:
    centre_ticks: Fraction
    bid_ticks: int | None
    ask_ticks: int | None
    bid_size: int
    ask_size: int
    adjustments: tuple[str, ...]


def plan_quotes(
    observation: MakerObservation, request: QuoteRequest, config: MakerConfig
) -> QuotePlan:
    """Round outward, avoid aggressive execution and reserve worst-case side capacity."""
    q, hard, soft = observation.account.inventory, config.hard_limit, config.soft_limit
    if abs(q) > hard:
        raise ValueError("inventory already exceeds the hard limit")
    centre = observation.reference_ticks + request.centre_shift_ticks
    prices = {
        Side.BUY: math.floor(centre - request.bid_distance_ticks),
        Side.SELL: math.ceil(centre + request.ask_distance_ticks),
    }
    quantities = {Side.BUY: request.bid_size, Side.SELL: request.ask_size}
    reasons = []
    for side in Side:
        original = quantities[side]
        increases = (q > soft and side is Side.BUY) or (q < -soft and side is Side.SELL)
        if increases:
            quantities[side] = original * (hard - abs(q)) // (hard - soft)
        capacity = hard - q if side is Side.BUY else hard + q
        quantities[side] = min(quantities[side], capacity)
        if quantities[side] != original:
            reasons.append(
                f"{side.value} size {original} → {quantities[side]}: inventory safety"
            )
        before = prices[side]
        if side is Side.BUY and observation.external_ask is not None:
            prices[side] = min(prices[side], observation.external_ask - 1)
        if side is Side.SELL and observation.external_bid is not None:
            prices[side] = max(prices[side], observation.external_bid + 1)
        if prices[side] <= 0:
            quantities[side] = 0
            reasons.append(f"{side.value} disabled: proposed price is nonpositive")
        elif before != prices[side]:
            reasons.append(f"{side.value} moved outward to remain passive")
    return QuotePlan(
        centre,
        prices[Side.BUY] if quantities[Side.BUY] else None,
        prices[Side.SELL] if quantities[Side.SELL] else None,
        quantities[Side.BUY],
        quantities[Side.SELL],
        tuple(reasons),
    )
