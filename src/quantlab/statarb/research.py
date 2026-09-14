"""Registered Phase 5 experiments; causal execution, sealed selection and honest failures."""

import copy
import itertools
import json
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np

from quantlab.research.codec import digest, plain
from quantlab.research.models import ExperimentSpec, SimulationOutcome, Variant
from quantlab.research.registry import claim_evaluation
from quantlab.research.seeds import SeedPlan
from quantlab.statarb.process import Asset, Process, scenario
from quantlab.statarb.session import StatArbSession
from quantlab.statarb.statistics import CausalModel, correlation
from quantlab.statarb.strategy import Rules

BASE_RULES = Rules(window=60, z_window=30, max_holding=30, block=20)
METRICS = (
    "net_pnl",
    "return_on_capital",
    "drawdown",
    "trade_count",
    "win_rate",
    "average_trade",
    "median_trade",
    "turnover",
    "mean_holding",
    "costs",
    "max_gross",
    "max_imbalance",
    "probability_loss",
    "worst_trade",
    "mean_entry_z",
    "mean_exit_z",
    "residual_inventory",
)


def generate(seed, *, name="stable", steps=320):
    p = scenario(name, seed=seed, steps=steps)
    rows = [np.round(p.prices, 2).tolist()]
    rows.extend(p.step() for _ in range(steps))
    return np.asarray(rows), digest(p.evidence)


def backtest(
    prices, *, rules=BASE_RULES, start=None, end=None, fee=0.005, spread_ticks=1, capture=False
):
    """Only one observed row reaches the session at a time. Trading interval [start,end)."""
    start = rules.window if start is None else start
    end = len(prices) if end is None else end
    if not rules.window <= start < end <= len(prices) or end > 2001:
        raise ValueError("Invalid chronological training/trading split")
    data = np.asarray(prices[:end], dtype=float)
    if data.ndim != 2 or data.shape[1] != 2 or not np.isfinite(data).all():
        raise ValueError("Backtest needs synchronized finite X,Y observations")
    # Initial market matches data; it never receives a pre-generated future path.
    config = Process(
        assets=[
            Asset("SA-X", initial=float(data[0, 0])),
            Asset("SA-Y", initial=float(data[0, 1])),
        ]
    ).config
    s = StatArbSession(
        steps=max(20, end),
        rules=asdict(rules),
        capture=capture,
        fee=fee,
        spread_ticks=spread_ticks,
        process_config=config,
    )
    s.model = CausalModel(
        window=rules.window,
        z_window=rules.z_window,
        mode=rules.mode,
        block=rules.block,
        origin=start,
    )
    for t in range(1, end):
        s.systematic = t >= start
        s.revision += 1
        s.publish(data[t].tolist())
    # Prespecified boundary liquidation uses CURRENT executable books, including leg failures.
    s.systematic = False
    s._close("prespecified sample boundary")
    s._execute_next()
    s._point()
    return s


def candidate_rules():
    """Small prespecified one-at-a-time sensitivity design, not a hidden huge grid."""
    base = asdict(BASE_RULES)
    variants = [base]
    for key, values in {
        "entry": (1.5, 2.5),
        "exit": (0.2, 0.7),
        "window": (40, 80),
        "z_window": (20, 50),
        "stop": (3, 5),
    }.items():
        variants.extend(base | {key: value} for value in values)
    return variants


def sweep(training, *, candidates=None):
    """Selection API accepts TRAINING ONLY. All discarded candidates and failures retained."""
    records = []
    for i, config in enumerate(candidates or candidate_rules()):
        try:
            rules = Rules(**config)
            s = backtest(training, rules=rules, start=max(80, rules.window, rules.z_window))
            records.append(
                dict(
                    candidate=i,
                    parameters=asdict(rules),
                    status="complete",
                    metrics=s.metrics(),
                )
            )
        except (ValueError, ArithmeticError) as exc:
            records.append(
                dict(
                    candidate=i,
                    parameters=copy.deepcopy(config),
                    status="failed",
                    error=str(exc),
                )
            )
    good = [r for r in records if r["status"] == "complete"]
    if not good:
        return dict(
            candidates=records,
            selected=None,
            criterion="maximum training net P&L; ties lowest index",
        )
    winner = max(good, key=lambda r: (r["metrics"]["net_pnl"], -r["candidate"]))
    return dict(
        candidates=records,
        selected=winner["candidate"],
        parameters=winner["parameters"],
        criterion="maximum training net P&L; ties lowest index",
        training_rows=len(training),
        training_fingerprint=digest(np.asarray(training).tolist()),
        evaluation_accessed=False,
    )


