"""Run, manually control, compare or replay the Phase 4 Market Making Lab."""

import argparse
from collections.abc import Callable
from pathlib import Path

from quantlab.market.config import SimulationConfig
from quantlab.market_making.analytics import lab_markouts
from quantlab.market_making.comparison import compare_strategies
from quantlab.market_making.config import MakerConfig, Strategy
from quantlab.market_making.journal import load_lab, save_lab
from quantlab.market_making.lab import MarketMakingLab, run_lab
from quantlab.market_making.quotes import QuoteRequest
from quantlab.market_making.records import LabResult
from quantlab.market_making.views import (
    money,
    render_comparison,
    render_debug,
    render_lab,
    render_observation,
)
from quantlab.tutor.market_making import LESSONS, Prediction


def manual_session(
    market: SimulationConfig,
    maker: MakerConfig,
    *,
    teach: bool = False,
    adaptive_tutor=None,
    debug: bool = False,
    read: Callable[[str], str] = input,
    write: Callable[[str], None] = print,
) -> LabResult:
    """Injectable terminal I/O supports deterministic scripted/manual teaching tests."""
    lab = MarketMakingLab(market, maker)
    observation = lab.advance_to_decision()
    request = QuoteRequest(
        maker.half_spread_ticks, maker.half_spread_ticks, maker.quote_size, maker.quote_size
    )
    number = 0
    while observation is not None:
        records = lab.observer_records()
        write(
            render_observation(
                observation,
                lab_markouts(records, market.markout_horizons_events),
                tick_size=market.tick_size,
            )
        )
        if debug:
            write(render_debug(records, horizons=market.markout_horizons_events))
        if adaptive_tutor is not None and number % 2 == 0:
            from quantlab.tutor.adapters import maker_contexts
            from quantlab.tutor.terminal import checkpoint

            contexts = maker_contexts(
                observation,
                source="phase4-manual",
                event=records[-1].public_event_number if records else 0,
                hard_limit=maker.hard_limit,
                tick_size=market.tick_size,
            )
            try:
                checkpoint(adaptive_tutor, contexts, read=read, write=write)
            except Exception as exc:
                write(
                    f"Tutor stopped: {type(exc).__name__}. Trading continues without tutoring."
                )
                adaptive_tutor = None
        prediction = None
        if teach and number in (0, 2, 4):
            prediction = Prediction(LESSONS[number // 2])
            write("PREDICT: " + prediction.lesson.question)
            while not prediction.ready:
                write(prediction.answer(read("Your prediction: ")))
        while True:
            text = read(
                "DECIDE: bid distance, ask distance, bid size, ask size "
                "(ticks/units; blank repeats; q stops): "
            ).strip()
            if text.lower() in ("q", "quit"):
                raise EOFError("manual session stopped before completion")
            try:
                if text:
                    bid, ask, bid_size, ask_size = text.split()
                    proposed = QuoteRequest(bid, ask, int(bid_size), int(ask_size))
                else:
                    proposed = request
                record = lab.decide(proposed)
                request = proposed
                break
            except (ValueError, TypeError) as exc:
                write(f"Invalid quote input: {exc}")
        write(f"DECIDE: posted {record.plan.bid_size} bid / {record.plan.ask_size} ask units.")
        if record.plan.adjustments:
            write("Adjustments: " + "; ".join(record.plan.adjustments))
        observation = lab.advance_to_decision()
        state = observation.account if observation is not None else lab.result().final_account
        write(
            f"RESULT: inventory {state.inventory:+d}; marked P&L "
            f"{money(state.total_pnl_ticks, market.tick_size)}."
        )
        if prediction:
            write("EXPLAIN: " + prediction.explain())
        number += 1
    return lab.result()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strategy", choices=("fixed", "inventory"))
    parser.add_argument(
        "--manual", action="store_true", help="choose quotes at fixed decision times"
    )
    parser.add_argument(
        "--teach", action="store_true", help="prediction/hint/retry loop in manual mode"
    )
    parser.add_argument("--seed", type=int, help="root seed, default 42 for a single run")
    parser.add_argument(
        "--duration", type=int, help="seconds: default 5 for demo, 30 for comparison"
    )
    parser.add_argument(
        "--debug", action="store_true", help="separately reveal observer-only diagnostics"
    )
    parser.add_argument("--limit", type=int, default=12, help="displayed maker event groups")
    parser.add_argument("--save", type=Path, help="save a complete privileged observer journal")
    parser.add_argument("--replay", type=Path, help="verify a saved lab without random draws")
    parser.add_argument(
        "--compare", action="store_true", help="paired fixed/inventory validation"
    )
    parser.add_argument(
        "--runs", type=int, default=20, help="paired seeds 0..runs-1, comparison only"
    )
    parser.add_argument(
        "--adaptive",
        action="store_true",
        help="Phase 7 local structured tutor in manual mode; separate maker progress file",
    )
    args = parser.parse_args()
    if args.adaptive and (not args.manual or args.teach or args.debug or args.replay):
        parser.error(
            "--adaptive requires --manual and a public view; "
            "do not combine with --teach, --debug or --replay"
        )
    adaptive_tutor = None
    if args.adaptive:
        from quantlab.tutor.progress import Progress
        from quantlab.tutor.service import Tutor

        try:
            adaptive_tutor = Tutor(Progress(Path.cwd() / "runs/learning/maker-progress.json"))
        except (ValueError, OSError) as exc:
            print(f"Tutor unavailable: {type(exc).__name__}. Trading continues.")
    if args.teach and not args.manual:
        parser.error("--teach requires --manual")
    if args.manual and args.strategy is not None:
        parser.error("--manual supplies its own strategy")
    if args.replay and (
        args.seed is not None
        or args.duration is not None
        or args.strategy
        or args.manual
        or args.compare
    ):
        parser.error("--replay uses its saved strategy, decisions and configuration")
    if args.compare and (args.manual or args.strategy or args.seed is not None or args.save):
        parser.error(
            "--compare uses both strategies and seeds 0..runs-1; --save is for single runs"
        )
    try:
        if args.compare:
            if not 1 <= args.runs <= 100:
                raise ValueError("comparison runs must be between 1 and 100")
            seconds = 30 if args.duration is None else args.duration
            runs = compare_strategies(
                seeds=tuple(range(args.runs)), duration_us=seconds * 1_000_000
            )
            print(f"{args.runs} paired seeds, 0..{args.runs - 1}; {seconds} seconds each.")
            print(render_comparison(runs))
            return
        if args.replay:
            result = load_lab(args.replay)
            print(
                "Replay verified: quote actions, executions, inventory and exact P&L reconcile."
            )
        else:
            market = SimulationConfig(
                seed=42 if args.seed is None else args.seed,
                duration_us=(5 if args.duration is None else args.duration) * 1_000_000,
                informed_rate_per_second=1,
            )
            maker = MakerConfig(
                strategy=Strategy.MANUAL if args.manual else Strategy(args.strategy or "fixed")
            )
            result = (
                manual_session(
                    market,
                    maker,
                    teach=args.teach,
                    debug=args.debug,
                    adaptive_tutor=adaptive_tutor,
                )
                if args.manual
                else run_lab(market, maker)
            )
        if args.save:
            save_lab(result, args.save)
        print(render_lab(result, debug=args.debug, limit=args.limit))
        if args.save:
            print(
                "Saved privileged observer journal (contains hidden values and signals): "
                f"{args.save}"
            )
    except (EOFError, KeyboardInterrupt):
        parser.exit(
            0, "Manual session stopped; no completed result or completed journal was claimed.\n"
        )
    except (ValueError, TypeError, RuntimeError, AssertionError, OSError) as exc:
        parser.exit(2, f"Market Making Lab failed: {exc}\n")


if __name__ == "__main__":
    main()
