"""Immutable session evidence, including a timestamped transaction tape."""

from dataclasses import dataclass

from quantlab.domain import Order
from quantlab.market.config import SimulationConfig
from quantlab.market.events import ScheduledEvent
from quantlab.market.signals import InformedAudit
from quantlab.orderbook import BookSnapshot, ExecutionReport, Trade


@dataclass(frozen=True, slots=True)
class EventRecord:
    """One atomic event's decision and consequences; latent fields are observer-only."""

    event: ScheduledEvent
    latent_before_ticks: float
    latent_after_ticks: float
    reason: str
    order: Order | None
    report: ExecutionReport | None
    book_after: BookSnapshot
    informed: InformedAudit | None = None


@dataclass(frozen=True, slots=True)
class TapeEntry:
    time_us: int
    event_sequence: int
    trade: Trade


@dataclass(frozen=True, slots=True)
class SessionResult:
    config: SimulationConfig
    simulator_version: str
    python_version: str
    events: tuple[EventRecord, ...]
    end_time_us: int

    @property
    def tape(self) -> tuple[TapeEntry, ...]:
        """Derived solely from executed trades, never from latent or quote updates."""
        return tuple(
            TapeEntry(record.event.time_us, record.event.sequence, trade)
            for record in self.events
            if record.report is not None
            for trade in record.report.trades
        )

    @property
    def final_book(self) -> BookSnapshot:
        return self.events[-1].book_after if self.events else BookSnapshot((), ())
