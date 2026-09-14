"""Auditable Phase 10 demonstrations and prespecified evaluation studies."""

import argparse
import cProfile
import json
import time
import tracemalloc
from dataclasses import replace
from pathlib import Path

from quantlab.research.codec import plain
from quantlab.research.engine import execute
from quantlab.research.replay import reproduce_run
from quantlab.statarb.examples import teaching_cases
from quantlab.statarb.research import (
    BASE_RULES,
    StatArbAdapter,
    backtest,
    evaluate_selection,
    experiment_spec,
    generate,
    invalid_lookahead,
    mining_universe,
    select_pair,
    sweep,
    walk_forward,
)
from quantlab.statarb.session import StatArbSession, replay
from quantlab.statarb.statistics import CausalModel


def save(path, data):
    path.write_text(json.dumps(plain(data), indent=2, allow_nan=False) + "\n")


def short_demos(directory):
    manual = StatArbSession(capture=False)
    manual.command("step", count=80)
    entry = manual.state()
    manual.command("pair", action="short")
    first = manual.state()
    manual.command("next_leg")
    complete = manual.state()
    manual.command("step", count=3)
    manual.command("close")
    manual.command("next_leg")
    manual.command("end")
    journal = manual.journal()
    replay(journal)
    save(directory / "manual-session.json", journal)
    leg = StatArbSession(capture=False, rules={"notional": 4000})
    leg.command("step", count=80)
    leg.command("liquidity", instrument="SA-X", depth=1)
    leg.command("pair", action="long")
    leg.command("next_leg")
    partial = leg.state()
    leg.command("step", count=2)
    delayed = leg.state()
    leg.command("close")
    leg.command("next_leg")
    leg.command("end")
    save(directory / "partial-session.json", leg.journal())
    systematic = StatArbSession(capture=False)
    systematic.command("step", count=80)
    systematic.command("auto", enabled=True)
    systematic.command("step", count=160)
    systematic.command("close")
    systematic.command("next_leg")
    systematic.command("end")
    save(directory / "systematic-session.json", systematic.journal())
    cases = teaching_cases()
    save(directory / "controlled-cases.json", cases)
    data, _ = generate(201042, steps=240)
    selected = sweep(data[:160])
    evaluated = evaluate_selection(
        data,
        selected,
        split=160,
        registry=directory / "evaluation-registry.jsonl",
        destination=directory / "parameter-sweep",
        seed=201042,
    )
    null, _ = mining_universe(201043, steps=240)
    mined = select_pair(null[:160])
    held = evaluate_selection(
        null,
        mined,
        split=160,
        registry=directory / "evaluation-registry.jsonl",
        destination=directory / "pair-mining",
        seed=201043,
        pair=mined["selected"],
    )
    fixed = backtest(data, start=160)
    wf, blocks = walk_forward(data, start=160)
    regime = {}
    for name in ("stable", "beta", "mean", "volatility", "decouple", "drift"):
        prices, _ = generate(201044, name=name, steps=320)
        s = backtest(prices, rules=replace(BASE_RULES, stop=4), start=100)
        regime[name] = dict(metrics=s.metrics(), trades=s.trades, decisions=s.decisions)
    costs = {}
    for name, fee, spread in [("low", 0.005, 1), ("high", 0.05, 5)]:
        s = backtest(data, start=160, fee=fee, spread_ticks=spread)
        costs[name] = s.metrics()
    result = dict(
        manual=dict(
            entry_signal=entry["signal"],
            first_leg=first["exposure"],
            completed_pair=complete["exposure"],
            risk=complete["risk"],
            metrics=manual.metrics(),
            trades=manual.trades,
            fills=manual.fills,
        ),
        systematic=dict(metrics=systematic.metrics(), trades=systematic.trades),
        leg_risk=dict(
            partial=partial["exposure"],
            positions=partial["markets"],
            fills=partial["fills"],
            delayed=delayed["exposure"],
            delayed_attribution=delayed["attribution"],
            metrics=leg.metrics(),
        ),
        sweep=dict(selection=selected, evaluation=evaluated),
        mining=dict(selection=mined, evaluation=held),
        walk_forward=dict(fixed=fixed.metrics(), walk_forward=wf.metrics(), blocks=blocks),
        regimes=regime,
        costs=costs,
        lookahead=dict(valid=backtest(data).metrics(), invalid=invalid_lookahead(data)),
    )
    save(directory / "demo.json", result)
    print("Short demos and holdout records saved", flush=True)


def profile(directory):
    tasks = {
        "rolling_regressions_1000": lambda: rolling(),
        "multi_asset_10_assets_1000_steps": lambda: multi(),
        "walk_forward_321_observations": lambda: walk_forward(generate(102004)[0], start=160),
        "pair_mining_28_candidates": lambda: select_pair(mining_universe(102005)[0][:160]),
    }
    timings = {}
    profiler = cProfile.Profile()
    profiler.enable()
    for name, fn in tasks.items():
        tracemalloc.start()
        start = time.perf_counter()
        fn()
        elapsed = time.perf_counter() - start
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        timings[name] = dict(seconds=elapsed, peak_mb=peak / 1024**2)
    profiler.disable()
    profiler.dump_stats(str(directory / "profile.pstats"))
    import pstats

    with (directory / "profile.txt").open("w") as f:
        pstats.Stats(profiler, stream=f).sort_stats("cumulative").print_stats(25)
    save(
        directory / "performance.json",
        dict(
            measured_with="cProfile + tracemalloc overhead; local Python process", tasks=timings
        ),
    )


def rolling():
    data, _ = generate(102002, steps=1100)
    m = CausalModel(mode="rolling")
    for t in range(80, 1080):
        m.at(data, t)


def multi():
    from quantlab.statarb.market import MultiMarket
    from quantlab.statarb.process import Asset, Process

    p = Process(seed=102003, assets=[Asset(f"M-{i}") for i in range(10)])
    m = MultiMarket([a.identifier for a in p.assets], p.prices.tolist(), capture=False)
    for _ in range(1000):
        m.publish(p.step())
    m.check()


def studies(directory):
    for index, name in enumerate(
        ("generalisation", "walk_forward", "costs", "regime", "mining")
    ):
        runs = 16 if name == "mining" else 32
        spec = experiment_spec(name, runs=runs, root=10101000 + index, pool="evaluation")
        print(f"Registered study {name}: {runs} seeds x 2 variants", flush=True)
        record = execute(
            spec,
            StatArbAdapter(),
            directory / "research" / name,
            evaluation_registry=directory / "evaluation-registry.jsonl",
        )
        # Reproduce the worst result per variant, preserving losing examples.
        reproduced = []
        for variant in spec.variants:
            rows = [
                r
                for r in record["runs"]
                if r["variant"] == variant.name and r["status"] == "complete"
            ]
            if rows:
                worst = min(rows, key=lambda r: r["metrics"]["net_pnl"])
                reproduce_run(record, StatArbAdapter(), variant.name, worst["run_index"])
                reproduced.append(dict(variant=variant.name, run_index=worst["run_index"]))
        save(directory / "research" / name / "reproduced-worst.json", reproduced)
        print(f"{name}: {record['status']}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=Path("docs/learning/phase_10"))
    parser.add_argument("--part", choices=["demos", "studies", "profile", "all"], default="all")
    args = parser.parse_args()
    args.directory.mkdir(parents=True, exist_ok=True)
    if args.part in ("demos", "all"):
        short_demos(args.directory)
    if args.part in ("studies", "all"):
        studies(args.directory)
    if args.part in ("profile", "all"):
        profile(args.directory)


if __name__ == "__main__":
    main()
