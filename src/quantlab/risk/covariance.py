"""Validated sample covariance and transparent quadratic risk decomposition."""

import math

import numpy as np

from quantlab.numerics import checked


def vector(values, name="vector"):
    try:
        a = np.asarray(values, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if a.ndim != 1 or not 1 <= len(a) <= 30 or not np.isfinite(a).all():
        raise ValueError(f"{name} requires 1–30 finite numbers")
    return a


@checked
def validate_covariance(values):
    a = np.asarray(values, dtype=float)
    if a.ndim != 2 or a.shape[0] != a.shape[1] or not 1 <= len(a) <= 30:
        raise ValueError("Covariance must be a square 1–30 factor matrix")
    if not np.isfinite(a).all():
        raise ValueError("Covariance contains missing or nonfinite values")
    scale = max(float(np.max(np.abs(a))), 1e-300)
    tol = scale * 1e-10
    if np.max(np.abs(a - a.T)) > tol:
        raise ValueError("Covariance must be symmetric; no automatic repair")
    # Only average roundoff-level asymmetry, explicitly disclosed.
    notes = []
    if not np.array_equal(a, a.T):
        notes.append("Roundoff-level asymmetry averaged within relative tolerance 1e-10")
    a = a / 2 + a.T / 2
    if (np.diag(a) < 0).any():
        raise ValueError("Variances must be nonnegative")
    eigen = np.linalg.eigvalsh(a)
    if eigen[0] < -tol:
        raise ValueError("Covariance is not positive semidefinite")
    if eigen[0] <= scale * 1e-8:
        notes.append(
            "Singular or near-singular covariance: allocations/contributions may be unstable"
        )
    return a, {
        "eigenvalues": eigen.tolist(),
        "warnings": notes,
        "tolerance": tol,
        "regularisation": "none",
    }


@checked
def estimate_covariance(returns, *, ddof=1, missing="reject"):
    if type(ddof) is not int or ddof not in (0, 1):
        raise ValueError("Use ddof=1 for sample or ddof=0 for population covariance")
    if missing not in ("reject", "listwise"):
        raise ValueError("Missing policy must be reject or explicit listwise deletion")
    a = np.asarray(returns, dtype=float)
    if a.ndim != 2 or not 1 <= a.shape[1] <= 30 or len(a) > 100_000:
        raise ValueError("Returns require observations by factors, at most 100,000 rows")
    good = np.isfinite(a).all(axis=1)
    removed = int((~good).sum())
    if removed and missing == "reject":
        raise ValueError(
            "Missing/nonfinite synchronised returns; choose explicit listwise deletion"
        )
    a = a[good]
    if len(a) < max(2, ddof + 1):
        raise ValueError("Insufficient complete return observations")
    centred = a - a.mean(axis=0)
    cov, diag = validate_covariance(centred.T @ centred / (len(a) - ddof))
    return {
        "covariance": cov.tolist(),
        "mean": a.mean(axis=0).tolist(),
        "n": len(a),
        "dropped": removed,
        "ddof": ddof,
        "convention": "sample N-1" if ddof else "population N",
        **diag,
    }


@checked
def correlation(covariance):
    a, _ = validate_covariance(covariance)
    sd = np.sqrt(np.diag(a))
    return [
        [float(a[i, j] / (sd[i] * sd[j])) if sd[i] * sd[j] else None for j in range(len(a))]
        for i in range(len(a))
    ]


@checked
def covariance_from_volatility(volatility, correlations):
    v = vector(volatility, "one-day volatility")
    c, _ = validate_covariance(correlations)
    if len(v) != len(c) or (v < 0).any() or not np.allclose(np.diag(c), 1, atol=1e-12):
        raise ValueError(
            "Correlation needs unit diagonal and matching nonnegative volatilities"
        )
    if np.max(np.abs(c)) > 1 + 1e-12:
        raise ValueError("Correlation must lie in [-1,1]")
    return np.outer(v, v) * c


@checked
def variance_decomposition(weights, covariance):
    w = vector(weights, "weights / GBP delta exposure")
    c, info = validate_covariance(covariance)
    if len(w) != len(c):
        raise ValueError("Weights and covariance dimensions differ")
    diagonal = w * w * np.diag(c)
    cross = [
        {"i": i, "j": j, "value": float(2 * w[i] * w[j] * c[i, j])}
        for i in range(len(w))
        for j in range(i + 1, len(w))
    ]
    variance = float(w @ c @ w)
    tolerance = float(np.abs(w) @ np.abs(c) @ np.abs(w)) * 1e-10
    if variance < -tolerance:
        raise ArithmeticError("Negative portfolio variance beyond roundoff tolerance")
    variance = max(0.0, variance)
    vol = math.sqrt(variance)
    stable = variance > max(tolerance, 1e-300)
    marginal = c @ w / vol if stable else None
    return {
        "variance": variance,
        "volatility": vol,
        "diagonal_terms": diagonal.tolist(),
        "cross_terms": cross,
        "diagonal_total": float(diagonal.sum()),
        "cross_total": sum(x["value"] for x in cross),
        "marginal_volatility": marginal.tolist() if stable else None,
        "component_volatility": (w * marginal).tolist() if stable else None,
        "warnings": info["warnings"]
        + (
            []
            if stable
            else ["Zero/near-cancelled variance: marginal and component volatility undefined"]
        ),
    }
