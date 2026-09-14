"""Common capabilities without requiring bars to pretend to be exchange queues."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class MarketEnvironment(Protocol):
    engine: str
    status: str

    def public(self) -> dict: ...
    def command(self, kind: str, **payload) -> dict: ...
    def journal(self) -> dict: ...
