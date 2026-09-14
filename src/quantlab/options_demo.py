"""Reproducible Phase 8 teaching evidence, including real manual stock orders."""

import argparse
import cProfile
import io
import json
import math
import pstats
import statistics
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

from quantlab.options.analytics import shock
from quantlab.options.iv import implied_volatility
from quantlab.options.models import PricingInputs
from quantlab.options.monte_carlo import monte_carlo_price, terminal_payoffs
from quantlab.options.pricing import finite_differences, greeks, parity_residual, price
from quantlab.options.research import OptionsAdapter
from quantlab.options.session import OptionsSession, replay_options
from quantlab.options_experiments import design
from quantlab.randomness import RandomStreams
from quantlab.research.codec import plain, write_new
from quantlab.research.engine import versions
from quantlab.tutor.derivatives import derivative_context
from quantlab.tutor.questions import question_for


def demonstrate():
    s = OptionsSession()
    opening = s.snapshot(include_curves=True)
    events = []

    def record(label, execution=None):
        snap = s.snapshot()
        events.append(
            {
                "event": label,
                "day": snap["elapsed_days"],
                "spot": snap["spot"],
                "greeks": snap["greeks"],
                "accounts": snap["accounts"],
                "stock_position": snap["stock"]["account"]["position"],
                "execution": execution,
            }
        )

    record("Inspect ATM call: strike 100, expiry day 30, multiplier 100")
    fill = s.command(
        "option_order",
        contract_id=s.selected,
        side="buy",
        quantity=1,
        quote_revision=s.quote_revision,
    )
    record("Buy one call at the displayed dealer ask", fill)
    context = derivative_context(s.snapshot(), "phase8-demo", "option_order")
    lessons = {
        key: question_for(key, context, 2).public(True)
        for key in ("premium", "contract_multiplier", "delta_hedging")
    }
    result = s.command("stock_order", side="sell", quantity=51)
    record("Manual market sell of 51 stock units through Phase 1 matching", result)
    s.command("step", count=1)
    record("Observe one new stock move; the old hedge is now imperfect")
    signed = round(-s.aggregate_greeks()["option_delta"]) - s.stock.account.inventory
    result = (
        s.command("stock_order", side="buy" if signed > 0 else "sell", quantity=abs(signed))
        if signed
        else {"actual_filled": 0}
    )
    record("Manual re-hedge: choose whole stock units from current delta", result)
    s.command("step", count=29)
    record("Advance to day 30: the call cash-settles once; stock remains held")
    result = s.command("stock_order", side="buy", quantity=-s.stock.account.inventory)
    record("Manually close the remaining short-stock hedge through the book", result)
    s.command("end")
    journal = s.journal()
    assert replay_options(journal).journal() == journal
    x = PricingInputs(100, 100, 1, 0.2, 0.05)
    difficult = PricingInputs(100, 120, 0.25, 0.3, 0.05)
    target = price("call", difficult)
    mc = [monte_carlo_price("call", x, paths=n, seed=42) for n in (100_000, 1_000_000)]
    return {
        "versions": versions(),
        "opening": opening,
        "events": events,
        "final": s.snapshot(),
        "journal": journal,
        "tutor_examples": lessons,
        "analytic": {
            "inputs": asdict(x),
            "call": price("call", x),
            "put": price("put", x),
            "parity_residual": parity_residual(price("call", x), price("put", x), x),
            "greeks": greeks("call", x).public(),
            "finite_difference": finite_differences("call", x).public(),
        },
        "iv": implied_volatility("call", x, price("call", x), initial=0.3).public(),
        "fallback": {
            "inputs": asdict(difficult),
            "target": target,
            "initial": 0.001,
            "initial_vega": greeks("call", PricingInputs(100, 120, 0.25, 0.001, 0.05)).vega,
            "result": implied_volatility("call", difficult, target, initial=0.001).public(),
        },
        "monte_carlo": mc,
        "shocks": {
            "small": shock("call", x, spot_change=0.1),
            "large": shock("call", x, spot_change=30),
            "gamma_theta": shock("call", x, spot_change=1, elapsed_days=1),
        },
    }


def profile(destination):
    x = PricingInputs(100, 100, 1, 0.2, 0.05)

    def timing(fn, repeats=5):
        measurements = []
        for _ in range(repeats):
            start = time.perf_counter()
            fn()
            measurements.append(time.perf_counter() - start)
        return statistics.median(measurements)

    # Same pre-generated normals for the numerical equivalence and compute-only timing.
    seed = RandomStreams(42).create("options.pricing.terminal-v1").getrandbits(128)
    z = np.random.Generator(np.random.PCG64(seed)).standard_normal(100_000)

    def scalar():
        return [math.exp(-0.05) * max(100 * math.exp(0.03 + 0.2 * v) - 100, 0) for v in z]

    def vector():
        return math.exp(-0.05) * np.maximum(100 * np.exp(0.03 + 0.2 * z) - 100, 0)

    assert np.allclose(scalar(), vector(), rtol=1e-12, atol=1e-12)
    assert np.array_equal(vector(), terminal_payoffs("call", x, paths=100_000, seed=42))
    configuration = design("frequency", 2).variants[0].configuration
    adapter = OptionsAdapter()
    a, b = adapter.run(42, configuration), adapter.run(42, configuration, full=True)
    assert a.metrics == b.metrics and a.trajectory_fingerprint == b.trajectory_fingerprint
    results = {
        "versions": versions(),
        "timing": "median of five warmed calls, wall seconds",
        "analytic_one_price": timing(lambda: price("call", x)),
        "mc_100k_full_estimation": timing(lambda: monte_carlo_price("call", x)),
        "mc_1m_full_estimation": timing(lambda: monte_carlo_price("call", x, paths=1_000_000)),
        "scalar_100k_payoff_only": timing(scalar),
        "vector_100k_payoff_only": timing(vector),
        "hedge_20day_research": timing(lambda: adapter.run(42, configuration)),
        "hedge_20day_full_evidence": timing(lambda: adapter.run(42, configuration, full=True)),
        "checks": "Scalar/vector values agree; reduced/full capture metrics and hashes agree",
    }
    profiler = cProfile.Profile()
    profiler.enable()
    for seed in range(20):
        adapter.run(seed, configuration)
    profiler.disable()
    out = io.StringIO()
    pstats.Stats(profiler, stream=out).sort_stats("cumulative").print_stats(25)
    (destination / "hedging-profile.txt").write_text(out.getvalue())
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    args.destination.mkdir(parents=True, exist_ok=True)
    result = demonstrate()
    journal = result.pop("journal")
    write_new(args.destination / "manual-session.json", journal)
    write_new(args.destination / "demo.json", result)
    write_new(args.destination / "performance.json", profile(args.destination))
    print(
        json.dumps(
            plain(
                {
                    "events": result["events"],
                    "analytic": result["analytic"],
                    "iv": result["iv"],
                    "fallback": result["fallback"],
                    "monte_carlo": result["monte_carlo"],
                }
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
