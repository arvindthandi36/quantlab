"""Bounded detached hypotheticals, exclusively through approved financial APIs."""

from dataclasses import asdict, replace
from fractions import Fraction

from quantlab.domain import LimitOrder, MarketOrder, PriceGrid, Side
from quantlab.execution import vwap
from quantlab.explainability.evidence import option_inputs
from quantlab.market_making.config import MakerConfig, Strategy
from quantlab.market_making.quotes import MakerObservation, plan_quotes
from quantlab.options.models import PricingInputs, number
from quantlab.options.pricing import greeks, price
from quantlab.orderbook import OrderBook
from quantlab.portfolio.accounting import MakerAccount
from quantlab.risk.analytics import RiskSettings, linear_risk
from quantlab.risk.portfolio import Portfolio, Position
from quantlab.strategies.market_making import quote_request


def pricing_inputs(snapshot):
    x = option_inputs(snapshot)
    if x["spot"] is None or x["time_years"] is None:
        raise ValueError("Choose an available option at this public point")
    return x["option_type"], PricingInputs(
        **{
            k: x[k]
            for k in ("spot", "strike", "time_years", "volatility", "rate", "dividend_yield")
        }
    )


def portfolio_from_public(p):
    names = Position.__dataclass_fields__
    rows = tuple(
        Position(**{k: v for k, v in row.items() if k in names})
        for row in p.get("positions", [])
    )
    names = Portfolio.__dataclass_fields__
    return Portfolio(
        positions=rows, **{k: v for k, v in p.items() if k in names and k != "positions"}
    )


def _summary(p, settings, covariance=None):
    return dict(portfolio=p.public(), linear_risk=linear_risk(p, settings, covariance))


def volatility(snapshot, p, risk_snapshot=None):
    if set(p) - {"volatility", "spot", "elapsed_days", "rate"}:
        raise ValueError("Unknown option hypothetical input")
    kind, x = pricing_inputs(snapshot)
    new = replace(
        x,
        volatility=number(p.get("volatility", x.volatility), "annual volatility", 0, 3),
        spot=number(p.get("spot", x.spot), "spot GBP", 0.01, 1e8),
        rate=number(p.get("rate", x.rate), "annual rate", -1, 1),
        time_years=x.time_years
        - number(p.get("elapsed_days", 0), "elapsed days", 0, x.time_years * 365) / 365,
    )

    def show(inputs):
        return dict(
            inputs=asdict(inputs),
            value=price(kind, inputs),
            greeks=greeks(kind, inputs).public(),
        )

    out = dict(
        before=show(x),
        after=show(new),
        controlled_inputs=p,
        note=(
            "Isolated model repricing. No quote, trade, mark or account is "
            "changed. Greeks are per underlying unit; vega uses a 1.0 volatility "
            "change."
        ),
    )
    if risk_snapshot:
        r = risk_snapshot["report"]
        original = portfolio_from_public(r["portfolio"])
        rows = []
        for row in original.positions:
            if row.kind == "stock":
                rows.append(row)
            else:
                moved = replace(row, volatility=new.volatility)
                rows.append(replace(moved, mark=price(moved.kind, moved.inputs())))
        hypothetical = replace(
            original, positions=tuple(rows), source="Hypothetical all-option IV replacement"
        )
        settings = RiskSettings(**r["settings"])
        out["portfolio_risk"] = dict(
            before=_summary(original, settings, r["covariance"]),
            after=_summary(hypothetical, settings, r["covariance"]),
            note=(
                "All option IV inputs replaced; stock marks and return covariance "
                "held fixed. Risk shown is the approved fast delta-normal "
                "approximation, not a new full Monte Carlo VaR. Model prices replace "
                "quoted option marks, so quote/model basis also changes."
            ),
        )
    return out


def correlation(snapshot, p):
    if set(p) != {"correlation"}:
        raise ValueError("Supply hypothetical correlation only")
    r = snapshot["report"]
    settings = RiskSettings(**r["settings"])
    rho = number(p["correlation"], "three-factor common correlation", -0.5, 1)
    changed = replace(settings, correlation=rho)
    portfolio = portfolio_from_public(r["portfolio"])
    return dict(
        before=dict(
            covariance=r["covariance"], **_summary(portfolio, settings, r["covariance"])
        ),
        after=dict(covariance=changed.covariance().tolist(), **_summary(portfolio, changed)),
        controlled_inputs=p,
        note=(
            "Hypothetical common correlation across the three named factors; "
            "current positions and configured daily volatilities held fixed. Any "
            "custom covariance is replaced in this hypothesis. Only the fast "
            "delta-normal risk API is called; no Monte Carlo or live limit "
            "update."
        ),
    )


