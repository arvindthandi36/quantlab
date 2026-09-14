"""Allowlisted projection of existing public values. No financial reimplementation."""

from copy import deepcopy
from fractions import Fraction

from quantlab.execution import vwap


def fields(value, names):
    return {k: deepcopy(value[k]) for k in names.split() if k in value}


def numeric(value):
    return type(value) in (int, float) or isinstance(value, str) and _fraction(value)


def _fraction(value):
    try:
        Fraction(value)
        return True
    except (ValueError, ZeroDivisionError):
        return False


def changes(before, after):
    """Differences of observed outputs, never fitted causal shares."""
    rows = []
    for key in sorted(before.keys() | after.keys()):
        a, b = before.get(key), after.get(key)
        if a != b:
            if isinstance(a, dict) and isinstance(b, dict):
                rows.extend({**r, "input": key + "." + r["input"]} for r in changes(a, b))
                continue
            row = dict(input=key, before=a, after=b, relation="observed changed input")
            if numeric(a) and numeric(b):
                row["difference"] = float(Fraction(str(b)) - Fraction(str(a)))
            rows.append(row)
    return rows


def result(value=None, unit=None, *, inputs=None, rows=None, note=None, visual=None):
    return dict(
        value=value,
        unit=unit,
        inputs=inputs or {},
        rows=rows or [],
        note=note or "Read from the selected public snapshot.",
        visual=visual,
    )


def option_inputs(state):
    q = state.get("selected") or {}
    return dict(
        spot=state.get("spot"),
        strike=q.get("strike"),
        time_years=q.get("remaining_years"),
        volatility=q.get("volatility_input"),
        rate=state.get("rate"),
        dividend_yield=state.get("dividend_yield"),
        option_type=q.get("type"),
        contract_id=q.get("id"),
        multiplier=q.get("multiplier"),
    )


def positions(public):
    return [
        fields(
            p,
            (
                "instrument underlying quantity multiplier mark spot kind strike "
                "years volatility rate dividend value delta_gbp"
            ),
        )
        | {"greeks": fields(p.get("greeks", {}), "delta gamma vega theta rho")}
        for p in public.get("positions", [])
    ]


