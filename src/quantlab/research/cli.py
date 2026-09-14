"""Discoverable research commands; predictions are supplied before sessions execute."""

import argparse
import sys
from pathlib import Path

from quantlab.research.adapters.maker import MakerAdapter, maker_configuration
from quantlab.research.analysis import extremes
from quantlab.research.codec import write_new
from quantlab.research.engine import execute, load_experiment
from quantlab.research.lessons import (
    RESEARCH_LESSONS,
    plot_precision,
    precision_experiment,
    predict,
    selection_demo,
    significance_demo,
)
from quantlab.research.models import ExperimentSpec, Variant
from quantlab.research.replay import save_reproduced_maker
from quantlab.research.reporting import plot_distribution, render_report
from quantlab.research.seeds import SeedPlan
from quantlab.research.sweeps import sweep_spec

RELATIONSHIPS = (
    ("average_absolute_inventory", "net_pnl"),
    ("maximum_absolute_inventory", "maximum_drawdown"),
    ("fill_rate", "markout_1"),
    ("turnover", "fees"),
)

PARAMETERS = {
    "k": ("strategy", "inventory_skew_ticks"),
    "half-spread": ("strategy", "half_spread_ticks"),
    "soft-limit": ("strategy", "soft_limit"),
    "volatility": ("market", "latent_sigma_ticks"),
    "signal-noise": ("market", "signal_noise_ticks"),
    "informed-intensity": ("market", "informed_rate_per_second"),
}


def comparison_spec(
    *,
    root=20260911,
    runs=1000,
    duration_us=30_000_000,
    pool="development",
    hypothesis,
    resamples=2000,
):
    return ExperimentSpec(
        "How do unchanged fixed and inventory-aware policies differ under the same weather?",
        hypothesis,
        SeedPlan(root, pool, runs),
        tuple(
            Variant(name, maker_configuration(duration_us=duration_us, strategy=name))
            for name in ("fixed", "inventory")
        ),
        MakerAdapter.name,
        bootstrap_resamples=resamples,
        relationships=RELATIONSHIPS,
    )


def parser():
    root = argparse.ArgumentParser(
        prog="quantlab-research",
        description=(
            "Hypothesis-first synthetic research. "
            "Synthetic performance is not real-world alpha."
        ),
    )
    sub = root.add_subparsers(dest="command", required=True)
    for command, help_text in (
        ("compare", "Paired fixed versus inventory-aware sessions"),
        ("sweep", "Repeated sessions for each value of one parameter"),
    ):
        p = sub.add_parser(command, help=help_text)
        p.add_argument("--runs", type=int, default=1000)
        p.add_argument("--root-seed", type=int, default=20260911)
        p.add_argument(
            "--duration", type=float, default=30, help="simulated seconds per session"
        )
        p.add_argument("--pool", choices=("development", "evaluation"), default="development")
        p.add_argument(
            "--registry", type=Path, default=Path("research/evaluation-access.jsonl")
        )
        p.add_argument(
            "--hypothesis", required=True, help="prediction to register before execution"
        )
        p.add_argument("--out", type=Path, required=True, help="new experiment directory")
        p.add_argument("--teach", action="store_true")
        if command == "sweep":
            p.add_argument("--parameter", choices=tuple(PARAMETERS), required=True)
            p.add_argument(
                "--values",
                required=True,
                help="comma-separated values; exact fractions allowed for k/spread",
            )
    p = sub.add_parser(
        "inspect", help="Read distributions; optionally export a histogram and ECDF"
    )
    p.add_argument("experiment", type=Path)
    p.add_argument("--metric", default="net_pnl")
    p.add_argument("--plot", type=Path)
    p = sub.add_parser("worst", help="Identify replayable extreme sessions")
    p.add_argument("experiment", type=Path)
    p.add_argument("--variant", default="inventory")
    p.add_argument("--metric", default="net_pnl")
    p.add_argument(
        "--largest", action="store_true", help="use for drawdown or maximum inventory"
    )
    p.add_argument("--count", type=int, default=3)
    p = sub.add_parser(
        "replay", help="Verify an exact run and save its existing full lab journal"
    )
    p.add_argument("experiment", type=Path)
    p.add_argument("--variant", default="inventory")
    p.add_argument(
        "--run", type=int, required=True, help="zero-based run address shown by worst"
    )
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--debug", action="store_true")
    p = sub.add_parser("precision", help="Inspect predeclared sample-size prefixes")
    p.add_argument("experiment", type=Path)
    p.add_argument("--sizes", default="100,400,1600")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--teach", action="store_true")
    p = sub.add_parser(
        "selection", help="Equal-skill control showing development selection and holdout"
    )
    p.add_argument("--root-seed", type=int, default=20260911)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--registry", type=Path, default=Path("research/evaluation-access.jsonl"))
    p.add_argument("--teach", action="store_true")
    p = sub.add_parser("significance", help="Tiny precise versus meaningful uncertain effects")
    p.add_argument("--root-seed", type=int, default=20260911)
    p.add_argument("--out", type=Path, required=True)
    return root


