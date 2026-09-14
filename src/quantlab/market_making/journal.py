"""Versioned observer journals and complete exchange/account replay without RNG draws."""

import json
from dataclasses import asdict, fields, replace
from enum import Enum
from fractions import Fraction
from pathlib import Path

from quantlab import LimitOrder, Side
from quantlab.domain import nonempty_identifier, positive_integer
from quantlab.market.config import SimulationConfig
from quantlab.market.journal import _record, _reject_nonfinite, _snapshot
from quantlab.market.replay import ReplayMarketEnvironment
from quantlab.market_making.config import MakerConfig, Strategy
from quantlab.market_making.lab import MarketMakingLab
from quantlab.market_making.quotes import QuotePlan, QuoteRequest
from quantlab.market_making.records import LabRecord, LabResult
from quantlab.orderbook import ExecutionReport, OrderView, Trade
from quantlab.portfolio.accounting import AccountSnapshot, MakerFill
from quantlab.strategies.market_making import quote_request


def replay_lab(result: LabResult) -> LabResult:
    """Replay saved background events AND maker cancel/replace actions; verify every record."""
    background = tuple(r.market for r in result.records if r.market is not None)

    def environment(config, book):
        return ReplayMarketEnvironment(config, book, background)

    lab = MarketMakingLab(
        result.market_config, result.maker_config, environment_factory=environment
    )
    requests = [r.request for r in result.records if r.kind == "quote"]
    for request in requests:
        observation = lab.advance_to_decision()
        if observation is None or request is None:
            raise ValueError("journal contains an extra or missing quote decision")
        if result.maker_config.strategy is not Strategy.MANUAL:
            if request != quote_request(observation, result.maker_config):
                raise ValueError("recorded quote request does not match the public strategy")
        lab.decide(request)
    if lab.advance_to_decision() is not None:
        raise ValueError("journal is missing a scheduled quote decision")
    actual = lab.result()
    if len(actual.records) != len(result.records):
        raise ValueError("lab journal event count does not reconcile")
    for index, (expected, replayed) in enumerate(
        zip(result.records, actual.records, strict=True)
    ):
        if expected != replayed:
            raise ValueError(f"lab replay mismatch at record {index}: exchange/account/quotes")
    return replace(
        actual, simulator_version=result.simulator_version, python_version=result.python_version
    )


def encode(value):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    raise TypeError(f"cannot encode {type(value).__name__}")


