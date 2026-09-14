import copy
from fractions import Fraction

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from quantlab.environments.historical import Execution, HistoricalSession, replay_historical
from quantlab.portfolio.accounting import AccountingError
from quantlab.research.codec import digest
from tests.markets.helpers import bars


def order(s, side="buy", quantity=5, **p):
    return s.command("order", instrument=s.instruments[0], side=side, quantity=quantity, **p)


@pytest.mark.parametrize("side,expected", [("buy", 101.01), ("sell", 100.99)])
def test_market_waits_for_next_close_and_adverse_slippage(side, expected):
    s = HistoricalSession([bars()])
    order(s, side)
    assert not s.fills and s.accounts[s.instruments[0]].inventory == 0
    s.command("step")
    assert s.fills[0]["price"] == expected and s.fills[0]["index"] == 1
    assert s.fills[0]["evidence"] == "SIMULATED HISTORICAL EXECUTION"
    s.check()


@pytest.mark.parametrize(
    "side,limit,fills",
    [
        ("buy", "100", False),
        ("buy", "101.01", True),
        ("sell", "102", False),
        ("sell", "100.99", True),
    ],
)
def test_limits_use_close_not_range(side, limit, fills):
    s = HistoricalSession([bars()])
    order(s, side, order_type="limit", price=limit)
    s.command("step")
    assert bool(s.fills) is fills
    assert s.orders[0]["remaining"] == (0 if fills else 5)


@pytest.mark.parametrize("kind", ["market", "limit"])
@pytest.mark.parametrize("volume,expected", [(0, 0), (9, 0), (10, 1), (25, 2), (100, 5)])
def test_paper_volume_floor_and_remainder_convention(kind, volume, expected):
    s = HistoricalSession([bars(volume=volume)])
    order(s, order_type=kind, **({"price": "120"} if kind == "limit" else {}))
    s.command("step")
    o = s.orders[0]
    assert o["filled"] == expected
    assert o["remaining"] == (5 - expected if kind == "limit" else 0)
    assert o["cancelled"] == (5 - expected if kind == "market" else 0)


def test_volume_shared_between_sides_and_submission_order():
    s = HistoricalSession([bars(volume=30)])
    order(s, quantity=2)
    order(s, "sell", 4)
    s.command("step")
    assert [f["quantity"] for f in s.fills] == [2, 1]
    assert s.orders[1]["cancelled"] == 3


def test_partial_limit_vwap_fees_and_fifo_realisation_reconcile():
    s = HistoricalSession([bars(volume=20)])
    order(s, quantity=5, order_type="limit", price="120")
    s.command("step", count=3)
    assert [f["quantity"] for f in s.fills] == [2, 2, 1]
    assert s.orders[0]["vwap"] == pytest.approx((2 * 101.01 + 2 * 99.01 + 102.01) / 5)
    order(s, "sell", 5)
    s.command("step")
    a = s.accounts[s.instruments[0]].snapshot()
    assert a.inventory == 3 and a.fees_ticks * s._datasets[0].tick == Fraction("0.007")
    assert (
        a.total_pnl_ticks
        == a.realised_trading_pnl_ticks + a.unrealised_pnl_ticks - a.fees_ticks
    )
    s.check()


def test_cancel_then_later_match_and_end_cancels_pending():
    s = HistoricalSession([bars()])
    first = order(s, order_type="limit", price="90")["order_id"]
    s.command("cancel", order_id=first)
    order(s)
    s.command("step")
    assert len(s.fills) == 1 and s.fills[0]["order_id"] != "paper-1"
    order(s, order_type="limit", price="1")
    s.command("end")
    assert not any(o["remaining"] for o in s.orders)
    assert s.summary()["largest_trade"] == 5 and s.summary()["worst_execution"]
    with pytest.raises(ValueError):
        s.command("step")


@pytest.mark.parametrize("quantity", [0, -1, True, 1.5, 1001])
def test_invalid_order_size_leaves_state_unchanged(quantity):
    s = HistoricalSession([bars()])
    before = digest(s.public())
    with pytest.raises(ValueError):
        order(s, quantity=quantity)
    assert digest(s.public()) == before


def test_pending_reservation_prevents_limit_bypass():
    s = HistoricalSession([bars()], {"position_limit": 5})
    order(s, quantity=5, order_type="limit", price="1")
    with pytest.raises(ValueError, match="position limit"):
        order(s, quantity=1)


