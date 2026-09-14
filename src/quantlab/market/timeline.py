"""Concise human-readable presentation of actual session evidence."""

from decimal import Decimal

from quantlab import LimitOrder, PriceGrid
from quantlab.analytics.markouts import Reference, analyse_markouts
from quantlab.domain import positive_integer
from quantlab.market.config import MICROSECONDS_PER_SECOND
from quantlab.market.events import EventKind
from quantlab.market.public import project_public
from quantlab.market.records import EventRecord, SessionResult
from quantlab.orderbook.display import render_depth


def _clock(time_us: int) -> str:
    # 09:30 is an illustrative label, not an exchange calendar or local wall clock.
    seconds, microseconds = divmod(time_us, MICROSECONDS_PER_SECOND)
    days, seconds = divmod(seconds + 9 * 3600 + 30 * 60, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    prefix = f"day+{days} " if days else ""
    fraction = f".{microseconds:06d}".rstrip("0") if microseconds else ""
    return f"{prefix}{hours:02d}:{minutes:02d}:{seconds:02d}{fraction}"


def _event_lines(record: EventRecord, grid: PriceGrid) -> list[str]:
    event = record.event
    prefix = f"{_clock(event.time_us)} [e{event.sequence}]"
    if event.kind is EventKind.LATENT:
        before = Decimal(str(record.latent_before_ticks)) * grid.tick_size
        after = Decimal(str(record.latent_after_ticks)) * grid.tick_size
        return [f"{prefix} LATENT £{before:.4f} → £{after:.4f}; observer only, no order."]
    trader = {
        EventKind.NOISE: "NOISE",
        EventKind.LIQUIDITY: "LIQUIDITY",
        EventKind.INFORMED: "INFORMED",
    }[event.kind]
    private = []
    if record.informed:
        audit, decision = record.informed, record.informed.decision
        buy = (
            "unavailable"
            if decision.buy_edge_ticks is None
            else f"{decision.buy_edge_ticks:.3f}"
        )
        sell = (
            "unavailable"
            if decision.sell_edge_ticks is None
            else f"{decision.sell_edge_ticks:.3f}"
        )
        private = [
            f"    Private: latent={record.latent_before_ticks:.3f} ticks; "
            f"signal={audit.signal.value_ticks:.3f}; error={audit.error_ticks:+.3f}.",
            f"    Estimate={decision.estimated_value_ticks:.3f}; "
            f"uncertainty={decision.posterior_sd_ticks:.3f}; "
            f"hurdle={decision.threshold_ticks:.3f} ticks.",
            f"    Edges: buy={buy}; sell={sell} ticks.",
        ]
    if record.order is None:
        return [f"{prefix} {trader}: {record.reason}", *private]
    order, report = record.order, record.report
    if report is None:
        raise ValueError("an order has no execution report")
    price = (
        f" limit £{grid.to_price(order.price_ticks)}"
        if isinstance(order, LimitOrder)
        else " market"
    )
    lines = [
        f"{prefix} {trader} {order.side.value} {order.quantity}{price} [{order.order_id}]",
        f"    Why: {record.reason}.",
    ]
    lines.extend(private)
    for trade in report.trades:
        lines.append(
            f"    Trade #{trade.trade_id}: {trade.quantity}"
            f" @ £{grid.to_price(trade.price_ticks)}; "
            f"resting {trade.maker_order_id} supplies the price."
        )
    if report.resting_quantity:
        why = (
            "no eligible opposing order" if not report.trades else "no more eligible liquidity"
        )
        lines.append(f"    {report.resting_quantity} remain in book: {why}.")
    if report.cancelled_quantity:
        lines.append(
            f"    {report.cancelled_quantity} unfilled/cancelled: opposing liquidity exhausted."
        )
    if not report.resting_quantity and not report.cancelled_quantity:
        lines.append("    Incoming order fully filled.")
    return lines


def render_timeline(
    session: SessionResult, *, debug: bool = False, limit: int = 20, expand_orders: bool = False
) -> str:
    """Render a bounded timeline; only explicit debug mode reveals latent values."""
    positive_integer(limit, "limit")
    if not debug:
        return _render_public(session, limit=limit, expand_orders=expand_orders)
    grid = PriceGrid(Decimal(session.config.tick_size))
    visible = session.events
    mode = (
        "OBSERVER DEBUG — truth/error private to observer; informed trader receives only signal"
    )
    phase = 3 if session.config.informed_rate_per_second else 2
    lines = [
        f"QuantLab Phase {phase} | seed={session.config.seed} | {mode}",
        "Start: empty book.",
    ]
    for record in visible[:limit]:
        lines.extend(_event_lines(record, grid))
    if len(visible) > limit:
        lines.append(
            f"... {len(visible) - limit} further visible events omitted; increase --limit."
        )
    volume = sum(entry.trade.quantity for entry in session.tape)
    final = session.final_book
    bid = "none" if final.best_bid is None else f"£{grid.to_price(final.best_bid)}"
    ask = "none" if final.best_ask is None else f"£{grid.to_price(final.best_ask)}"
    lines.append(
        f"End {_clock(session.end_time_us)}: {len(session.events)} events; "
        f"{len(session.tape)} trades / {volume} units. Best bid {bid}; ask {ask}."
    )
    lines.extend(
        ("Final visible depth:", render_depth(final, grid, expand_orders=expand_orders))
    )
    if session.config.informed_rate_per_second:
        lines.extend(_markout_lines(session, limit))
    return "\n".join(lines)


def _markout_lines(session: SessionResult, limit: int) -> list[str]:
    marks = analyse_markouts(session)
    trade_ids = list(dict.fromkeys(m.trade_id for m in marks))
    lines = ["Provider markouts (ticks/unit; + favourable, - adverse; event horizons):"]
    for trade_id in trade_ids[:limit]:
        for reference in Reference:
            group = [m for m in marks if m.trade_id == trade_id and m.reference is reference]
            values = "; ".join(
                f"h={m.horizon_events}: "
                + (
                    f"{m.provider_markout_ticks:+.3f}"
                    if m.provider_markout_ticks is not None
                    else m.status.value
                )
                for m in group
            )
            lines.append(f"  Trade #{trade_id} [{reference.value}] {values}")
    if not marks:
        lines.append("  No trades; no markouts.")
    if len(trade_ids) > limit:
        lines.append(f"  {len(trade_ids) - limit} further trade markout groups omitted.")
    return lines


def _render_public(session: SessionResult, *, limit: int, expand_orders: bool) -> str:
    """Render only sanitised types; do not inspect any private event diagnostics."""
    public = project_public(session)
    grid = PriceGrid(Decimal(public.tick_size))
    lines = ["QuantLab | PUBLIC VIEW", "Start: empty book."]
    for record in public.events[:limit]:
        order, report = record.order, record.report
        price = (
            f"limit £{grid.to_price(order.price_ticks)}"
            if isinstance(order, LimitOrder)
            else "market"
        )
        lines.append(
            f"{_clock(record.time_us)} {order.order_id}: "
            f"{order.side.value} {order.quantity} {price}"
        )
        for trade in report.trades:
            lines.append(
                f"    Trade #{trade.trade_id}: {trade.quantity} "
                f"@ £{grid.to_price(trade.price_ticks)}; "
                f"resting {trade.maker_order_id}."
            )
        if report.resting_quantity:
            lines.append(
                f"    {report.resting_quantity} remain in book; "
                "no more eligible opposite liquidity."
            )
        if report.cancelled_quantity:
            lines.append(
                f"    {report.cancelled_quantity} unfilled/cancelled; "
                "opposite liquidity exhausted."
            )
    if len(public.events) > limit:
        lines.append(
            f"... {len(public.events) - limit} further visible events omitted; "
            "increase --limit."
        )
    trades = [t for r in public.events for t in r.report.trades]
    lines.append(
        f"End {_clock(public.final.time_us)}: {len(trades)} trades / "
        f"{sum(t.quantity for t in trades)} units."
    )
    lines.extend(
        (
            "Final visible depth:",
            render_depth(public.final.book, grid, expand_orders=expand_orders),
        )
    )
    return "\n".join(lines)
