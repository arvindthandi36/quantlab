"""Reproducible core workloads. Run from the checkout: python -m scripts.core_benchmark."""

import cProfile
import gc
import io
import json
import pstats
import resource
import statistics
import tempfile
import time
import tracemalloc
from pathlib import Path

import numpy as np

from quantlab import LimitOrder, MarketOrder, OrderBook, Side
from quantlab.market.config import SimulationConfig
from quantlab.market.simulation import run_simulation
from quantlab.options.models import PricingInputs
from quantlab.options.monte_carlo import monte_carlo_price
from quantlab.options.session import OptionsConfig, OptionsSession, replay_options
from quantlab.research.adapters.maker import MakerAdapter, maker_configuration
from quantlab.research.codec import canonical, digest
from quantlab.research.engine import execute, versions
from quantlab.research.models import ExperimentSpec, Variant
from quantlab.research.performance import profile_adapter
from quantlab.research.seeds import SeedPlan
from quantlab.risk.monte_carlo import monte_carlo_risk, vector_option_prices
from quantlab.risk.portfolio import Portfolio, Position
from quantlab.statarb.process import Process
from quantlab.statarb.statistics import CausalModel
from quantlab.trading.replay import dumps, loads
from quantlab.trading.scenarios import select_scenario
from quantlab.trading.session import TradingSession

DEST = Path("docs/release/phase_11")
RESULT = {
    "versions": versions(),
    "seed": 111042,
    "measurements": {},
    "note": "Sequential local wall-clock measurements; no other validation workload running. "
    "Memory uses tracemalloc (Python-tracked, not all native allocation). "
    "These are correctness/engineering workloads, not strategy evidence.",
}


def save():
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / "benchmarks.json").write_text(json.dumps(RESULT, indent=2, allow_nan=False) + "\n")


def measured(name, function):
    start = time.perf_counter()
    value = function()
    elapsed = time.perf_counter() - start
    RESULT["measurements"][name] = {"seconds": elapsed, "result": value}
    save()
    print(name, round(elapsed, 4), flush=True)


def matching():
    b = OrderBook()
    for i in range(10000):
        b.submit(LimitOrder(f"s{i}", Side.SELL, 3, 10000 + i % 5))
        r = b.submit(MarketOrder(f"b{i}", Side.BUY, 5))
        assert r.executed_quantity == r.buyer_filled_quantity == r.seller_filled_quantity == 3
        assert r.cancelled_quantity == 2
    b.check_invariants()
    return {"orders": 20000, "trades": 10000, "filled_units_each_side": 30000, "resting": 0}


def events():
    s = run_simulation(
        SimulationConfig(
            seed=111042,
            duration_us=300_000_000,
            noise_rate_per_second=8,
            liquidity_rate_per_second=6,
            informed_rate_per_second=3,
        )
    )
    return {
        "events": len(s.events),
        "journal_bytes": len(canonical(s)),
        "fingerprint": digest(s),
        "seconds_simulated": 300,
    }


def research():
    adapter = MakerAdapter()
    config = maker_configuration(duration_us=2_000_000)
    spec = ExperimentSpec(
        "Does a 1000-run batch finish and reconcile?",
        "Every requested independent seed completes with real accounting invariants enabled.",
        SeedPlan(111042, "development", 1000),
        (Variant("fixed", config),),
        adapter.name,
        bootstrap_resamples=100,
    )
    with tempfile.TemporaryDirectory() as tmp:
        r = execute(spec, adapter, Path(tmp) / "batch")
        assert r["status"] == "complete"
        result = {
            "runs": len(r["runs"]),
            "status": r["status"],
            "outcome_digest": r["outcome_digest"],
            "duration_per_market_seconds": 2,
            "variants": 1,
            "bytes_on_disk": sum(p.stat().st_size for p in Path(tmp).rglob("*") if p.is_file()),
        }
    return result


def risk():
    p = Portfolio(
        tuple(
            Position(f"C{k}", "S", (-1 if k % 2 else 1), 100, 2, 100, "call", k, 1, 0.2)
            for k in range(90, 111, 2)
        ),
        10000,
    )
    r = monte_carlo_risk(p, ["S"], [[0.0001]], [0], paths=100000, seed=111042)
    assert r["full"]["es"] >= r["full"]["var"]
    return {
        "paths": 100000,
        "option_positions": 11,
        "var": r["full"]["var"],
        "es": r["full"]["es"],
        "retained_json_bytes": len(canonical(r)),
    }


