"""Loss-positive VaR/ES with an explicit discrete tail-mass convention."""

import math
from statistics import NormalDist

import numpy as np

from quantlab.numerics import checked
from quantlab.options.models import number
from quantlab.risk.covariance import variance_decomposition, vector


def confidence(value):
    return number(value, "confidence", 0.5, 0.9999)


@checked
def empirical_risk(losses, alpha=0.95, *, full=False):
    alpha = confidence(alpha)
    a = np.asarray(losses, dtype=float)
    if a.ndim != 1 or len(a) < 2 or not np.isfinite(a).all():
        raise ValueError("At least two finite loss observations required")
    ordered = np.sort(a)
    # Round only floating-point integer artefacts, not the quantile itself.
    boundary = alpha * len(a)
    if abs(boundary - round(boundary)) < 1e-10:
        boundary = float(round(boundary))
    index = math.ceil(boundary) - 1
    var = float(ordered[index])
    mass = len(a) - boundary
    whole = int(math.floor(mass))
    fraction = mass - whole
    total = float(ordered[-whole:].sum()) if whole else 0.0
    if fraction:
        total += fraction * float(ordered[-whole - 1])
    es = total / mass
    if es + 1e-10 * max(1, abs(var)) < var:
        raise ArithmeticError("Expected Shortfall is less severe than VaR")
    counts, edges = np.histogram(a, bins=min(30, max(1, int(math.sqrt(len(a))))))
    tail = {
        "var": var,
        "es": es,
        "confidence": alpha,
        "n": len(a),
        "tail_mass": mass,
        "whole_tail_observations": whole,
        "boundary_weight": fraction,
        "worst": ordered[-min(8, len(a)) :][::-1].tolist(),
        "histogram": {"edges": edges.tolist(), "counts": counts.tolist()},
        "mean_loss": float(a.mean()),
        "loss_sd": float(a.std(ddof=1)),
        "warnings": (
            ["Fewer than 20 effective tail observations; tail estimate is noisy"]
            if mass < 20
            else []
        ),
        "convention": (
            "Inverse empirical CDF VaR; ES averages exact worst 1-alpha mass "
            "with fractional boundary atom"
        ),
        "interpretation": "Model/data loss threshold, never a maximum possible loss",
    }
    if full:
        tail["losses"] = a.tolist()
    return tail


@checked
def parametric_risk(exposures, covariance, means=None, *, alpha=0.95, days=1, options=False):
    alpha = confidence(alpha)
    if type(days) is not int or not 1 <= days <= 252:
        raise ValueError("Horizon requires 1–252 whole calendar model days")
    w = vector(exposures)
    mu = vector(means if means is not None else np.zeros(len(w)))
    if len(mu) != len(w):
        raise ValueError("Mean vector dimension differs")
    d = variance_decomposition(w, covariance)
    sd = d["volatility"] * math.sqrt(days)
    mean_loss = -float(w @ mu) * days
    z = NormalDist().inv_cdf(alpha)
    var = mean_loss + z * sd
    es = mean_loss + math.exp(-z * z / 2) / math.sqrt(2 * math.pi) / (1 - alpha) * sd
    return {
        "var": var,
        "es": es,
        "confidence": alpha,
        "days": days,
        "mean_loss": mean_loss,
        "loss_sd": sd,
        "decomposition": d,
        "method": "Delta-normal approximation" if options else "Linear-normal approximation",
        "warnings": d["warnings"]
        + [
            "IID one-day arithmetic moments scaled only for linear P&L; normal tails assumed",
            "Options curvature, volatility changes, decay and cash carry are omitted"
            if options
            else "Changing volatility, correlation, costs and fat tails are omitted",
        ],
        "interpretation": "VaR is a model loss threshold, never maximum loss",
    }
