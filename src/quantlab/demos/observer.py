"""Ended-demo observer presentation; this payload must never enter public checkpoints."""

from quantlab.trading.analytics import money


def market_review(records, markouts, owned_ids):
    last = None
    timeline = []
    signals = []
    for r in records:
        executions = r.report.trades if r.report else ()
        if executions:
            last = executions[-1].price_ticks
        timeline.append(
            {
                "time_us": r.event.time_us,
                "event": r.event.kind.value,
                "latent_value_GBP": money(r.latent_after_ticks),
                "best_bid_GBP": money(r.book_after.best_bid),
                "best_ask_GBP": money(r.book_after.best_ask),
                "last_transaction_GBP": money(last),
                "action": r.reason,
                "order_side": r.order.side.value if r.order else None,
                "order_quantity": r.order.quantity if r.order else None,
                "executions": [
                    {
                        "quantity": t.quantity,
                        "price_GBP": money(t.price_ticks),
                        "trade_id": t.trade_id,
                    }
                    for t in executions
                ],
            }
        )
        if r.informed:
            a = r.informed
            d = a.decision
            signals.append(
                {
                    "time_us": r.event.time_us,
                    "latent_GBP": money(r.latent_before_ticks),
                    "signal_GBP": money(a.signal.value_ticks),
                    "signal_error_ticks": a.error_ticks,
                    "estimated_value_GBP": money(d.estimated_value_ticks),
                    "threshold_ticks": d.threshold_ticks,
                    "buy_edge_ticks": d.buy_edge_ticks,
                    "sell_edge_ticks": d.sell_edge_ticks,
                    "chosen_action": d.order.side.value if d.order else "hold",
                }
            )
    matured = [
        {
            "trade_id": m.trade_id,
            "provider_side": m.provider_side.value,
            "execution_GBP": money(m.execution_price_ticks),
            "reference": m.reference.value,
            "horizon_events": m.horizon_events,
            "maturity_time_us": m.maturity_time_us,
            "subsequent_reference_GBP": money(m.reference_after_ticks),
            "provider_markout_GBP_per_unit": money(m.provider_markout_ticks),
            "your_order": m.trade_id in owned_ids,
            "status": m.status.value,
        }
        for m in markouts
        if m.provider_markout_ticks is not None
    ]
    return {
        "timeline": timeline,
        "signals": signals,
        "matured_markouts": matured,
        "flow": [
            "Latent model value",
            "Different agent information",
            "Order decision",
            "Limit order book",
            "FIFO matching",
            "Transaction price",
        ],
        "reference_note": (
            "Latent-reference markouts are observer diagnostics. "
            "Public-midpoint markouts use a different reference; "
            "neither is realised P&L."
        ),
    }
