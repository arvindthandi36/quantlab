"""Test oracle: flat records, full scans and explicit sorting for each match.

This deliberately does not import the engine or its storage/eligibility helpers.
It is not a second production implementation or a performance benchmark.
"""

from dataclasses import dataclass


@dataclass
class Record:
    order_id: str
    side: str
    price: int
    remaining: int
    sequence: int


class ReferenceBook:
    def __init__(self):
        self.orders: list[Record] = []
        self.sequence = 0
        self.trade_count = 0
        self.volume = 0

    def submit(self, order_id, side, quantity, limit):
        self.sequence += 1
        remaining = quantity
        trades = []
        direction = 1 if side == "buy" else -1
        while remaining:
            eligible = [
                record
                for record in self.orders
                if record.side != side
                and (limit is None or direction * (record.price - limit) <= 0)
            ]
            if not eligible:
                break
            maker = sorted(eligible, key=lambda r: (direction * r.price, r.sequence))[0]
            size = min(remaining, maker.remaining)
            self.trade_count += 1
            self.volume += size
            trades.append((self.trade_count, maker.order_id, order_id, maker.price, size, side))
            maker.remaining -= size
            remaining -= size
            if not maker.remaining:
                self.orders.remove(maker)
        resting = remaining if limit is not None else 0
        cancelled = remaining if limit is None else 0
        if resting:
            self.orders.append(Record(order_id, side, limit, resting, self.sequence))
        return trades, resting, cancelled

    def cancel(self, order_id):
        for record in self.orders:
            if record.order_id == order_id:
                self.orders.remove(record)
                return record.remaining
        return None

    def state(self):
        return sorted(
            (r.order_id, r.side, r.price, r.remaining, r.sequence) for r in self.orders
        )
