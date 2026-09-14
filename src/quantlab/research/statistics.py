"""Session-level estimation; no treating correlated fills as independent observations."""

import math
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from scipy.stats import t

from quantlab.numerics import checked


def sample(values, *, minimum: int = 1) -> np.ndarray:
    items = list(values)
    if any(isinstance(x, (bool, str)) or x is None for x in items):
        raise ValueError("statistics require explicit finite numeric observations")
    result = np.asarray(items, dtype=float)
    if result.ndim != 1 or len(result) < minimum or not np.isfinite(result).all():
        raise ValueError(f"need at least {minimum} finite scalar observations")
    return result


@checked
def quantile(values, probability: float) -> float:
    if isinstance(probability, bool) or not 0 <= probability <= 1:
        raise ValueError("quantile probability must lie in [0, 1]")
    return float(np.quantile(sample(values), probability, method="linear"))


@dataclass(frozen=True, slots=True)
class Interval:
    low: float
    high: float
    confidence: float
    method: str


def _confidence(value):
    if isinstance(value, bool) or not 0 < value < 1:
        raise ValueError("confidence must lie strictly between zero and one")


@checked
def mean_interval(values, confidence: float = 0.95) -> Interval:
    _confidence(confidence)
    x = sample(values, minimum=2)
    mean = float(np.mean(x))
    se = float(np.std(x, ddof=1) / math.sqrt(len(x)))
    margin = float(t.ppf((1 + confidence) / 2, len(x) - 1)) * se
    return Interval(mean - margin, mean + margin, confidence, "Student t mean")


@dataclass(frozen=True, slots=True)
class Summary:
    requested: int
    available: int
    missing: int
    mean: float | None
    median: float | None
    variance: float | None
    standard_deviation: float | None
    standard_error: float | None
    p05: float | None
    p25: float | None
    p75: float | None
    p95: float | None
    minimum: float | None
    maximum: float | None
    mean_ci: Interval | None


@checked
def summarise(values, confidence: float = 0.95) -> Summary:
    _confidence(confidence)
    items = list(values)
    usable = [x for x in items if x is not None]
    if not usable:
        return Summary(len(items), 0, len(items), *([None] * 12))
    x = sample(usable)
    n = len(x)
    variance = float(np.var(x, ddof=1)) if n > 1 else None
    sd = math.sqrt(variance) if variance is not None else None
    return Summary(
        len(items),
        n,
        len(items) - n,
        float(np.mean(x)),
        float(np.median(x)),
        variance,
        sd,
        sd / math.sqrt(n) if sd is not None else None,
        *[quantile(x, p) for p in (0.05, 0.25, 0.75, 0.95)],
        float(np.min(x)),
        float(np.max(x)),
        mean_interval(x, confidence) if n > 1 else None,
    )


@dataclass(frozen=True, slots=True)
class BootstrapResult:
    estimate: float
    standard_error: float
    interval: Interval
    seed: int
    resamples: int
    observational_unit: str


@checked
def bootstrap(
    values,
    *,
    seed: int,
    resamples: int = 2000,
    confidence: float = 0.95,
    statistic: Callable = np.mean,
    unit: str = "complete independent session",
) -> BootstrapResult:
    """Percentile bootstrap; callable statistics consume a 1D resampled session vector."""
    _confidence(confidence)
    x = sample(values, minimum=2)
    if type(seed) is not int or seed < 0:
        raise ValueError("bootstrap seed must be a nonnegative integer")
    if type(resamples) is not int or resamples < 2:
        raise ValueError("bootstrap requires at least two resamples")
    rng = np.random.Generator(np.random.PCG64(seed))
    estimates = np.empty(resamples)
    # Bounded index batches; no resamples × n array retained for large experiments.
    batch = max(1, min(128, 1_000_000 // len(x)))
    for start in range(0, resamples, batch):
        indices = rng.integers(0, len(x), size=(min(batch, resamples - start), len(x)))
        draws = x[indices]
        if statistic is np.mean:
            estimates[start : start + len(draws)] = np.mean(draws, axis=1)
        else:
            estimates[start : start + len(draws)] = [statistic(row) for row in draws]
    sample(estimates)
    estimate = float(statistic(x))
    if not math.isfinite(estimate):
        raise ValueError("bootstrap statistic must be finite")
    alpha = (1 - confidence) / 2
    return BootstrapResult(
        estimate,
        float(np.std(estimates, ddof=1)),
        Interval(
            quantile(estimates, alpha),
            quantile(estimates, 1 - alpha),
            confidence,
            "percentile bootstrap",
        ),
        seed,
        resamples,
        unit,
    )


def paired_differences(first, second) -> np.ndarray:
    """second minus first; the engine aligns by run address, never by sorted outcome."""
    a, b = sample(first), sample(second)
    if len(a) != len(b):
        raise ValueError("paired samples must have the same length")
    return b - a


def paired_analysis(
    first, second, *, seed: int, resamples: int = 2000, practical_threshold: float = 0.05
) -> dict:
    if not math.isfinite(practical_threshold) or practical_threshold < 0:
        raise ValueError("practical threshold must be finite and nonnegative")
    differences = paired_differences(first, second)
    description = summarise(differences)
    test_statistic = p_value = standardised = None
    note = "Paired two-sided t test: H0 E[D]=0; H1 E[D] differs from zero."
    if len(differences) < 2 or description.standard_deviation == 0:
        note += " Test undefined: insufficient observations or zero estimated variance."
    else:
        test_statistic = description.mean / description.standard_error
        p_value = float(2 * t.sf(abs(test_statistic), len(differences) - 1))
        standardised = description.mean / description.standard_deviation
    return {
        "difference": "second minus first",
        "summary": description,
        "bootstrap": bootstrap(
            differences, seed=seed, resamples=resamples, unit="complete matched session pair"
        )
        if len(differences) > 1
        else None,
        "proportion_positive": float(np.mean(differences > 0)),
        "proportion_negative": float(np.mean(differences < 0)),
        "proportion_zero": float(np.mean(differences == 0)),
        "t_statistic": test_statistic,
        "degrees_of_freedom": len(differences) - 1,
        "p_value_two_sided": p_value,
        "standardised_paired_effect": standardised,
        "practical_threshold": practical_threshold,
        "mean_exceeds_practical_threshold": abs(description.mean) > practical_threshold,
        "note": note + " Statistical significance is not strategy validity or practical value.",
    }


def relationship(first, second) -> dict:
    a, b = list(first), list(second)
    if len(a) != len(b):
        raise ValueError("relationship inputs must align by session")
    pairs = [(x, y) for x, y in zip(a, b, strict=True) if x is not None and y is not None]
    result = {
        "available": len(pairs),
        "missing": len(a) - len(pairs),
        "covariance": None,
        "correlation": None,
    }
    if len(pairs) >= 2:
        x, y = (sample(v) for v in zip(*pairs, strict=True))
        result["covariance"] = float(np.cov(x, y, ddof=1)[0, 1])
        if np.std(x) and np.std(y):
            result["correlation"] = float(np.corrcoef(x, y)[0, 1])
    return result


def tail_risk(values, thresholds=(0.0, -0.25, -0.5, -1.0)) -> dict:
    x = sample(values)
    thresholds = sample(thresholds)
    tail_count = max(1, math.ceil(0.05 * len(x)))
    return {
        "probability_below": {str(float(a)): float(np.mean(x < a)) for a in thresholds},
        "worst": float(np.min(x)),
        "p05": quantile(x, 0.05),
        "worst_five_percent_mean": float(np.mean(np.sort(x)[:tail_count])),
        "tail_count": tail_count,
        "convention": "strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes",
    }
