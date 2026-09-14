"""A modest paired validation experiment, not a general Monte Carlo research engine."""

from dataclasses import dataclass, replace

from quantlab.market.config import SimulationConfig
from quantlab.market_making.analytics import (
    MakerDiagnostics,
    MarkoutSummary,
    diagnostics,
    lab_markouts,
    summarise_markouts,
)
from quantlab.market_making.config import MakerConfig, Strategy
from quantlab.market_making.lab import run_lab
from quantlab.market_making.records import LabResult
from quantlab.portfolio.accounting import AccountSnapshot


@dataclass(frozen=True, slots=True)
class ComparisonRun:
    seed: int
    strategy: Strategy
    account: AccountSnapshot
    diagnostics: MakerDiagnostics
    markouts: tuple[MarkoutSummary, ...]


def exogenous_signature(result: LabResult) -> tuple:
    """Only exogenous shocks/arrivals/signals, not prices/fills changed by the policy."""
    return tuple(
        (
            r.market.event.time_us,
            r.market.event.sequence,
            r.market.event.kind,
            r.market.latent_before_ticks,
            r.market.latent_after_ticks,
            None if r.market.informed is None else r.market.informed.signal,
        )
        for r in result.records
        if r.market is not None
    )


def compare_strategies(
    *,
    seeds: tuple[int, ...] = tuple(range(20)),
    duration_us: int = 30_000_000,
    maker: MakerConfig | None = None,
) -> tuple[ComparisonRun, ...]:
    """Common named streams per paired seed; all runs retained without tuning/selection."""
    if not seeds or len(seeds) > 100 or len(set(seeds)) != len(seeds):
        raise ValueError("comparison requires 1–100 distinct seeds")
    runs = []
    base = maker or MakerConfig()
    for seed in seeds:
        market = SimulationConfig(
            seed=seed, duration_us=duration_us, informed_rate_per_second=1
        )
        fixed = run_lab(market, replace(base, strategy=Strategy.FIXED))
        aware = run_lab(market, replace(base, strategy=Strategy.INVENTORY))
        if exogenous_signature(fixed) != exogenous_signature(aware):
            raise AssertionError(
                "paired strategy environments do not share exogenous randomness"
            )
        for result in (fixed, aware):
            marks = lab_markouts(result.records, market.markout_horizons_events)
            summaries = summarise_markouts(marks, horizons=market.markout_horizons_events)
            runs.append(
                ComparisonRun(
                    seed,
                    result.maker_config.strategy,
                    result.final_account,
                    diagnostics(result.records),
                    tuple(summaries),
                )
            )
    return tuple(runs)
