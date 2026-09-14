"""Small sessions on the existing matching, accounting and synthetic information engines."""

from dataclasses import replace

from quantlab.demos import SEED
from quantlab.demos.models import Evidence, Moment, choice
from quantlab.demos.projections import calculation, point
from quantlab.research.codec import plain
from quantlab.trading.replay import journal
from quantlab.trading.scenarios import select_scenario
from quantlab.trading.session import TradingSession

LIMITS = (
    (
        "One synthetic venue with immediate order arrival, finite depth "
        "and no communication latency."
    ),
    (
        "P&L uses a public mark. Marked gains do not establish decision "
        "quality or guarantee liquidation."
    ),
)


def order_session(*, market=False, book=None, initial_position=0):
    base = select_scenario(seed=SEED, duration_seconds=20)
    config = replace(
        base.market,
        duration_us=5_000_000,
        noise_rate_per_second=1 if market else 0,
        liquidity_rate_per_second=0.6 if market else 0,
        informed_rate_per_second=2 if market else 0,
    )
    return TradingSession(
        replace(
            base,
            market=config,
            automated_maker=False,
            initial_position=initial_position,
            position_limit=50,
            initial_book=book
            or (
                ("buy", 9999, 10),
                ("buy", 9998, 20),
                ("sell", 10001, 3),
                ("sell", 10002, 4),
                ("sell", 10004, 8),
            ),
        )
    )


def act(s, kind, **p):
    r = s.command(kind, **p)
    if not r.get("ok", True):
        raise ValueError("Demo engine rejected its instruction: " + str(r))
    return r


def build(spec, branch="full"):
    s = order_session(initial_position=8 if spec.builder == "skew" else 0)
    if spec.builder == "skew":
        s = TradingSession(s.scenario, mode="manual_maker")
    moments = []

    def event(key, title, action, concept, kind, payload, question=None, **extra):
        before = point(s.public_snapshot())
        act(s, kind, **payload)
        moments.append(
            Moment(
                key,
                title,
                action,
                concept,
                before,
                point(s.public_snapshot()),
                question,
                **extra,
            )
        )

    if spec.builder in ("order", "partial"):
        q = 10 if spec.builder == "order" else 20
        event(
            "submit",
            "A buy order meets finite depth",
            f"Submit BUY {q} MARKET",
            "vwap",
            "order",
            dict(side="buy", quantity=q, order_type="market"),
            choice(
                "vwap",
                "Will every executed unit trade at the best ask?",
                hints=(
                    "Count units available at the cheapest ask.",
                    "The matching engine takes cheaper asks before dearer ones.",
                ),
            ),
            observation=(
                "An ask is an offer to sell. The lowest ask is cheapest. Read "
                "quantity as units available at that price."
            ),
            result_note=(
                "Each fill is priced at the resting seller's quote. The order's "
                "executed VWAP weights those actual prices by units; fees are "
                "booked separately."
            ),
            expected_event="Market order; FIFO executions; exact account reconciliation",
            capture_before="order-before-submit",
            capture_after="order-after-multifill",
        )
    elif spec.builder == "queue":
        event(
            "rest",
            "Join an existing price level",
            "Place BUY 2 LIMIT at £99.99",
            "queue_priority",
            "order",
            dict(side="buy", quantity=2, order_type="limit", price="99.99"),
            choice(
                "queue_priority",
                "Does joining the bid let your order jump ahead of older orders?",
            ),
        )
        event(
            "cancel",
            "Withdraw the unfilled instruction",
            "Cancel your resting order",
            "limit_orders",
            "cancel",
            {"order_id": "user-1"},
            choice("limit_orders", "Does cancelling a resting order undo earlier trades?"),
        )
    elif spec.builder == "long_short":
        event(
            "long",
            "Buy units",
            "BUY 3 MARKET",
            "position",
            "order",
            dict(side="buy", quantity=3, order_type="market"),
            choice(
                "position",
                "Which way does inventory move after a buy?",
                correct="up",
                options=(("up", "Increases"), ("down", "Decreases")),
            ),
        )
        event(
            "short",
            "Sell more than you own",
            "SELL 5 MARKET",
            "unrealised_pnl",
            "order",
            dict(side="sell", quantity=5, order_type="market"),
            choice(
                "position",
                "After owning 3 and selling 5, is your position short?",
                correct="yes",
            ),
        )
    else:
        from quantlab.explainability.sandbox import inventory

        snapshot = s.public_snapshot()
        result = inventory(snapshot, {"inventory": -8, "sensitivity": 0.5, "half_spread": 2})
        moments.append(
            Moment(
                "skew",
                "Quote with inventory",
                "Compare the existing quote policy at long and short inventory",
                "quote_skew",
                point(snapshot),
                calculation(result, note=result["note"]),
                choice("inventory", "Does a wider quoted spread guarantee a profitable fill?"),
            )
        )
    act(s, "end")
    return Evidence(
        spec,
        moments,
        {"seed": SEED, "scenario": "predeclared finite book", "branch": branch},
        LIMITS,
        journal(s),
    )


