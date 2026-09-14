"""N independent FIFO venues driven by synchronized already-public observations."""

from fractions import Fraction

import numpy as np

from quantlab import LimitOrder, Side
from quantlab.options.underlying import UnderlyingVenue


class PublicVenue(UnderlyingVenue):
    def __init__(self, spot, *, steps=1000, depth=40, fee=0.005, spread_ticks=1, capture=True):
        self.published_ticks = round(spot * 100)
        self.quote_counter = 0
        super().__init__(
            spot,
            steps=steps,
            depth=max(1, depth),
            fee=fee,
            spread_ticks=spread_ticks,
            capture=capture,
        )
        if depth == 0:
            self.liquidity(0)

    def _reference(self, owner="user"):
        return Fraction(self.published_ticks), "published synchronized reference"

    def liquidity(self, depth):
        if type(depth) is not int or not 0 <= depth <= 10000:
            raise ValueError("Depth must be 0–10000 whole units at best price")
        self.depth = depth
        self.refresh(self.published_ticks / 100, self.now_us // 1_000_000)

    def refresh(self, spot, step):
        ticks = round(spot * 100)
        if ticks <= self.spread_ticks + 1:
            raise ValueError("Published price cannot support positive executable quotes")
        self._time(step * 1_000_000)
        self.published_ticks = ticks
        self.quote_counter += 1
        self.public_number += 1
        for level in self.book.snapshot().bids + self.book.snapshot().asks:
            for order in level.orders:
                if order.order_id not in self.owners:
                    self._cancel(order.order_id)
        if self.depth:
            for side in (Side.BUY, Side.SELL):
                sign = 1 if side == Side.SELL else -1
                for level, (distance, qty) in enumerate(
                    ((self.spread_ticks, self.depth), (self.spread_ticks + 1, self.depth * 4))
                ):
                    order = LimitOrder(
                        f"sa-{self.quote_counter}-{side.value}-{level}",
                        side,
                        qty,
                        ticks + sign * distance,
                    )
                    report = self.book.submit(order)
                    self._fills(report, Fraction(ticks))
        self.revision += 1
        self._public_event("Public observation published; finite FIFO quotes refreshed")
        self.check_invariants()


class MultiMarket:
    def __init__(
        self,
        identifiers,
        prices,
        *,
        steps=1000,
        depth=40,
        fee=0.005,
        spread_ticks=1,
        capture=True,
    ):
        if len(identifiers) != len(prices) or len(set(identifiers)) != len(prices):
            raise ValueError("Unique instrument IDs must match price dimensions")
        if not 2 <= len(prices) <= 30:
            raise ValueError("Market requires 2–30 assets")
        self.identifiers = tuple(identifiers)
        self.venues = {
            k: PublicVenue(
                p, steps=steps, depth=depth, fee=fee, spread_ticks=spread_ticks, capture=capture
            )
            for k, p in zip(identifiers, prices, strict=True)
        }
        self.history = [list(prices)]
        self.t = 0

    def publish(self, prices):
        a = np.asarray(prices, dtype=float)
        if a.shape != (len(self.venues),) or not np.isfinite(a).all() or (a <= 0.05).any():
            raise ValueError("One finite positive published price per asset required")
        self.t += 1
        for venue, price in zip(self.venues.values(), a, strict=True):
            venue.refresh(float(price), self.t)
        self.history.append(a.tolist())

    def positions(self):
        return {k: v.account.inventory for k, v in self.venues.items()}

    def check(self):
        for venue in self.venues.values():
            venue.check_invariants()
