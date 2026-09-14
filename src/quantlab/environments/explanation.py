"""Environment-aware projections; builders receive public snapshots only."""

import copy

import numpy as np

from quantlab.explainability import SCHEMA
from quantlab.explainability.evidence import changes, fields, ground, result
from quantlab.explainability.registry import ASSUMPTIONS, CONCEPTS, DEPTHS, resolve
from quantlab.risk.metrics import empirical_risk
from quantlab.risk.monte_carlo import revalue_returns
from quantlab.risk.portfolio import Portfolio, Position

HISTORICAL_NOTE = (
    "The replay records the movement but does not establish why the real market moved."
)
BAR_NOTE = (
    "SIMULATED EXECUTION ON HISTORICAL DATA: next revealed close, "
    "adverse tick slippage, shared volume participation and explicit "
    "fees. High/low does not trigger fills; no historical queue or "
    "observed order book is inferred."
)


def historical_ground(key, s, selector=None):
    a = s["account"]
    orders = s["orders"]
    order = (
        next((o for o in orders if o["order_id"] == selector), None)
        if selector
        else orders[-1]
        if orders
        else None
    )
    if key in (
        "vwap",
        "market_orders",
        "limit_orders",
        "partial_fills",
        "order_size",
    ):
        if order is None:
            return result(note="No paper order is recorded at this point. " + BAR_NOTE)
        return result(
            order["vwap"]
            if key == "vwap"
            else fields(order, "original filled remaining cancelled status"),
            "GBP per executed unit" if key == "vwap" else "paper quantities",
            inputs=copy.deepcopy(order),
            rows=order["fills"],
            note=BAR_NOTE,
            visual={"kind": "fills", "rows": order["fills"]},
        )
    if key in (
        "pnl_attribution",
        "realised_pnl",
        "unrealised_pnl",
        "fees",
        "position",
        "inventory",
        "drawdown",
    ):
        v = {
            "pnl_attribution": a["pnl"],
            "realised_pnl": a["realised_gross"],
            "unrealised_pnl": a["unrealised"],
            "fees": a["fees"],
            "position": a["positions"],
            "inventory": a["positions"],
            "drawdown": a["drawdown"],
        }[key]
        return result(
            v,
            "GBP / named instrument units",
            inputs=fields(a, "cash positions realised_gross unrealised fees pnl drawdown"),
            rows=s["fills"][-10:],
            note=(
                "Existing FIFO ledgers: realised gross plus unrealised minus fees "
                "reconciles to marked P&L. Imported closes are marks, not "
                "liquidation promises. "
            )
            + BAR_NOTE,
        )
    if key in (
        "var",
        "expected_shortfall",
    ):
        r = s["risk"]
        return result(
            r.get("es" if key == "expected_shortfall" else "var"),
            "GBP loss over one observation interval",
            inputs=fields(
                r, "confidence n observed_through lookback_returns horizon assumption"
            )
            | {"positions": a["positions"]},
            note=(
                "LIVE REPLAY RISK ESTIMATE. Current holdings revalued against "
                "revealed past returns only. No future returns or option prices "
                "are used. "
            )
            + r.get("reason", ""),
            visual={"kind": "histogram", "threshold": r.get("var"), **r.get("histogram", {})},
        )
    if key in (
        "regression",
        "regression_beta",
        "residual",
        "z_score",
        "correlation",
        "stat_arb_signal",
        "lookahead_bias",
    ):
        sig = s["signal"]
        v = {
            "regression": sig.get("fit"),
            "regression_beta": sig.get("fit", {}).get("beta"),
            "residual": sig.get("spread"),
            "z_score": sig.get("z"),
            "correlation": sig.get("price_correlation"),
            "stat_arb_signal": sig.get("action"),
        }.get(key)
        return result(
            v,
            "named pair units / dimensionless z",
            inputs=copy.deepcopy(sig),
            note=(
                "Existing Phase 10 causal model: training and normalisation "
                "exclude later observations. This is a relationship estimate, not "
                "proof of convergence or causation."
            ),
        )
    if key in (
        "covariance",
        "portfolio_variance",
        "stress_testing",
        "bid",
        "ask",
        "spread",
        "depth",
        "queue_priority",
        "implied_volatility",
        "option_pricing",
        "delta",
        "gamma",
        "vega",
        "markouts",
    ):
        return result(
            note=(
                "This dataset contains OHLCV bars only. Observed quotes, queue "
                "depth, option chains and exchange markouts are unavailable. No "
                "value is invented."
            )
        )
    if key not in ("current_price", "historical_replay", "market_environments"):
        return result(
            note="This measure is not available from this bar-replay adapter. " + BAR_NOTE
        )
    rows = [dict(instrument=k, **v[-1]) for k, v in s["observations"].items()]
    return result(
        rows,
        "recorded OHLCV; GBP prices",
        inputs={"observations": rows, "execution_model": s["execution"]},
        note=HISTORICAL_NOTE
        if s["environment"]["data_kind"] == "recorded"
        else (
            "These are artificial test bars, not real market history. The "
            "same time-causal replay rules apply."
        ),
    )