def main(argv=None, *, read=input, write=print):
    command_parser = parser()
    args = command_parser.parse_args(argv)
    try:
        lesson = answers = None
        if getattr(args, "teach", False):
            lesson = RESEARCH_LESSONS[
                0 if args.command == "precision" else 2 if args.command == "selection" else 1
            ]
            answers = predict(lesson, read=read, write=write)
        if args.command in ("compare", "sweep"):
            duration = args.duration * 1_000_000
            if not duration.is_integer() or duration <= 0:
                raise ValueError(
                    "duration must be positive and resolve to integer microseconds"
                )
            adapter = MakerAdapter()
            if args.command == "compare":
                spec = comparison_spec(
                    root=args.root_seed,
                    runs=args.runs,
                    duration_us=int(duration),
                    pool=args.pool,
                    hypothesis=args.hypothesis,
                )
            else:
                values = tuple(v.strip() for v in args.values.split(","))
                if args.parameter == "soft-limit":
                    values = tuple(int(v) for v in values)
                elif PARAMETERS[args.parameter][0] == "market":
                    values = tuple(float(v) for v in values)
                spec = sweep_spec(
                    question=f"What trade-offs change as {args.parameter} changes?",
                    hypothesis=args.hypothesis,
                    seeds=SeedPlan(args.root_seed, args.pool, args.runs),
                    adapter=adapter,
                    base_configuration=maker_configuration(
                        duration_us=int(duration), strategy="inventory"
                    ),
                    parameter=PARAMETERS[args.parameter],
                    values=values,
                    relationships=RELATIONSHIPS,
                )
            write("RUN — register the hypothesis, then simulate every requested session.")
            result = execute(
                spec,
                adapter,
                args.out,
                evaluation_registry=args.registry,
                progress=lambda n, total: (
                    write(f"Completed {n}/{total} run addresses")
                    if n == total or n % 100 == 0
                    else None
                ),
            )
            write("OBSERVE — " + str(args.out / "summary.md"))
            if result["status"] != "complete":
                write("Incomplete experiment; inference disabled. Inspect retained errors.")
                return 1
            plot_distribution(result, args.out / "distribution.png")
            if args.command == "sweep":
                from quantlab.research.adapters.maker_reporting import plot_sweep

                plot_sweep(
                    result, args.out / "tradeoffs.png", parameter=PARAMETERS[args.parameter]
                )
            write(result["interpretation"])
        elif args.command == "inspect":
            result = load_experiment(args.experiment)
            write(render_report(result))
            if args.plot:
                plot_distribution(result, args.plot, args.metric)
        elif args.command == "worst":
            result = load_experiment(args.experiment)
            for row in extremes(
                result, args.variant, args.metric, largest=args.largest, count=args.count
            ):
                write(
                    f"Run #{row['run_index']} | {args.variant} | {args.metric}="
                    f"{row['metrics'][args.metric]} | seed {row['simulation_seed']}"
                )
        elif args.command == "replay":
            from quantlab.market_making.views import render_lab

            lab = save_reproduced_maker(
                load_experiment(args.experiment), args.variant, args.run, args.out
            )
            write(render_lab(lab, debug=args.debug))
            write(
                f"Verified exact journal saved to {args.out}. Journal is observer/debug data."
            )
        elif args.command == "precision":
            result = precision_experiment(
                load_experiment(args.experiment),
                sizes=tuple(int(n) for n in args.sizes.split(",")),
            )
            write_new(args.out, result)
            plot_precision(result, args.out.with_suffix(".png"))
            write("OBSERVE — " + str(args.out))
        elif args.command == "selection":
            result = selection_demo(args.out, root=args.root_seed, registry=args.registry)
            write("OBSERVE — " + str(args.out / "selection-result.json"))
            write(
                f"Selected {result['selected_variant']['name']}; development mean "
                f"{result['development']['mean']:.4f}, "
                f"evaluation mean {result['evaluation']['mean']:.4f}."
            )
        elif args.command == "significance":
            write_new(args.out, significance_demo(root=args.root_seed))
            write(str(args.out))
        if lesson is not None:
            write("INTERPRET — " + lesson.explanation)
            write(
                "CRITIQUE — Which independence, selection or synthetic-model assumption "
                "limits the conclusion? Your prediction is not a mastery score."
            )
            evidence_path = (
                args.out / "teaching.json"
                if args.out.is_dir()
                else args.out.with_suffix(".teaching.json")
            )
            write_new(
                evidence_path,
                {
                    "question": lesson.question,
                    "answers_before_run": answers,
                    "explanation_after_observation": lesson.explanation,
                },
            )
        return 0
    except (ValueError, TypeError, OSError, KeyError) as exc:
        write(f"Research error: {exc}")
        return 2
    except (EOFError, KeyboardInterrupt):
        write("Stopped. Any existing registration and partial run log remain for inspection.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
