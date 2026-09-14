"""Detached public risk positions. Accounting remains in the existing ledgers."""

import math
from dataclasses import asdict, dataclass

from quantlab.options.models import PricingInputs
from quantlab.options.pricing import greeks, price
from quantlab.portfolio.accounting import AccountingError


@dataclass(frozen=True)
class Position:
    instrument: str
    underlying: str
    quantity: int
    multiplier: int
    mark: float
    spot: float
    kind: str = "stock"
    strike: float = 0
    years: float = 0
    volatility: float = 0
    rate: float = 0
    dividend: float = 0

    def __post_init__(self):
        if self.kind not in ("stock", "call", "put"):
            raise ValueError("Unknown risk instrument type")
        if (
            type(self.quantity) is not int
            or type(self.multiplier) is not int
            or self.multiplier < 1
        ):
            raise ValueError("Whole quantities and positive contract multipliers required")
        for k in ("mark", "spot", "strike", "years", "volatility", "rate", "dividend"):
            if not math.isfinite(getattr(self, k)):
                raise ValueError("Nonfinite public position")
        if self.spot <= 0 or self.mark < 0:
            raise ValueError("Positive stock spot and nonnegative mark required")
        if self.kind == "stock" and self.multiplier != 1:
            raise ValueError("Stock quantity is in units; stock multiplier must be 1")
        if self.kind != "stock":
            self.inputs()

    def inputs(self):
        return PricingInputs(
            self.spot, self.strike, self.years, self.volatility, self.rate, self.dividend
        )

    @property
    def units(self):
        return self.quantity * self.multiplier

    @property
    def value(self):
        return self.units * self.mark

    def sensitivities(self):
        if self.kind == "stock":
            return dict(delta=float(self.quantity), gamma=0.0, vega=0.0, theta=0.0, rho=0.0)
        g = greeks(self.kind, self.inputs()).scaled(self.units)
        result = {k: getattr(g, k) for k in ("delta", "gamma", "vega", "theta", "rho")}
        if any(v is None for v in result.values()):
            raise ValueError("Risk Greeks undefined at an option kink")
        return result


@dataclass(frozen=True)
class Portfolio:
    positions: tuple[Position, ...]
    cash: float
    realised_gross: float = 0
    unrealised: float = 0
    fees: float = 0
    financing: float = 0
    initial_capital: float = 0
    drawdown: float = 0
    source: str = "Actual QuantLab accounts"

    @property
    def equity(self):
        return self.cash + sum(p.value for p in self.positions)

    def public(self):
        rows = []
        factors = {}
        for p in self.positions:
            g = p.sensitivities()
            f = factors.setdefault(
                p.underlying,
                dict(spot=p.spot, delta=0.0, gamma=0.0, vega=0.0, theta=0.0, rho=0.0),
            )
            if not math.isclose(f["spot"], p.spot, rel_tol=1e-12):
                raise ValueError("One underlying must have one current spot")
            for key in g:
                f[key] += g[key]
            rows.append(
                asdict(p) | {"value": p.value, "greeks": g, "delta_gbp": g["delta"] * p.spot}
            )
        long = sum(max(0, p.value) for p in self.positions)
        short = sum(max(0, -p.value) for p in self.positions)
        gross = long + short
        dgross = sum(abs(r["delta_gbp"]) for r in rows)
        for r in rows:
            r["value_share"] = abs(r["value"]) / gross if gross else 0
            r["delta_share"] = abs(r["delta_gbp"]) / dgross if dgross else 0
        return {
            "positions": rows,
            "cash": self.cash,
            "market_value": long - short,
            "equity": self.equity,
            "initial_capital": self.initial_capital,
            "realised_gross": self.realised_gross,
            "unrealised": self.unrealised,
            "fees": self.fees,
            "financing": self.financing,
            "pnl": self.equity - self.initial_capital,
            "drawdown": self.drawdown,
            "long": long,
            "short": short,
            "gross": gross,
            "net": long - short,
            "delta_gbp": sum(r["delta_gbp"] for r in rows),
            "gross_delta_gbp": sum(abs(f["delta"] * f["spot"]) for f in factors.values()),
            "factors": factors,
            "greeks": {
                k: sum(f[k] for f in factors.values())
                for k in ("delta", "gamma", "vega", "theta", "rho")
            },
            "largest_position_share": max((r["value_share"] for r in rows), default=0),
            "largest_delta_share": max((r["delta_share"] for r in rows), default=0),
            "hhi": sum(r["value_share"] ** 2 for r in rows),
            "max_position": max((abs(p.quantity) for p in self.positions), default=0),
            "source": self.source,
        }


def from_accounts(options=None, stocks=None, *, drawdown=0):
    """Read ledgers, preserve fee convention, independently reconcile aggregated equity."""
    positions = []
    cash = realised = unrealised = fees = funding = capital = 0.0
    if options is not None:
        options.stock.check_invariants()
        options.portfolio.check(options._marks())
        a = options.accounts()
        cash += float(a["cash"])
        realised += float(a["option_realised_gross"] + a["stock_realised_gross"])
        unrealised += float(a["option_unrealised"] + a["stock_unrealised"])
        fees += float(a["fees"])
        funding += float(a["financing"])
        if options.stock.account.inventory:
            positions.append(
                Position(
                    "QL-STOCK",
                    "QL-STOCK",
                    options.stock.account.inventory,
                    1,
                    options.spot,
                    options.spot,
                )
            )
        for key, c in options.portfolio.contracts.items():
            n = options.portfolio.quantity(key)
            if n:
                q = options.quotes[key]
                x = q.inputs
                positions.append(
                    Position(
                        key,
                        "QL-STOCK",
                        n,
                        c.multiplier,
                        float(q.midpoint),
                        x.spot,
                        c.option_type.value,
                        x.strike,
                        x.time_years,
                        x.volatility,
                        x.rate,
                        x.dividend_yield,
                    )
                )
    for name, session in (stocks or {}).items():
        session.check_invariants()
        a = session.account.snapshot()
        cash += float(a.cash_ticks / 100)
        capital += float(session.account.starting_equity / 100)
        realised += float(a.realised_trading_pnl_ticks / 100)
        unrealised += float(a.unrealised_pnl_ticks / 100)
        fees += float(a.fees_ticks / 100)
        if a.inventory:
            s = float(a.reference_ticks / 100)
            positions.append(Position(name, name, a.inventory, 1, s, s))
    p = Portfolio(
        tuple(positions), cash, realised, unrealised, fees, funding, capital, drawdown
    )
    if not math.isclose(
        p.equity - capital, realised + unrealised + funding - fees, abs_tol=1e-7
    ):
        raise AccountingError("Risk aggregation disagrees with the actual account ledgers")
    return p


def model_basis(portfolio):
    return sum(
        p.units * (p.mark - price(p.kind, p.inputs()))
        for p in portfolio.positions
        if p.kind != "stock"
    )