def project(key, s, selector=None):
    if s["engine"] != "historical" and key in ("current_price", "market_environments"):
        c = s["core"]
        value = c.get("reference", c.get("spot", (c.get("history") or [None])[-1]))
        return result(
            value,
            "GBP / named instrument prices",
            inputs={"observed_price": value},
            note=s["environment"]["truth"],
        )
    return (
        historical_ground(key, s, selector)
        if s["engine"] == "historical"
        else ground(key, s["core"], s["engine"], selector)
    )


def explain(s, concept, *, depth="beginner", selector=None, previous=None, mode="live"):
    key = resolve(concept)
    if depth not in DEPTHS:
        raise ValueError("Choose a supported explanation depth")
    if mode not in ("live", "post_session"):
        raise ValueError(
            "Observer information requires the separate ended-session reveal control"
        )
    if mode == "post_session" and s["status"] != "ended":
        raise ValueError("Post-session explanations require the ended frame")
    meta = CONCEPTS[key].public()
    historical = s["engine"] == "historical"
    if historical and key in (
        "market_orders",
        "limit_orders",
        "partial_fills",
        "queue_priority",
    ):
        meta = copy.deepcopy(meta)
        meta["definition"] = (
            "A paper instruction evaluated under the next-close execution rule."
        )
        meta["changes"] = (
            "Later revealed close, volume budget, slippage, fees and your instruction."
        )
        meta["limitation"] = BAR_NOTE
    if historical:
        assumptions = [
            {
                "name": "Historical observation and paper execution",
                "description": BAR_NOTE,
                "failure": "Bars cannot establish real exchange fills or why a market moved.",
            },
            {
                "name": "Dataset consistency",
                "description": (
                    "All OHLC fields use the declared adjustment basis, timezone and units."
                ),
                "failure": (
                    "Bad provenance, missing intervals or corporate actions can make "
                    "comparisons misleading."
                ),
            },
        ]
    else:
        assumptions = [ASSUMPTIONS[k] for k in meta["assumptions"]]
    now = project(key, s, selector)
    old = project(key, previous, selector) if previous else None
    point = fields(s, "index timestamp revision status frame_index")
    env = s["environment"]
    label = ("SELECTED REPLAY POINT — " if s.get("replay") else "ACTUAL SESSION — ") + env[
        "badge"
    ]
    evidence_type = "PUBLIC SYNTHETIC OBSERVATION"
    if historical:
        evidence_type = (
            "SIMULATED HISTORICAL EXECUTION"
            if key in ("vwap", "market_orders", "limit_orders", "partial_fills", "order_size")
            else "HISTORICAL OBSERVATION"
            if key in ("current_price", "historical_replay")
            else "MODEL CALCULATION"
        )
        if (
            env["data_kind"] == "artificial_fixture"
            and evidence_type == "HISTORICAL OBSERVATION"
        ):
            evidence_type = "ARTIFICIAL TEST OBSERVATION"
    return {
        "schema": SCHEMA,
        "concept": meta,
        "current": now,
        "depth": depth,
        "mode": mode,
        "label": label,
        "environment": copy.deepcopy(env) | {"adapter": s["engine"]},
        "source": {
            "environment": env["type"].lower(),
            "point": point,
            "relation": "historical observation / simulated execution"
            if historical
            else "controlled synthetic model",
        },
        "change": {
            "available": old is not None,
            "before": old["value"] if old else None,
            "after": now["value"],
            "previous_point": fields(previous, "index timestamp revision frame_index")
            if previous
            else None,
            "label": "Main changed public inputs; no inferred real-market causal percentages",
            "inputs": changes(old["inputs"], now["inputs"]) if old else [],
        },
        "dependency_trace": [
            {
                "from": "revealed observations and your instructions",
                "to": key,
                "relation": "calculated from / observed context",
            }
        ],
        "assumptions": assumptions,
        "quiz_allowed": True,
        "selectors": [
            {"id": o["order_id"], "label": o["order_id"] + " · " + o["side"]}
            for o in s.get("orders", s.get("core", {}).get("orders", []))
        ][-100:],
        "evidence_labels": [
            {
                "type": evidence_type,
                "text": now["note"],
            }
        ],
    }


