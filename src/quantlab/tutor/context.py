"""Information boundary: detached allowlisted facts, never an exchange or observer log."""

import math
from dataclasses import dataclass
from fractions import Fraction
from types import MappingProxyType

from quantlab.research.codec import digest

FIELDS = {
    "book": {"bid", "ask", "spread", "position", "limit", "reference"},
    "execution": {
        "order_id",
        "side",
        "original",
        "filled",
        "remaining",
        "cancelled",
        "vwap",
        "fills",
        "type",
        "price",
        "position",
        "limit",
        "reference",
    },
    "position": {"position", "limit", "reference", "realised", "unrealised", "pnl", "drawdown"},
    "markout": {"trade_id", "role", "horizon", "value", "observed_time_us"},
    "quotes": {"position", "limit", "reference", "bids", "asks"},
    "research": {
        "variant",
        "n",
        "mean",
        "sd",
        "se",
        "ci_low",
        "ci_high",
        "minimum",
        "maximum",
        "paired",
        "paired_se",
        "unpaired_se",
        "mean_difference",
        "variant_count",
        "metric",
        "unit",
        "source_digest",
    },
}
FILL_FIELDS = {"price", "quantity", "side", "role"}
FIELDS["derivatives"] = {
    "contract_id",
    "option_type",
    "spot",
    "strike",
    "time_years",
    "multiplier",
    "quantity",
    "model_value",
    "bid",
    "ask",
    "midpoint",
    "volatility",
    "implied_volatility",
    "rate",
    "delta",
    "gamma",
    "vega",
    "theta",
    "rho",
    "option_delta",
    "portfolio_delta",
    "stock_position",
    "option_pnl",
    "hedge_pnl",
    "total_pnl",
    "realised_volatility",
    "event_type",
    "trade_quantity",
    "trade_premium",
    "premium_cash_flow",
    "fee",
    "trade_side",
    "solver_method",
    "solver_iterations",
    "solver_residual",
    "solver_converged",
    "mc_estimate",
    "mc_se",
    "mc_paths",
}
FIELDS["risk"] = {
    "equity",
    "pnl",
    "gross",
    "delta",
    "gamma",
    "vega",
    "var",
    "es",
    "confidence",
    "horizon",
    "sample_n",
    "correlation",
    "variance",
    "cross_variance",
    "concentration",
    "scenario_pnl",
    "scenario_residual",
    "optimisation_variance",
}
FIELDS["statarb"] = {
    "t",
    "alpha",
    "beta",
    "r_squared",
    "fit_end",
    "spread",
    "mean",
    "sd",
    "z",
    "correlation",
    "pnl",
    "gross",
    "net",
    "imbalance",
    "costs",
    "factor_exposure",
}
OPTION_TEXT = {"contract_id", "option_type", "event_type", "trade_side", "solver_method"}


def _number(value):
    if type(value) not in (str, int, float) or isinstance(value, bool):
        raise ValueError("Public numeric fact has invalid type")
    result = Fraction(str(value))
    if not math.isfinite(float(result)):
        raise ValueError("Public numeric fact is not finite")
    return value


@dataclass(frozen=True)
class PublicContext:
    source: str
    kind: str
    event: int
    time_us: int
    facts: object

    def __post_init__(self):
        if self.kind not in FIELDS or set(self.facts) != FIELDS[self.kind]:
            raise ValueError("Non-public or unsupported context field")
        if (
            type(self.event) is not int
            or self.event < 0
            or type(self.time_us) is not int
            or self.time_us < 0
        ):
            raise ValueError("Invalid public context clock")
        if not isinstance(self.source, str) or len(self.source) > 200:
            raise ValueError("Invalid context source")
        facts = dict(self.facts)
        for key, value in facts.items():
            if key == "fills":
                cleaned = []
                for fill in value:
                    if set(fill) != FILL_FIELDS:
                        raise ValueError("Execution facts must exclude counterparty identity")
                    _number(fill["price"])
                    if type(fill["quantity"]) is not int or fill["quantity"] <= 0:
                        raise ValueError("Invalid executed quantity")
                    if fill["side"] not in ("buy", "sell") or fill["role"] not in (
                        "provider",
                        "aggressor",
                    ):
                        raise ValueError("Invalid public execution side/role")
                    cleaned.append(MappingProxyType(dict(fill)))
                facts[key] = tuple(cleaned)
            elif key in ("bids", "asks"):
                facts[key] = tuple(_number(x) for x in value)
            elif key in ("paired", "solver_converged"):
                if value is None and key == "solver_converged":
                    continue
                if type(value) is not bool:
                    raise ValueError("Pairing flag must be boolean")
            elif key in OPTION_TEXT or key in (
                "order_id",
                "side",
                "role",
                "type",
                "variant",
                "metric",
                "unit",
                "source_digest",
            ):
                if not isinstance(value, str) or len(value) > 200:
                    raise ValueError("Invalid public text field")
            elif value is not None and key not in (
                "order_id",
                "side",
                "role",
                "type",
                "variant",
                "metric",
                "unit",
                "source_digest",
                "paired",
            ):
                _number(value)
        object.__setattr__(self, "facts", MappingProxyType(facts))

    def public(self):
        return {
            "source": self.source,
            "kind": self.kind,
            "event": self.event,
            "time_us": self.time_us,
            "facts": {
                k: [dict(f) for f in v]
                if k == "fills"
                else list(v)
                if isinstance(v, tuple)
                else v
                for k, v in self.facts.items()
            },
        }

    @property
    def key(self):
        return digest(self.public())


def trading_contexts(snapshot, source):
    """Read only selected Phase 6 public fields; unknown keys are never copied."""
    number, time = snapshot["public_event"], snapshot["time_us"]
    account = snapshot["account"]
    common = {
        "position": account["position"],
        "limit": account["position_limit"],
        "reference": snapshot["reference"],
    }
    result = [
        PublicContext(
            source,
            "book",
            number,
            time,
            {
                **common,
                "bid": snapshot["best_bid"],
                "ask": snapshot["best_ask"],
                "spread": snapshot["spread"],
            },
        )
    ]
    for order in snapshot["orders"]:
        facts = {
            k: order[k]
            for k in (
                "order_id",
                "side",
                "original",
                "filled",
                "remaining",
                "cancelled",
                "vwap",
                "type",
                "price",
            )
        }
        facts["fills"] = [{k: f[k] for k in FILL_FIELDS} for f in order["fills"]]
        result.append(PublicContext(source, "execution", number, time, facts | common))
    result.append(
        PublicContext(
            source,
            "position",
            number,
            time,
            common
            | {
                "realised": account["realised"],
                "unrealised": account["unrealised"],
                "pnl": account["total_pnl"],
                "drawdown": account["max_drawdown"],
            },
        )
    )
    for mark in snapshot["markouts"]:
        if (
            mark["status"] == "matured"
            and mark["value"] is not None
            and mark["observed_time_us"] is not None
            and mark["observed_time_us"] <= time
        ):
            result.append(
                PublicContext(
                    source, "markout", number, time, {k: mark[k] for k in FIELDS["markout"]}
                )
            )
    if snapshot["mode"] == "manual_maker":
        result.append(
            PublicContext(
                source,
                "quotes",
                number,
                time,
                common
                | {
                    "bids": [
                        o["price"]
                        for o in snapshot["orders"]
                        if o["remaining"] and o["side"] == "buy"
                    ],
                    "asks": [
                        o["price"]
                        for o in snapshot["orders"]
                        if o["remaining"] and o["side"] == "sell"
                    ],
                },
            )
        )
    return tuple(result)


def context_from_dict(raw):
    return PublicContext(**raw)
