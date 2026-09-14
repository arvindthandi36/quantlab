"""A new public quote source; stock orders still use the Phase 6 execution pipeline."""

from fractions import Fraction

from quantlab import LimitOrder, Side
from quantlab.market.config import SimulationConfig
from quantlab.trading.scenarios import Scenario
from quantlab.trading.session import TradingSession


class ExternalClock:
    next_event_time_us = None

    def record_external_execution(self, report):
        pass  # No hidden agents or RNG; the derivative lab supplies observed stock steps.


class UnderlyingVenue(TradingSession):
    def __init__(self, spot, *, steps, depth=1000, fee=0.001, spread_ticks=1, capture=True):
        self.retain_evidence = capture
        self.depth, self.spread_ticks = depth, spread_ticks
        ticks = round(spot * 100)
        market = SimulationConfig(
            duration_us=(steps + 1) * 1_000_000,
            opening_reference_ticks=ticks,
            initial_latent_ticks=ticks,
        )
        initial = tuple(
            (side, ticks + sign * distance, qty)
            for side, sign in (("buy", -1), ("sell", 1))
            for distance, qty in ((spread_ticks, depth), (spread_ticks + 1, depth * 4))
        )
        scenario = Scenario(
            "derivatives-stock",
            "Derivatives underlying",
            "Stock hedges execute against actual resting orders",
            market,
            initial,
            position_limit=100_000,
            cash_ticks=Fraction(0),
            fee_ticks=Fraction(str(fee)) * 100,
            automated_maker=False,
        )
        super().__init__(scenario, environment_factory=lambda c, b: ExternalClock())

    def _checkpoint(self, kind, **detail):
        if self.retain_evidence:
            super()._checkpoint(kind, **detail)

    def refresh(self, spot, step):
        ticks = round(spot * 100)
        if ticks <= self.spread_ticks + 1:
            raise ValueError("stock observation too low for positive executable quote prices")
        self._mark()
        self._time(step * 1_000_000)
        self.public_number += 1
        for level in self.book.snapshot().bids + self.book.snapshot().asks:
            for order in level.orders:
                if order.order_id not in self.owners:
                    self._cancel(order.order_id)
        for side in (Side.BUY, Side.SELL):
            sign = -1 if side == Side.BUY else 1
            for level, (distance, quantity) in enumerate(
                ((self.spread_ticks, self.depth), (self.spread_ticks + 1, self.depth * 4))
            ):
                order = LimitOrder(
                    f"stock-{step}-{side.value}-{level}",
                    side,
                    quantity,
                    ticks + sign * distance,
                )
                midpoint = self.book.snapshot().mid_price_ticks
                report = self.book.submit(order)
                self._fills(report, midpoint)
        self.revision += 1
        self._public_event("Observed stock move; external FIFO liquidity refreshed")
        self._checkpoint("observed-stock", spot_ticks=ticks)
