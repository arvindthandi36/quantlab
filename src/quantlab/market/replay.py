"""Verify recorded market sources without random draws, including a shared lab book."""

import math

from quantlab import LimitOrder, MarketOrder, OrderBook
from quantlab.agents.basic import PublicObservation
from quantlab.agents.informed import InformedTrader
from quantlab.market.config import SimulationConfig
from quantlab.market.events import EventKind
from quantlab.market.records import EventRecord, SessionResult
from quantlab.orderbook import BookSnapshot, ExecutionReport


class ReplayMarketEnvironment:
    """Replay only recorded background events; a lab interleaves its own quote actions.

    This is privileged observer evidence. Signals are re-evaluated using only
    current public quotes; no future record is handed to an agent.
    """

    def __init__(
        self,
        config: SimulationConfig,
        book: OrderBook,
        records: tuple[EventRecord, ...],
        *,
        end_time_us: int | None = None,
    ) -> None:
        if len(records) > config.max_events:
            raise ValueError("journal exceeds configured event budget")
        self.config, self._book, self._records = config, book, records
        self.end_time_us = config.duration_us if end_time_us is None else end_time_us
        if type(self.end_time_us) is not int or not 0 <= self.end_time_us <= config.duration_us:
            raise ValueError("invalid replay end time")
        self._index = 0
        self._previous_key = (-1, -1)
        self._seen: set[int] = set()
        self._latent = float(config.initial_latent_ticks)
        self._latent_count = 0
        self._last_trade = None
        self._informed = InformedTrader(
            config.informed_prior_sd_ticks,
            config.informed_cost_ticks,
            config.informed_minimum_edge_ticks,
            config.informed_uncertainty_multiplier,
        )

    @property
    def next_event_time_us(self) -> int | None:
        if self._index == len(self._records):
            return None
        return self._records[self._index].event.time_us

    def observation(self) -> PublicObservation:
        return PublicObservation(
            self._book.best_bid,
            self._book.best_ask,
            self._last_trade,
            self.config.opening_reference_ticks,
        )

    def record_external_execution(self, report: ExecutionReport) -> None:
        """Mirror caller executions when interleaving recorded background events."""
        if report.trades:
            self._last_trade = report.trades[-1].price_ticks

    def finish(self) -> None:
        if self._index != len(self._records):
            raise ValueError("journal has unprocessed background events")
        if self._latent_count != self.end_time_us // self.config.latent_step_us:
            raise ValueError("journal is missing scheduled latent updates")

    def step(self) -> EventRecord | None:
        if self._index == len(self._records):
            self.finish()
            return None
        record = self._records[self._index]
        event, config = record.event, self.config
        if type(event.time_us) is not int or not 0 < event.time_us <= self.end_time_us:
            raise ValueError("journal contains invalid event time")
        if type(event.sequence) is not int or event.sequence <= 0:
            raise ValueError("journal contains invalid event sequence")
        key = event.time_us, event.sequence
        if key <= self._previous_key or event.sequence in self._seen:
            raise ValueError("journal is out of order or repeats an event sequence")
        for value in (record.latent_before_ticks, record.latent_after_ticks):
            if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                raise ValueError("journal contains invalid latent value")
        if record.latent_before_ticks != self._latent:
            raise ValueError("journal latent value is discontinuous")
        if event.kind is not EventKind.INFORMED and record.informed is not None:
            raise ValueError("private informed audit attached to wrong event kind")
        if event.kind is EventKind.INFORMED:
            audit = record.informed
            if audit is None or config.informed_rate_per_second <= 0:
                raise ValueError("informed event has no enabled signal source/audit")
            if audit.signal.noise_sd_ticks != config.signal_noise_ticks:
                raise ValueError("signal noise differs from configured accuracy")
            if audit.error_ticks != audit.signal.value_ticks - self._latent:
                raise ValueError(
                    "recorded signal error does not reconcile with current latent value"
                )
            expected = self._informed.decide(
                f"{event.kind.value}-{event.sequence}",
                self.observation(),
                audit.signal,
                now_us=event.time_us,
            )
            if (
                expected != audit.decision
                or expected.order != record.order
                or expected.reason != record.reason
            ):
                raise ValueError(
                    "informed estimate/decision does not match its current information"
                )
        if event.kind is EventKind.LATENT:
            self._latent_count += 1
            if event.time_us != self._latent_count * config.latent_step_us:
                raise ValueError("journal latent update is off its configured schedule")
            if record.order is not None or record.report is not None:
                raise ValueError("a latent update cannot submit orders or generate trades")
        elif event.kind in (EventKind.NOISE, EventKind.LIQUIDITY, EventKind.INFORMED):
            if record.latent_before_ticks != record.latent_after_ticks:
                raise ValueError("a trader event cannot change latent value")
            if record.order is None:
                if event.kind is EventKind.LIQUIDITY or record.report is not None:
                    raise ValueError("invalid skipped trader event")
            else:
                expected_type = MarketOrder if event.kind is EventKind.LIQUIDITY else LimitOrder
                if not isinstance(record.order, expected_type):
                    raise ValueError("journal trader submitted an unsupported order type")
                if record.order.order_id != f"{event.kind.value}-{event.sequence}":
                    raise ValueError("journal order ID does not identify its source event")
                actual = self._book.submit(record.order)
                if actual != record.report:
                    raise ValueError(f"execution report mismatch at event {event.sequence}")
                if actual.trades:
                    self._last_trade = actual.trades[-1].price_ticks
        else:
            raise ValueError("journal contains unsupported event kind")
        self._book.check_invariants()
        if self._book.snapshot() != record.book_after:
            raise ValueError(f"book snapshot mismatch at event {event.sequence}")
        self._latent = record.latent_after_ticks
        self._previous_key = key
        self._seen.add(event.sequence)
        self._index += 1
        return record


def replay_session(session: SessionResult) -> BookSnapshot:
    """Verify standalone Phase 2/3 evidence; consistency does not imply authenticity."""
    if session.end_time_us != session.config.duration_us:
        raise ValueError("journal does not cover the configured horizon")
    book = OrderBook()
    environment = ReplayMarketEnvironment(session.config, book, session.events)
    submitted = cancelled = 0
    while (record := environment.step()) is not None:
        if record.report:
            submitted += record.report.requested_quantity
            cancelled += record.report.cancelled_quantity
    final_book = book.snapshot()
    resting = sum(level.quantity for level in final_book.bids + final_book.asks)
    if submitted != 2 * book.traded_volume + resting + cancelled:
        raise ValueError("replay quantity conservation failed")
    return final_book
