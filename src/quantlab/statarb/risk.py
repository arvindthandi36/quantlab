"""Actual account bridge to Phase 9; no independent P&L or VaR implementation."""

from dataclasses import replace

import numpy as np

from quantlab.risk.covariance import estimate_covariance
from quantlab.risk.metrics import parametric_risk
from quantlab.risk.portfolio import Portfolio, from_accounts
from quantlab.risk.scenarios import Scenario, scenario_pnl


def portfolio(market, *, capital=10000, drawdown=0):
    p = from_accounts(stocks=market.venues, drawdown=drawdown)
    return replace(
        p,
        cash=p.cash + capital,
        initial_capital=p.initial_capital + capital,
        source="Actual Phase 6 stat-arb FIFO accounts + explicit research capital",
    )


def observed_covariance(history):
    a = np.asarray(history[-81:], dtype=float)
    if len(a) < 4:
        return None
    return np.asarray(estimate_covariance(np.diff(a, axis=0) / a[:-1])["covariance"])


def analyse_market(market, *, capital=10000, drawdown=0):
    p = portfolio(market, capital=capital, drawdown=drawdown)
    c = observed_covariance(market.history)
    w = np.array(
        [
            market.venues[k].account.inventory * market.history[-1][i]
            for i, k in enumerate(market.identifiers)
        ]
    )
    linear = None if c is None else parametric_risk(w, c, alpha=0.95)
    # One observable proxy factor: X return. Estimated loadings are causal sample covariances.
    loadings = None if c is None or c[0, 0] <= 1e-16 else c[:, 0] / c[0, 0]
    return dict(
        portfolio=p.public(),
        factors=list(market.identifiers),
        covariance=None if c is None else c.tolist(),
        linear=linear,
        factor_proxy=market.identifiers[0],
        estimated_loadings=None if loadings is None else loadings.tolist(),
        factor_exposure=None if loadings is None else float(w @ loadings),
        stresses={
            "both_down_5pct": scenario_pnl(p, Scenario(stock_return=-0.05)),
            "Y_down_5pct_X_flat": scenario_pnl(
                p, Scenario(), factor_returns={market.identifiers[1]: -0.05}
            ),
        },
        label="95% one-observation delta-normal VaR/ES; past 80 observed returns, zero drift. "
        "Not calibrated daily risk; X is an observed proxy, not the hidden true factor.",
    )


def consolidated(base, base_factors, base_covariance, market, *, capital=10000):
    """Read-only combined risk over actual ledgers; disjoint instrument names enforced."""
    extra = portfolio(market, capital=capital)
    factors = list(base_factors) + list(market.identifiers)
    if len(factors) != len(set(factors)):
        raise ValueError("Linked portfolios require distinct underlying identifiers")
    p = Portfolio(
        base.positions + extra.positions,
        base.cash + extra.cash,
        base.realised_gross + extra.realised_gross,
        base.unrealised + extra.unrealised,
        base.fees + extra.fees,
        base.financing + extra.financing,
        base.initial_capital + extra.initial_capital,
        source="Consolidated actual Risk Lab and Stat Arb accounts",
    )
    c = observed_covariance(market.history)
    linear = None
    if c is not None:
        covariance = np.zeros((len(factors), len(factors)))
        n = len(base_factors)
        covariance[:n, :n], covariance[n:, n:] = base_covariance, c
        exposures = p.public()["factors"]
        w = [
            exposures.get(k, {}).get("delta", 0) * exposures.get(k, {}).get("spot", 0)
            for k in factors
        ]
        linear = parametric_risk(w, covariance, alpha=0.95)
    return dict(
        portfolio=p.public(),
        linear=linear,
        factors=factors,
        stress=scenario_pnl(p, Scenario(stock_return=-0.05)),
        statarb_factor=analyse_market(market, capital=capital)["factor_exposure"],
        assumption="Cross-lab covariance assumed zero; one stat-arb observation mapped to "
        "one risk day for this illustrative joint stress only. Separate time "
        "scales and unknown cross-correlations limit this estimate.",
        limits_scope="Existing Risk Lab limits cover its original three venues. "
        "Stat Arb limits are enforced in the Stat Arb session.",
    )