def lab_json(result: LabResult) -> str:
    replay_lab(result)
    return (
        json.dumps(
            {"lab_schema_version": 1, "result": asdict(result)},
            default=encode,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def save_lab(result: LabResult, path: str | Path) -> None:
    """Saved lab journals include private observer state regardless of display mode."""
    Path(path).write_text(lab_json(result), encoding="utf-8")


def _integer(value, name, *, signed=False, positive=False):
    if type(value) is not int or (not signed and value < 0) or (positive and value == 0):
        raise ValueError(f"invalid integer {name}")
    return value


def _fraction(value):
    if type(value) not in (str, int):
        raise ValueError("journal rational must be an integer or exact string")
    return Fraction(value)


def _view(raw):
    command = LimitOrder(
        raw["order_id"], Side(raw["side"]), raw["remaining_quantity"], raw["price_ticks"]
    )
    positive_integer(raw["arrival_sequence"], "arrival_sequence")
    return OrderView(
        command.order_id,
        command.side,
        command.price_ticks,
        command.quantity,
        raw["arrival_sequence"],
    )


def _report(raw):
    for key in ("arrival_sequence", "requested_quantity"):
        positive_integer(raw[key], key)
    for key in (
        "resting_quantity",
        "cancelled_quantity",
        "buyer_filled_quantity",
        "seller_filled_quantity",
    ):
        _integer(raw[key], key)
    nonempty_identifier(raw["order_id"])
    trades = []
    for trade in raw["trades"]:
        for key in ("trade_id", "quantity", "price_ticks"):
            positive_integer(trade[key], key)
        for key in ("maker_order_id", "taker_order_id"):
            nonempty_identifier(trade[key])
        trades.append(Trade(**{**trade, "aggressor_side": Side(trade["aggressor_side"])}))
    return ExecutionReport(**{**raw, "trades": tuple(trades)})


def _account(raw):
    values = {}
    for field in fields(AccountSnapshot):
        value = raw[field.name]
        values[field.name] = (
            _fraction(value)
            if field.name.endswith("_ticks")
            else _integer(value, field.name, signed=field.name == "inventory")
        )
    if set(values) != set(raw):
        raise ValueError("unexpected account field")
    return AccountSnapshot(**values)


def _fill(raw):
    values = dict(raw)
    values["side"] = Side(raw["side"])
    for key in ("trade_id", "public_event_number", "quantity", "price_ticks"):
        positive_integer(raw[key], key)
    _integer(raw["time_us"], "fill time")
    for key in ("fee_ticks", "reference_before_ticks", "midpoint_before_ticks"):
        values[key] = None if raw[key] is None else _fraction(raw[key])
    return MakerFill(**values)


def _lab_record(raw):
    _integer(raw["time_us"], "record time")
    _integer(raw["public_event_number"], "public event number")
    if raw["kind"] not in ("market", "quote", "end"):
        raise ValueError("unknown lab record kind")
    nonempty_identifier(raw["reference_source"], "reference source")
    request = None if raw["request"] is None else QuoteRequest(**raw["request"])
    plan = raw["plan"]
    if plan is not None:
        for key in ("bid_ticks", "ask_ticks"):
            if plan[key] is not None:
                positive_integer(plan[key], key)
        for key in ("bid_size", "ask_size"):
            _integer(plan[key], key)
        if any(not isinstance(reason, str) for reason in plan["adjustments"]):
            raise ValueError("quote adjustments must be text")
        plan = QuotePlan(
            **{
                **plan,
                "centre_ticks": _fraction(plan["centre_ticks"]),
                "adjustments": tuple(plan["adjustments"]),
            }
        )
    return LabRecord(
        raw["time_us"],
        raw["kind"],
        raw["public_event_number"],
        None if raw["market"] is None else _record(raw["market"]),
        request,
        plan,
        tuple(_view(o) for o in raw["cancelled"]),
        tuple(LimitOrder(**{**o, "side": Side(o["side"])}) for o in raw["placed"]),
        tuple(_report(r) for r in raw["reports"]),
        _snapshot(raw["book_after"]),
        tuple(_view(o) for o in raw["own_quotes"]),
        raw["reference_source"],
        _account(raw["account"]),
        tuple(_fill(f) for f in raw["fills"]),
    )


def load_lab(path: str | Path) -> LabResult:
    try:
        payload = json.loads(
            Path(path).read_text(encoding="utf-8"), parse_constant=_reject_nonfinite
        )
        if type(payload["lab_schema_version"]) is not int or payload["lab_schema_version"] != 1:
            raise ValueError("unsupported lab journal schema")
        raw = payload["result"]
        config = dict(raw["market_config"])
        config["markout_horizons_events"] = tuple(config["markout_horizons_events"])
        maker = {**raw["maker_config"], "strategy": Strategy(raw["maker_config"]["strategy"])}
        for name in ("simulator_version", "python_version"):
            nonempty_identifier(raw[name], name)
        result = LabResult(
            SimulationConfig(**config),
            MakerConfig(**maker),
            raw["simulator_version"],
            raw["python_version"],
            tuple(_lab_record(r) for r in raw["records"]),
        )
        replay_lab(result)
        return result
    except (
        TypeError,
        ValueError,
        KeyError,
        AttributeError,
        ZeroDivisionError,
        AssertionError,
    ) as exc:
        raise ValueError(f"invalid lab journal: {exc}") from exc
