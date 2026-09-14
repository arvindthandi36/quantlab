"""Compact public presentation; observer debug is a separate explicitly requested panel."""

from decimal import Decimal, localcontext
from fractions import Fraction

from quantlab.analytics.markouts import Markout, Reference
from quantlab.market_making.analytics import (
    diagnostics,
    informed_fill_percentage,
    lab_markouts,
    public_frames,
    summarise_markouts,
)
from quantlab.market_making.comparison import ComparisonRun
from quantlab.market_making.config import Strategy
from quantlab.market_making.quotes import MakerObservation
from quantlab.market_making.records import LabRecord, LabResult


def money(ticks, tick_size: str = "0.01") -> str:
    if ticks is None:
        return "unavailable"
    with localcontext() as context:
        context.prec = 32
        value = (
            Decimal(ticks.numerator) / Decimal(ticks.denominator)
            if isinstance(ticks, Fraction)
            else Decimal(str(ticks))
        ) * Decimal(tick_size)
        return f"{'-' if value < 0 else ''}£{abs(value):.4f}"


def _clock(time_us: int) -> str:
    return f"+{time_us / 1_000_000:.3f}s"


def render_markouts(marks: tuple[Markout, ...], *, last: int = 3) -> list[str]:
    ids = list(dict.fromkeys(m.trade_id for m in marks))[-last:]
    lines = []
    for trade_id in ids:
        references = list(dict.fromkeys(m.reference for m in marks if m.trade_id == trade_id))
        for reference in references:
            values = []
            for mark in marks:
                if mark.trade_id == trade_id and mark.reference is reference:
                    value = (
                        f"{float(mark.provider_markout_ticks):+.3f} ticks/unit"
                        if mark.provider_markout_ticks is not None
                        else mark.status.value
                    )
                    values.append(f"h{mark.horizon_events} {value}")
            lines.append(f"  Fill #{trade_id} [{reference.value}]: " + "; ".join(values))
    return lines or ["  No own fills yet."]


def render_observation(
    observation: MakerObservation, marks: tuple[Markout, ...], *, tick_size="0.01"
) -> str:
    """Accept only public data types; do not inspect a complete observer session."""
    if any(mark.reference is not Reference.MIDPOINT for mark in marks):
        raise ValueError("normal manual view cannot accept private-reference markouts")
    state = observation.account
    lines = [
        f"OBSERVE {_clock(observation.time_us)} | inventory {state.inventory:+d}",
        f"Best bid {money(observation.best_bid, tick_size)} / "
        f"ask {money(observation.best_ask, tick_size)}",
        f"Reference {money(observation.reference_ticks, tick_size)} "
        f"({observation.reference_source})",
        f"Cash {money(state.cash_ticks, tick_size)} | "
        f"marked P&L {money(state.total_pnl_ticks, tick_size)}",
        "Your resting quotes: "
        + (
            ", ".join(
                f"{o.side.value} {o.remaining_quantity} @ {money(o.price_ticks, tick_size)}"
                for o in observation.quotes
            )
            or "none"
        ),
        "Recent own fills: "
        + (
            ", ".join(
                f"#{f.trade_id} {f.side.value} {f.quantity} @ {money(f.price_ticks, tick_size)}"
                for f in observation.recent_fills
            )
            or "none"
        ),
        "Provider markouts: public-event horizons, + favourable / - adverse:",
    ]
    lines.extend(render_markouts(marks))
    return "\n".join(lines)


def render_debug(
    records: tuple[LabRecord, ...], *, horizons: tuple[int, ...] = (1, 5, 20)
) -> str:
    market = [r.market for r in records if r.market is not None]
    lines = ["OBSERVER DEBUG — private information, never a normal strategy input"]
    if market:
        lines.append(f"Current latent: {market[-1].latent_after_ticks:.3f} ticks")
    for event in [r for r in market if r.informed is not None][-2:]:
        audit = event.informed
        lines.append(
            f"  {_clock(event.event.time_us)} signal {audit.signal.value_ticks:.3f}, "
            f"error {audit.error_ticks:+.3f}, "
            f"estimate {audit.decision.estimated_value_ticks:.3f}, "
            f"hurdle {audit.decision.threshold_ticks:.3f}: {audit.decision.reason}"
        )
    percent = informed_fill_percentage(records)
    lines.append(
        "Maker fills against informed traders: "
        + (f"{percent:.1f}% of execution records" if percent is not None else "unavailable")
    )
    lines.extend(render_markouts(lab_markouts(records, horizons, debug=True)))
    return "\n".join(lines)


