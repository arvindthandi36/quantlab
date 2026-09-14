"""Explicit public projections: no private records, actor labels, seeds or latent data."""

from dataclasses import dataclass, replace

from quantlab.domain import Order
from quantlab.market.records import SessionResult
from quantlab.orderbook import BookSnapshot, ExecutionReport, PriceLevel


@dataclass(frozen=True, slots=True)
class PublicEvent:
    time_us: int
    order: Order
    report: ExecutionReport
    book_after: BookSnapshot


@dataclass(frozen=True, slots=True)
class PublicSnapshot:
    time_us: int
    book: BookSnapshot
    last_trade_ticks: int | None


@dataclass(frozen=True, slots=True)
class PublicSession:
    """Safe presentation data, deliberately without a reference to observer state."""

    tick_size: str
    events: tuple[PublicEvent, ...]
    final: PublicSnapshot


def anonymous_book(book: BookSnapshot, aliases: dict[str, str]) -> BookSnapshot:
    """Keep genuine depth/FIFO while stripping source-encoding order identifiers."""

    def levels(side: tuple[PriceLevel, ...]) -> tuple[PriceLevel, ...]:
        return tuple(
            PriceLevel(
                level.price_ticks,
                tuple(replace(o, order_id=aliases[o.order_id]) for o in level.orders),
            )
            for level in side
        )

    return BookSnapshot(levels(book.bids), levels(book.asks))


def project_public(session: SessionResult) -> PublicSession:
    """Publish only submitted instructions and executions, never private non-actions."""
    aliases: dict[str, str] = {}
    events = []
    last_trade = None
    for record in session.events:
        if record.order is None:
            continue
        if record.report is None:
            raise ValueError("cannot publish an instruction without an execution report")
        aliases[record.order.order_id] = f"order-{record.report.arrival_sequence}"
        order = replace(record.order, order_id=aliases[record.order.order_id])
        trades = tuple(
            replace(
                t,
                maker_order_id=aliases[t.maker_order_id],
                taker_order_id=aliases[t.taker_order_id],
            )
            for t in record.report.trades
        )
        report = replace(record.report, order_id=order.order_id, trades=trades)
        events.append(
            PublicEvent(
                record.event.time_us, order, report, anonymous_book(record.book_after, aliases)
            )
        )
        if trades:
            last_trade = trades[-1].price_ticks
    final = PublicSnapshot(
        session.end_time_us, anonymous_book(session.final_book, aliases), last_trade
    )
    return PublicSession(session.config.tick_size, tuple(events), final)
