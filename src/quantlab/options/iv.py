"""Feasibility checks, safeguarded Newton and a bisection fallback with diagnostics."""

from dataclasses import asdict, dataclass, replace

from quantlab.options.models import number
from quantlab.options.pricing import bounds, greeks, price


@dataclass(frozen=True)
class IVResult:
    volatility: float | None
    converged: bool
    status: str
    method: str
    iterations: int
    residual: float
    bracket: tuple[float, float]
    newton_steps: int
    bisection_steps: int

    def public(self):
        return asdict(self)


def implied_volatility(
    kind,
    inputs,
    market_price,
    *,
    initial=0.2,
    max_iterations=100,
    price_tolerance=1e-10,
    vol_tolerance=1e-8,
    newton_iterations=8,
):
    target = number(market_price, "option market price GBP per underlying unit", 0)
    initial = number(initial, "initial volatility (annual decimal)", 0, 5)
    number(price_tolerance, "pricing tolerance", 1e-15, 1e-3)
    number(vol_tolerance, "volatility tolerance", 1e-12, 1e-2)
    if type(max_iterations) is not int or not 1 <= max_iterations <= 1000:
        raise ValueError("iteration limit must be an integer in 1–1000")
    if type(newton_iterations) is not int or not 0 <= newton_iterations <= max_iterations:
        raise ValueError("Newton budget must fit the total iteration budget")
    lower, upper = bounds(kind, inputs)
    if inputs.time_years == 0:
        raise ValueError("Implied volatility is undefined at expiry")
    if target < lower or target >= upper:
        raise ValueError(
            f"Option price outside finite-IV feasibility bounds [{lower}, {upper})"
        )
    if target - lower <= max(price_tolerance, upper * 1e-14):
        return IVResult(
            None,
            False,
            "price indistinguishable from zero-volatility bound",
            "boundary check",
            0,
            lower - target,
            (0, 0),
            0,
            0,
        )
    lo, hi = 0.0, 0.5
    while price(kind, replace(inputs, volatility=hi)) < target and hi < 5:
        hi = min(5.0, hi * 2)
    if price(kind, replace(inputs, volatility=hi)) < target:
        return IVResult(
            None,
            False,
            "no bracket within supported volatility range [0,5]",
            "bracket search",
            0,
            price(kind, replace(inputs, volatility=hi)) - target,
            (lo, hi),
            0,
            0,
        )
    sigma = initial if lo < initial < hi else (lo + hi) / 2
    n_newton = n_bisect = 0
    residual = float("inf")
    for iteration in range(1, max_iterations + 1):
        trial = replace(inputs, volatility=sigma)
        residual = price(kind, trial) - target
        vega = greeks(kind, trial).vega or 0.0
        # Small price error is insufficient if vega makes the inferred IV unstable.
        if (
            abs(residual) <= price_tolerance
            and vega > 1e-10
            and (abs(residual) / vega <= vol_tolerance or hi - lo <= vol_tolerance)
        ):
            method = (
                "Newton"
                if n_bisect == 0
                else ("bisection" if n_newton == 0 else "Newton + bisection")
            )
            return IVResult(
                sigma,
                True,
                "converged",
                method,
                iteration,
                residual,
                (lo, hi),
                n_newton,
                n_bisect,
            )
        if residual > 0:
            hi = sigma
        else:
            lo = sigma
        candidate = sigma - residual / vega if vega > 1e-10 else None
        if (
            iteration <= newton_iterations
            and candidate is not None
            and lo < candidate < hi
            and abs(candidate - sigma) < 0.75 * (hi - lo)
        ):
            sigma = candidate
            n_newton += 1
        else:
            sigma = (lo + hi) / 2
            n_bisect += 1
    return IVResult(
        None,
        False,
        "iteration limit; no reliable IV returned",
        "Newton + bisection" if n_newton else "bisection",
        max_iterations,
        residual,
        (lo, hi),
        n_newton,
        n_bisect,
    )
