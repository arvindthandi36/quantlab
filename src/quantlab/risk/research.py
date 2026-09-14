"""Phase 5 registered portfolio experiments, using actual executed starting portfolios."""

from dataclasses import asdict, replace

from quantlab.options.session import OptionsSession
from quantlab.options.underlying import UnderlyingVenue
from quantlab.research.codec import digest
from quantlab.research.models import ExperimentSpec, SimulationOutcome, Variant
from quantlab.research.seeds import SeedPlan
from quantlab.risk.analytics import FACTORS, RiskSettings, linear_risk
from quantlab.risk.monte_carlo import monte_carlo_risk
from quantlab.risk.portfolio import from_accounts


class RiskAdapter:
    name = "portfolio-full-revaluation-v1"

    def validate(self, c):
        if not isinstance(c, dict) or set(c) != {"settings", "portfolio"}:
            raise ValueError("Risk research requires settings and executed portfolio recipe")
        RiskSettings(**c["settings"])
        if c["portfolio"] not in ("two_stocks", "hedged_call", "short_straddle"):
            raise ValueError("Unknown executed research portfolio")

    def environment_key(self, c):
        self.validate(c)
        # Prefix nesting pairs sample-size variants. Distribution uses a second radial stream.
        return {"stream": "risk.standard-normal-v1", "days": c["settings"].get("days", 1)}

    def run(self, seed, configuration, *, full=False):
        self.validate(configuration)
        settings = RiskSettings(**configuration["settings"])
        s = OptionsSession(capture=full)
        b = UnderlyingVenue(100, steps=252, capture=full)
        recipe = configuration["portfolio"]
        if recipe == "two_stocks":
            s.command("stock_order", side="buy", quantity=50, order_type="market")
            b.command("order", side="buy", quantity=50, order_type="market")
        else:
            for kind in ("call",) if recipe == "hedged_call" else ("call", "put"):
                key = next(
                    k
                    for k, c in s.contracts.items()
                    if c.option_type == kind
                    and float(c.strike_gbp) == 100
                    and float(c.expiry_years * 365) == 30
                )
                s.command(
                    "option_order",
                    contract_id=key,
                    side="buy" if recipe == "hedged_call" else "sell",
                    quantity=5,
                    quote_revision=s.quote_revision,
                )
            s.command("hedge")
        p = from_accounts(s, {"QL-SECOND": b})
        r = monte_carlo_risk(
            p,
            FACTORS,
            settings.covariance(),
            settings.means,
            alpha=settings.confidence,
            days=settings.days,
            paths=settings.paths,
            seed=seed,
            distribution=settings.distribution,
            df=settings.df,
            full=full,
        )
        linear = linear_risk(p, settings)
        metrics = {
            "var": r["full"]["var"],
            "es": r["full"]["es"],
            "delta_var": linear["var"],
            "full_minus_delta_var": r["full"]["var"] - linear["var"],
            "es_minus_var": r["full"]["es"] - r["full"]["var"],
            "mean_loss": r["full"]["mean_loss"],
        }
        evidence = {"portfolio": p.public(), "risk": r, "metrics": metrics}
        if not full:
            evidence["risk"] = {
                **r,
                "full": {k: v for k, v in r["full"].items() if k != "losses"},
                "delta": {k: v for k, v in r["delta"].items() if k != "losses"},
            }
        # Full/summary have identical fingerprint, excluding retained paths.
        canonical_risk = {
            **r,
            "full": {k: v for k, v in r["full"].items() if k != "losses"},
            "delta": {k: v for k, v in r["delta"].items() if k != "losses"},
        }
        return SimulationOutcome(
            metrics,
            digest({"seed": seed, "common_stream": self.environment_key(configuration)}),
            digest({"portfolio": p.public(), "risk": canonical_risk}),
            coverage={"paths": settings.paths, "units": "GBP", "recipe": recipe},
            journal=evidence if full else None,
        )

    def metric_units(self, c):
        return dict.fromkeys(
            ("var", "es", "delta_var", "full_minus_delta_var", "es_minus_var", "mean_loss"),
            "GBP",
        )


def experiment_spec(experiment, *, runs=32, root=99009, pool="development", paths=5000):
    base = RiskSettings(paths=paths)
    designs = {
        "correlation": (
            "How does higher assumed correlation affect this executed two-stock portfolio?",
            (
                "With both stocks long and unchanged volatility, higher correlation should "
                "increase loss VaR on average."
            ),
            "two_stocks",
            "var",
            [
                ("rho_0", replace(base, correlation=0)),
                ("rho_09", replace(base, correlation=0.9)),
            ],
        ),
        "tails": (
            "How do covariance-matched heavy tails affect option Expected Shortfall?",
            (
                "Covariance-matched t(5) shocks may worsen ES for a short gamma portfolio; "
                "normal VaR need not order the tails."
            ),
            "short_straddle",
            "es",
            [("normal", base), ("student_5", replace(base, distribution="student"))],
        ),
        "nonlinearity": (
            "How does horizon change full versus delta-normal VaR on an executed hedged call?",
            (
                "Full-minus-delta VaR can change as option decay and curvature accumulate; "
                "delta neutrality alone will not remove loss."
            ),
            "hedged_call",
            "full_minus_delta_var",
            [("one_day", base), ("five_days", replace(base, days=5))],
        ),
        "sample_size": (
            "How does path count affect the variability of estimated VaR?",
            (
                "Across independent seed addresses, larger nested samples should reduce "
                "estimation variability, not model error."
            ),
            "two_stocks",
            "var",
            [
                ("small", replace(base, paths=250)),
                ("large", replace(base, paths=max(paths, 2000))),
            ],
        ),
    }
    if experiment not in designs:
        raise ValueError("Unknown risk experiment")
    q, h, recipe, metric, variants = designs[experiment]
    return ExperimentSpec(
        q,
        h,
        SeedPlan(root, pool, runs),
        tuple(Variant(n, {"settings": asdict(s), "portfolio": recipe}) for n, s in variants),
        RiskAdapter.name,
        paired=experiment != "nonlinearity",
        primary_metric=metric,
        bootstrap_resamples=500,
        practical_threshold=0.1,
        limitations=(
            "Synthetic executed starting portfolios; fixed assumptions, not forecasts.",
            "Normal/t distributions share Gaussian shocks; transformed returns differ.",
            "Sample-size variants use nested path prefixes; uncertainty excludes model error.",
            "Different horizons are explicitly unpaired; no false identical-environment claim.",
        ),
    )
