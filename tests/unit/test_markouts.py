from dataclasses import replace

import pytest

from quantlab import LimitOrder, MarketOrder, OrderBook, Side
from quantlab.agents.basic import PublicObservation
from quantlab.agents.informed import InformedTrader, PrivateSignal
from quantlab.analytics.markouts import MarkoutStatus, Reference, analyse_markouts
from quantlab.market.config import SimulationConfig
from quantlab.market.events import EventKind, ScheduledEvent
from quantlab.market.records import EventRecord, SessionResult
from quantlab.market.signals import InformedAudit


def _path(informed_side: Side, *, future_quote: bool = True) -> SessionResult:
    """Controlled exogenous path; trades still come from the actual matching engine.

    This is an analytic sign/horizon fixture, not a claimed seed-generated sample.
    Neither the trader nor matcher receives the later reference outcomes.
    """
    book, records = OrderBook(), []
    direction = 1 if informed_side is Side.BUY else -1
    latent = 10000 + 8 * direction

    def append(order=None, *, audit=None, updated_latent=None):
        nonlocal latent
        number = len(records) + 1
        before = latent
        if updated_latent is not None:
            latent = updated_latent
        report = None if order is None else book.submit(order)
        kind = (
            EventKind.LATENT
            if order is None
            else (EventKind.INFORMED if audit else EventKind.NOISE)
        )
        records.append(
            EventRecord(
                ScheduledEvent(number, number, kind),
                before,
                latent,
                "controlled reference path",
                order,
                report,
                book.snapshot(),
                audit,
            )
        )

    append(LimitOrder("anchor", informed_side, 2, 10000))
    append(LimitOrder("stale", informed_side.opposite, 1, 10000 + 5 * direction))
    signal = PrivateSignal(3, latent + 0.5 * direction, 1)
    decision = InformedTrader().decide(
        "informed",
        PublicObservation(book.best_bid, book.best_ask, None, 10000),
        signal,
        now_us=3,
    )
    assert decision.order is not None and decision.order.side is informed_side
    append(decision.order, audit=InformedAudit(signal, signal.value_ticks - latent, decision))
    if future_quote:
        append(LimitOrder("later", informed_side.opposite, 2, 10000 + 15 * direction))
    else:
        append(updated_latent=latent)
    append(updated_latent=latent + 2 * direction)
    return SessionResult(
        SimulationConfig(duration_us=5, markout_horizons_events=(1, 2, 20)),
        "fixture",
        "fixture",
        tuple(records),
        5,
    )


@pytest.mark.parametrize("side", list(Side))
def test_informed_buy_and_sell_can_turn_positive_spread_proxy_into_negative_markout(side):
    session = _path(side)
    marks = analyse_markouts(session)
    mid = next(m for m in marks if m.reference is Reference.MIDPOINT and m.horizon_events == 1)
    assert mid.initial_edge_ticks == 2.5
    assert mid.reference_move_ticks == -5.0
    assert mid.provider_markout_ticks == -2.5
    assert mid.initial_edge_ticks + mid.reference_move_ticks == mid.provider_markout_ticks
    latent = next(m for m in marks if m.reference is Reference.LATENT and m.horizon_events == 2)
    assert latent.provider_markout_ticks == -5
    assert latent.provider_side is side.opposite


@pytest.mark.parametrize("side", list(Side))
def test_positive_provider_markout_when_future_reference_moves_in_its_favour(side):
    session = _path(side)
    records = list(session.events)
    trade = records[2].report.trades[0]
    favourable = trade.price_ticks + (2 if side is Side.SELL else -2)
    records[-1] = replace(records[-1], latent_after_ticks=favourable)
    marks = analyse_markouts(replace(session, events=tuple(records)))
    latent = next(m for m in marks if m.reference is Reference.LATENT and m.horizon_events == 2)
    assert latent.provider_markout_ticks == 2


