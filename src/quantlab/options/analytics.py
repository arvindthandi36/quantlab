"""Server-side curve data and explicitly local Greek shock approximations."""

import math
from dataclasses import replace

from quantlab.options.models import number
from quantlab.options.pricing import greeks, payoff, price


def curves(kind, inputs, *, points=61):
    if type(points) is not int or not 5 <= points <= 201:
        raise ValueError("curve points must be 5–201")
    center = inputs.strike
    result = []
    for i in range(points):
        spot = center * (0.5 + i / (points - 1))
        x = replace(inputs, spot=spot)
        g = greeks(kind, x)
        result.append(
            {
                "spot": spot,
                "payoff": payoff(kind, spot, inputs.strike),
                "value": price(kind, x),
                "delta": g.delta,
                "gamma": g.gamma,
            }
        )
    return result


def shock(kind, inputs, *, spot_change=0, volatility_change=0, elapsed_days=0, rate_change=0):
    ds = number(spot_change, "spot change GBP")
    dv = number(volatility_change, "volatility change (absolute decimal)")
    dt = number(elapsed_days, "elapsed ACT/365 days", 0, inputs.time_years * 365) / 365
    dr = number(rate_change, "rate change (absolute decimal)")
    shocked = replace(
        inputs,
        spot=inputs.spot + ds,
        volatility=inputs.volatility + dv,
        time_years=max(0, inputs.time_years - dt),
        rate=inputs.rate + dr,
    )
    g = greeks(kind, inputs)
    old, new = price(kind, inputs), price(kind, shocked)
    first = None if g.delta is None else g.delta * ds
    approximation = (
        None
        if any(getattr(g, k) is None for k in ("delta", "gamma", "vega", "theta", "rho"))
        else g.delta * ds + 0.5 * g.gamma * ds**2 + g.vega * dv + g.theta * dt + g.rho * dr
    )
    return {
        "original": old,
        "repriced": new,
        "exact_change": new - old,
        "delta_only_change": first,
        "greek_change": approximation,
        "approximation_error": None if approximation is None else new - old - approximation,
        "spot_change": ds,
        "volatility_change": dv,
        "elapsed_days": dt * 365,
        "rate_change": dr,
        "unit": "GBP per underlying unit",
        "assumption": "Local fixed-volatility partial derivatives; cross/higher terms omitted",
    }


def realised_volatility(spots, dt_years):
    if len(spots) < 2 or dt_years <= 0:
        return None
    returns = [math.log(b / a) for a, b in zip(spots, spots[1:], strict=False)]
    # Quadratic variation, not demeaned sample SD; disclose finite-sample drift contribution.
    return math.sqrt(sum(r * r for r in returns) / (len(returns) * dt_years))