def order_size(snapshot, p):
    if set(p) - {"quantity", "side"} or "quantity" not in p:
        raise ValueError("Supply quantity and optional side")
    size = p["quantity"]
    if type(size) is not int or not 1 <= size <= 10000:
        raise ValueError("Hypothetical quantity must be 1–10,000 whole units")
    side = Side(p.get("side", "buy"))
    book = OrderBook()
    grid = PriceGrid()
    count = 0
    for name, direction in (("bids", Side.BUY), ("asks", Side.SELL)):
        for level in snapshot.get(name, []):
            queue = level.get("queue") or [{"quantity": level["quantity"]}]
            for item in queue:
                count += 1
                if count > 10000:
                    raise ValueError("Frozen book exceeds 10,000-order sandbox budget")
                book.submit(
                    LimitOrder(
                        f"frozen-{count}",
                        direction,
                        item["quantity"],
                        grid.to_ticks(level["price"]),
                    )
                )
    report = book.submit(MarketOrder("hypothetical", side, size))
    book.check_invariants()
    rows = [
        dict(price=f"{t.price_ticks / 100:.2f}", quantity=t.quantity) for t in report.trades
    ]
    value = vwap((r["price"], r["quantity"]) for r in rows)
    return dict(
        submitted=size,
        side=side.value,
        filled=report.executed_quantity,
        unfilled=size - report.executed_quantity,
        vwap=None if value is None else float(value),
        exact_vwap_gbp=None if value is None else str(value),
        fills=rows,
        note=(
            "HYPOTHETICAL SNAPSHOT ANALYSIS. Existing FIFO matching against "
            "frozen displayed liquidity, including displayed own orders. No live "
            "account, self-trade policy, fees, reserved capacity or subsequent "
            "market reaction is simulated. Unfilled market remainder cancels."
        ),
    )


def inventory(snapshot, p):
    if set(p) - {"inventory", "sensitivity", "half_spread"} or "inventory" not in p:
        raise ValueError("Supply inventory and optional sensitivity/half-spread in ticks")
    q = p["inventory"]
    hard = snapshot["account"]["position_limit"]
    if type(q) is not int or abs(q) > hard:
        raise ValueError(
            "Hypothetical inventory must be whole units within the displayed limit"
        )
    if snapshot.get("reference") is None:
        raise ValueError("A public reference is required")
    reference = Fraction(snapshot["reference"]) * 100
    sensitivity = number(p.get("sensitivity", 0.5), "sensitivity ticks/unit", 0, 10)
    spread = number(p.get("half_spread", 2), "half spread ticks", 0.01, 100)
    config = MakerConfig(
        strategy=Strategy.INVENTORY,
        hard_limit=hard,
        soft_limit=max(1, hard // 2),
        inventory_skew_ticks=str(sensitivity),
        half_spread_ticks=str(spread),
    )

    def show(quantity):
        a = MakerAccount(
            Fraction(1000000), reference, hard_limit=hard, initial_position=quantity
        )
        bid = (
            None
            if snapshot.get("best_bid") is None
            else PriceGrid().to_ticks(snapshot["best_bid"])
        )
        ask = (
            None
            if snapshot.get("best_ask") is None
            else PriceGrid().to_ticks(snapshot["best_ask"])
        )
        obs = MakerObservation(
            snapshot.get("time_us", 0),
            bid,
            ask,
            bid,
            ask,
            reference,
            "frozen public reference",
            a.snapshot(),
            (),
            (),
        )
        request = quote_request(obs, config)
        plan = plan_quotes(obs, request, config)
        return dict(
            inventory=quantity,
            request={
                k: str(v) if isinstance(v, Fraction) else v for k, v in asdict(request).items()
            },
            plan={k: str(v) if isinstance(v, Fraction) else v for k, v in asdict(plan).items()},
        )

    return dict(
        before=show(snapshot["account"]["position"]),
        after=show(q),
        configuration={
            k: str(v) if isinstance(v, Fraction) else v.value if isinstance(v, Strategy) else v
            for k, v in asdict(config).items()
        },
        note=(
            "Hypothetical application of the approved inventory strategy; the "
            "live manual quote rule is unchanged. Beyond the soft limit, the core"
            " increases skew and reduces the inventory-increasing side. Outward "
            "grid rounding and passive-price adjustments still apply."
        ),
    )


def threshold(snapshot, p):
    from quantlab.statarb.statistics import CausalModel
    from quantlab.statarb.strategy import Rules, decision

    if set(p) != {"entry"}:
        raise ValueError("Supply a hypothetical entry threshold")
    rules = Rules(**snapshot["rules"])
    changed = replace(rules, entry=number(p["entry"], "entry threshold", 0, 100))
    data = snapshot["history"][: snapshot["t"] + 1]
    if len(data) > 2001:
        raise ValueError("Threshold analysis is limited to 2,001 published rows")
    model = CausalModel(
        window=rules.window, z_window=rules.z_window, mode=rules.mode, block=rules.block
    )
    rows = []
    for t in range(len(data)):
        sig = model.at(data, t)
        if sig.get("z") is None:
            continue
        a, why_a = decision(rules, sig)
        b, why_b = decision(changed, sig)
        rows.append(
            dict(t=t, z=sig["z"], before=a, after=b, before_reason=why_a, after_reason=why_b)
        )
    return dict(
        before_entry=rules.entry,
        after_entry=changed.entry,
        observations=len(data),
        rows=rows,
        note=(
            "Published synthetic session prefix only. Each signal is evaluated as"
            " if flat through the approved decision API; this is a qualification "
            "scan, not a backtest, execution forecast or registered evaluation. "
            "Holdout research results are never accessed or changed."
        ),
    )
