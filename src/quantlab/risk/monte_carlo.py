"""Joint physical-return scenarios with full option repricing and independent seeds."""

import math
from dataclasses import replace

import numpy as np

from quantlab.options.models import number
from quantlab.options.pricing import price, price_many
from quantlab.risk.covariance import validate_covariance, vector
from quantlab.risk.metrics import empirical_risk
from quantlab.risk.scenarios import validate_horizon


def factor_matrix(covariance):
    c, info = validate_covariance(covariance)
    try:
        factor = np.linalg.cholesky(c)
        method = "Cholesky"
    except np.linalg.LinAlgError:
        eigen, vectors = np.linalg.eigh(c)
        factor = vectors @ np.diag(np.sqrt(np.maximum(eigen, 0)))
        method = "PSD eigenfactor (singular covariance)"
        if (eigen < 0).any():
            info["warnings"].append(
                "Roundoff-negative eigenvalues truncated at disclosed tolerance"
            )
    return factor, info | {"factor_method": method}


def joint_returns(
    covariance, means, *, paths=10000, days=1, seed=99042, distribution="normal", df=5
):
    if type(paths) is not int or not 2 <= paths <= 200_000:
        raise ValueError("Risk simulation requires 2–200,000 paths")
    if type(days) is not int or not 1 <= days <= 252:
        raise ValueError("Risk horizon requires 1–252 whole calendar model days")
    if type(seed) is not int or not 0 <= seed < 2**1024:
        raise ValueError("Analysis seed must be an integer in [0,2^1024)")
    mu = vector(means, "mean returns")
    factor, info = factor_matrix(covariance)
    if len(mu) != len(factor) or paths * days * len(mu) > 20_000_000:
        raise ValueError("Return dimension differs or local scenario budget exceeds 20M draws")
    if distribution not in ("normal", "student"):
        raise ValueError("Return model must be normal or student")
    df = number(df, "Student t degrees of freedom", 2.01, 100)
    # Namespaced independent analysis stream, never the market RNG.
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence([seed, 9009])))
    z = rng.standard_normal((paths, days, len(mu)))
    if distribution == "student":
        # Common radial scaling creates a multivariate t, preserving covariance at df>2.
        radial = np.random.Generator(np.random.PCG64(np.random.SeedSequence([seed, 9010])))
        z *= np.sqrt((df - 2) / radial.chisquare(df, size=(paths, days, 1)))
    daily = z @ factor.T + mu
    if np.any(daily <= -1):
        raise ValueError(
            "Arithmetic return model sampled <= -100%; change assumptions, no silent clipping"
        )
    terminal = np.prod(1 + daily, axis=1) - 1
    if not np.isfinite(terminal).all():
        raise ArithmeticError("Scenario return overflow")
    return terminal, info | {
        "distribution": distribution,
        "df": df if distribution == "student" else None,
        "seed": seed,
        "paths": paths,
        "days": days,
    }


def vector_option_prices(position, spots, years):
    """Compatibility adapter to the authoritative options pricing kernel."""
    return price_many(position.kind, replace(position.inputs(), time_years=years), spots)


def revalue_returns(portfolio, factors, returns, *, days=1, cash_rate=0):
    validate_horizon(portfolio, days)
    cash_rate = number(cash_rate, "cash risk rate", -1, 1)
    a = np.asarray(returns, dtype=float)
    if a.ndim != 2 or a.shape[1] != len(factors) or not np.isfinite(a).all() or (a <= -1).any():
        raise ValueError("Finite scenario rows require one simple return > -100% per factor")
    if len(set(factors)) != len(factors):
        raise ValueError("Risk factors must be distinct")
    dt = days / 365
    full = np.full(len(a), portfolio.cash * math.expm1(cash_rate * dt))
    delta = np.zeros(len(a))
    for p in portfolio.positions:
        if p.underlying not in factors:
            raise ValueError(f"No return factor for {p.underlying}")
        ds = p.spot * a[:, factors.index(p.underlying)]
        delta += p.sensitivities()["delta"] * ds
        if p.kind == "stock":
            full += p.quantity * ds
        else:
            values = vector_option_prices(p, p.spot + ds, max(0, p.years - dt))
            full += p.units * (values - price(p.kind, p.inputs()))
    if not np.isfinite(full).all():
        raise ArithmeticError("Nonfinite repriced portfolio P&L")
    return -full, -delta


def monte_carlo_risk(
    portfolio,
    factors,
    covariance,
    means,
    *,
    alpha=0.95,
    paths=10000,
    days=1,
    seed=99042,
    distribution="normal",
    df=5,
    cash_rate=0,
    full=False,
):
    validate_horizon(portfolio, days)
    returns, info = joint_returns(
        covariance, means, paths=paths, days=days, seed=seed, distribution=distribution, df=df
    )
    losses, linear = revalue_returns(
        portfolio, factors, returns, days=days, cash_rate=cash_rate
    )
    return {
        "full": empirical_risk(losses, alpha, full=full),
        "delta": empirical_risk(linear, alpha, full=full),
        "simulation": info,
        "warning": (
            "Physical IID daily arithmetic-return scenarios; fixed IV; no forecast or guarantee"
        ),
    }


def historical_risk(
    portfolio,
    factors,
    observations,
    *,
    alpha=0.95,
    days=1,
    cash_rate=0,
    full=False,
    label="User-supplied empirical sample",
):
    a = np.asarray(observations, dtype=float)
    if a.ndim != 2 or a.shape[1] != len(factors) or len(a) < 2 or not np.isfinite(a).all():
        raise ValueError("Empirical returns must be complete synchronised observations")
    if type(days) is not int or days < 1 or len(a) // days < 2:
        raise ValueError("Need at least two non-overlapping horizon blocks")
    if (a <= -1).any():
        raise ValueError("Simple returns must exceed -100%")
    blocks = len(a) // days
    scenarios = np.prod(1 + a[: blocks * days].reshape(blocks, days, len(factors)), axis=1) - 1
    losses, linear = revalue_returns(
        portfolio, factors, scenarios, days=days, cash_rate=cash_rate
    )
    return {
        "full": empirical_risk(losses, alpha, full=full),
        "delta": empirical_risk(linear, alpha, full=full),
        "days": days,
        "blocks": blocks,
        "unused_rows": len(a) - blocks * days,
        "sample": label,
        "warning": "Non-overlapping compounded blocks; the sample may omit future crises",
    }