def mining_universe(seed, *, assets=8, steps=320):
    if type(assets) is not int or not 3 <= assets <= 15:
        raise ValueError("Pair mining uses 3–15 assets in a fixed universe")
    p = Process(seed=seed, assets=[Asset(f"NULL-{i}") for i in range(assets)])
    rows = [p.prices.tolist()]
    rows.extend(p.step() for _ in range(steps))
    return np.asarray(rows), digest(p.evidence)


def select_pair(training, *, rules=BASE_RULES):
    """No evaluation argument exists: the selector cannot inspect the withheld block."""
    a = np.asarray(training, dtype=float)
    if a.ndim != 2 or not 3 <= a.shape[1] <= 15:
        raise ValueError("Supply training rows for the fixed multi-asset universe")
    records = []
    for x, y in itertools.combinations(range(a.shape[1]), 2):
        pair = a[:, [x, y]]
        try:
            s = backtest(pair, rules=rules, start=max(80, rules.window))
            records.append(
                dict(
                    pair=[x, y],
                    status="complete",
                    price_correlation=correlation(*pair.T),
                    metrics=s.metrics(),
                )
            )
        except (ValueError, ArithmeticError) as exc:
            records.append(dict(pair=[x, y], status="failed", error=str(exc)))
    good = [r for r in records if r["status"] == "complete"]
    if not good:
        raise ValueError("All candidate pairs failed; no winner exists")
    best = max(good, key=lambda r: (r["metrics"]["net_pnl"], -r["pair"][0], -r["pair"][1]))
    return dict(
        universe=[f"NULL-{i}" for i in range(a.shape[1])],
        candidates=records,
        parameters=asdict(rules),
        selected=best["pair"],
        criterion="largest training net P&L; ties lexicographic pair order",
        training_rows=len(a),
        training_fingerprint=digest(a.tolist()),
        evaluation_accessed=False,
        warning=(
            "All assets are unrelated random walks. Ranking many candidates "
            "creates selection bias."
        ),
    )


def evaluate_selection(prices, selection, *, split, registry, destination, seed, pair=None):
    """Persist the choice and claim evaluation access BEFORE evaluating withheld prices."""
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "selection.json").write_text(json.dumps(plain(selection), indent=2) + "\n")
    warnings = claim_evaluation(registry, design_digest=digest(selection), seeds=(seed,))
    data = np.asarray(prices)
    if pair is not None:
        data = data[:, pair]
    selected = Rules(**selection["parameters"])
    try:
        result = backtest(data, rules=selected, start=split)
        output = dict(
            status="complete",
            metrics=result.metrics(),
            trades=result.trades,
            warnings=warnings,
            selection_digest=digest(selection),
            split=split,
            evaluation_accessed=True,
        )
    except Exception as exc:
        output = dict(
            status="failed",
            error=str(exc),
            warnings=warnings,
            selection_digest=digest(selection),
            split=split,
            evaluation_accessed=True,
        )
    (destination / "evaluation.json").write_text(json.dumps(plain(output), indent=2) + "\n")
    return output


