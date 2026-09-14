"""Registered Phase 8 development experiments; no post-result parameter tuning."""

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from quantlab.options.research import OptionsAdapter
from quantlab.options.session import OptionsConfig, replay_options
from quantlab.research.codec import plain, write_new
from quantlab.research.engine import execute
from quantlab.research.models import ExperimentSpec, Variant
from quantlab.research.replay import reproduce_run
from quantlab.research.seeds import SeedPlan


def design(experiment, runs=1000, root=88042):
    market = asdict(
        OptionsConfig(
            strikes=(100,),
            expiries_days=(20,),
            steps=20,
            skew=0,
            curvature=0,
        )
    )
    base = dict(
        market=market,
        option_type="call",
        strike=100,
        expiry_days=20,
        quantity=1,
        hedge_frequency=1,
    )
    if experiment == "frequency":
        variants = tuple(
            Variant(f"every-{n}" if n else "no-hedge", base | {"hedge_frequency": n})
            for n in (1, 5, 20, 0)
        )
        hypothesis = (
            "More frequent hedging is expected to reduce interval delta exposure and "
            "the dispersion of terminal hedging P&L, while increasing execution costs. "
            "Mean net P&L need not improve. Compare daily, five-day, twenty-day and no hedge."
        )
    elif experiment == "volatility":
        variants = tuple(
            Variant(f"process-vol-{v:g}", base | {"market": market | {"process_volatility": v}})
            for v in (0.15, 0.2, 0.3)
        )
        hypothesis = (
            "At fixed 20% quote volatility, higher underlying process variance should "
            "raise average long-call daily-hedged P&L. Discrete hedges, costs and individual "
            "path variation prevent a guaranteed per-path ordering."
        )
    else:
        raise ValueError("Choose frequency or volatility")
    return ExperimentSpec(
        f"Phase 8 {experiment}: one long ATM call, multiplier 100, twenty ACT/365 days",
        hypothesis,
        SeedPlan(root, "development", runs),
        variants,
        OptionsAdapter.name,
        bootstrap_resamples=1000,
        relationships=(("fees", "turnover"),),
    )


def run_study(experiment, destination, runs=1000, root=88042):
    spec, adapter = design(experiment, runs, root), OptionsAdapter()

    def progress(done, total):
        if done % 100 == 0 or done == total:
            print(f"{experiment}: {done}/{total} paired paths completed", flush=True)

    record = execute(spec, adapter, destination, progress=progress)
    if record["status"] != "complete":
        raise RuntimeError(f"Study incomplete: {record['warnings']}")
    worst = min(record["runs"], key=lambda row: row["metrics"]["net_pnl"])
    outcome = reproduce_run(record, adapter, worst["variant"], worst["run_index"])
    replay_options(outcome.journal)
    write_new(Path(destination) / "verified-worst-session.json", outcome.journal)
    write_new(
        Path(destination) / "reproduction.json",
        {
            "variant": worst["variant"],
            "run_index": worst["run_index"],
            "outcome_digest": record["outcome_digest"],
            "verification": (
                "Full regeneration matched batch metrics and hashes; replay verified"
            ),
        },
    )
    summary = {
        "status": record["status"],
        "elapsed_seconds": record["elapsed_seconds"],
        "runs": len(record["runs"]),
        "versions": record["versions"],
        "variants": {
            key: {
                metric: value["distributions"][metric]
                for metric in (
                    "net_pnl",
                    "fees",
                    "gross_hedging_error",
                    "rms_delta",
                    "drawdown",
                    "turnover",
                    "realised_volatility",
                    "option_gross_pnl",
                    "hedge_gross_pnl",
                )
            }
            for key, value in record["analysis"]["variants"].items()
        },
        "paired": record["analysis"]["paired"],
    }
    write_new(Path(destination) / "phase8-summary.json", summary)
    print(json.dumps(plain(summary), indent=2), flush=True)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--runs", type=int, default=1000)
    parser.add_argument("--root", type=int, default=88042)
    args = parser.parse_args()
    for experiment in ("frequency", "volatility"):
        run_study(experiment, args.destination / experiment, args.runs, args.root)


if __name__ == "__main__":
    main()
