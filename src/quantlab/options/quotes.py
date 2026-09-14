"""Finite synthetic dealer quotes. This is deliberately not an option limit book."""

import math
from dataclasses import dataclass
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal, localcontext
from fractions import Fraction

from quantlab.options.iv import IVResult, implied_volatility
from quantlab.options.models import PricingInputs, exact, number
from quantlab.options.pricing import bounds, greeks, payoff, price


def quantize(value, places=6, rounding=None):
    value = exact(value)
    with localcontext() as ctx:
        ctx.prec = 48
        decimal = Decimal(value.numerator) / Decimal(value.denominator)
        return Fraction(decimal.quantize(Decimal(1).scaleb(-places), rounding=rounding))


def smile_volatility(spot, strike, base, skew=-0.15, curvature=0.25):
    number(base, "base annual decimal volatility", 0.001, 3)
    number(skew, "synthetic skew", -1, 1)
    number(curvature, "synthetic smile curvature", 0, 2)
    m = math.log(strike / spot)
    return min(3.0, max(0.001, base * (1 + skew * m + curvature * m * m)))


@dataclass
class OptionQuote:
    contract: object
    revision: int
    model_value: float
    volatility_input: float
    bid: Fraction
    ask: Fraction
    bid_size: int
    ask_size: int
    inputs: PricingInputs

    @property
    def midpoint(self):
        return (self.bid + self.ask) / 2

    def public(self, elapsed_years=0):
        intrinsic = payoff(self.contract.option_type, self.inputs.spot, self.inputs.strike)
        _, upper = bounds(self.contract.option_type, self.inputs)
        iv = (
            IVResult(
                None,
                False,
                "rounded quote at upper bound; finite IV undefined",
                "boundary check",
                0,
                0.0,
                (0.0, 5.0),
                0,
                0,
            )
            if float(self.midpoint) == upper
            else implied_volatility(
                self.contract.option_type, self.inputs, float(self.midpoint)
            )
        )
        return {
            **self.contract.public(elapsed_years),
            "revision": self.revision,
            "model_value": self.model_value,
            "volatility_input": self.volatility_input,
            "bid": float(self.bid),
            "ask": float(self.ask),
            "midpoint": float(self.midpoint),
            "intrinsic": intrinsic,
            "time_value": float(self.midpoint) - intrinsic,
            "moneyness": (
                "ATM"
                if self.inputs.spot == self.inputs.strike
                else "ITM"
                if intrinsic > 0
                else "OTM"
            ),
            "bid_size": self.bid_size,
            "ask_size": self.ask_size,
            "iv": iv.public(),
            "greeks": greeks(self.contract.option_type, self.inputs).public(),
            "contract_greeks": greeks(self.contract.option_type, self.inputs)
            .scaled(self.contract.multiplier)
            .public(),
            "mechanism": "Finite synthetic dealer quote; IOC remainder cancels",
        }


def make_quote(
    contract,
    spot,
    elapsed_years,
    base_volatility,
    rate,
    *,
    revision,
    size=20,
    half_spread=0.015,
    skew=-0.15,
    curvature=0.25,
):
    if contract.remaining(elapsed_years) == 0:
        raise ValueError("Expired options have settlement payoff, not live quotes")
    sigma = smile_volatility(spot, float(contract.strike_gbp), base_volatility, skew, curvature)
    x = PricingInputs.for_contract(contract, spot, elapsed_years, sigma, rate)
    model = price(contract.option_type, x)
    lower, upper = bounds(contract.option_type, x)
    # Outward quote rounding, clipped to feasible bounds. No hidden quote noise.
    floor = quantize(lower, rounding=ROUND_CEILING)
    ceiling = quantize(upper, rounding=ROUND_FLOOR)
    if floor >= ceiling:
        raise ValueError("Contract's feasible range is below quote precision")
    bid = max(floor, quantize(max(lower, model - half_spread), rounding=ROUND_FLOOR))
    ask = min(ceiling, quantize(min(upper, model + half_spread), rounding=ROUND_CEILING))
    if bid > ask:
        raise ArithmeticError("Synthetic option quotes crossed")
    return OptionQuote(contract, revision, model, sigma, bid, ask, size, size, x)