def trading(key, s, selector=None):
    a = s.get("account", {})
    base = fields(s, "best_bid best_ask mid reference reference_source")
    if key in ("bid", "ask", "spread", "midpoint"):
        value = s.get(
            {"bid": "best_bid", "ask": "best_ask", "spread": "spread", "midpoint": "mid"}[key]
        )
        return result(
            value,
            "GBP per unit",
            inputs=base,
            visual=dict(
                kind="quotes",
                rows=[
                    dict(label="Bid", value=s.get("best_bid")),
                    dict(label="Ask", value=s.get("best_ask")),
                ],
            ),
        )
    if key in (
        "vwap",
        "market_orders",
        "limit_orders",
        "partial_fills",
        "order_size",
        "slippage",
        "execution_cost",
    ):
        orders = s.get("orders", [])
        order = (
            next((o for o in orders if o["order_id"] == selector), None)
            if selector
            else (orders[-1] if orders else None)
        )
        if order is None:
            return result(
                note=(
                    "No selected order is recorded at this point. Submit an order, or "
                    "select an earlier recorded order; no fill price has been invented."
                )
            )
        fills = [
            fields(f, "trade_id time_us side quantity role price fee") for f in order["fills"]
        ]
        actual = fields(
            order, "order_id side type price original filled remaining cancelled status"
        )
        if key == "vwap":
            # Reuse the authoritative exact VWAP API, explicitly in GBP.
            exact = vwap((f["price"], f["quantity"]) for f in fills)
            actual["exact_vwap_gbp"] = str(exact) if exact is not None else None
            actual["fills"] = fills
            return result(
                order.get("vwap"),
                "GBP per executed unit, fees separate",
                inputs=actual,
                rows=fills,
                note=(
                    "Calculated from these recorded fills using the same execution "
                    "calculation as the order book. Larger fills receive more weight. "
                    "Display is rounded to five decimal places; the exact fraction is "
                    "retained."
                ),
                visual=dict(kind="fills", rows=fills),
            )
        if key in ("slippage", "execution_cost"):
            return result(
                inputs=actual,
                rows=fills,
                note=(
                    "These are the actual fills and separately recorded fees. This order "
                    "view does not retain a declared pre-trade benchmark, so no slippage "
                    "number is asserted. Use the frozen-book sandbox for a clearly "
                    "labelled hypothetical comparison."
                ),
            )
        return result(
            order.get("status"),
            "order outcome",
            inputs=actual,
            rows=fills,
            note=(
                "The existing engine records fills, the resting remainder and any "
                "cancelled quantity. A limit order's price bounds eligibility; "
                "executions occur at resting opposite prices."
            ),
        )
    if key in (
        "position",
        "inventory",
        "realised_pnl",
        "unrealised_pnl",
        "pnl_attribution",
        "fees",
        "drawdown",
        "exposure",
    ):
        field = {
            "position": "position",
            "inventory": "position",
            "realised_pnl": "realised",
            "unrealised_pnl": "unrealised",
            "pnl_attribution": "total_pnl",
            "fees": "fees",
            "drawdown": "drawdown",
            "exposure": "exposure",
        }[key]
        inputs = fields(
            a,
            (
                "cash position average_entry realised unrealised total_pnl fees "
                "exposure max_drawdown"
            ),
        ) | fields(s, "reference reference_source")
        return result(
            a.get(field),
            "units" if key in ("position", "inventory") else "GBP",
            inputs=inputs,
            rows=[
                fields(f, "trade_id time_us side quantity price fee")
                for f in s.get("trades", [])[-10:]
            ],
            note=(
                "Stock-desk realised P&L is already net of expensed fees. Total "
                "equals that realised amount plus unrealised P&L. Fees are shown for "
                "context and must not be subtracted twice. Open inventory is valued "
                "at the displayed public reference."
            ),
        )
    if key == "markouts":
        rows = [
            fields(
                m,
                (
                    "trade_id role side horizon value status observed_time_us price "
                    "reference signed_markout"
                ),
            )
            for m in s.get("markouts", [])
        ]
        return result(
            rows[-1] if rows else None,
            "GBP per unit; own-side sign",
            rows=rows,
            note=(
                "Only markouts already present at this public point are available. "
                "Positive favours your side; negative opposes it. A pending horizon "
                "is not zero and does not reveal a later price."
            ),
        )
    if key in (
        "depth",
        "queue_priority",
        "quote_skew",
        "spread_capture",
        "adverse_selection",
        "order_flow",
    ):
        rows = []
        for side in ("bids", "asks"):
            rows += [
                dict(side=side, **fields(level, "price quantity order_count own_quantity"))
                for level in s.get(side, [])[:12]
            ]
        own = [
            fields(o, "order_id side price original filled remaining status")
            for o in s.get("orders", [])
            if o.get("remaining", 0)
        ]
        return result(
            own
            if key == "quote_skew"
            else rows
            if key in ("depth", "queue_priority")
            else s.get("quant", {}).get("flow_imbalance")
            if key == "order_flow"
            else None,
            "actual resting quotes"
            if key == "quote_skew"
            else "displayed price levels"
            if key in ("depth", "queue_priority")
            else "public mechanism / unavailable scalar",
            rows=rows,
            inputs=base | fields(a, "position position_limit") | {"own_resting_orders": own},
            note=(
                "These are public displayed levels and your own resting orders. "
                "Manual quote shifts are user-selected; private counterparty type is "
                "not inferred. Quotes may also be rounded outward or reduced by "
                "position limits. This legacy public view does not retain a separate "
                "spread-capture attribution, so no such amount is invented."
            ),
        )
    return result(
        inputs=base,
        note=(
            "This concept describes the displayed engine mechanism. It is not a "
            "separate numerical metric."
        ),
    )


