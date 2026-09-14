"""An integer simulation clock and a chronological heap with deterministic ties."""

import heapq
from dataclasses import dataclass, field
from enum import Enum


class EventKind(Enum):
    LATENT = "latent_update"
    NOISE = "noise_arrival"
    LIQUIDITY = "liquidity_arrival"
    INFORMED = "informed_arrival"


@dataclass(frozen=True, slots=True, order=True)
class ScheduledEvent:
    """Sort by elapsed microseconds, then scheduling sequence; never by event kind."""

    time_us: int
    sequence: int
    kind: EventKind = field(compare=False)


class EventQueue:
    """Single-threaded queue; the clock jumps between events without wall-clock waits."""

    def __init__(self) -> None:
        self._now_us = 0
        self._sequence = 0
        self._heap: list[ScheduledEvent] = []

    @property
    def now_us(self) -> int:
        return self._now_us

    def _validate_time(self, time_us: int) -> None:
        if type(time_us) is not int:
            raise TypeError("time_us must be integer microseconds")
        if time_us < self._now_us:
            raise ValueError("cannot move or schedule in the past")

    def schedule(self, time_us: int, kind: EventKind) -> ScheduledEvent:
        """Enqueue an event; equal times preserve the order of schedule calls."""
        self._validate_time(time_us)
        if not isinstance(kind, EventKind):
            raise TypeError("kind must be an EventKind")
        self._sequence += 1
        event = ScheduledEvent(time_us, self._sequence, kind)
        heapq.heappush(self._heap, event)
        return event

    def peek(self) -> ScheduledEvent | None:
        return self._heap[0] if self._heap else None

    def pop(self) -> ScheduledEvent:
        """Execute next clock jump; an empty queue raises IndexError."""
        if not self._heap:
            raise IndexError("event queue is empty")
        event = heapq.heappop(self._heap)
        self._now_us = event.time_us
        return event

    def advance_to(self, time_us: int) -> None:
        """Finish an idle interval without skipping an event due at or before its end."""
        self._validate_time(time_us)
        if self._heap and self._heap[0].time_us <= time_us:
            raise ValueError("cannot advance past a pending event")
        self._now_us = time_us
