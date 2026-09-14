"""Interleave public maker decisions with the unchanged background event sources."""

import platform

from quantlab import LimitOrder, OrderBook, Side, __version__
from quantlab.market.config import SimulationConfig
from quantlab.market.simulation import MarketEnvironment
from quantlab.market_making.config import MakerConfig
from quantlab.market_making.quotes import MakerObservation, QuoteRequest, plan_quotes
from quantlab.market_making.records import LabRecord, LabResult, public_reference
from quantlab.portfolio.accounting import AccountingError, MakerAccount, MakerFill
from quantlab.strategies.market_making import quote_request


class MarketMakingLab:
    """Manual decisions pause on a public fixed clock, never on private agent arrivals.

    advance_to_decision() → observe → decide(request) → advance_to_decision().
    run() supplies the configured baseline automatically. Full records are observer-only.
    """

    def __init__(
        self,
        market: SimulationConfig,
        maker: MakerConfig,
        *,
        environment_factory=None,
        retain_records: bool = True,
        record_sink=None,
    ):
        self.market_config, self.maker_config = market, maker
        self._book = OrderBook()
        self._environment = (
            MarketEnvironment(market, self._book, retain_records=retain_records)
            if environment_factory is None
            else environment_factory(market, self._book)
        )
        self._retain_records = retain_records
        self._record_sink = record_sink
        self._account = MakerAccount(
            maker.initial_cash_ticks,
            market.opening_reference_ticks,
            hard_limit=maker.hard_limit,
        )
        self._owned: set[str] = set()
        self._current: list[str] = []
        self._records: list[LabRecord] = []
        self._decision_number = 0
        self._public_number = 0
        self._now_us = 0
        self._waiting = False
        self._finished = False
        self._failed = False
        self._submitted = 0
        self._cancelled = 0

    def _healthy(self) -> None:
        if self._failed:
            raise RuntimeError("lab previously failed; discard this instance")

    def _reference(self):
        return public_reference(
            self._book.snapshot(),
            self._owned,
            self._environment.observation().last_trade_ticks,
            self.market_config.opening_reference_ticks,
        )

    def _own_quotes(self):
        return tuple(
            order for key in self._current if (order := self._book.get_order(key)) is not None
        )

    def observation(self) -> MakerObservation:
        """Only available at an ordinary scheduled decision, not private event boundaries."""
        self._healthy()
        if not self._waiting:
            raise RuntimeError("advance to a public decision before requesting observation")
        reference, source, bid, ask = self._reference()
        return MakerObservation(
            self._now_us,
            self._book.best_bid,
            self._book.best_ask,
            bid,
            ask,
            reference,
            source,
            self._account.snapshot(),
            self._own_quotes(),
            self._account.fills[-5:],
        )

    def _check(self) -> None:
        self._book.check_invariants()
        self._account.check_invariants()
        active = [
            o
            for level in self._book.snapshot().bids + self._book.snapshot().asks
            for o in level.orders
            if o.order_id in self._owned
        ]
        if {o.order_id for o in active} != {o.order_id for o in self._own_quotes()}:
            raise AccountingError("stale owned order escaped current quote registry")
        for side in Side:
            orders = [o for o in active if o.side is side]
            capacity = (
                self.maker_config.hard_limit - self._account.inventory
                if side is Side.BUY
                else self.maker_config.hard_limit + self._account.inventory
            )
            if len(orders) > 1 or sum(o.remaining_quantity for o in orders) > capacity:
                raise AccountingError("resting-order reservation breaches inventory capacity")
        resting = sum(
            level.quantity for level in self._book.snapshot().bids + self._book.snapshot().asks
        )
        if self._submitted != 2 * self._book.traded_volume + resting + self._cancelled:
            raise AccountingError("lab global order quantity does not reconcile")

    def _append(
        self,
        kind,
        *,
        market=None,
        request=None,
        plan=None,
        cancelled=(),
        placed=(),
        reports=(),
        fills=(),
    ) -> LabRecord:
        reference, source, _, _ = self._reference()
        self._account.mark(reference)
        self._check()
        record = LabRecord(
            self._now_us,
            kind,
            self._public_number,
            market,
            request,
            plan,
            cancelled,
            placed,
            reports,
            self._book.snapshot(),
            self._own_quotes(),
            source,
            self._account.snapshot(),
            fills,
        )
        if self._retain_records:
            self._records.append(record)
        if self._record_sink is not None:
            self._record_sink(record)
        return record

    def _market_step(self) -> None:
        reference, _, _, _ = self._reference()
        midpoint = self._book.mid_price_ticks
        self._account.mark(reference)
        event = self._environment.step()
        if event is None:
            raise RuntimeError("market source ended before its announced next event")
        self._now_us = event.event.time_us
        fills = []
        if event.report is not None:
            self._public_number += 1
            self._submitted += event.report.requested_quantity
            self._cancelled += event.report.cancelled_quantity
            for trade in event.report.trades:
                if trade.taker_order_id in self._owned:
                    raise AccountingError("maker unexpectedly took liquidity")
                if trade.maker_order_id in self._owned:
                    fill = MakerFill(
                        trade.trade_id,
                        self._now_us,
                        self._public_number,
                        trade.aggressor_side.opposite,
                        trade.quantity,
                        trade.price_ticks,
                        self.maker_config.fee_ticks * trade.quantity,
                        reference,
                        midpoint,
                    )
                    self._account.apply(fill)
                    fills.append(fill)
        self._append("market", market=event, fills=tuple(fills))

    def _cancel_quotes(self):
        cancelled = tuple(
            order for key in self._current if (order := self._book.cancel(key)) is not None
        )
        self._cancelled += sum(order.remaining_quantity for order in cancelled)
        self._current.clear()
        return cancelled

    def advance_to_decision(self) -> MakerObservation | None:
        """Process a whole public decision interval; return None after horizon completion."""
        self._healthy()
        if self._waiting:
            return self.observation()
        if self._finished:
            return None
        try:
            decision_time = self._decision_number * self.maker_config.refresh_us
            end = min(decision_time, self.market_config.duration_us)
            while (
                next_time := self._environment.next_event_time_us
            ) is not None and next_time <= end:
                self._market_step()
            self._now_us = end
            self._account.mark(self._reference()[0])
            if end == self.market_config.duration_us:
                self._environment.finish()
                cancelled = self._cancel_quotes()
                if cancelled:
                    self._public_number += 1
                self._append("end", cancelled=cancelled)
                self._finished = True
                return None
            if self._decision_number >= self.maker_config.max_decisions:
                raise RuntimeError("maker decision budget exceeded")
            self._waiting = True
            return self.observation()
        except Exception:
            self._failed = True
            raise

    def decide(self, request: QuoteRequest) -> LabRecord:
        """Replace both sides atomically; safety adjusts sizes/prices with explicit reasons."""
        self._healthy()
        if not isinstance(request, QuoteRequest):
            raise TypeError("decision must be a validated QuoteRequest")
        observation = self.observation()
        plan = plan_quotes(observation, request, self.maker_config)
        try:
            self._check()
            cancelled = self._cancel_quotes()
            orders, reports = [], []
            for side, price, size in (
                (Side.BUY, plan.bid_ticks, plan.bid_size),
                (Side.SELL, plan.ask_ticks, plan.ask_size),
            ):
                if size:
                    order = LimitOrder(
                        f"mm-{self._decision_number}-{side.value}", side, size, price
                    )
                    report = self._book.submit(order)
                    if report.trades or report.resting_quantity != size:
                        raise AccountingError(
                            "passive quote unexpectedly executed on submission"
                        )
                    self._owned.add(order.order_id)
                    self._current.append(order.order_id)
                    self._submitted += size
                    orders.append(order)
                    reports.append(report)
            if cancelled or orders:
                self._public_number += 1
            record = self._append(
                "quote",
                request=request,
                plan=plan,
                cancelled=cancelled,
                placed=tuple(orders),
                reports=tuple(reports),
            )
            self._decision_number += 1
            self._waiting = False
            return record
        except Exception:
            self._failed = True
            raise

    def observer_records(self) -> tuple[LabRecord, ...]:
        """Privileged history for research/debug; never a strategy or normal-view input."""
        if not self._retain_records:
            raise RuntimeError("lightweight mode does not retain an event journal")
        return tuple(self._records)

    def result(self) -> LabResult:
        self._healthy()
        if not self._finished:
            raise RuntimeError("lab has not completed its configured horizon")
        if not self._retain_records:
            raise RuntimeError("lightweight mode exposes results through its record sink")
        return LabResult(
            self.market_config,
            self.maker_config,
            __version__,
            platform.python_version(),
            tuple(self._records),
        )

    def run_to_completion(self) -> None:
        """Complete automatic decisions; a batch sink can retain only summary evidence."""
        while (observation := self.advance_to_decision()) is not None:
            self.decide(quote_request(observation, self.maker_config))

    def run(self) -> LabResult:
        self.run_to_completion()
        return self.result()


def run_lab(
    market: SimulationConfig | None = None, maker: MakerConfig | None = None
) -> LabResult:
    """Fresh automatic session; independent named market streams preserve comparable seeds."""
    return MarketMakingLab(
        market or SimulationConfig(informed_rate_per_second=1), maker or MakerConfig()
    ).run()