@pytest.mark.parametrize(
    "field,value",
    [
        ("participation", 0),
        ("participation", 1.1),
        ("slippage_ticks", -1),
        ("slippage_ticks", True),
        ("fee_per_unit", -1),
        ("initial_cash", 0),
        ("position_limit", 0),
    ],
)
def test_execution_config_rejected(field, value):
    with pytest.raises(ValueError):
        Execution(**{field: value})


def test_conservation_corruption_fails_loudly_and_poisons_session():
    s = HistoricalSession([bars()])
    order(s)
    s.command("step")
    s.orders[0]["filled"] += 1
    with pytest.raises(AccountingError):
        s.check()
    assert s.status == "failed"
    with pytest.raises(ValueError):
        s.command("step")


@settings(max_examples=30, deadline=None)
@given(
    st.lists(
        st.tuples(st.sampled_from(["buy", "sell", "step", "cancel"]), st.integers(1, 6)),
        min_size=1,
        max_size=25,
    )
)
def test_generated_mixed_operations_conserve(operations):
    s = HistoricalSession([bars(tuple(100 + i % 4 for i in range(40)), volume=30)])
    for kind, q in operations:
        if kind == "step":
            s.command("step")
        elif kind == "cancel":
            open_orders = [o for o in s.orders if o["remaining"]]
            if open_orders:
                s.command("cancel", order_id=open_orders[0]["order_id"])
        else:
            order(s, kind, q, order_type="limit", price="120" if kind == "buy" else "80")
        s.check()
        a, b = s.accounts[s.instruments[0]], s.counterparties[s.instruments[0]]
        assert (
            sum(f.quantity for f in a.fills)
            == sum(f.quantity for f in b.fills)
            == sum(f["quantity"] for f in s.fills)
        )
        assert a.inventory + b.inventory == 0


def test_step_time_stops_at_permissible_observation_and_no_rewind():
    s = HistoricalSession([bars()])
    s.command("step_time", seconds=59)
    assert s.index == 0
    s.command("step_time", seconds=120)
    assert s.index == 2
    with pytest.raises(ValueError):
        s.command("step", count=-1)


def test_replay_every_action_and_exact_original_dataset():
    d = bars()
    s = HistoricalSession([d])
    order(s)
    s.command("step")
    s.command("end")
    r, frames = replay_historical(s.journal(), [d])
    assert digest(r.public()) == digest(s.public())
    assert len(frames) == 4 and frames[1]["fills"] == []
    with pytest.raises(ValueError, match="fingerprint"):
        replay_historical(s.journal(), [bars(volume=99)])


@pytest.mark.parametrize(
    "tamper", ["version", "execution", "metadata", "range", "action", "final"]
)
def test_replay_corruption_fails(tamper):
    d = bars()
    s = HistoricalSession([d])
    order(s)
    s.command("step")
    s.command("end")
    j = copy.deepcopy(s.journal())
    if tamper == "version":
        j["execution_version"] = "later"
    if tamper == "execution":
        j["execution"]["fee_per_unit"] = "0.03"
    if tamper == "metadata":
        j["datasets"][0]["metadata"]["source"] = "forged"
    if tamper == "range":
        j["datasets"][0]["timestamp_range"][1] = "tomorrow"
    if tamper == "action":
        j["actions"][0]["payload"]["quantity"] = 4
    if tamper == "final":
        j["final_digest"] = "0" * 64
    with pytest.raises(ValueError):
        replay_historical(j, [d])


def test_largest_position_captures_opposite_fills_at_same_bar():
    s = HistoricalSession([bars(volume=100)])
    order(s, quantity=5)
    order(s, "sell", 5)
    s.command("step")
    s.command("end")
    assert s.summary()["largest_position"] == 5
    assert s.accounts[s.instruments[0]].inventory == 0


@pytest.mark.parametrize(
    "field,value", [("quantity", 99), ("side", "sell"), ("exact_price", "1")]
)
def test_tape_tampering_cannot_pass_ledger_conservation(field, value):
    s = HistoricalSession([bars()])
    order(s)
    s.command("step")
    s.fills[0][field] = value
    with pytest.raises(AccountingError):
        s.check()
