"""Public-only diagnostics. Money is exact internally; numeric chart values are views."""

import math
from decimal import Decimal, localcontext
from fractions import Fraction


def money(ticks, tick_size="0.01", places=5):
    if ticks is None:
        return None
    amount = Fraction(ticks) * Fraction(tick_size)
    with localcontext() as context:
        context.prec = 40
        value = Decimal(amount.numerator) / Decimal(amount.denominator)
        return format(value, f".{places}f")


def quant_metrics(book, tape):
    bid = sum(level.quantity for level in book.bids[:5])
    ask = sum(level.quantity for level in book.asks[:5])
    prices = [t["price_ticks"] for t in tape[-21:]]
    returns = [math.log(b / a) for a, b in zip(prices, prices[1:], strict=False)]
    recent = tape[-20:]
    buy = sum(t["quantity"] for t in recent if t["aggressor_side"] == "buy")
    sell = sum(t["quantity"] for t in recent if t["aggressor_side"] == "sell")
    return {
        "depth_imbalance_top_5": (bid - ask) / (bid + ask) if bid + ask else None,
        "last_log_return": returns[-1] if returns else None,
        "realised_volatility_trade_window": math.sqrt(sum(r * r for r in returns))
        if returns
        else None,
        "return_observations": len(returns),
        "trade_window_count": len(recent),
        "aggressor_buy_volume": buy,
        "aggressor_sell_volume": sell,
        "flow_imbalance": (buy - sell) / (buy + sell) if buy + sell else None,
    }


GLOSSARY = {
    "Bid": "A resting offer to buy. Best bid is the highest visible buying price.",
    "Ask": "A resting offer to sell. Best ask is the lowest visible selling price.",
    "Spread": "Best ask minus best bid. It is a price gap, not guaranteed profit.",
    "Mid": "Halfway between best bid and ask. Nobody promises to trade there.",
    "Market order": "Trade now against available opposite orders. Unfilled remainder cancels.",
    "Limit order": "Buy no higher, or sell no lower, than your limit. The remainder queues.",
    "Position": "Units owned: positive is long, negative is short. Buys add; sells subtract.",
    "P&L": "Profit and loss from opening equity. The public mark values unsold inventory.",
    "VWAP": "Sum of each fill's price × quantity, divided by total filled units.",
    "Partial fill": "Only some requested units traded. A limit remainder may keep waiting.",
}
