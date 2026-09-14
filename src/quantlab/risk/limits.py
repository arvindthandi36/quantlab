"""Soft warnings and hard ingress constraints, including unfilled-order reservations."""

from dataclasses import dataclass, replace
from itertools import product

from quantlab.options.models import number
from quantlab.risk.analytics import linear_risk
from quantlab.risk.portfolio import Position

METRICS = ("gross", "net", "delta", "gamma", "vega", "position", "var", "drawdown")


@dataclass(frozen=True)
class Limit:
    metric: str
    maximum: float
    mode: str = "soft"

    def __post_init__(self):
        if self.metric not in METRICS or self.mode not in ("soft", "hard"):
            raise ValueError("Choose a supported risk metric and soft/hard limit")
        object.__setattr__(self, "maximum", number(self.maximum, "maximum risk", 0, 1e12))


def values(portfolio, settings, covariance=None):
    p = portfolio.public()
    f = p["factors"]
    return {
        "gross": p["gross"],
        "net": abs(p["net"]),
        "delta": sum(abs(x["delta"]) for x in f.values()),
        "gamma": sum(abs(x["gamma"]) for x in f.values()),
        "vega": sum(abs(x["vega"]) for x in f.values()),
        "position": p["max_position"],
        "var": max(0, linear_risk(portfolio, settings, covariance)["var"]),
        "drawdown": p["drawdown"],
    }


def reserved_values(portfolio, settings, venues, covariance=None):
    """Convex linear-normal/exposure limits: maximum over independent buy/sell endpoints.

    Reservations use public limit execution prices and current marks. They are a risk
    calculation only, never an accounting adjustment or a claimed future execution.
    """
    alternatives = []
    for name, venue in venues.items():
        live = venue._live("user")
        choices = [(0, 0.0)]
        for side, sign in (("buy", 1), ("sell", -1)):
            selected = [o for o in live if o.side.value == side]
            n = sum(o.remaining_quantity for o in selected) * sign
            cash = (
                -sum(o.remaining_quantity * float(o.price_ticks / 100) for o in selected) * sign
            )
            cash -= sum(o.remaining_quantity for o in selected) * float(
                venue.scenario.fee_ticks / 100
            )
            if n:
                choices.append((n, cash))
        alternatives.append((name, float(venue.account.reference / 100), choices))
    result = values(portfolio, settings, covariance)
    for combination in product(*(x[2] for x in alternatives)):
        positions = list(portfolio.positions)
        extra_cash = 0.0
        for (name, spot, _), (n, cash) in zip(alternatives, combination, strict=True):
            if not n:
                continue
            extra_cash += cash
            existing = next(
                (p for p in positions if p.instrument == name and p.kind == "stock"), None
            )
            if existing:
                positions.remove(existing)
                positions.append(replace(existing, quantity=existing.quantity + n))
            else:
                positions.append(Position(name, name, n, 1, spot, spot))
        proposed = replace(
            portfolio, positions=tuple(positions), cash=portfolio.cash + extra_cash
        )
        changed = values(proposed, settings, covariance)
        changed["drawdown"] = portfolio.drawdown + max(0, portfolio.equity - proposed.equity)
        result = {k: max(result[k], changed[k]) for k in result}
    return result


def check_limits(limits, after, *, before=None):
    warnings = []
    for limit in limits:
        observed = after[limit.metric]
        if observed > limit.maximum + 1e-9:
            worsening = before is None or observed > before[limit.metric] + 1e-9
            blocked = limit.mode == "hard" and worsening
            warnings.append(
                {
                    "metric": limit.metric,
                    "mode": limit.mode,
                    "maximum": limit.maximum,
                    "observed": observed,
                    "blocked": blocked,
                    "message": f"{limit.metric}: {observed:.6g} exceeds {limit.maximum:.6g}; "
                    + (
                        "hard limit prohibits this increase"
                        if blocked
                        else "existing breach is not increased"
                        if limit.mode == "hard"
                        else "soft warning"
                    ),
                }
            )
    return warnings
