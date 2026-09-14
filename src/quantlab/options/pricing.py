"""Black–Scholes–Merton; OTM-tail evaluation then parity avoids ITM cancellation."""

import math
from dataclasses import asdict, dataclass, replace

from quantlab.options.models import OptionType, PricingInputs, number


def cdf(x):
    return 0.5 * math.erfc(-x / math.sqrt(2))


def density(x):
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def payoff(option_type, spot, strike):
    spot = number(spot, "settlement spot", 0, 1e12)
    strike = number(strike, "strike", 1e-8, 1e12)
    return max(0.0, (spot - strike) * (1 if OptionType(option_type) == OptionType.CALL else -1))


def bounds(option_type, inputs):
    kind = OptionType(option_type)
    a = inputs.spot * math.exp(-inputs.dividend_yield * inputs.time_years)
    b = inputs.strike * math.exp(-inputs.rate * inputs.time_years)
    return (max(a - b, 0.0), a) if kind == OptionType.CALL else (max(b - a, 0.0), b)


def _terms(x):
    t, sigma = x.time_years, x.volatility
    a, b = x.spot * math.exp(-x.dividend_yield * t), x.strike * math.exp(-x.rate * t)
    w = sigma * math.sqrt(t)
    log_forward = math.log(x.spot / x.strike) + (x.rate - x.dividend_yield) * t
    if w == 0:
        raise ValueError("Time × volatility is below representable pricing precision")
    d1 = log_forward / w + w / 2
    return a, b, d1, d1 - w


def _price_kernel(kind, spot, strike, t, sigma, rate, dividend, *, xp, normal, choose):
    """One BSM algorithm; scalar math and array ufuncs are numerical backends."""
    sign = 1 if kind == OptionType.CALL else -1
    if t == 0:
        return choose(sign * (spot - strike) > 0, sign * (spot - strike), 0.0)
    a, b = spot * math.exp(-dividend * t), strike * math.exp(-rate * t)
    intrinsic = sign * (a - b)
    lower = choose(intrinsic > 0, intrinsic, 0.0)
    if sigma == 0:
        return lower
    w = sigma * math.sqrt(t)
    if w == 0:
        raise ValueError("Time × volatility is below representable pricing precision")
    d1 = (xp.log(spot / strike) + (rate - dividend) * t) / w + w / 2
    d2 = d1 - w
    otm = choose(a <= b, a * normal(d1) - b * normal(d2), b * normal(-d2) - a * normal(-d1))
    tolerance = 1e-13 * choose(a > b, a, b)
    invalid = otm < -tolerance
    if bool(invalid.any()) if hasattr(invalid, "any") else invalid:
        raise ArithmeticError("Black–Scholes tail calculation lost numerical precision")
    return lower + choose(otm > 0, otm, 0.0)


def price(option_type, inputs: PricingInputs):
    return _price_kernel(
        OptionType(option_type),
        inputs.spot,
        inputs.strike,
        inputs.time_years,
        inputs.volatility,
        inputs.rate,
        inputs.dividend_yield,
        xp=math,
        normal=cdf,
        choose=lambda condition, yes, no: yes if condition else no,
    )


def price_many(option_type, inputs: PricingInputs, spots):
    """Same price kernel over finite GBP spots, for scenario revaluation."""
    import numpy as np
    from scipy.special import ndtr

    values = np.asarray(spots, dtype=float)
    if not np.isfinite(values).all() or (values < 1e-8).any() or (values > 1e12).any():
        raise ValueError("Scenario spots must be finite GBP prices in [1e-8, 1e12]")
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        return _price_kernel(
            OptionType(option_type),
            values,
            inputs.strike,
            inputs.time_years,
            inputs.volatility,
            inputs.rate,
            inputs.dividend_yield,
            xp=np,
            normal=ndtr,
            choose=np.where,
        )


@dataclass(frozen=True)
class Greeks:
    delta: float | None
    gamma: float | None
    vega: float | None
    theta: float | None
    rho: float | None
    status: str = "analytic; volatility held fixed"

    def scaled(self, factor):
        return Greeks(
            *(
                None if getattr(self, k) is None else getattr(self, k) * factor
                for k in ("delta", "gamma", "vega", "theta", "rho")
            ),
            self.status,
        )

    def public(self):
        return asdict(self) | {
            "vega_per_vol_point": None if self.vega is None else self.vega / 100,
            "theta_per_day": None if self.theta is None else self.theta / 365,
            "rho_per_rate_point": None if self.rho is None else self.rho / 100,
        }


def greeks(option_type, x: PricingInputs):
    kind = OptionType(option_type)
    sign = 1 if kind == OptionType.CALL else -1
    t, sigma, s, k, r, q = (
        x.time_years,
        x.volatility,
        x.spot,
        x.strike,
        x.rate,
        x.dividend_yield,
    )
    if t == 0:
        delta = None if s == k else (float(sign) if sign * (s - k) > 0 else 0.0)
        return Greeks(
            delta,
            None if s == k else 0.0,
            0.0,
            None,
            0.0,
            "expired payoff; theta undefined, strike kink not differentiable",
        )
    a, b = s * math.exp(-q * t), k * math.exp(-r * t)
    if sigma == 0:
        if a == b:
            return Greeks(
                None,
                None,
                a * math.sqrt(t) * density(0),
                None,
                None,
                "zero-volatility forward kink; vega is right derivative",
            )
        itm = sign * (a - b) > 0
        return Greeks(
            sign * math.exp(-q * t) if itm else 0.0,
            0.0,
            0.0,
            sign * (q * a - r * b) if itm else 0.0,
            sign * t * b if itm else 0.0,
            "zero volatility; away from forward kink",
        )
    a, b, d1, d2 = _terms(x)
    nd1, nd2, phi = cdf(sign * d1), cdf(sign * d2), density(d1)
    return Greeks(
        sign * math.exp(-q * t) * nd1,
        math.exp(-q * t) * phi / (s * sigma * math.sqrt(t)),
        a * phi * math.sqrt(t),
        -a * phi * sigma / (2 * math.sqrt(t)) + sign * q * a * nd1 - sign * r * b * nd2,
        sign * t * b * nd2,
    )


def parity_residual(call, put, x):
    return (
        call
        - put
        - (
            x.spot * math.exp(-x.dividend_yield * x.time_years)
            - x.strike * math.exp(-x.rate * x.time_years)
        )
    )


def finite_differences(kind, x):
    if x.time_years <= 0 or x.volatility <= 0:
        raise ValueError("Finite-difference validation requires positive time and volatility")

    def first(key, h):
        value = getattr(x, key)
        return (
            price(kind, replace(x, **{key: value + h}))
            - price(kind, replace(x, **{key: value - h}))
        ) / (2 * h)

    h = x.spot * 1e-4
    gamma = (
        price(kind, replace(x, spot=x.spot + h))
        - 2 * price(kind, x)
        + price(kind, replace(x, spot=x.spot - h))
    ) / h**2
    return Greeks(
        first("spot", h),
        gamma,
        first("volatility", min(1e-5, x.volatility / 4)),
        -first("time_years", min(1e-5, x.time_years / 4)),
        first("rate", 1e-5),
        "central finite differences",
    )
