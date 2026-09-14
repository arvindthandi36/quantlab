"""Fixed and inventory-aware baselines; risk reservations live in a common layer."""

from fractions import Fraction

from quantlab.market_making.config import MakerConfig, Strategy
from quantlab.market_making.quotes import MakerObservation, QuoteRequest


def quote_request(observation: MakerObservation, config: MakerConfig) -> QuoteRequest:
    """Positive inventory LOWERS the centre; negative inventory RAISES it."""
    if config.strategy is Strategy.MANUAL:
        raise ValueError("manual strategy needs an explicit user quote request")
    shift = Fraction(0)
    if config.strategy is Strategy.INVENTORY:
        q = observation.account.inventory
        excess = Fraction(
            max(0, abs(q) - config.soft_limit), config.hard_limit - config.soft_limit
        )
        shift = -config.inventory_skew_ticks * q * (1 + excess)
    return QuoteRequest(
        config.half_spread_ticks,
        config.half_spread_ticks,
        config.quote_size,
        config.quote_size,
        shift,
    )