def walk_forward(prices, *, rules=BASE_RULES, start=160):
    s = backtest(prices, rules=replace(rules, mode="walk_forward"), start=start)
    blocks = []
    for lo in range(start, len(prices), rules.block):
        hi = min(lo + rules.block, len(prices))
        points = [p for p in s.path if lo <= p["t"] < hi]
        decisions = [d for d in s.decisions if lo <= d["t"] < hi]
        trades = [t["exit"] for t in s.trades if lo <= t["exit"]["t"] < hi and t.get("fills")]
        previous = [p for p in s.path if p["t"] < lo]
        fills = [f for f in s.fills if lo <= f["t"] < hi]
        blocks.append(
            dict(
                start=lo,
                end=hi,
                fit=decisions[0].get("estimation_fit") if decisions else None,
                pnl=points[-1]["pnl"] - previous[-1]["pnl"] if points and previous else 0,
                turnover=sum(f["price"] * f["quantity"] for f in fills),
                drawdown=max((p["drawdown"] for p in points), default=0),
                hit_rate=sum(t["net_pnl"] > 0 for t in trades) / len(trades)
                if trades
                else None,
                spread_range=[
                    min((p["spread"] for p in points if p["spread"] is not None), default=0),
                    max((p["spread"] for p in points if p["spread"] is not None), default=0),
                ],
            )
        )
    return s, blocks


def invalid_lookahead(prices, *, quantity=5):
    """INVALID future-return oracle. Isolated from CausalModel and live commands."""
    a = np.asarray(prices)
    venue = StatArbSession(capture=False, steps=max(20, len(a)))
    # Use actual books, so the deliberate fault is future information, not omitted costs.
    venue.market.venues["SA-X"].refresh(float(a[0, 0]), 0)
    venue.market.venues["SA-Y"].refresh(float(a[0, 1]), 0)
    future_spread_moves = np.diff(a[:, 1] - a[:, 0])
    for t, move in enumerate(future_spread_moves):
        for i, k in enumerate(("SA-X", "SA-Y")):
            v = venue.market.venues[k]
            target = (1 if move > 0 else -1) * quantity * (-1 if i == 0 else 1)
            difference = target - v.account.inventory
            if difference:
                v.command(
                    "order",
                    side="buy" if difference > 0 else "sell",
                    quantity=abs(difference),
                    order_type="market",
                )
            v.refresh(float(a[t + 1, i]), t + 1)
    for v in venue.market.venues.values():
        if v.account.inventory:
            v.command(
                "order",
                side="sell" if v.account.inventory > 0 else "buy",
                quantity=abs(v.account.inventory),
                order_type="market",
            )
    p = sum(
        float(v.account.snapshot().total_pnl_ticks / 100) for v in venue.market.venues.values()
    )
    return dict(
        label="INVALID — future-return oracle; rejected methodology",
        net_pnl=p,
        leak="At t the position uses the sign of spread[t+1]-spread[t], unavailable at t",
        fees_and_spreads="Both legs executed through current FIFO books",
        deployable=False,
    )


