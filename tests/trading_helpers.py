from dataclasses import replace

from quantlab import MarketOrder, Side
from quantlab.market.events import EventKind, ScheduledEvent
from quantlab.market.records import EventRecord
from quantlab.trading.scenarios import SCENARIOS
from quantlab.trading.session import TradingSession


def quiet(**overrides):
    base = SCENARIOS["normal"]
    market = replace(
        base.market,
        duration_us=10_000_000,
        noise_rate_per_second=0,
        liquidity_rate_per_second=0,
        informed_rate_per_second=0,
    )
    return replace(base, market=market, automated_maker=False, **overrides)


def order(session, side="buy", quantity=1, price=None):
    payload = {
        "side": side,
        "quantity": quantity,
        "order_type": "market" if price is None else "limit",
    }
    if price is not None:
        payload["price"] = price
    return session.command("order", **payload)


class ScriptedLiquidity:
    """Explicit deterministic test input; real matching, never scripted executions."""

    def __init__(self, config, book, actions):
        self.config, self.book, self.actions = config, book, list(actions)
        self.index = 0

    @property
    def next_event_time_us(self):
        return self.actions[self.index][0] if self.index < len(self.actions) else None

    def record_external_execution(self, report):
        pass

    def step(self):
        time, side, qty = self.actions[self.index]
        self.index += 1
        event = ScheduledEvent(time, self.index, EventKind.LIQUIDITY)
        command = MarketOrder(f"liquidity_arrival-{self.index}", Side(side), qty)
        report = self.book.submit(command)
        value = float(self.config.initial_latent_ticks)
        return EventRecord(
            event,
            value,
            value,
            "test liquidity need",
            command,
            report,
            self.book.snapshot(),
            None,
        )


def scripted(actions, **overrides):
    # No latent update falls within this short fixture's horizon.
    scenario = quiet(**overrides)
    scenario = replace(scenario, market=replace(scenario.market, duration_us=900_000))
    return TradingSession(
        scenario, environment_factory=lambda c, b: ScriptedLiquidity(c, b, actions)
    )
