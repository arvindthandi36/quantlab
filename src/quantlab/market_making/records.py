"""Complete observer evidence for interleaved background events and maker actions."""

from dataclasses import dataclass
from fractions import Fraction

from quantlab.domain import LimitOrder
from quantlab.market.config import SimulationConfig
from quantlab.market.records import EventRecord
from quantlab.market_making.config import MakerConfig
from quantlab.market_making.quotes import QuotePlan, QuoteRequest
from quantlab.orderbook import BookSnapshot, ExecutionReport, OrderView
from quantlab.portfolio.accounting import AccountSnapshot, MakerFill


@dataclass(frozen=True, slots=True)
class LabRecord:
    time_us: int
    kind: str
    public_event_number: int
    market: EventRecord | None
    request: QuoteRequest | None
    plan: QuotePlan | None
    cancelled: tuple[OrderView, ...]
    placed: tuple[LimitOrder, ...]
    reports: tuple[ExecutionReport, ...]
    book_after: BookSnapshot
    own_quotes: tuple[OrderView, ...]
    reference_source: str
    account: AccountSnapshot
    fills: tuple[MakerFill, ...]


@dataclass(frozen=True, slots=True)
class LabResult:
    market_config: SimulationConfig
    maker_config: MakerConfig
    simulator_version: str
    python_version: str
    records: tuple[LabRecord, ...]

    @property
    def final_account(self) -> AccountSnapshot:
        return self.records[-1].account

    @property
    def fills(self) -> tuple[MakerFill, ...]:
        return tuple(fill for record in self.records for fill in record.fills)


def public_reference(
    book: BookSnapshot, owned_ids: set[str], last_trade: int | None, opening: int
) -> tuple[Fraction, str, int | None, int | None]:
    """Exclude own displayed orders; every input is an observable market fact."""
    bid = next(
        (
            level.price_ticks
            for level in book.bids
            if any(o.order_id not in owned_ids for o in level.orders)
        ),
        None,
    )
    ask = next(
        (
            level.price_ticks
            for level in book.asks
            if any(o.order_id not in owned_ids for o in level.orders)
        ),
        None,
    )
    if bid is not None and ask is not None:
        reference, source = Fraction(bid + ask, 2), "external midpoint"
    elif last_trade is not None:
        reference, source = Fraction(last_trade), "last transaction fallback"
    else:
        reference, source = Fraction(opening), "public opening fallback"
    return reference, source, bid, ask
