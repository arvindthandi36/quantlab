"""Environment-labelled adapters for the existing registered research engine."""

from dataclasses import replace

from quantlab.environments.data import integer
from quantlab.environments.historical import HistoricalSession
from quantlab.environments.scenarios import SPECS
from quantlab.research.adapters.maker import MakerAdapter, maker_configuration
from quantlab.research.codec import digest, plain
from quantlab.research.engine import execute
from quantlab.research.models import ExperimentSpec, SimulationOutcome, Variant
from quantlab.research.seeds import SeedPlan
from quantlab.trading.scenarios import select_scenario


def scenario_configuration(key, *, strategy="fixed", seconds=10):
    if key not in ("normal", "high_volatility", "toxic_flow"):
        raise ValueError(
            "Initial comparison supports normal, high volatility and informed-flow scenarios"
        )
    integer(seconds, "Comparison seconds", 1, 60)
    from dataclasses import asdict

    market = asdict(select_scenario(SPECS[key]["preset"], duration_seconds=seconds).market)
    market.pop("seed")
    base = maker_configuration(strategy=strategy, duration_us=seconds * 1_000_000)
    base["market"] = market
    return plain(
        {
            "environment": {
                "type": "SCENARIO",
                "scenario": key,
                "source": "QuantLab controlled synthetic model",
            },
            "engine": base,
        }
    )


class ScenarioAdapter:
    name = "environment-scenario-maker-v1"

    def validate(self, c):
        if set(c) != {"environment", "engine"} or c["environment"].get("type") != "SCENARIO":
            raise ValueError("Scenario comparison cannot silently pool other environment types")
        if c["environment"].get("scenario") not in ("normal", "high_volatility", "toxic_flow"):
            raise ValueError("Unknown comparison scenario")
        MakerAdapter().validate(c["engine"])
        key = c["environment"]["scenario"]
        seconds = c["engine"]["market"]["duration_us"] // 1_000_000
        expected = scenario_configuration(key, seconds=seconds)
        if (
            c["environment"] != expected["environment"]
            or c["engine"]["market"] != expected["engine"]["market"]
        ):
            raise ValueError("Scenario label does not match its registered market parameters")

    def environment_key(self, c):
        return {
            "environment": c["environment"],
            "engine": MakerAdapter().environment_key(c["engine"]),
        }

    def run(self, seed, c, *, full=False):
        self.validate(c)
        # Different regimes have different exogenous configurations. Independent streams
        # avoid claiming the paired core design or treating shared random draws as independent.
        actual_seed = int(
            digest({"seed": seed, "scenario": c["environment"]["scenario"]})[:16], 16
        )
        out = MakerAdapter().run(actual_seed, c["engine"], full=full)
        return replace(
            out,
            coverage=out.coverage
            | {"environment": c["environment"], "actual_seed": actual_seed},
        )

    def metric_units(self, c):
        return MakerAdapter().metric_units(c["engine"])


def compare_scenarios(directory, *, runs=3, seconds=10, strategy="fixed"):
    integer(runs, "Independent comparison runs", 2, 10)
    adapter = ScenarioAdapter()
    spec = ExperimentSpec(
        "How robust is the same maker policy across controlled scenarios?",
        "Execution, inventory and tail outcomes can differ despite the same policy.",
        SeedPlan(131042, "development", runs),
        tuple(
            Variant(k, scenario_configuration(k, strategy=strategy, seconds=seconds))
            for k in ("normal", "high_volatility", "toxic_flow")
        ),
        adapter.name,
        paired=False,
        bootstrap_resamples=100,
        limitations=(
            "Controlled scenario comparison; never a forecast of real-market performance.",
            (
                "Independent scenario-specific streams; unpaired comparisons, "
                "conditional on the model."
            ),
            (
                "Arrival rates and model volatility differ; the paths are not "
                "claimed to be identical."
            ),
        ),
    )
    return execute(spec, adapter, directory)