def options(key, s, selector=None):
    q = s.get("selected") or {}
    x = option_inputs(s)
    if key in (
        "delta",
        "gamma",
        "vega",
        "theta",
        "rho",
        "delta_hedging",
        "contract_multiplier",
        "option_pricing",
        "black_scholes",
        "volatility",
        "implied_volatility",
        "root_finding",
    ):
        g = fields(
            q.get("greeks", {}),
            (
                "delta gamma vega theta rho vega_per_vol_point theta_per_day "
                "rho_per_rate_point status"
            ),
        )
        value = (
            g.get(key)
            if key in g
            else (
                q.get("multiplier")
                if key == "contract_multiplier"
                else q.get("iv", {}).get("volatility")
                if key in ("implied_volatility", "root_finding")
                else s.get("greeks", {}).get("delta")
                if key == "delta_hedging"
                else x.get("volatility")
                if key == "volatility"
                else q.get("model_value")
            )
        )
        if key in ("delta", "gamma", "vega", "theta", "rho") and selector == "portfolio":
            value = s.get("greeks", {}).get(key)
        inputs = x | dict(
            per_unit_greeks=g,
            contract_greeks=fields(q.get("contract_greeks", {}), "delta gamma vega theta rho"),
            portfolio_greeks=fields(
                s.get("greeks", {}), "delta option_delta gamma vega theta rho"
            ),
            positions=[
                fields(p, "id quantity multiplier value") for p in s.get("positions", [])
            ],
        )
        if key in ("implied_volatility", "root_finding"):
            inputs.update(
                quote_midpoint=q.get("midpoint"),
                solver=fields(
                    q.get("iv", {}),
                    "converged status method iterations residual bracket volatility",
                ),
            )
        units = {
            "delta": "per-unit value change / GBP stock move",
            "gamma": "delta change / GBP stock move",
            "vega": "GBP per unit per 1.0 volatility change",
            "theta": "GBP per unit per elapsed year",
            "rho": "GBP per unit per 1.0 rate change",
            "delta_hedging": "stock-equivalent units",
            "contract_multiplier": "underlying units per contract",
            "volatility": "annual decimal",
            "implied_volatility": "annual decimal",
        }
        unit = (
            "aggregate portfolio sensitivity; signed quantities and multipliers included"
            if selector == "portfolio"
            else units.get(key, "GBP per underlying unit")
        )
        return result(
            value,
            unit,
            inputs=inputs,
            rows=[
                fields(h, "step stock_quantity option_delta residual_delta fee")
                for h in s.get("hedges", [])[-5:]
            ],
            note=(
                "Selected-contract values are per underlying unit. Contract and "
                "portfolio sensitivities retain multipliers and signed quantities. "
                "Changes in displayed inputs are observed contributors, not an "
                "additive causal attribution."
            ),
            visual=dict(
                kind="curve",
                rows=[fields(p, "spot value delta gamma") for p in s.get("curves", [])],
            )
            if isinstance(s.get("curves"), list)
            else None,
        )
    if key in (
        "pnl_attribution",
        "realised_pnl",
        "unrealised_pnl",
        "fees",
        "position",
        "drawdown",
        "exposure",
    ):
        a = s.get("accounts", {})
        inp = fields(
            a,
            (
                "cash option_value stock_value option_realised_gross "
                "stock_realised_gross option_unrealised stock_unrealised "
                "option_gross_pnl hedge_gross_pnl fees financing total_pnl drawdown"
            ),
        )
        value = (
            fields(a, "option_realised_gross stock_realised_gross")
            if key == "realised_pnl"
            else fields(a, "option_unrealised stock_unrealised")
            if key == "unrealised_pnl"
            else [fields(p, "id type quantity multiplier") for p in s.get("positions", [])]
            if key == "position"
            else fields(s.get("greeks", {}), "delta gamma vega theta rho")
            if key == "exposure"
            else a.get(
                "fees" if key == "fees" else "drawdown" if key == "drawdown" else "total_pnl"
            )
        )
        return result(
            value,
            "signed contracts"
            if key == "position"
            else "aggregate sensitivities"
            if key == "exposure"
            else "GBP",
            inputs=inp,
            rows=[
                fields(t, "contract_id side quantity premium_cash_flow fee step price")
                for t in s.get("option_trades", [])[-10:]
            ],
            note=(
                "Existing ledgers separate option and hedge gross P&L, financing and "
                "fees. Execution cash is a balance-sheet movement, not automatically "
                "profit."
            ),
        )
    if key in ("standard_error", "monte_carlo"):
        mc = s.get("analysis", {}).get("mc", {}).get("data", {})
        return result(
            mc.get("estimate" if key == "monte_carlo" else "standard_error"),
            "GBP per unit",
            inputs=fields(mc, "estimate standard_error paths seed confidence_interval"),
            note=(
                "Existing selected-contract Monte Carlo analysis, if one has been "
                "requested. Explain does not start a simulation."
            ),
        )
    return result(
        inputs=x,
        note=(
            "The current contract supplies the context. No separate value is "
            "claimed for this concept."
        ),
    )