def render_lab(result: LabResult, *, debug=False, limit=12) -> str:
    if type(limit) is not int or limit <= 0:
        raise ValueError("limit must be positive")
    frames = public_frames(result.records)
    tick = result.market_config.tick_size
    lines = [f"QuantLab Market Making Lab | {result.maker_config.strategy.value} | PUBLIC VIEW"]
    relevant = [f for f in frames if f.action != "public order" or f.fills]
    for frame in relevant[:limit]:
        if frame.plan is not None:
            plan = frame.plan
            lines.append(
                f"{_clock(frame.time_us)} centre {money(plan.centre_ticks, tick)}: "
                f"bid {plan.bid_size} @ {money(plan.bid_ticks, tick)}, "
                f"ask {plan.ask_size} @ {money(plan.ask_ticks, tick)}; "
                f"inventory {frame.account.inventory:+d}"
            )
            if plan.adjustments:
                lines.append("  " + "; ".join(plan.adjustments))
        for fill in frame.fills:
            lines.append(
                f"{_clock(frame.time_us)} Fill #{fill.trade_id}: {fill.side.value} "
                f"{fill.quantity} @ {money(fill.price_ticks, tick)}; "
                f"inventory {frame.account.inventory:+d}, "
                f"marked P&L {money(frame.account.total_pnl_ticks, tick)}"
            )
    if len(relevant) > limit:
        lines.append(f"... {len(relevant) - limit} further maker event groups omitted.")
    state, stats = result.final_account, diagnostics(result.records)
    lines.extend(
        [
            f"End: inventory {state.inventory:+d}; maker quotes cancelled; "
            "inventory remains marked.",
            f"Execution cash {money(state.execution_cash_ticks, tick)}; "
            f"fees {money(state.fees_ticks, tick)}; "
            f"cash balance {money(state.cash_ticks, tick)}.",
            f"FIFO realised trading P&L {money(state.realised_trading_pnl_ticks, tick)}; "
            f"realised after fees {money(state.realised_pnl_ticks, tick)}; "
            f"unrealised {money(state.unrealised_pnl_ticks, tick)}.",
            f"Total marked P&L {money(state.total_pnl_ticks, tick)} = "
            f"execution-edge proxy {money(state.spread_capture_ticks, tick)} + "
            f"inventory/reference movement {money(state.inventory_movement_ticks, tick)} - "
            f"fees {money(state.fees_ticks, tick)}.",
            f"Fills {stats.fills}: {stats.buy_fills} buys/{stats.sell_fills} sells; "
            f"units {stats.buy_units} bought/{stats.sell_units} sold; "
            f"executed/posted {float(stats.fill_rate):.1%}."
            if stats.fill_rate is not None
            else "No posted units.",
            f"Time-weighted inventory {float(stats.average_inventory):+.3f}; "
            f"average |inventory| {float(stats.average_absolute_inventory):.3f}; "
            f"RMS {stats.rms_inventory:.3f}; "
            f"max |inventory| {stats.maximum_absolute_inventory}.",
            f"Average own quoted spread {money(stats.average_quoted_spread_ticks, tick)} "
            f"({float(stats.two_sided_quote_time_fraction):.1%} time coverage); "
            f"effective spread {money(stats.average_effective_spread_ticks, tick)} "
            f"({stats.effective_spread_covered_units} units covered).",
            f"Turnover {money(stats.turnover_ticks, tick)}; "
            f"maximum observed drawdown {money(stats.maximum_drawdown_ticks, tick)}.",
            stats.attribution_comment,
            "Provider midpoint markouts (public-event horizons; diagnostic, not cash P&L):",
        ]
    )
    lines.extend(
        render_markouts(
            lab_markouts(result.records, result.market_config.markout_horizons_events)
        )
    )
    for summary in summarise_markouts(
        lab_markouts(result.records, result.market_config.markout_horizons_events),
        horizons=result.market_config.markout_horizons_events,
    ):
        lines.append(
            f"  Mean h{summary.horizon_events}: {money(summary.mean_ticks, tick)}/unit; "
            f"units available {summary.available_units}, missing {summary.missing_units}, "
            f"pending {summary.pending_units}."
        )
    if debug:
        lines.append(f"Observer reproduction seed: {result.market_config.seed}")
        lines.append(
            render_debug(result.records, horizons=result.market_config.markout_horizons_events)
        )
    return "\n".join(lines)


def render_comparison(runs: tuple[ComparisonRun, ...], *, tick_size="0.01") -> str:
    grouped = {
        s: [r for r in runs if r.strategy is s] for s in (Strategy.FIXED, Strategy.INVENTORY)
    }
    lines = [
        "Paired validation: common exogenous randomness; no claim of strategy superiority.",
        "Metric | Fixed | Inventory-aware",
        "--- | ---: | ---:",
    ]
    measures = (
        ("Mean P&L", lambda r: r.account.total_pnl_ticks, True),
        (
            "Mean average absolute inventory",
            lambda r: r.diagnostics.average_absolute_inventory,
            False,
        ),
        ("Mean RMS inventory", lambda r: r.diagnostics.rms_inventory, False),
        (
            "Mean maximum absolute inventory",
            lambda r: r.diagnostics.maximum_absolute_inventory,
            False,
        ),
        ("Mean maximum drawdown", lambda r: r.diagnostics.maximum_drawdown_ticks, True),
        ("Mean execution-edge proxy", lambda r: r.account.spread_capture_ticks, True),
        (
            "Mean inventory/reference movement",
            lambda r: r.account.inventory_movement_ticks,
            True,
        ),
        ("Mean fees", lambda r: r.account.fees_ticks, True),
    )
    for label, get, currency in measures:
        values = []
        for group in grouped.values():
            average = sum((get(r) for r in group), Fraction(0)) / len(group)
            values.append(money(average, tick_size) if currency else f"{float(average):.3f}")
        lines.append(label + " | " + " | ".join(values))
    for horizon in (1, 5, 20):
        values = []
        for group in grouped.values():
            marks = [m for r in group for m in r.markouts if m.horizon_events == horizon]
            units = sum(m.available_units for m in marks)
            total = sum(m.available_units + m.pending_units + m.missing_units for m in marks)
            value = (
                sum((m.weighted_sum_ticks for m in marks), Fraction(0)) / units
                if units
                else None
            )
            values.append(f"{money(value, tick_size)}/unit ({units}/{total} units available)")
        lines.append(f"Pooled h{horizon} public-midpoint markout | " + " | ".join(values))
    return "\n".join(lines)
