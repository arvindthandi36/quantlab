"""Full model changes, Greek attribution, explicit non-accounting stress results."""

import math
from dataclasses import asdict, dataclass, replace

from quantlab.options.models import number
from quantlab.options.pricing import price


@dataclass(frozen=True)
class Scenario:
    name: str = "CUSTOM"
    stock_return: float = 0
    volatility_change: float = 0
    rate_change: float = 0
    days: float = 0
    liquidation_bps: float = 0
    correlation: float | None = None

    def __post_init__(self):
        if not isinstance(self.name, str) or not 1 <= len(self.name) <= 80:
            raise ValueError("Scenario name requires 1–80 characters")
        for key, lo, hi in (
            ("stock_return", -0.95, 3),
            ("volatility_change", -3, 3),
            ("rate_change", -0.5, 0.5),
            ("days", 0, 252),
            ("liquidation_bps", 0, 10000),
        ):
            object.__setattr__(self, key, number(getattr(self, key), key, lo, hi))
        if self.correlation is not None:
            object.__setattr__(
                self, "correlation", number(self.correlation, "correlation", -0.5, 1)
            )


NAMED = {
    s.name: s
    for s in (
        Scenario("NORMAL", days=1),
        Scenario("EQUITY SELL-OFF", stock_return=-0.10),
        Scenario("VOLATILITY SPIKE", volatility_change=0.20),
        Scenario("CORRELATION BREAKDOWN", correlation=0.9),
        Scenario("LIQUIDITY SHOCK", liquidation_bps=100),
        Scenario(
            "COMBINED STRESS",
            stock_return=-0.10,
            volatility_change=0.20,
            rate_change=0.005,
            liquidation_bps=100,
            correlation=0.9,
        ),
        Scenario("EQUITY -5%", stock_return=-0.05),
        Scenario("VOL +5 POINTS", volatility_change=0.05),
    )
}


def validate_horizon(portfolio, days):
    earliest = min(
        (p.years * 365 for p in portfolio.positions if p.kind != "stock"), default=252
    )
    if days > earliest + 1e-10:
        raise ValueError(
            "Horizon exceeds first live expiry; terminal-only risk cannot recover earlier"
            " settlement"
        )


def scenario_pnl(portfolio, scenario, *, factor_returns=None, cash_rate=0):
    validate_horizon(portfolio, scenario.days)
    dt = scenario.days / 365
    cash_rate = number(cash_rate, "cash risk rate", -1, 1)
    rows = []
    totals = dict(
        delta=0.0, gamma=0.0, vega=0.0, theta=0.0, rho=0.0, cash_carry=0.0, liquidity=0.0
    )
    for p in portfolio.positions:
        ret = (factor_returns or {}).get(p.underlying, scenario.stock_return)
        number(ret, "factor return", -0.999999, 10)
        ds = p.spot * ret
        g = p.sensitivities()
        parts = {
            "delta": g["delta"] * ds,
            "gamma": 0.5 * g["gamma"] * ds * ds,
            "vega": g["vega"] * scenario.volatility_change,
            "theta": g["theta"] * dt,
            "rho": g["rho"] * scenario.rate_change,
        }
        if p.kind == "stock":
            full = p.quantity * ds
        else:
            x = p.inputs()
            after = replace(
                x,
                spot=x.spot + ds,
                volatility=x.volatility + scenario.volatility_change,
                rate=x.rate + scenario.rate_change,
                time_years=max(0, x.time_years - dt),
            )
            full = p.units * (price(p.kind, after) - price(p.kind, x))
        liquidity = -abs(p.value) * scenario.liquidation_bps / 10000
        parts["liquidity"] = liquidity
        full += liquidity
        approx = sum(parts.values())
        for k, v in parts.items():
            totals[k] += v
        rows.append(
            {
                "instrument": p.instrument,
                "full_pnl": full,
                "approximate_pnl": approx,
                "residual": full - approx,
                **parts,
            }
        )
    carry = portfolio.cash * math.expm1((cash_rate + scenario.rate_change) * dt)
    totals["cash_carry"] = carry
    full = sum(r["full_pnl"] for r in rows) + carry
    approx = sum(totals.values())
    return {
        "scenario": asdict(scenario),
        "full_pnl": full,
        "loss": -full,
        "approximate_pnl": approx,
        "residual": full - approx,
        "contributions": totals,
        "positions": sorted(rows, key=lambda r: r["full_pnl"]),
        "warnings": [
            "Hypothetical model changes; never booked as realised P&L",
            "Frozen quote/model basis and sticky strike IV; Greek terms are an approximation",
        ]
        + (
            ["Correlation changes the distribution, not a deterministic mark by itself"]
            if scenario.correlation is not None
            else []
        ),
    }
