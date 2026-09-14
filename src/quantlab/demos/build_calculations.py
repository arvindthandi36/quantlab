"""Adapters to existing risk and statistical-arbitrage teaching calculations."""

from dataclasses import asdict
from functools import lru_cache

from quantlab.demos import SEED
from quantlab.demos.build_trading import act
from quantlab.demos.models import Evidence, Moment, choice
from quantlab.demos.projections import calculation, point
from quantlab.options.analytics import shock
from quantlab.options.models import PricingInputs
from quantlab.research.codec import plain
from quantlab.risk.analytics import diversification, tail_example
from quantlab.statarb.examples import relationship_example, teaching_cases
from quantlab.statarb.research import generate
from quantlab.statarb.session import StatArbSession
from quantlab.statarb.statistics import CausalModel


@lru_cache(maxsize=1)
def cases():
    return teaching_cases()


def series(name, rows, x="Observation", y="Value"):
    return {
        "title": name,
        "x": x,
        "y": y,
        "series": [
            {"name": name, "points": [[i, v] for i, v in enumerate(rows) if v is not None]}
        ],
    }


def build(spec, branch="full"):
    family = spec.builder
    note = (
        "Existing controlled teaching calculation, not a forecast or a production risk model."
    )
    limits = [note]
    moments = []
    journal = None
    config = {"seed": SEED, "source": "approved teaching functions"}

    def event(key, title, action, concept, before, after, prompt, **extra):
        moments.append(
            Moment(key, title, action, concept, before, after, choice(concept, prompt), **extra)
        )

    if family == "tails":
        tails = tail_example()
        before = calculation(
            {
                name: {k: r[k] for k in ("var", "confidence", "n", "convention")}
                for name, r in tails.items()
            },
            note=(
                "Two controlled loss samples; VaR comes from the existing inverse "
                "empirical CDF convention."
            ),
        )
        after = calculation(
            tails,
            note=(
                "Expected Shortfall averages the exact worst 5% mass. The sample "
                "contains only five effective tail observations; fees and returns "
                "are not being simulated here."
            ),
            charts=tuple(
                {
                    "title": name + " loss tail",
                    "x": "Worst observation rank",
                    "y": "Loss £",
                    "threshold": r["var"],
                    "threshold_label": "VaR",
                    "series": [
                        {
                            "name": "Worst losses (ES uses worst 5)",
                            "points": [[i + 1, v] for i, v in enumerate(r["worst"])],
                        }
                    ],
                }
                for name, r in tails.items()
            ),
        )
        event(
            "tail",
            "Look beyond the threshold",
            "Reveal the severity of the loss tail",
            "expected_shortfall",
            before,
            after,
            "If the two VaR values match, must their tail risks be similar?",
            capture_after="var-vs-es-tail",
        )
        limits.extend(
            (
                (
                    "These are deliberately constructed loss distributions, not "
                    "sampled live portfolios."
                ),
                "VaR is not a maximum loss; ES is an average within a model/data tail.",
            )
        )
    elif family == "diversification":
        data = diversification()
        event(
            "correlation",
            "Hold exposures and vary co-movement",
            "Calculate the controlled covariance allocations",
            "diversification",
            calculation({k: v for k, v in data.items() if k != "rows"}),
            calculation(data),
            "Do two asset names guarantee effective diversification?",
        )
    elif family == "stress":
        x = PricingInputs(100, 100, 30 / 365, 0.2)
        event(
            "shock",
            "A model is an approximation",
            "Compare small and large shocks with exact repricing",
            "stress_testing",
            calculation(asdict(x)),
            calculation(
                {
                    "small": shock("call", x, spot_change=1, volatility_change=0.01),
                    "large": shock("call", x, spot_change=-15, volatility_change=0.15),
                }
            ),
            "Must a local Greek approximation stay accurate for a large shock?",
        )
    elif family == "regression":
        event(
            "fit",
            "Fit a straight relationship",
            "Run existing ordinary least squares",
            "regression",
            calculation({"x": [1, 2, 3, 4, 5], "y": [5, 8, 11, 14, 17]}),
            calculation(cases()["cases"]["exact_regression"]),
            "Does an exact sample fit guarantee a future relationship?",
        )
    elif family in ("pairs", "mining"):
        data = cases()
        names = ("noncointegrated", "stable") if family == "pairs" else ("spurious",)
        # These are completed independent datasets, not a user's unseen future.
        initial = {
            ("Pair A" if i == 0 else "Pair B"): {
                "price_correlation": data["cases"][name]["correlation"]
            }
            for i, name in enumerate(names)
        }
        charts = []
        for i, name in enumerate(names):
            d = data["cases"][name]
            label = "Pair A" if i == 0 else "Pair B"
            charts.append(
                {
                    "title": label + " prices (completed teaching sample)",
                    "x": "Observation",
                    "y": "Price £",
                    "series": [
                        {"name": a, "points": [[t, r[j]] for t, r in enumerate(d["prices"])]}
                        for j, a in enumerate(("X", "Y"))
                    ],
                }
            )
        before = calculation(initial, note=data["label"], charts=charts)
        after = calculation(
            {name: data["cases"][name] for name in names},
            note=data["label"],
            charts=tuple(
                c
                for name in names
                for c in (
                    series(name + " residual", data["cases"][name]["residual"], y="Residual £"),
                    series(name + " causal z-score", data["cases"][name]["z"], y="Z-score"),
                )
            ),
        )
        event(
            "relationship",
            "Similar pictures can hide different relationships",
            "Inspect regression residuals and past-window z-scores",
            "residual",
            before,
            after,
            "Does high price correlation alone establish cointegration?",
            capture_after="correlation-vs-residual",
        )
        if family == "pairs":
            data_break, _ = generate(101001, name="decouple", steps=400)
            broken = relationship_example(data_break)
            event(
                "break",
                "Challenge the stable relationship",
                "Apply the existing decoupling scenario and recalculate residuals",
                "model_risk",
                after,
                calculation(
                    {"decoupled": broken},
                    charts=(
                        series(
                            "Deliberately broken relationship: residual",
                            broken["residual"],
                            y="Residual £",
                        ),
                    ),
                ),
                "Does a relationship that used to be stable have to remain stable?",
            )
            limits.append(
                "Known synthetic process labels support a model claim, not an "
                "empirical cointegration test. Exact observed correlations are "
                "shown, not replaced with 0.98."
            )
        config = {
            "seeds": [101001, 101002, 101003],
            "source": "Phase 10 independent completed teaching cases",
        }
    elif family == "lookahead":
        data, _ = generate(201042, steps=120)
        model = CausalModel(window=40, z_window=20)
        before = model.at(data, 80)
        changed = data.copy()
        changed[81:] *= 1.7
        after = model.at(changed, 80)
        event(
            "future",
            "Use only the observed prefix",
            "Alter rows after observation 80; recalculate the signal at 80",
            "lookahead_bias",
            calculation({"original_signal_at_80": plain(before)}),
            calculation(
                {
                    "original_signal_at_80": plain(before),
                    "changed_future_signal_at_80": plain(after),
                    "identical": plain(before) == plain(after),
                    "changed_rows": list(range(81, len(data))),
                }
            ),
            "Should changing only unseen future rows change today's causal signal?",
        )
    elif family == "leg":
        s = StatArbSession(
            seed=SEED, steps=60, rules={"window": 20, "z_window": 12, "block": 10}
        )
        act(s, "step", count=32)
        ids = s.market.identifiers
        act(s, "liquidity", instrument=ids[1], depth=0)
        before = point(s.state(), "statarb")
        act(s, "order", instrument=ids[0], side="buy", quantity=2, order_type="market")
        first = point(s.state(), "statarb")
        event(
            "first-leg",
            "Two venues, two instructions",
            "Buy 2 units of the first instrument",
            "leg_risk",
            before,
            first,
            "Does a completed first leg guarantee a completed hedge leg?",
        )
        act(s, "order", instrument=ids[1], side="sell", quantity=2, order_type="market")
        event(
            "second-leg",
            "Request the offsetting leg",
            "Sell 2 units in the empty second venue",
            "leg_risk",
            first,
            point(s.state(), "statarb"),
            "Can an empty book supply a market-order fill?",
        )
        act(s, "end")
        journal = s.journal()
    else:
        raise ValueError("Unknown calculation adapter")
    return Evidence(spec, moments, config, tuple(limits), journal)
