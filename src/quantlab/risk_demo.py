"""Deterministic executed portfolio demo and options-heavy risk profiling."""

import argparse
import cProfile
import io
import json
import pstats
import time
import tracemalloc
from pathlib import Path

from quantlab.options.session import OptionsSession
from quantlab.research.codec import digest
from quantlab.risk.analytics import FACTORS, RiskSettings, diversification, tail_example
from quantlab.risk.monte_carlo import monte_carlo_risk
from quantlab.risk.portfolio import from_accounts
from quantlab.risk.session import RiskSession, replay_risk


def demo(destination):
    path = Path(destination)
    path.mkdir(parents=True, exist_ok=True)
    s = RiskSession()
    timeline = []

    def act(label, target, kind, /, **p):
        r = s.execute(target, kind, **p)
        state = r["state"]
        report = state["report"]
        portfolio = report["portfolio"]
        timeline.append(
            {
                "event": label,
                "result": r["result"],
                "delta": portfolio["greeks"]["delta"],
                "vega": portfolio["greeks"]["vega"],
                "pnl": portfolio["pnl"],
                "cash": portfolio["cash"],
                "equity": portfolio["equity"],
                "parametric_var": report["parametric"]["var"],
                "historical_var": report["historical"]["full"]["var"],
                "mc_var": report["monte_carlo"]["full"]["var"],
                "mc_es": report["monte_carlo"]["full"]["es"],
                "scenario": state["scenario"],
                "challenge": state["challenge"],
            }
        )
        return state

    act(
        "Buy one ATM call at the actual dealer ask",
        "options",
        "option_order",
        contract_id=s.options.selected,
        side="buy",
        quantity=1,
        quote_revision=s.options.quote_revision,
    )
    act(
        "Set hard delta limit 55",
        "risk",
        "limits",
        limits=[{"metric": "delta", "maximum": 55, "mode": "hard"}],
    )
    act(
        "Try buying 10 more stock units: prohibited",
        "options",
        "stock_order",
        side="buy",
        quantity=10,
        order_type="market",
    )
    act("Challenge: full MC VaR at most £20", "risk", "challenge", kind="var", target=20)
    act(
        "Sell 51 underlying units through the FIFO exchange",
        "options",
        "stock_order",
        side="sell",
        quantity=51,
        order_type="market",
    )
    hedged = s.state()
    act("Delta neutral, volatility rises 20 points", "risk", "scenario", volatility_change=0.20)
    act("Small stock shock +0.1%", "risk", "scenario", stock_return=0.001)
    act(
        "Custom shock: stock -8%, vol +12 points, rate +50 bps",
        "risk",
        "scenario",
        stock_return=-0.08,
        volatility_change=0.12,
        rate_change=0.005,
    )
    act("Clear delta limit for a separate two-stock comparison", "risk", "limits", limits=[])
    act(
        "Buy 50 QL-SECOND shares",
        "second",
        "order",
        side="buy",
        quantity=50,
        order_type="market",
    )
    act(
        "Buy 50 QL-STOCK shares",
        "options",
        "stock_order",
        side="buy",
        quantity=50,
        order_type="market",
    )
    diversified = s.state()
    act("Stress correlation from .25 to .9", "risk", "scenario", correlation=0.9)
    act(
        "Solve minimum variance with risky cap 40%, cash exactly 20%",
        "risk",
        "optimise",
        max_weight=0.4,
        min_cash=0.2,
        max_cash=0.2,
        means=[0.0003, 0.0002, 0.0001],
        frontier_points=9,
    )
    allocation = s.state()["optimisation"]
    act("Observe one actual model day", "options", "step", count=1)
    act("End, retain marked positions and save reproducible evidence", "risk", "end")
    journal = s.journal()
    replayed, frames = replay_risk(journal, frames=True)
    if replayed.journal() != journal:
        raise AssertionError("Demo replay differs")
    result = {
        "timeline": timeline,
        "hedged_report": hedged["report"],
        "diversified_report": diversified["report"],
        "allocation": allocation,
        "diversification": diversification(),
        "tail_example": tail_example(),
        "replay_frames": len(frames),
        "journal_digest": digest(journal),
    }
    (path / "demo.json").write_text(json.dumps(result, indent=2) + "\n")
    (path / "manual-session.json").write_text(json.dumps(journal, indent=2) + "\n")
    for row in timeline:
        print(
            f"{row['event']}: delta {row['delta']:.4f}; MC VaR £{row['mc_var']:.4f}; "
            f"ES £{row['mc_es']:.4f}; actual P&L £{row['pnl']:.4f}"
        )
    return result


def performance(destination):
    path = Path(destination)
    path.mkdir(parents=True, exist_ok=True)
    s = OptionsSession(capture=False)
    for key in s.quotes:
        s.command(
            "option_order",
            contract_id=key,
            side="buy",
            quantity=1,
            quote_revision=s.quote_revision,
        )
    s.command("hedge")
    portfolio = from_accounts(s)
    settings = RiskSettings()
    results = []
    profiler = cProfile.Profile()
    for paths in (5000, 100000):
        for full in (False, True):
            tracemalloc.start()
            start = time.perf_counter()
            profiler.enable()
            r = monte_carlo_risk(
                portfolio,
                FACTORS,
                settings.covariance(),
                settings.means,
                paths=paths,
                seed=99042,
                full=full,
            )
            profiler.disable()
            elapsed = time.perf_counter() - start
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            results.append(
                {
                    "paths": paths,
                    "mode": "full retained losses" if full else "summary",
                    "options": 20,
                    "seconds": elapsed,
                    "peak_traced_bytes": peak,
                    "var": r["full"]["var"],
                    "es": r["full"]["es"],
                }
            )
    out = io.StringIO()
    pstats.Stats(profiler, stream=out).sort_stats("cumulative").print_stats(25)
    (path / "profile.txt").write_text(out.getvalue())
    (path / "performance.json").write_text(json.dumps(results, indent=2) + "\n")
    return results


def main():
    parser = argparse.ArgumentParser(
        description="QuantLab Phase 9 executed portfolio-risk demo"
    )
    parser.add_argument("--output", default="runs/risk/demo")
    parser.add_argument("--profile", action="store_true")
    args = parser.parse_args()
    demo(args.output)
    if args.profile:
        print(json.dumps(performance(args.output), indent=2))


if __name__ == "__main__":
    main()
