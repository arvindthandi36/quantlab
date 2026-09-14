"""Stable OLS and explicitly causal model vintages; no stationarity p-values."""

import math
from dataclasses import asdict, dataclass

import numpy as np

from quantlab.numerics import checked


def observations(values, *, minimum=3):
    a = np.asarray(values, dtype=float)
    if a.ndim != 1 or len(a) < minimum or not np.isfinite(a).all():
        raise ValueError(
            f"Need at least {minimum} finite synchronized observations; missing rejected"
        )
    return a


@dataclass(frozen=True)
class Fit:
    alpha: float
    beta: float
    r_squared: float | None
    alpha_se: float
    beta_se: float
    n: int
    start: int = 0
    end: int = 0
    warnings: tuple = ()

    def residual(self, x, y):
        return np.asarray(y) - self.alpha - self.beta * np.asarray(x)

    def public(self):
        return asdict(self)


@checked
def ols(x, y, *, start=0, end=None):
    x, y = observations(x), observations(y)
    if x.shape != y.shape:
        raise ValueError("Synchronized X and Y lengths must agree")
    centre = float(x.mean())
    scale = float(np.std(x))
    if scale <= max(1e-10, abs(centre) * 1e-10):
        raise ValueError("Constant or effectively constant predictor: hedge ratio unidentified")
    design = np.column_stack((np.ones(len(x)), (x - centre) / scale))
    coefficients, _, rank, singular = np.linalg.lstsq(design, y, rcond=1e-12)
    if rank != 2 or singular[-1] / singular[0] < 1e-10:
        raise ValueError("Rank-deficient or ill-conditioned regression")
    beta = float(coefficients[1] / scale)
    alpha = float(coefficients[0] - beta * centre)
    e = y - (alpha + beta * x)
    sse = float(e @ e)
    sxx = float((x - centre) @ (x - centre))
    syy = float((y - y.mean()) @ (y - y.mean()))
    if not all(math.isfinite(v) for v in (alpha, beta, sse, sxx, syy)):
        raise ValueError("OLS overflow: no estimate returned; rescale observations")
    variance = sse / (len(x) - 2)
    notes = ["Conventional SE assumes IID homoskedastic errors; no price-series inference"]
    if float(np.max(np.abs(e))) > 3 * max(float(np.std(e)), 1e-10):
        notes.append("Large residual: outlier sensitivity; inspect observations")
    if syy <= 1e-20:
        notes.append("Constant response: R² undefined")
    return Fit(
        alpha,
        beta,
        None if syy <= 1e-20 else 1 - sse / syy,
        math.sqrt(variance * (1 / len(x) + centre**2 / sxx)),
        math.sqrt(variance / sxx),
        len(x),
        start,
        start + len(x) if end is None else end,
        tuple(notes),
    )


@checked
def correlation(x, y):
    x, y = observations(x, minimum=2), observations(y, minimum=2)
    if x.shape != y.shape:
        raise ValueError("Correlation lengths differ")
    if min(float(np.std(x)), float(np.std(y))) <= 1e-12:
        return None
    return float(np.corrcoef(x, y)[0, 1])


@checked
def zscore(current, past, *, window):
    if type(window) is not int or window < 3:
        raise ValueError("Z window must be at least 3")
    a = np.asarray(past, dtype=float)
    if len(a) < window:
        return dict(
            z=None, mean=None, sd=None, n=len(a), reason="insufficient past observations"
        )
    a = observations(a[-window:])
    if not math.isfinite(current):
        raise ValueError("Current spread is nonfinite")
    mean, sd = float(a.mean()), float(a.std(ddof=1))
    tolerance = max(1e-9, abs(mean) * 1e-10)
    return dict(
        z=(current - mean) / sd if sd > tolerance else None,
        mean=mean,
        sd=sd,
        n=window,
        reason=None if sd > tolerance else "effectively zero spread volatility",
    )


@checked
def diagnostics(values):
    a = observations(values, minimum=6)
    phi = half_life = None
    try:
        phi = ols(a[:-1], a[1:]).beta
        if 0 < phi < 1:
            half_life = -math.log(2) / math.log(phi)
    except ValueError:
        pass
    mid = len(a) // 2
    counts, edges = np.histogram(a, bins=min(16, max(4, len(a) // 8)))
    return dict(
        mean=float(a.mean()),
        sd=float(a.std(ddof=1)),
        autocorrelation=correlation(a[:-1], a[1:]),
        phi=phi,
        half_life=half_life,
        first_mean=float(a[:mid].mean()),
        second_mean=float(a[mid:].mean()),
        first_sd=float(a[:mid].std(ddof=1)),
        second_sd=float(a[mid:].std(ddof=1)),
        histogram=dict(counts=counts.tolist(), edges=edges.tolist()),
        label="Descriptive AR(1), not ADF, not a unit-root or cointegration test",
        warning="Half-life is conditional on 0 < fitted phi < 1, not a convergence deadline",
    )


class CausalModel:
    def __init__(self, *, window=80, z_window=40, mode="fixed", block=20, origin=None):
        if any(type(n) is not int or not 6 <= n <= 2000 for n in (window, z_window, block)):
            raise ValueError("Model windows/block require whole numbers 6–2000")
        if mode not in ("fixed", "rolling", "walk_forward"):
            raise ValueError("Unknown estimation schedule")
        self.window, self.z_window, self.mode, self.block = window, z_window, mode, block
        self.origin = window if origin is None else origin
        if type(self.origin) is not int or self.origin < window:
            raise ValueError("Fit origin must allow the complete past window")
        self.fit = None

    def at(self, published, t):
        # Prefix slicing happens BEFORE validation or fitting: future values are unobserved.
        if type(t) is not int or t < 0 or t >= len(published):
            raise ValueError("Observation index outside published history")
        prefix = np.asarray(published[: t + 1], dtype=float)
        if prefix.ndim != 2 or prefix.shape[1] != 2 or not np.isfinite(prefix).all():
            raise ValueError("Model requires finite public X,Y pairs")
        if t < max(self.origin, self.z_window):
            return {
                "available": False,
                "reason": "collecting past training and z windows",
                "t": t,
            }
        if self.mode == "fixed":
            end = self.origin
        elif self.mode == "walk_forward":
            end = self.origin + (t - self.origin) // self.block * self.block
        else:
            end = t
        start = end - self.window
        if self.fit is None or (self.fit.start, self.fit.end) != (start, end):
            self.fit = ols(prefix[start:end, 0], prefix[start:end, 1], start=start, end=end)
        return self.with_fit(prefix, t, self.fit)

    def with_fit(self, prefix, t, fit):
        if fit.end > t:
            raise ValueError("Future model vintage cannot produce this signal")
        a = np.asarray(prefix[: t + 1], dtype=float)
        past = a[max(0, t - self.z_window) : t]
        spread = float(fit.residual(*a[t]))
        past_spreads = fit.residual(past[:, 0], past[:, 1])
        z = zscore(spread, past_spreads, window=self.z_window)
        prices = a[max(0, t - self.window) : t + 1]
        returns = np.diff(prices, axis=0) / prices[:-1]
        return dict(
            available=True,
            t=t,
            fit=fit.public(),
            spread=spread,
            price_difference=float(a[t, 1] - a[t, 0]),
            **z,
            price_correlation=correlation(prices[:, 0], prices[:, 1]),
            return_correlation=correlation(returns[:, 0], returns[:, 1]),
            diagnostics=diagnostics(past_spreads),
            normalization_start=max(0, t - self.z_window),
            normalization_end=t,
        )