def market(spec, branch="full"):
    picked = spec.builder == "picked_off"
    s = order_session(
        market=True, book=(("buy", 10004, 20), ("sell", 10006, 20)) if picked else None
    )
    if picked:
        # Explicit controlled stale quote, fixed before sampling; no seed/outcome search.
        base = s.scenario
        s = TradingSession(
            replace(
                base,
                market=replace(
                    base.market,
                    initial_latent_ticks=10020,
                    noise_rate_per_second=1,
                    liquidity_rate_per_second=0.6,
                ),
            )
        )
        act(s, "order", side="sell", quantity=3, order_type="limit", price="100.05")
    moments = []
    prior = point(s.public_snapshot())
    while s.status != "ended":
        act(s, "step_event")
        current = point(s.public_snapshot())
        if current["core"]["public_event"] != prior["core"]["public_event"]:
            idx = len(moments)
            moments.append(
                Moment(
                    f"market-{idx}",
                    "The next public market update",
                    "Advance to the next public event",
                    "markouts" if picked else "current_price",
                    prior,
                    current,
                    choice(
                        "adverse_selection" if picked else "current_price",
                        "Does seeing a trade establish that the buyer had better information?"
                        if picked
                        else "Must the next transaction price equal an unseen model value?",
                    )
                    if idx == 0
                    else None,
                    observation=(
                        "You see public quotes and trades. A participant's private signal "
                        "and the model's latent value are not part of this view."
                    ),
                    result_note=(
                        "The public tape records an execution at a resting quote. A "
                        "participant's identity or private motive cannot be inferred from "
                        "this fill alone."
                    ),
                    capture_before=(
                        "picked-off-before-fill" if picked else "synthetic-before-event"
                    )
                    if idx == 0
                    else None,
                    capture_after=(
                        "picked-off-after-event" if picked else "synthetic-after-event"
                    )
                    if idx == 0
                    else None,
                )
            )
            prior = current
    # Limit presentation to a representative chronological sample, always keep final maturity.
    if len(moments) > 6:
        moments = moments[:5] + moments[-1:]
    records = (
        s.environment._records
    )  # Trusted builder only; never public projections or questions.
    import platform

    from quantlab import __version__
    from quantlab.analytics.markouts import analyse_markouts
    from quantlab.market.records import SessionResult

    session = SessionResult(
        s.scenario.market, __version__, platform.python_version(), tuple(records), s.now_us
    )
    audit = []
    for r in records:
        audit.append(
            plain(
                {
                    "event": r.event,
                    "latent_before_ticks": r.latent_before_ticks,
                    "latent_after_ticks": r.latent_after_ticks,
                    "reason": r.reason,
                    "informed": r.informed,
                    "order": r.order,
                    "executions": r.report.trades if r.report else [],
                }
            )
        )
    from quantlab.demos.observer import market_review

    markouts = analyse_markouts(session)
    review = market_review(
        records, markouts, {t["trade_id"] for t in s.public_snapshot()["trades"]}
    )
    return Evidence(
        spec,
        moments,
        {"seed": SEED, "scenario": "controlled synthetic information experiment"},
        LIMITS
        + (
            (
                "The stale-quote setup deliberately starts with a model value "
                "different from public quotes. Its value and noisy signals are "
                "revealed only in explicit ended-demo hindsight."
            ),
            (
                "A negative provider markout can occur without informed trading. "
                "Observer latent and public midpoint references are different "
                "diagnostics, not realised P&L."
            ),
        ),
        journal(s),
        private={
            "label": "OBSERVER ONLY · completed model path · ticks, not pounds",
            "events": audit,
            "markouts": plain(markouts),
            "review": review,
            "maker_saw": "Public book, own fills and inventory; no signal or latent value.",
            ("informed_saw"): (
                "Public reference plus a current noisy signal. Realised signal "
                "error was unavailable to the trader."
            ),
        },
    )