class HistoricalPairAdapter:
    name = "environment-historical-paper-pair-v1"

    def __init__(self, datasets):
        self.datasets = tuple(datasets)

    def validate(self, c):
        if set(c) != {"environment", "entry", "training_end", "evaluation_end", "mode"} or c[
            "environment"
        ] != {"type": "HISTORICAL", "fingerprints": [d.fingerprint for d in self.datasets]}:
            raise ValueError(
                "Historical research requires its declared original datasets; no "
                "mixed environments"
            )
        if len(self.datasets) != 2:
            raise ValueError("Pair research requires two compatible series")
        integer(c["training_end"], "Training end", 20, len(self.datasets[0].bars) - 2)
        integer(
            c["evaluation_end"],
            "Evaluation end",
            c["training_end"] + 1,
            len(self.datasets[0].bars) - 1,
        )
        if c["entry"] not in (2.0, 2.5) or c["mode"] not in (
            "fixed",
            "rolling",
            "walk_forward",
        ):
            raise ValueError("Choose the declared threshold and causal fitting schedule")

    def environment_key(self, c):
        return c["environment"]

    def metric_units(self, c):
        return {"net_pnl": "GBP", "drawdown": "GBP", "fills": "count"}

    def run(self, seed, c, *, full=False):
        self.validate(c)
        from quantlab.statarb.strategy import Rules, decision

        s = HistoricalSession(
            self.datasets,
            model={"window": c["training_end"], "z_window": 12, "mode": c["mode"], "block": 10},
        )
        rules = Rules(entry=c["entry"])
        for t in range(c["evaluation_end"]):
            held = any(a.inventory for a in s.accounts.values())
            if t >= c["training_end"]:
                sig = s.signal()
                action, _ = decision(rules, sig, held=held, age=0, pnl=0, gross=0, imbalance=0)
                # Fixed one-unit legs; no claim of queue liquidity or beta neutrality.
                if action in ("long", "short") and not held:
                    for k, side in zip(
                        s.instruments,
                        ("sell", "buy") if action == "long" else ("buy", "sell"),
                        strict=True,
                    ):
                        s.command(
                            "order", instrument=k, side=side, quantity=1, order_type="market"
                        )
                elif action == "close" and held:
                    for k, a in s.accounts.items():
                        if a.inventory:
                            s.command(
                                "order",
                                instrument=k,
                                side="sell" if a.inventory > 0 else "buy",
                                quantity=abs(a.inventory),
                                order_type="market",
                            )
            s.command("step", count=1)
        s.command("end") if s.status != "ended" else None
        a = s.portfolio().public()
        return SimulationOutcome(
            {"net_pnl": a["pnl"], "drawdown": a["drawdown"], "fills": len(s.fills)},
            digest(c["environment"]),
            digest(s.public()),
            {"environment": c["environment"], "independent_historical_paths": 1},
            s.journal() if full else None,
        )


def historical_study(
    datasets, directory, *, training_end=30, evaluation_end=80, mode="rolling"
):
    adapter = HistoricalPairAdapter(datasets)
    env = {"type": "HISTORICAL", "fingerprints": [d.fingerprint for d in datasets]}
    variants = tuple(
        Variant(
            f"entry-{v}",
            {
                "environment": env,
                "entry": v,
                "training_end": training_end,
                "evaluation_end": evaluation_end,
                "mode": mode,
            },
        )
        for v in (2.0, 2.5)
    )
    spec = ExperimentSpec(
        "How do two prespecified entry thresholds behave on this one recorded path?",
        "A stricter threshold changes qualification; it need not improve executed outcomes.",
        SeedPlan(131042, "development", 1),
        variants,
        adapter.name,
        bootstrap_resamples=100,
        limitations=(
            "One historical path, not independent Monte Carlo trials; no generalisation claim.",
            (
                "Training/evaluation boundaries are explicit and fitting is "
                "causal. Fixed unit sizing is not beta neutral."
            ),
            (
                "Next-close bar paper execution; terminal inventory is marked, "
                "not falsely liquidated."
            ),
        ),
    )
    return execute(spec, adapter, directory)