def test_markouts_are_pending_until_exact_maturity_and_never_read_later_records():
    session = _path(Side.BUY)
    assert analyse_markouts(session, as_of_events=2) == ()  # No trade yet.
    at_fill = analyse_markouts(session, as_of_events=3)
    assert all(m.status is MarkoutStatus.PENDING for m in at_fill)
    assert all(
        m.provider_markout_ticks is m.reference_after_ticks is m.maturity_time_us is None
        for m in at_fill
    )
    at_h1 = analyse_markouts(session, as_of_events=4)
    assert all(m.status is MarkoutStatus.AVAILABLE for m in at_h1 if m.horizon_events == 1)
    assert all(m.status is MarkoutStatus.PENDING for m in at_h1 if m.horizon_events > 1)
    poisoned = replace(
        session,
        events=session.events[:-1] + (replace(session.events[-1], latent_after_ticks=1e90),),
    )
    assert analyse_markouts(poisoned, as_of_events=4) == at_h1
    final = analyse_markouts(session)
    assert all(m.status is MarkoutStatus.PENDING for m in final if m.horizon_events == 20)


def test_missing_midpoint_does_not_fall_back_to_latent_or_last_trade():
    marks = analyse_markouts(_path(Side.BUY, future_quote=False))
    mid = next(m for m in marks if m.reference is Reference.MIDPOINT and m.horizon_events == 1)
    latent = next(m for m in marks if m.reference is Reference.LATENT and m.horizon_events == 1)
    assert mid.status is MarkoutStatus.MISSING
    assert mid.reference_after_ticks is mid.provider_markout_ticks is None
    assert mid.maturity_time_us == 4
    assert latent.status is MarkoutStatus.AVAILABLE


def _orders_session(orders):
    book, records = OrderBook(), []
    for i, order in enumerate(orders, 1):
        report = book.submit(order)
        kind = EventKind.LIQUIDITY if isinstance(order, MarketOrder) else EventKind.NOISE
        records.append(
            EventRecord(
                ScheduledEvent(i, i, kind),
                10000,
                10000,
                "test order path",
                order,
                report,
                book.snapshot(),
            )
        )
    return SessionResult(
        SimulationConfig(duration_us=len(orders), markout_horizons_events=(1, 2)),
        "fixture",
        "fixture",
        tuple(records),
        len(orders),
    )


def test_future_midpoint_markout_can_exist_without_an_initial_midpoint():
    session = _orders_session(
        [
            LimitOrder("a", Side.SELL, 1, 10005),
            MarketOrder("buy", Side.BUY, 1),
            LimitOrder("b", Side.BUY, 1, 10006),
            LimitOrder("new-a", Side.SELL, 1, 10008),
        ]
    )
    mid = next(
        m
        for m in analyse_markouts(session)
        if m.reference is Reference.MIDPOINT and m.horizon_events == 2
    )
    assert mid.provider_markout_ticks == -2
    assert (
        mid.initial_edge_ticks is mid.reference_move_ticks is mid.reference_before_ticks is None
    )


def test_multi_fill_order_uses_one_pretrade_reference_and_one_maturity_event():
    session = _orders_session(
        [
            LimitOrder("b", Side.BUY, 2, 99),
            LimitOrder("a1", Side.SELL, 1, 101),
            LimitOrder("a2", Side.SELL, 2, 102),
            MarketOrder("buy", Side.BUY, 3),
            LimitOrder("new-a", Side.SELL, 1, 105),
        ]
    )
    mids = [
        m
        for m in analyse_markouts(session)
        if m.reference is Reference.MIDPOINT and m.horizon_events == 1
    ]
    assert [m.quantity for m in mids] == [1, 2]
    assert [m.reference_before_ticks for m in mids] == [100, 100]
    assert [m.maturity_event_number for m in mids] == [5, 5]
    assert [m.provider_markout_ticks for m in mids] == [-1, 0]


@pytest.mark.parametrize("cutoff", [-1, True, 1.5, 100])
def test_invalid_as_of_cutoffs_fail(cutoff):
    with pytest.raises(ValueError, match="as_of_events"):
        analyse_markouts(_path(Side.BUY), as_of_events=cutoff)
