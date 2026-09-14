"""Public-clock markouts and explicitly defined maker diagnostics, separate from cash."""

import math
from dataclasses import dataclass
from fractions import Fraction

from quantlab.analytics.markouts import Markout, MarkoutStatus, Reference
from quantlab.domain import Side
from quantlab.market.events import EventKind
from quantlab.market_making.quotes import QuotePlan
from quantlab.market_making.records import LabRecord
from quantlab.orderbook import OrderView
from quantlab.portfolio.accounting import AccountSnapshot, MakerFill


@dataclass(frozen=True, slots=True)
class PublicLabFrame:
    time_us: int
    public_event_number: int
    action: str
    best_bid: int | None
    best_ask: int | None
    reference_source: str
    account: AccountSnapshot
    own_quotes: tuple[OrderView, ...]
    fills: tuple[MakerFill, ...]
    plan: QuotePlan | None


def public_frames(records: tuple[LabRecord, ...]) -> tuple[PublicLabFrame, ...]:
    """No observer references, hidden timestamps, actor types, seeds or external IDs."""
    return tuple(
        PublicLabFrame(
            r.time_us,
            r.public_event_number,
            "public order" if r.kind == "market" else r.kind,
            r.book_after.best_bid,
            r.book_after.best_ask,
            r.reference_source,
            r.account,
            r.own_quotes,
            r.fills,
            r.plan,
        )
        for r in records
        if r.kind != "market" or (r.market and r.market.order is not None)
    )


def lab_markouts(
    records: tuple[LabRecord, ...],
    horizons: tuple[int, ...] = (1, 5, 20),
    *,
    debug: bool = False,
    as_of_records: int | None = None,
) -> tuple[Markout, ...]:
    """h counts subsequent PUBLIC EXCHANGE EVENTS, not Phase 3's private event clock.

    A prefix cutoff prevents any lookahead into already-stored future records.
    Debug adds a separately labelled latent reference at the same public maturities.
    """
    count = len(records) if as_of_records is None else as_of_records
    if type(count) is not int or not 0 <= count <= len(records):
        raise ValueError("as_of_records must identify an available prefix")
    if (
        not isinstance(horizons, tuple)
        or not horizons
        or any(type(h) is not int or h <= 0 for h in horizons)
        or tuple(sorted(set(horizons))) != horizons
    ):
        raise ValueError("markout horizons must be positive, increasing and unique")
    occurred = records[:count]
    maturity = {}
    last_public, latent = 0, None
    for record in occurred:
        if debug and record.market is not None:
            latent = record.market.latent_after_ticks
        if record.public_event_number > last_public:
            maturity[record.public_event_number] = (
                record.time_us,
                record.book_after.mid_price_ticks,
                latent,
            )
            last_public = record.public_event_number
    results = []
    for record in occurred:
        for fill in record.fills:
            sign = 1 if fill.side is Side.BUY else -1
            references = (
                (Reference.MIDPOINT, Reference.LATENT) if debug else (Reference.MIDPOINT,)
            )
            for reference in references:
                before = (
                    fill.midpoint_before_ticks
                    if reference is Reference.MIDPOINT
                    else record.market.latent_before_ticks
                )
                initial = None if before is None else sign * (before - fill.price_ticks)
                for horizon in horizons:
                    target = fill.public_event_number + horizon
                    when = after = movement = value = None
                    status = MarkoutStatus.PENDING
                    if target in maturity:
                        when, mid, truth = maturity[target]
                        after = mid if reference is Reference.MIDPOINT else truth
                        status = (
                            MarkoutStatus.MISSING if after is None else MarkoutStatus.AVAILABLE
                        )
                        if after is not None:
                            value = sign * (after - fill.price_ticks)
                            movement = None if before is None else sign * (after - before)
                    results.append(
                        Markout(
                            fill.trade_id,
                            fill.time_us,
                            fill.public_event_number,
                            horizon,
                            target,
                            when,
                            reference,
                            fill.side,
                            fill.quantity,
                            fill.price_ticks,
                            before,
                            after,
                            initial,
                            movement,
                            value,
                            status,
                        )
                    )
    return tuple(results)


@dataclass(frozen=True, slots=True)
class MakerDiagnostics:
    fills: int
    buy_fills: int
    sell_fills: int
    buy_units: int
    sell_units: int
    posted_units: int
    fill_rate: Fraction | None
    average_inventory: Fraction
    average_absolute_inventory: Fraction
    rms_inventory: float
    maximum_absolute_inventory: int
    average_quoted_spread_ticks: Fraction | None
    two_sided_quote_time_fraction: Fraction
    average_effective_spread_ticks: Fraction | None
    effective_spread_covered_units: int
    turnover_ticks: int
    maximum_drawdown_ticks: Fraction
    attribution_comment: str


