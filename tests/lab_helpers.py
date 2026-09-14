"""Declared deterministic order paths; every consequence uses the actual matcher."""

from dataclasses import replace

from quantlab import LimitOrder
from quantlab.agents.basic import PublicObservation
from quantlab.market.config import SimulationConfig
from quantlab.market.events import EventKind, ScheduledEvent
from quantlab.market.records import EventRecord
from quantlab.market_making.config import MakerConfig, Strategy
from quantlab.market_making.lab import MarketMakingLab
from quantlab.market_making.quotes import QuoteRequest


def scripted_lab(instructions, *, maker=None, duration=5):
    market = SimulationConfig(
        duration_us=duration,
        latent_step_us=duration + 1,
        opening_reference_ticks=100,
        initial_latent_ticks=100,
    )

    class ScriptedFeed:
        def __init__(self, config, book):
            self.book, self.index, self.last = book, 0, None

        @property
        def next_event_time_us(self):
            return instructions[self.index][0] if self.index < len(instructions) else None

        def observation(self):
            return PublicObservation(self.book.best_bid, self.book.best_ask, self.last, 100)

        def finish(self):
            assert self.index == len(instructions)

        def step(self):
            time, order = instructions[self.index]
            self.index += 1
            kind = EventKind.NOISE if isinstance(order, LimitOrder) else EventKind.LIQUIDITY
            order = replace(order, order_id=f"{kind.value}-{self.index}")
            report = self.book.submit(order)
            if report.trades:
                self.last = report.trades[-1].price_ticks
            return EventRecord(
                ScheduledEvent(time, self.index, kind),
                100.0,
                100.0,
                "declared test instruction",
                order,
                report,
                self.book.snapshot(),
            )

    return MarketMakingLab(
        market,
        maker or MakerConfig(strategy=Strategy.MANUAL, refresh_us=2),
        environment_factory=ScriptedFeed,
    )


def finish_manual(lab, request=None):
    request = QuoteRequest() if request is None else request
    while lab.advance_to_decision() is not None:
        lab.decide(request)
    return lab.result()