def what_if(s, kind, inputs):
    from quantlab.environments.data import integer
    from quantlab.explainability import sandbox

    if not isinstance(inputs, dict):
        raise ValueError("Hypothetical inputs must be an object")
    if s["engine"] == "historical":
        if kind != "position_risk" or set(inputs) - {"quantity", "instrument"}:
            raise ValueError(
                "Historical what-if supports current position risk; future fills "
                "cannot be predicted from unseen bars"
            )
        k = inputs.get("instrument", s["instruments"][0])
        integer(inputs.get("quantity"), "Hypothetical signed quantity", -1000, 1000)
        if k not in s["instruments"]:
            raise ValueError("Choose a revealed instrument")
        data = [s["observations"][i] for i in s["instruments"]]
        if len(data[0]) < 3:
            raise ValueError("Reveal at least two returns first")
        positions = []
        for i in s["instruments"]:
            old = next((p for p in s["account"]["positions"] if p["instrument"] == i), None)
            q = inputs["quantity"] if i == k else old["quantity"] if old else 0
            price = s["observations"][i][-1]["close"]
            positions.append(Position(i, i, q, 1, price, price))
        p = Portfolio(tuple(positions), s["account"]["cash"])
        prices = np.array([[r[j]["close"] for r in data] for j in range(len(data[0]))])[-251:]
        losses, _ = revalue_returns(
            p, s["instruments"], prices[1:] / prices[:-1] - 1, days=1, cash_rate=0
        )
        r = {
            "before": s["risk"],
            "after": empirical_risk(losses),
            "note": (
                "HYPOTHETICAL current holding, no execution. Same revealed-return "
                "window; cash held fixed, fees and trading costs omitted."
            ),
        }
    else:
        fn = {
            "order_size": sandbox.order_size,
            "inventory": sandbox.inventory,
            "volatility": sandbox.volatility,
            "entry_threshold": sandbox.threshold,
        }.get(kind)
        allowed = {
            "trading": ("order_size", "inventory"),
            "options": ("volatility",),
            "statarb": ("entry_threshold",),
        }
        if not fn or kind not in allowed[s["engine"]]:
            raise ValueError("Choose an available environment hypothetical")
        r = fn(copy.deepcopy(s["core"]), copy.deepcopy(inputs))
    return {
        "schema": SCHEMA,
        "label": "HYPOTHETICAL ANALYSIS — " + s["environment"]["badge"],
        "kind": kind,
        "result": r,
        "isolation": (
            "Detached public inputs only. Accounts, research, journals, "
            "learner mastery and market RNG are unchanged."
        ),
    }