@dataclass(frozen=True, slots=True)
class MarkoutSummary:
    horizon_events: int
    weighted_sum_ticks: Fraction
    available_units: int
    missing_units: int
    pending_units: int

    @property
    def mean_ticks(self) -> Fraction | None:
        return self.weighted_sum_ticks / self.available_units if self.available_units else None


def summarise_markouts(
    marks: tuple[Markout, ...], *, horizons: tuple[int, ...] | None = None
) -> tuple[MarkoutSummary, ...]:
    """Volume-weight public midpoint marks; missing/pending units never enter the mean."""
    if any(m.reference is not Reference.MIDPOINT for m in marks):
        raise ValueError("public summary requires midpoint markouts only")
    summaries = []
    for horizon in sorted({m.horizon_events for m in marks}) if horizons is None else horizons:
        group = [m for m in marks if m.horizon_events == horizon]
        available = [m for m in group if m.provider_markout_ticks is not None]
        summaries.append(
            MarkoutSummary(
                horizon,
                sum((m.quantity * m.provider_markout_ticks for m in available), Fraction(0)),
                sum(m.quantity for m in available),
                sum(m.quantity for m in group if m.status is MarkoutStatus.MISSING),
                sum(m.quantity for m in group if m.status is MarkoutStatus.PENDING),
            )
        )
    return tuple(summaries)


def diagnostics(records: tuple[LabRecord, ...]) -> MakerDiagnostics:
    """Time-weight inventory/quotes; volume-weight spread. Use occurred public facts only."""
    frames = public_frames(records)
    if not frames or frames[0].time_us != 0:
        raise ValueError("diagnostics require a session beginning at time zero")
    elapsed = frames[-1].time_us
    area = abs_area = square_area = quote_area = quote_time = 0
    for before, after in zip(frames, frames[1:], strict=False):
        dt = after.time_us - before.time_us
        if dt < 0:
            raise ValueError("public frames are out of time order")
        q = before.account.inventory
        area += dt * q
        abs_area += dt * abs(q)
        square_area += dt * q * q
        bids = [o for o in before.own_quotes if o.side is Side.BUY]
        asks = [o for o in before.own_quotes if o.side is Side.SELL]
        if bids and asks:
            quote_time += dt
            quote_area += dt * (asks[0].price_ticks - bids[0].price_ticks)
    fills = tuple(f for frame in frames for f in frame.fills)
    buys = [f for f in fills if f.side is Side.BUY]
    sells = [f for f in fills if f.side is Side.SELL]
    posted = sum(r.bid_size + r.ask_size for frame in frames if (r := frame.plan) is not None)
    traded = sum(f.quantity for f in fills)
    covered = [f for f in fills if f.midpoint_before_ticks is not None]
    covered_units = sum(f.quantity for f in covered)
    effective = sum(
        (2 * f.signed_quantity * (f.midpoint_before_ticks - f.price_ticks) for f in covered),
        Fraction(0),
    )
    peak = drawdown = Fraction(0)
    for frame in frames:
        peak = max(peak, frame.account.total_pnl_ticks)
        drawdown = max(drawdown, peak - frame.account.total_pnl_ticks)
    account = frames[-1].account
    if account.total_pnl_ticks > 0 and account.inventory_movement_ticks > max(
        account.spread_capture_ticks, Fraction(0)
    ):
        comment = (
            "Positive P&L is dominated by inventory/reference movement, not execution edge."
        )
    elif account.total_pnl_ticks > 0:
        comment = (
            "Positive marked P&L; execution edge contributed. "
            "Review markouts and inventory risk."
        )
    else:
        comment = (
            "Nonpositive marked P&L; inspect execution edge, "
            "inventory movement and fees separately."
        )
    return MakerDiagnostics(
        len(fills),
        len(buys),
        len(sells),
        sum(f.quantity for f in buys),
        sum(f.quantity for f in sells),
        posted,
        Fraction(traded, posted) if posted else None,
        Fraction(area, elapsed) if elapsed else Fraction(0),
        Fraction(abs_area, elapsed) if elapsed else Fraction(0),
        math.sqrt(square_area / elapsed) if elapsed else 0.0,
        account.maximum_absolute_inventory,
        Fraction(quote_area, quote_time) if quote_time else None,
        Fraction(quote_time, elapsed) if elapsed else Fraction(0),
        effective / covered_units if covered_units else None,
        covered_units,
        sum(f.quantity * f.price_ticks for f in fills),
        drawdown,
        comment,
    )


def informed_fill_percentage(records: tuple[LabRecord, ...]) -> float | None:
    """Observer-only fraction of maker execution records, not share of units."""
    fills = sum(len(r.fills) for r in records)
    informed = sum(
        len(r.fills)
        for r in records
        if r.market is not None and r.market.event.kind is EventKind.INFORMED
    )
    return 100 * informed / fills if fills else None
