"""Run or replay a short, explained Phase 2/3 market session."""

import argparse
from pathlib import Path

from quantlab.market.config import MICROSECONDS_PER_SECOND, SimulationConfig
from quantlab.market.journal import load_session, save_session
from quantlab.market.simulation import run_simulation
from quantlab.market.timeline import render_timeline


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, help="root seed (default 42)")
    parser.add_argument("--duration", type=int, help="whole simulated seconds (default 5)")
    parser.add_argument(
        "--informed", action="store_true", help="enable Phase 3 informed arrivals at 1/s"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="reveal observer latent values, signals and markouts",
    )
    parser.add_argument(
        "--limit", type=int, default=20, help="maximum displayed events (default 20)"
    )
    parser.add_argument("--save", type=Path, help="save the complete observer journal as JSON")
    parser.add_argument(
        "--expand-orders", action="store_true", help="show FIFO orders in final depth"
    )
    parser.add_argument(
        "--replay", type=Path, help="verify/replay a saved journal, without RNG draws"
    )
    args = parser.parse_args()
    if args.replay and (args.seed is not None or args.duration is not None or args.informed):
        parser.error(
            "--replay uses saved configuration; do not supply --seed, --duration or --informed"
        )
    try:
        if args.replay:
            session = load_session(args.replay)
            print("Replay verified: every recorded execution and book snapshot matches.")
        else:
            config = SimulationConfig(
                seed=42 if args.seed is None else args.seed,
                duration_us=(5 if args.duration is None else args.duration)
                * MICROSECONDS_PER_SECOND,
                informed_rate_per_second=1.0 if args.informed else 0.0,
            )
            session = run_simulation(config)
        output = render_timeline(
            session, debug=args.debug, limit=args.limit, expand_orders=args.expand_orders
        )
        if args.save:
            save_session(session, args.save)
        print(output)
        if args.save:
            print(
                "Saved observer journal (includes latent state and any private signals): "
                f"{args.save}"
            )
    except (ValueError, RuntimeError, OSError) as exc:
        parser.exit(2, f"Simulation/replay failed: {exc}\n")


if __name__ == "__main__":
    main()
