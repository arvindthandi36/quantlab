"""One risk report consumed by CLI, browser, research and tutor."""

from dataclasses import asdict, dataclass

import numpy as np

from quantlab.options.models import number
from quantlab.risk.covariance import (
    correlation,
    covariance_from_volatility,
    estimate_covariance,
)
from quantlab.risk.metrics import confidence, empirical_risk, parametric_risk
from quantlab.risk.monte_carlo import historical_risk, joint_returns, monte_carlo_risk
from quantlab.risk.scenarios import NAMED, scenario_pnl, validate_horizon

FACTORS = ("QL-STOCK", "QL-DESK", "QL-SECOND")


@dataclass(frozen=True)
class RiskSettings:
    confidence: float = 0.95
    days: int = 1
    daily_volatility: tuple = (0.012, 0.010, 0.008)
    means: tuple = (0.0, 0.0, 0.0)
    correlation: float = 0.25
    paths: int = 5000
    seed: int = 99042
    sample_seed: int = 77042
    sample_size: int = 500
    distribution: str = "normal"
    df: float = 5.0
    cash_rate: float = 0.0

    def __post_init__(self):
        object.__setattr__(self, "confidence", confidence(self.confidence))
        object.__setattr__(
            self, "correlation", number(self.correlation, "correlation", -0.5, 1)
        )
        for key, lo, hi in (
            ("days", 1, 252),
            ("paths", 2, 200_000),
            ("sample_size", 2, 100_000),
        ):
            if type(getattr(self, key)) is not int or not lo <= getattr(self, key) <= hi:
                raise ValueError(f"{key} requires an integer in {lo}–{hi}")
        for key in ("seed", "sample_seed"):
            if type(getattr(self, key)) is not int or not 0 <= getattr(self, key) < 2**1024:
                raise ValueError("Analysis/sample seed must be a nonnegative integer < 2^1024")
        for key, lo, hi in (("daily_volatility", 0, 0.2), ("means", -0.2, 0.2)):
            v = tuple(number(x, key, lo, hi) for x in getattr(self, key))
            if len(v) != len(FACTORS):
                raise ValueError("One assumption per named return factor required")
            object.__setattr__(self, key, v)
        if self.distribution not in ("normal", "student"):
            raise ValueError("Return distribution must be normal or student")
        object.__setattr__(self, "df", number(self.df, "t degrees of freedom", 2.01, 100))
        object.__setattr__(self, "cash_rate", number(self.cash_rate, "cash risk rate", -1, 1))

    def covariance(self, corr=None):
        rho = self.correlation if corr is None else corr
        c = np.full((3, 3), rho)
        np.fill_diagonal(c, 1.0)
        return covariance_from_volatility(self.daily_volatility, c)


def exposures(portfolio):
    f = portfolio.public()["factors"]
    return [f[k]["delta"] * f[k]["spot"] if k in f else 0.0 for k in FACTORS]


def linear_risk(portfolio, settings, covariance=None):
    return parametric_risk(
        exposures(portfolio),
        settings.covariance() if covariance is None else covariance,
        settings.means,
        alpha=settings.confidence,
        days=settings.days,
        options=any(p.kind != "stock" for p in portfolio.positions),
    )


def diversification(budget=10000.0, daily_vol=0.01, alpha=0.95):
    rows = []
    for label, w, rho in (
        ("Concentrated", [1, 0], 0),
        ("Imperfect correlation", [0.5, 0.5], 0.25),
        ("Strong correlation", [0.5, 0.5], 0.95),
        ("Negative correlation", [0.5, 0.5], -0.5),
        ("Identical exposure", [0.5, 0.5], 1),
    ):
        c = covariance_from_volatility([daily_vol, daily_vol], [[1, rho], [rho, 1]])
        risk = parametric_risk(np.array(w) * budget, c, alpha=alpha)
        rows.append(
            {
                "label": label,
                "weights": w,
                "correlation": rho,
                "var": risk["var"],
                "volatility_gbp": risk["loss_sd"],
                "expected_return": 0.0,
                "decomposition": risk["decomposition"],
            }
        )
    return {
        "budget": budget,
        "daily_volatility": daily_vol,
        "rows": rows,
        "label": (
            "Controlled hypothetical equal-volatility, equal-mean allocations; "
            "not actual trades"
        ),
    }


