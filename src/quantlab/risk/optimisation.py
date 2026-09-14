"""Constrained synthetic allocation studies; never orders or forecasts."""

import numpy as np
from scipy.optimize import linprog, minimize

from quantlab.numerics import checked
from quantlab.options.models import number
from quantlab.risk.covariance import validate_covariance, vector


@checked
def optimise(
    covariance,
    means,
    *,
    long_only=True,
    max_weight=1.0,
    min_cash=0.0,
    risk_aversion=None,
    target_return=None,
    max_cash=1.0,
):
    c, diag = validate_covariance(covariance)
    mu = vector(means, "synthetic expected returns")
    if len(c) != len(mu) or type(long_only) is not bool:
        raise ValueError("Matching mean vector and boolean long-only flag required")
    cap = number(max_weight, "risky asset weight cap", 0.01, 1)
    cash = number(min_cash, "minimum cash", 0, 1)
    cash_cap = number(max_cash, "maximum cash", cash, 1)
    aversion = (
        None if risk_aversion is None else number(risk_aversion, "risk aversion", 0.0001, 1e6)
    )
    target = None if target_return is None else number(target_return, "target return", -10, 10)
    n = len(mu)
    sigma = np.zeros((n + 1, n + 1))
    sigma[:n, :n] = c
    expected = np.r_[mu, 0.0]
    bounds = [(0 if long_only else -cap, cap)] * n + [(cash, cash_cap)]
    aeq, beq = [np.ones(n + 1)], [1.0]
    if target is not None:
        aeq.append(expected)
        beq.append(target)
    feasibility = linprog(
        np.zeros(n + 1), A_eq=np.array(aeq), b_eq=beq, bounds=bounds, method="highs"
    )
    if not feasibility.success:
        raise ValueError("Allocation constraints are infeasible")
    scale = max(float(np.max(np.abs(c))), 1e-12)

    def objective(w):
        variance = float(w @ sigma @ w)
        return variance if aversion is None else 0.5 * aversion * variance - float(w @ expected)

    def gradient(w):
        return (2 * sigma @ w if aversion is None else aversion * sigma @ w - expected) / scale

    result = minimize(
        lambda w: objective(w) / scale,
        feasibility.x,
        jac=gradient,
        method="SLSQP",
        bounds=bounds,
        constraints={
            "type": "eq",
            "fun": lambda w: np.array(aeq) @ w - beq,
            "jac": lambda w: np.array(aeq),
        },
        options={"ftol": 1e-11, "maxiter": 1000},
    )
    w = result.x
    residual = float(np.max(np.abs(np.array(aeq) @ w - beq)))
    bound_error = max(max(lo - x, x - hi, 0) for x, (lo, hi) in zip(w, bounds, strict=True))
    if not result.success or residual > 1e-7 or bound_error > 1e-7 or not np.isfinite(w).all():
        raise ValueError(f"Allocation solver failed validation: {result.message}")
    return {
        "success": True,
        "message": str(result.message),
        "weights": w.tolist(),
        "cash_weight": float(w[-1]),
        "variance": float(w @ sigma @ w),
        "volatility": float(np.sqrt(max(0, w @ sigma @ w))),
        "expected_return": float(w @ expected),
        "objective": objective(w),
        "budget_residual": residual,
        "bound_violation": float(bound_error),
        "constraints": {
            "sum_weights": 1,
            "long_only": long_only,
            "risky_cap": cap,
            "minimum_cash": cash,
            "maximum_cash": cash_cap,
            "target_return": target,
        },
        "iterations": int(result.nit),
        "warnings": diag["warnings"]
        + [
            "Synthetic expectations are assumptions, not reliable forecasts",
            (
                "Cash is zero-return/zero-variance here: unconstrained minimum risk may be "
                "all cash"
            ),
            (
                "Weights are an allocation study; trading accounts are changed only by actual"
                " orders"
            ),
        ],
    }


def frontier(covariance, means, *, points=9, **kwargs):
    if type(points) is not int or not 2 <= points <= 30:
        raise ValueError("Frontier requires 2–30 target points")
    mu = vector(means)
    rows = []
    for target in np.linspace(0, max(0, float(mu.max())), points):
        try:
            rows.append(optimise(covariance, mu, target_return=float(target), **kwargs))
        except ValueError as exc:
            rows.append({"success": False, "target_return": float(target), "message": str(exc)})
    return rows
