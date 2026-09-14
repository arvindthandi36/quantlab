"""Versioned JSON evidence; no pickle, code evaluation or random draws on load."""

import json
import math
from dataclasses import asdict
from enum import Enum
from pathlib import Path
from typing import Any

from quantlab import LimitOrder, MarketOrder, Side
from quantlab.agents.informed import InformedDecision, PrivateSignal
from quantlab.domain import nonempty_identifier, positive_integer, validate_order
from quantlab.market.config import SimulationConfig
from quantlab.market.events import EventKind, ScheduledEvent
from quantlab.market.records import EventRecord, SessionResult
from quantlab.market.replay import replay_session
from quantlab.market.signals import InformedAudit
from quantlab.orderbook import BookSnapshot, ExecutionReport, OrderView, PriceLevel, Trade

SCHEMA_VERSION = 2


def _integers(raw: dict[str, Any], names: tuple[str, ...], *, positive: bool = True) -> None:
    for name in names:
        value = raw[name]
        if positive:
            positive_integer(value, name)
        elif type(value) is not int or value < 0:
            raise ValueError(f"{name} must be a nonnegative integer")


def _enum_value(value: object) -> str:
    if isinstance(value, Enum):
        return value.value
    raise TypeError(f"cannot encode {type(value).__name__}")


def session_json(session: SessionResult) -> str:
    """Encode complete configuration and observer evidence without NaN/Infinity."""
    replay_session(session)
    payload = {"schema_version": SCHEMA_VERSION, "session": asdict(session)}
    return (
        json.dumps(payload, default=_enum_value, indent=2, sort_keys=True, allow_nan=False)
        + "\n"
    )


def save_session(session: SessionResult, path: str | Path) -> None:
    """Write an explicit destination; the saved observer log includes latent state."""
    Path(path).write_text(session_json(session), encoding="utf-8")


def _snapshot(raw: dict[str, Any]) -> BookSnapshot:
    def order_view(raw_order: dict[str, Any]) -> OrderView:
        side = Side(raw_order["side"])
        validate_order(raw_order["order_id"], side, raw_order["remaining_quantity"])
        _integers(raw_order, ("price_ticks", "arrival_sequence"))
        return OrderView(**{**raw_order, "side": side})

    def levels(items: list[dict[str, Any]]) -> tuple[PriceLevel, ...]:
        for item in items:
            _integers(item, ("price_ticks",))
        return tuple(
            PriceLevel(
                item["price_ticks"],
                tuple(order_view(o) for o in item["orders"]),
            )
            for item in items
        )

    return BookSnapshot(levels(raw["bids"]), levels(raw["asks"]))


def _record(raw: dict[str, Any]) -> EventRecord:
    event = raw["event"]
    command = raw["order"]
    order = None
    if command is not None:
        cls = LimitOrder if "price_ticks" in command else MarketOrder
        order = cls(**{**command, "side": Side(command["side"])})
    report = raw["report"]
    if report is not None:
        _integers(report, ("arrival_sequence", "requested_quantity"))
        _integers(
            report,
            (
                "resting_quantity",
                "cancelled_quantity",
                "buyer_filled_quantity",
                "seller_filled_quantity",
            ),
            positive=False,
        )
        for trade in report["trades"]:
            _integers(trade, ("trade_id", "price_ticks", "quantity"))
        trades = tuple(
            Trade(**{**t, "aggressor_side": Side(t["aggressor_side"])})
            for t in report["trades"]
        )
        report = ExecutionReport(**{**report, "trades": trades})
    if not isinstance(raw["reason"], str) or not raw["reason"].strip():
        raise ValueError("event reason must be a nonempty string")
    return EventRecord(
        ScheduledEvent(**{**event, "kind": EventKind(event["kind"])}),
        raw["latent_before_ticks"],
        raw["latent_after_ticks"],
        raw["reason"],
        order,
        report,
        _snapshot(raw["book_after"]),
        _informed(raw.get("informed")),
    )


def _informed(raw: dict[str, Any] | None) -> InformedAudit | None:
    if raw is None:
        return None
    decision = raw["decision"]
    for name, value in {**decision, "error_ticks": raw["error_ticks"]}.items():
        if name not in ("order", "reason") and value is not None:
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError(f"invalid private diagnostic {name}")
    command = decision["order"]
    order = (
        None if command is None else LimitOrder(**{**command, "side": Side(command["side"])})
    )
    return InformedAudit(
        PrivateSignal(**raw["signal"]),
        raw["error_ticks"],
        InformedDecision(**{**decision, "order": order}),
    )


def _reject_nonfinite(token: str) -> None:
    raise ValueError(f"nonfinite JSON number {token} is not permitted")


def load_session(path: str | Path) -> SessionResult:
    """Read a supported journal and verify matching; malformed evidence raises.

    Replay uses saved instructions even if RNG distribution implementations have
    changed. Seed regeneration should use the recorded simulator/Python versions.
    """
    try:
        payload = json.loads(
            Path(path).read_text(encoding="utf-8"), parse_constant=_reject_nonfinite
        )
        if type(payload["schema_version"]) is not int or payload["schema_version"] not in (
            1,
            SCHEMA_VERSION,
        ):
            raise ValueError("unsupported journal schema version")
        raw = payload["session"]
        config = dict(raw["config"])
        if "markout_horizons_events" in config:
            config["markout_horizons_events"] = tuple(config["markout_horizons_events"])
        if payload["schema_version"] == 1 and (
            config.get("informed_rate_per_second", 0) != 0
            or any(r.get("informed") is not None for r in raw["events"])
        ):
            raise ValueError("legacy schema cannot contain informed flow")
        _integers(raw, ("end_time_us",))
        nonempty_identifier(raw["simulator_version"], "simulator_version")
        nonempty_identifier(raw["python_version"], "python_version")
        session = SessionResult(
            SimulationConfig(**config),
            raw["simulator_version"],
            raw["python_version"],
            tuple(_record(record) for record in raw["events"]),
            raw["end_time_us"],
        )
        replay_session(session)
        return session
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise ValueError(f"invalid session journal: {exc}") from exc