def tail_example():
    # Same inverse-CDF 95% threshold, different severities in the final observation.
    a = [0.0] * 94 + [10.0] * 5 + [20.0]
    b = [0.0] * 94 + [10.0] * 5 + [200.0]
    return {"mild": empirical_risk(a), "severe": empirical_risk(b)}


def analyse(portfolio, settings, *, observations=None, covariance=None, full=False):
    c = settings.covariance() if covariance is None else covariance
    public = portfolio.public()
    linear = linear_risk(portfolio, settings, c)
    if observations is None:
        observations, _ = joint_returns(
            settings.covariance(),
            settings.means,
            paths=settings.sample_size,
            seed=settings.sample_seed,
        )
        label = "Fixed synthetic sample (independent sample seed; NOT observed market history)"
    else:
        label = "User-supplied synchronised empirical one-day simple returns"
    estimated = estimate_covariance(observations)
    try:
        validate_horizon(portfolio, settings.days)
    except ValueError as exc:
        empty = {
            "var": None,
            "es": None,
            "confidence": settings.confidence,
            "n": 0,
            "tail_mass": 0,
            "boundary_weight": 0,
            "worst": [],
            "histogram": {"edges": [], "counts": []},
            "warnings": [str(exc)],
            "convention": "Unavailable: selected horizon crosses an unsettled expiry",
        }
        historical = {
            "full": empty,
            "delta": empty,
            "sample": label,
            "blocks": 0,
            "unused_rows": len(observations),
            "days": settings.days,
        }
        mc = {
            "full": empty,
            "delta": empty,
            "simulation": {
                "paths": settings.paths,
                "distribution": settings.distribution,
                "factor_method": "not run",
                "warnings": [str(exc)],
            },
        }
    else:
        historical = historical_risk(
            portfolio,
            FACTORS,
            observations,
            alpha=settings.confidence,
            days=settings.days,
            cash_rate=settings.cash_rate,
            full=full,
            label=label,
        )
        mc = monte_carlo_risk(
            portfolio,
            FACTORS,
            c,
            settings.means,
            alpha=settings.confidence,
            paths=settings.paths,
            days=settings.days,
            seed=settings.seed,
            distribution=settings.distribution,
            df=settings.df,
            cash_rate=settings.cash_rate,
            full=full,
        )
    stresses = []
    for scenario in NAMED.values():
        try:
            row = scenario_pnl(portfolio, scenario, cash_rate=settings.cash_rate)
            if scenario.correlation is not None:
                row["correlation_risk"] = linear_risk(
                    portfolio, settings, settings.covariance(scenario.correlation)
                )
            stresses.append(row)
        except ValueError as exc:
            stresses.append({"scenario": asdict(scenario), "unavailable": str(exc)})
    return {
        "portfolio": public,
        "settings": asdict(settings),
        "factors": list(FACTORS),
        "covariance": np.asarray(c).tolist(),
        "correlation": correlation(c),
        "sample_covariance": estimated,
        "covariance_source": "Custom / estimated matrix override"
        if covariance is not None
        else "Configured volatility and correlation",
        "sample_correlation": correlation(estimated["covariance"]),
        "parametric": linear,
        "historical": historical,
        "monte_carlo": mc,
        "stresses": stresses,
        "diversification": diversification(max(public["gross_delta_gbp"], 10000)),
        "tail_example": tail_example(),
        "units": "GBP loss; one-day simple-return covariance; ACT/365 calendar horizon",
        "warnings": [
            "Precise estimates are conditional on model/data, not forecasts",
            (
                "Delta-normal risk omits nonlinear/volatility risk; inspect full revaluation "
                "and stresses"
            ),
            (
                "Greeks summed across different stocks are descriptive; factor exposures "
                "retain identity"
            ),
        ],
    }
