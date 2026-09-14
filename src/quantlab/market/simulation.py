"""Connect independent event sources to the existing matching engine."""

import platform

from quantlab import OrderBook, __version__
from quantlab.agents.basic import LiquidityTrader, NoiseTrader, PublicObservation
from quantlab.agents.informed import InformedTrader
from quantlab.market.config import SimulationConfig
from quantlab.market.events import EventKind, EventQueue
from quantlab.market.processes import exponential_wait_us, fundamental_step
from quantlab.market.public import PublicSnapshot, anonymous_book
from quantlab.market.records import EventRecord, SessionResult
from quantlab.market.signals import InformedAudit, sample_signal
from quantlab.orderbook import ExecutionReport
from quantlab.randomness import RandomStreams


class MarketEnvironment:
    """Background sources sharing a caller-owned exchange.

    The caller must separately journal its external actions.
    Each trader arrival includes decision, immediate submission and matching as
    one atomic event. There is no simulated communication latency. Initial
    scheduling order is latent, noise, liquidity, informed; equal-time ties are FIFO.
    """

    def __init__(
        self, config: SimulationConfig, book: OrderBook, *, retain_records: bool = True
    ) -> None:
        self.config = config
        self._queue = EventQueue()
        self._book = book
        self._latent_ticks = float(config.initial_latent_ticks)
        self._last_trade_ticks: int | None = None
        self._public_time_us = 0
        self._records: list[EventRecord] = []
        self._retain_records = retain_records
        self._event_count = 0
        self._failed = False
        streams = RandomStreams(config.seed)
        self._latent_rng = streams.create("market.latent")
        self._signal_rng = streams.create("market.informed.signals")
        self._arrival_rngs = {
            EventKind.NOISE: streams.create("market.noise.arrivals"),
            EventKind.LIQUIDITY: streams.create("market.liquidity.arrivals"),
            EventKind.INFORMED: streams.create("market.informed.arrivals"),
        }
        self._decision_rngs = {
            EventKind.NOISE: streams.create("market.noise.decisions"),
            EventKind.LIQUIDITY: streams.create("market.liquidity.decisions"),
        }
        self._rates = {
            EventKind.NOISE: config.noise_rate_per_second,
            EventKind.LIQUIDITY: config.liquidity_rate_per_second,
            EventKind.INFORMED: config.informed_rate_per_second,
        }
        self._noise = NoiseTrader(config.noise_price_radius_ticks, config.noise_max_quantity)
        self._liquidity = LiquidityTrader(config.liquidity_max_quantity)
        self._informed = InformedTrader(
            config.informed_prior_sd_ticks,
            config.informed_cost_ticks,
            config.informed_minimum_edge_ticks,
            config.informed_uncertainty_multiplier,
        )
        self._queue.schedule(config.latent_step_us, EventKind.LATENT)
        for kind in (EventKind.NOISE, EventKind.LIQUIDITY, EventKind.INFORMED):
            self._schedule_arrival(kind)

    @property
    def now_us(self) -> int:
        return self._queue.now_us

    @property
    def next_event_time_us(self) -> int | None:
        """Observer scheduler access; never pass this clock to normal agents."""
        event = self._queue.peek()
        return (
            event.time_us
            if event is not None and event.time_us <= self.config.duration_us
            else None
        )

    def observation(self) -> PublicObservation:
        """Expose the same past/present information available to a noise trader."""
        return PublicObservation(
            self._book.best_bid,
            self._book.best_ask,
            self._last_trade_ticks,
            self.config.opening_reference_ticks,
        )

    def record_external_execution(self, report: ExecutionReport) -> None:
        """A caller's real exchange executions are public; this consumes no RNG."""
        if report.trades:
            self._last_trade_ticks = report.trades[-1].price_ticks

    def finish(self) -> None:
        """Finish the source clock only after every event in its horizon was processed."""
        if self.next_event_time_us is not None:
            raise RuntimeError("background market still has due events")
        self.step()

    def _schedule_arrival(self, kind: EventKind) -> None:
        rate = self._rates[kind]
        if rate:
            wait = exponential_wait_us(rate, self._arrival_rngs[kind])
            self._queue.schedule(self.now_us + wait, kind)

    def step(self) -> EventRecord | None:
        """Process the next due event; None means the complete horizon was reached.

        The event cap raises rather than returning a truncated run as successful.
        A latent-process failure propagates; discard that failed simulator.
        """
        if self._failed:
            raise RuntimeError("simulation previously failed; discard this instance")
        try:
            return self._process_next()
        except Exception:
            # An event may already have changed the clock/book. Never resume it
            # as if the failed event were a successful, complete market history.
            self._failed = True
            raise

    def _process_next(self) -> EventRecord | None:
        upcoming = self._queue.peek()
        if upcoming is None or upcoming.time_us > self.config.duration_us:
            self._queue.advance_to(self.config.duration_us)
            self._public_time_us = self.now_us
            return None
        if self._event_count >= self.config.max_events:
            raise RuntimeError("event budget exceeded; shorten duration or raise max_events")
        event = self._queue.pop()
        before = self._latent_ticks
        order = report = None
        informed = None
        if event.kind is EventKind.LATENT:
            self._latent_ticks = fundamental_step(
                before,
                self.config.latent_sigma_ticks,
                self.config.latent_step_us,
                self._latent_rng,
            )
            reason = "scheduled Gaussian value update; no direct order or perfect observation"
            self._queue.schedule(event.time_us + self.config.latent_step_us, EventKind.LATENT)
        else:
            order_id = f"{event.kind.value}-{event.sequence}"
            if event.kind is EventKind.INFORMED:
                signal = sample_signal(
                    before, event.time_us, self.config.signal_noise_ticks, self._signal_rng
                )
                decision = self._informed.decide(
                    order_id, self.observation(), signal, now_us=event.time_us
                )
                informed = InformedAudit(signal, signal.value_ticks - before, decision)
            else:
                rng = self._decision_rngs[event.kind]
                decision = (
                    self._noise.decide(order_id, self.observation(), rng)
                    if event.kind is EventKind.NOISE
                    else self._liquidity.decide(order_id, rng)
                )
            order, reason = decision.order, decision.reason
            if order is not None:
                report = self._book.submit(order)
                if report.trades:
                    self._last_trade_ticks = report.trades[-1].price_ticks
            self._schedule_arrival(event.kind)
        self._book.check_invariants()
        record = EventRecord(
            event,
            before,
            self._latent_ticks,
            reason,
            order,
            report,
            self._book.snapshot(),
            informed,
        )
        self._event_count += 1
        if self._retain_records:
            self._records.append(record)
        if order is not None:
            self._public_time_us = event.time_us
        return record


class MarketSimulation(MarketEnvironment):
    """Standalone initially empty market with complete Phase 2/3 session evidence."""

    def __init__(self, config: SimulationConfig) -> None:
        super().__init__(config, OrderBook())

    def public_snapshot(self) -> PublicSnapshot:
        """Latest public update; private arrivals must not leak through timestamps.

        Time advances on submitted orders, or to the declared horizon on completion.
        The observer's internal clock remains separately available through now_us.
        """
        aliases = {
            r.order.order_id: f"order-{r.report.arrival_sequence}"
            for r in self._records
            if r.order is not None and r.report is not None
        }
        return PublicSnapshot(
            self._public_time_us,
            anonymous_book(self._book.snapshot(), aliases),
            self._last_trade_ticks,
        )

    def run(self) -> SessionResult:
        """Complete this session, including any events already processed via step()."""
        while self.step() is not None:
            pass
        return SessionResult(
            self.config,
            __version__,
            platform.python_version(),
            tuple(self._records),
            self.now_us,
        )


def run_simulation(config: SimulationConfig | None = None) -> SessionResult:
    """Run a new market without launching a UI or using global random state."""
    return MarketSimulation(config if config is not None else SimulationConfig()).run()