def rolling():
    process = Process(seed=111042)
    prices = [process.step() for _ in range(2000)]
    model = CausalModel(mode="rolling")
    last = None
    for t in range(80, 2000):
        last = model.at(prices, t)
    return {
        "fits": 1920,
        "history_observations": 2000,
        "last_fit_end": last["fit"]["end"],
        "last_signal_digest": digest(last),
    }


def options_soak():
    s = OptionsSession(
        OptionsConfig(seed=111042, steps=252, expiries_days=(365,), strikes=(100,))
    )
    s.command(
        "option_order",
        contract_id=s.selected,
        side="buy",
        quantity=1,
        quote_revision=s.quote_revision,
    )
    s.command("set_auto", frequency=1)
    samples = []
    for i in range(252):
        s.command("step", count=1)
        if (i + 1) % 63 == 0:
            gc.collect()
            samples.append(
                {
                    "day": i + 1,
                    "public_bytes": len(canonical(s.snapshot())),
                }
            )
    tracemalloc.start()
    public = canonical(s.snapshot())
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del public
    if s.status == "active":
        s.command("end")
    s.accounts()
    s.stock.check_invariants()
    j = s.journal()
    assert replay_options(j).journal() == j
    return {
        "steps": 252,
        "hedge_decisions": len(s.hedges),
        "stock_fills": len(s.stock.account.fills),
        "journal_bytes": len(canonical(j)),
        "final_snapshot_serialization_peak_traced_bytes": peak,
        "checkpoints": samples,
        "replay": True,
        "note": "Linear audit-history retention within the 252-step cap.",
    }


def manual_soak():
    s = TradingSession(select_scenario(seed=111042, duration_seconds=300))
    for _ in range(250):
        s.command("order", side="buy", quantity=1, order_type="market")
        s.command("order", side="sell", quantity=1, order_type="market")
        s.command("step_event")
        if s.status == "ended":
            break
    s.command("end")
    s.check_invariants()
    raw = dumps(s)
    assert loads(raw).public_snapshot() == s.public_snapshot()
    return {
        "actions": len(s.actions),
        "evidence_events": len(s.evidence),
        "journal_bytes": len(raw),
        "public_bytes": len(canonical(s.public_snapshot())),
        "replay": True,
    }


def main():
    measured("matching_20000_orders", matching)
    profile = cProfile.Profile()
    profile.runcall(matching)
    out = io.StringIO()
    pstats.Stats(profile, stream=out).strip_dirs().sort_stats("cumulative").print_stats(15)
    RESULT["matching_profile"] = out.getvalue()
    measured("event_simulation_300_seconds", events)
    measured("research_1000_runs", research)
    measured(
        "option_mc_1000000_paths",
        lambda: monte_carlo_price(
            "call", PricingInputs(100, 100, 1, 0.2, 0.05), paths=1000000, seed=111042
        ),
    )
    measured("risk_100000_scenarios", risk)
    measured("rolling_statarb_2000_observations", rolling)
    measured(
        "full_vs_light_memory",
        lambda: profile_adapter(
            MakerAdapter(),
            maker_configuration(duration_us=30_000_000),
            seeds=(111042, 111043, 111044),
        ),
    )
    measured("manual_soak", manual_soak)
    measured("options_hedge_soak", options_soak)
    p = Position("C", "X", 1, 100, 2.3, 100, "call", 100, 30 / 365, 0.2)
    x = np.linspace(1, 200, 100000)
    trials = []
    for _ in range(5):
        start = time.perf_counter()
        vector_option_prices(p, x, 29 / 365)
        trials.append(time.perf_counter() - start)
    RESULT["shared_pricing_kernel_after"] = {
        "seconds": trials,
        "median": statistics.median(trials),
        "note": "Source consolidation and numerical validation; not a speed optimisation.",
    }
    RESULT["process_peak_rss_platform_units"] = resource.getrusage(
        resource.RUSAGE_SELF
    ).ru_maxrss
    save()


if __name__ == "__main__":
    main()
