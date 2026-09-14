"""Provider-signed markouts at exact subsequent-event horizons, with explicit maturity."""

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction

from quantlab.domain import Side
from quantlab.market.records import SessionResult
from quantlab.orderbook import BookSnapshot


class Reference(Enum):
    MIDPOINT = "public_midpoint"
    LATENT = "observer_latent"


class MarkoutStatus(Enum):
    AVAILABLE = "available"
    PENDING = "horizon_not_reached"
    MISSING = "reference_unavailable_at_horizon"


@dataclass(frozen=True, slots=True)
class Markout:
    trade_id: int
    trade_time_us: int
    trade_event_number: int
    horizon_events: int
    maturity_event_number: int
    maturity_time_us: int | None
    reference: Reference
    provider_side: Side
    quantity: int
    execution_price_ticks: int
    reference_before_ticks: float | Fraction | None
    reference_after_ticks: float | Fraction | None
    initial_edge_ticks: float | Fraction | None
    reference_move_ticks: float | Fraction | None
    provider_markout_ticks: float | Fraction | None
    status: MarkoutStatus


def _midpoint(book: BookSnapshot) -> float | None:
    mid = book.mid_price_ticks
    return None if mid is None else float(mid)


def analyse_markouts(
    session: SessionResult, *, as_of_events: int | None = None
) -> tuple[Markout, ...]:
    """Observer analytics. Never read a record beyond the explicit occurred-event cutoff.

    Event numbers are one-based; a trade in event n matures at n+h. Pending
    horizons have no future reference, maturity time or markout. References do
    not fall back to each other. Fee/P&L accounting is outside this diagnostic.
    """
    count = len(session.events) if as_of_events is None else as_of_events
    if type(count) is not int or not 0 <= count <= len(session.events):
        raise ValueError("as_of_events must count an available prefix of the session")
    occurred = session.events[:count]
    results = []
    before_book = BookSnapshot((), ())
    for index, record in enumerate(occurred):
        if record.report:
            for trade in record.report.trades:
                provider_side = trade.aggressor_side.opposite
                direction = 1 if provider_side is Side.BUY else -1
                for reference in Reference:
                    before = (
                        _midpoint(before_book)
                        if reference is Reference.MIDPOINT
                        else record.latent_before_ticks
                    )
                    initial = (
                        None if before is None else direction * (before - trade.price_ticks)
                    )
                    for horizon in session.config.markout_horizons_events:
                        target = index + horizon
                        maturity_time = future = movement = markout = None
                        status = MarkoutStatus.PENDING
                        if target < count:
                            matured = occurred[target]
                            maturity_time = matured.event.time_us
                            future = (
                                _midpoint(matured.book_after)
                                if reference is Reference.MIDPOINT
                                else matured.latent_after_ticks
                            )
                            status = (
                                MarkoutStatus.MISSING
                                if future is None
                                else MarkoutStatus.AVAILABLE
                            )
                            if future is not None:
                                markout = direction * (future - trade.price_ticks)
                                movement = (
                                    None if before is None else direction * (future - before)
                                )
                        results.append(
                            Markout(
                                trade.trade_id,
                                record.event.time_us,
                                index + 1,
                                horizon,
                                target + 1,
                                maturity_time,
                                reference,
                                provider_side,
                                trade.quantity,
                                trade.price_ticks,
                                before,
                                future,
                                initial,
                                movement,
                                markout,
                                status,
                            )
                        )
        before_book = record.book_after
    return tuple(results)