def risk(key, s, selector=None):
    r = s.get("report", {})
    p, settings = r.get("portfolio", {}), r.get("settings", {})
    inputs = dict(
        holdings=positions(p),
        settings=fields(
            settings,
            (
                "confidence days daily_volatility means correlation paths seed "
                "distribution df cash_rate"
            ),
        ),
        covariance=deepcopy(r.get("covariance")),
        factors=deepcopy(r.get("factors")),
        covariance_source=r.get("covariance_source"),
    )
    if key in ("var", "expected_shortfall"):
        method = selector or "monte_carlo"
        if method not in ("monte_carlo", "historical", "parametric"):
            raise ValueError("Choose Monte Carlo, historical or parametric risk")
        d = r.get(method, {})
        d = d if method == "parametric" else d.get("full", {})
        inputs.update(
            method=method,
            estimate=fields(
                d, "confidence n tail_mass boundary_weight convention days warnings"
            ),
        )
        return result(
            d.get("var" if key == "var" else "es"),
            "GBP loss",
            inputs=inputs,
            rows=[
                fields(x, "loss index") if isinstance(x, dict) else {"loss": x}
                for x in d.get("worst", [])[:10]
            ],
            note=(
                "Read from the existing risk report; no Monte Carlo run is triggered."
                " These results are conditional on holdings, return scenarios and "
                "pricing assumptions. Main changed inputs are reported without causal"
                " percentages."
            ),
            visual=dict(
                kind="histogram",
                **fields(d.get("histogram", {}), "edges counts"),
                threshold=d.get("var"),
            ),
        )
    metric = {
        "correlation": r.get("correlation"),
        "covariance": r.get("covariance"),
        "covariance_matrices": r.get("covariance"),
        "portfolio_variance": r.get("parametric", {}).get("decomposition", {}).get("variance"),
        "diversification": r.get("parametric", {}).get("decomposition"),
        "exposure": p.get("gross_delta_gbp"),
        "drawdown": p.get("drawdown"),
        "pnl_attribution": p.get("pnl"),
        "stress_testing": (s.get("scenario") or {}).get("full_pnl"),
        "portfolio_optimisation": s.get("optimisation"),
    }
    if key == "pnl_attribution":
        inputs = fields(
            p,
            (
                "cash market_value equity initial_capital realised_gross unrealised "
                "financing fees pnl"
            ),
        ) | {"holdings": positions(p)}
    if key == "stress_testing":
        inputs["scenario"] = fields(
            s.get("scenario") or {}, "scenario full_pnl approximate_pnl residual contributions"
        )
    return result(
        metric.get(key),
        "return²"
        if key in ("covariance", "covariance_matrices")
        else "dimensionless"
        if key == "correlation"
        else "GBP²"
        if key == "portfolio_variance"
        else "GBP / named output",
        inputs=inputs,
    )