class StatArbAdapter:
    name = "causal-statarb-fifo-v1"

    def validate(self, c):
        if set(c) != {"experiment", "variant", "steps", "split"}:
            raise ValueError("Unknown stat-arb research configuration")
        if c["experiment"] not in (
            "generalisation",
            "walk_forward",
            "costs",
            "regime",
            "mining",
        ):
            raise ValueError("Unknown research design")
        valid = {
            "generalisation": ("in_sample", "out_of_sample"),
            "walk_forward": ("fixed", "walk_forward"),
            "costs": ("low", "high"),
            "regime": ("stable", "drift"),
            "mining": ("in_sample", "out_of_sample"),
        }
        if c["variant"] not in valid[c["experiment"]]:
            raise ValueError("Unknown registered variant")
        if (
            type(c["steps"]) is not int
            or not 200 <= c["steps"] <= 1000
            or not 100 <= c["split"] < c["steps"] - 20
        ):
            raise ValueError("Invalid research length/split")

    def environment_key(self, c):
        self.validate(c)
        return dict(
            process="unrelated-universe"
            if c["experiment"] == "mining"
            else c["variant"]
            if c["experiment"] == "regime"
            else "stable",
            steps=c["steps"],
        )

    def run(self, seed, configuration, *, full=False):
        self.validate(configuration)
        c, selection, blocks = configuration, None, None
        if c["experiment"] == "mining":
            data, env = mining_universe(seed, assets=8, steps=c["steps"])
            selection = select_pair(data[: c["split"]])
            pair = data[:, selection["selected"]]
        else:
            pair, env = generate(
                seed,
                name=c["variant"] if c["experiment"] == "regime" else "stable",
                steps=c["steps"],
            )
        rules = BASE_RULES
        start, end = c["split"], len(pair)
        if c["experiment"] == "generalisation":
            candidates = [asdict(replace(BASE_RULES, entry=z)) for z in (1.5, 2, 2.5)]
            selection = sweep(pair[: c["split"]], candidates=candidates)
            rules = Rules(**selection["parameters"])
        if c["experiment"] in ("generalisation", "mining"):
            span = min(c["split"] - 80, len(pair) - c["split"])
            start, end = (
                (c["split"] - span, c["split"])
                if c["variant"] == "in_sample"
                else (c["split"], c["split"] + span)
            )
        if c["experiment"] == "walk_forward" and c["variant"] == "walk_forward":
            s, blocks = walk_forward(pair, start=start)
        else:
            s = backtest(
                pair,
                rules=rules,
                start=start,
                end=end,
                fee=0.05 if c["experiment"] == "costs" and c["variant"] == "high" else 0.005,
                spread_ticks=5 if c["experiment"] == "costs" and c["variant"] == "high" else 1,
            )
        metrics = {k: s.metrics()[k] for k in METRICS}
        evidence = dict(
            selection=selection,
            blocks=blocks,
            metrics=metrics,
            trades=s.trades,
            fills=s.fills,
            path=s.path,
            decisions=s.decisions,
        )
        return SimulationOutcome(
            metrics,
            env,
            digest(evidence),
            coverage=dict(
                trading_start=start,
                trading_end=end,
                selection=selection,
                blocks=blocks,
                residual_positions=s.market.positions(),
            ),
            journal=evidence if full else None,
        )

    def metric_units(self, c):
        return {
            k: "GBP"
            if k
            in (
                "net_pnl",
                "drawdown",
                "average_trade",
                "median_trade",
                "turnover",
                "costs",
                "max_gross",
                "max_imbalance",
                "worst_trade",
            )
            else "fraction"
            if k in ("return_on_capital", "win_rate", "probability_loss")
            else "observations"
            if k == "mean_holding"
            else "units"
            for k in METRICS
        }


def experiment_spec(
    experiment, *, runs=16, root=101010, pool="development", steps=320, split=160
):
    designs = {
        "generalisation": (
            "Does training-selected performance persist on untouched future observations?",
            (
                "Selecting the best of three training thresholds creates "
                "optimism; held-out outcomes may weaken."
            ),
            ("in_sample", "out_of_sample"),
        ),
        "walk_forward": (
            "Does causal refitting improve this fixed strategy out of sample?",
            "Refitting changes hedge estimates and turnover; improvement is not guaranteed.",
            ("fixed", "walk_forward"),
        ),
        "costs": (
            "How do higher two-leg execution costs affect net outcomes?",
            "Higher spreads and fees should reduce net P&L under this fixed environment.",
            ("low", "high"),
        ),
        "regime": (
            "What happens when a previously stable residual acquires a unit root and drift?",
            "An old relationship may fail despite stops and reassuring training fits.",
            ("stable", "drift"),
        ),
        "mining": (
            "Does the best unrelated training pair survive an untouched test?",
            (
                "Ranking 28 null pairs creates winner's curse; selected in-sample"
                " success need not persist."
            ),
            ("in_sample", "out_of_sample"),
        ),
    }
    if experiment not in designs:
        raise ValueError("Unknown experiment")
    q, h, variants = designs[experiment]
    spec = ExperimentSpec(
        q,
        h,
        SeedPlan(root, pool, runs),
        tuple(
            Variant(v, dict(experiment=experiment, variant=v, steps=steps, split=split))
            for v in variants
        ),
        StatArbAdapter.name,
        paired=experiment != "regime",
        bootstrap_resamples=500,
        limitations=(
            "Synthetic results do not establish real-market alpha.",
            "Training-selected performance is optimistic; evaluation never selects thresholds.",
            (
                "The initial fit origin differs across disjoint time blocks; "
                "blocks may have different lengths."
            ),
            "Confidence intervals exclude process, liquidity and model uncertainty.",
        ),
    )
    for v in spec.variants:
        StatArbAdapter().validate(v.configuration)
    return spec