def statarb(key, s, selector=None):
    sig = s.get("signal", {})
    fit = fields(sig.get("fit", {}), "alpha beta start end n r_squared warnings")
    inp = fields(
        sig, "t available reason spread mean sd n normalization_start normalization_end"
    ) | {"fit": fit}
    hist = s.get("history", [])
    if hist:
        point = s.get("t", len(hist) - 1)
        inp["current_X_Y"] = deepcopy(hist[point])
    if key in (
        "z_score",
        "residual",
        "regression",
        "regression_beta",
        "correlation",
        "standard_deviation",
        "stat_arb_signal",
        "lookahead_bias",
    ):
        value = {
            "z_score": sig.get("z"),
            "residual": sig.get("spread"),
            "regression": fit,
            "regression_beta": fit.get("beta"),
            "correlation": sig.get("price_correlation"),
            "standard_deviation": sig.get("sd"),
            "stat_arb_signal": s.get("decisions", [])[-1:],
        }.get(key)
        inp["rules"] = fields(
            s.get("rules", {}),
            "entry exit stop window z_window mode block max_holding max_loss max_gross",
        )
        return result(
            value,
            "dimensionless" if key in ("z_score", "correlation") else "named model units",
            inputs=inp,
            note=(
                "The current residual uses the current published X,Y pair and a fit "
                "ending before this point. Normalisation uses earlier residuals only."
                " Undefined or insufficient-history scores remain unavailable."
            ),
            visual=dict(
                kind="residual",
                value=sig.get("spread"),
                mean=sig.get("mean"),
                sd=sig.get("sd"),
                z=sig.get("z"),
            ),
        )
    m = s.get("metrics", {})
    inp = fields(m, "net_pnl fees execution_cost costs turnover drawdown residual_inventory")
    inp["exposure"] = fields(s.get("exposure", {}), "gross net imbalance factor_exposure")
    inp["pending_leg"] = [fields(p, "instrument quantity reason") for p in s.get("pending", [])]
    value = (
        m.get("costs")
        if key == "execution_cost"
        else m.get("net_pnl")
        if key == "pnl_attribution"
        else m.get("drawdown")
        if key == "drawdown"
        else [fields(v, "instrument position") for v in s.get("markets", [])]
        if key == "position"
        else fields(s.get("exposure", {}), "gross net imbalance factor_exposure")
        if key == "leg_risk"
        else None
    )
    return result(
        value,
        "units per named instrument" if key == "position" else "GBP / named exposure",
        inputs=inp,
        rows=[
            fields(f, "instrument side quantity price fee t") for f in s.get("fills", [])[-10:]
        ],
        note=(
            "Only filled legs enter the account. Pending hedge intentions are not"
            " positions. Public attribution comes from the existing paired "
            "execution engine."
        ),
    )


def ground(key, state, lab, selector=None):
    if lab in ("trading", "maker"):
        return trading(key, state, selector)
    if lab == "options":
        return options(key, state, selector)
    if lab == "risk":
        return risk(key, state, selector)
    if lab == "statarb":
        return statarb(key, state, selector)
    if lab == "research":
        facts = state.get("facts", {})
        field = {
            "standard_error": "se",
            "standard_deviation": "sd",
            "sample_mean": "mean",
        }.get(key)
        return result(
            fields(facts, "ci_low ci_high")
            if key == "confidence_intervals" and "ci_low" in facts
            else facts.get(field),
            facts.get("unit"),
            inputs=fields(
                facts,
                (
                    "variant metric n mean sd se ci_low ci_high paired paired_se "
                    "unpaired_se variant_count source_digest"
                ),
            ),
            note=(
                "Existing verified research context; the experimental unit is a "
                "complete independent run. No study is launched or modified by this "
                "explanation."
            ),
        )
    return result(
        inputs=fields(state, "attempts correct incorrect"),
        note=(
            "Reading is not assessed learning evidence. Only your explicit quiz "
            "interactions can add answer evidence."
        ),
    )
