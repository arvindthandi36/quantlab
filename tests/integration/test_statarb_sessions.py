import copy
import json

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from quantlab.portfolio.accounting import AccountingError
from quantlab.research.codec import digest
from quantlab.statarb.market import MultiMarket
from quantlab.statarb.research import backtest, generate
from quantlab.statarb.risk import consolidated, portfolio
from quantlab.statarb.session import StatArbSession, replay
from quantlab.statarb.strategy import Rules


def ready(**kw):
    s = StatArbSession(capture=False, **kw)
    assert s.command("step", count=80)["ok"]
    return s


@pytest.mark.parametrize("action", ["long", "short"])
@pytest.mark.parametrize("order", ["x_first", "y_first"])
def test_pair_sequential_and_real_fifo(action, order):
    s = ready(rules={"execution_order": order})
    s.command("pair", action=action)
    q = s.market.positions()
    assert sum(v != 0 for v in q.values()) == 1 and len(s.pending) == 1
    assert s._exposure()["imbalance"] > 0
    s.command("next_leg")
    assert all(q != 0 for q in s.market.positions().values())
    for f in s.fills:
        assert f["price"] != f["reference"] and f["fee"] > 0
    for v in s.market.venues.values():
        assert v.account.fills and v.book.traded_volume > 0
        v.check_invariants()
    if action == "long":
        assert s.market.positions()["SA-Y"] > 0 > s.market.positions()["SA-X"]
    else:
        assert s.market.positions()["SA-X"] > 0 > s.market.positions()["SA-Y"]


def test_no_liquidity_second_leg_not_invented_and_can_close_later():
    s = ready()
    s.command("liquidity", instrument="SA-X", depth=0)
    s.command("pair", action="long")
    s.command("next_leg")
    assert s.market.positions()["SA-X"] == 0 and s.market.positions()["SA-Y"] > 0
    assert not s.pending and s._exposure()["imbalance"] > 0
    s.command("step", count=1)
    assert s.attribution["temporary_directional"] != 0
    s.command("close")
    s.command("next_leg")
    assert not any(s.market.positions().values())
    assert s.trades[0]["exit"]["net_pnl"] == pytest.approx(s.metrics()["net_pnl"])


def test_second_leg_partial_and_slippage_multiple_levels():
    s = ready(rules={"notional": 4000})
    s.command("liquidity", instrument="SA-X", depth=1)
    s.command("pair", action="long")
    s.command("next_leg")
    assert s.market.positions()["SA-X"] == -5
    fills = [f for f in s.fills if f["instrument"] == "SA-X"]
    assert len(fills) == 2 and fills[0]["quantity"] == 1 and fills[1]["quantity"] == 4
    assert fills[1]["price"] < fills[0]["price"]
    assert any(o.cancelled > 0 for o in s.market.venues["SA-X"].orders.values())


def test_close_with_no_liquidity_retains_inventory():
    s = ready()
    s.command("pair", action="short")
    s.command("next_leg")
    s.command("liquidity", instrument="SA-X", depth=0)
    s.command("close")
    s.command("next_leg")
    assert s.active and s.market.positions()["SA-X"] != 0
    s.command("end")
    assert s.metrics()["residual_inventory"] > 0


def test_wait_creates_no_fill_or_time():
    s = ready()
    before = (s.market.t, list(s.fills), s.market.positions())
    s.command("wait")
    assert before == (s.market.t, s.fills, s.market.positions())


def test_manual_limit_cancel_and_later_matching():
    s = ready()
    p = s.market.history[-1][0]
    assert s.command(
        "order",
        instrument="SA-X",
        side="buy",
        quantity=3,
        order_type="limit",
        price=f"{p - 0.2:.2f}",
    )["ok"]
    assert not s.fills and s.active
    v = s.market.venues["SA-X"]
    oid = next(iter(v.orders))
    assert s.command("cancel", instrument="SA-X", order_id=oid)["ok"]
    assert not v._live("user")
    s.command("order", instrument="SA-Y", side="sell", quantity=2)
    assert s.market.positions()["SA-Y"] == -2
    s.market.check()


def test_passive_fill_uses_new_public_mark_in_attribution():
    s = ready()
    p = s.market.history[-1][0]
    s.command(
        "order",
        instrument="SA-X",
        side="buy",
        quantity=2,
        order_type="limit",
        price=str(round(p - 0.1, 2)),
    )
    prices = s.market.history[-1].copy()
    prices[0] -= 1
    s.publish(prices)
    assert s.market.positions()["SA-X"] == 2
    s._point()
    assert s.fills[0]["role"] == "provider"


@pytest.mark.parametrize("name", ["stable", "beta", "mean", "volatility", "decouple", "drift"])
def test_systematic_accounts_reconcile_through_regimes(name):
    s = ready(scenario_name=name)
    s.command("auto", enabled=True)
    s.command("step", count=160)
    s.market.check()
    s._point()
    assert len(s.decisions) == 240
    for d in s.decisions:
        if d["signal"].get("available"):
            assert d["signal"]["fit"]["end"] <= d["t"]
    assert all("reason" in d for d in s.decisions)


def test_forced_accounting_discrepancy_fails_loudly():
    s = ready()
    s.attribution["fees"] += 1
    with pytest.raises(AccountingError):
        s.command("wait")
    assert s.status == "failed"


@pytest.mark.parametrize("action", ["long", "short"])
def test_roundtrip_costs_both_sides_and_both_legs(action):
    s = ready()
    s.command("pair", action=action)
    s.command("next_leg")
    s.command("close")
    s.command("next_leg")
    assert s.metrics()["net_pnl"] == pytest.approx(-s.metrics()["costs"])
    assert len(s.fills) == 4 and all(f["fee"] > 0 for f in s.fills)
    assert s.trades[0]["exit"]["gross_pnl"] == pytest.approx(0)
    assert len(s.trades[0]["entry"]["executions"]) == 2


def test_deterministic_replay_and_rejected_actions():
    s = ready()
    assert not s.command("pair", action="wrong")["ok"]
    s.command("liquidity", instrument="SA-X", depth=1)
    s.command("pair", action="long")
    s.command("step", count=3)
    s.command("close")
    s.command("next_leg")
    s.command("end")
    j = s.journal()
    r, frames = replay(j, frames=True)
    assert digest(r.journal()) == digest(j)
    assert len(frames) == len(s.actions) + 1
    assert frames[0]["t"] == 0 and frames[-1]["status"] == "ended"


@pytest.mark.parametrize("field", ["history", "evidence", "fills", "final"])
def test_replay_rejects_tampering(field):
    s = ready()
    s.command("pair", action="short")
    s.command("end")
    j = copy.deepcopy(s.journal())
    if isinstance(j[field], list):
        j[field] = j[field][:-1]
    else:
        j[field]["t"] += 1
    with pytest.raises(ValueError):
        replay(j)


def test_public_information_schema_has_no_process_or_future_data():
    s = ready(scenario_name="beta")
    state = s.state()
    raw = json.dumps(state)
    for key in (
        '"seed"',
        '"latent"',
        '"innovations"',
        '"break_at"',
        '"process_config"',
        '"evidence"',
    ):
        assert key not in raw
    assert len(state["history"]) == 81
    assert max(d["t"] for d in state["decisions"]) == 80
    with pytest.raises(ValueError):
        s.journal()


@pytest.mark.parametrize("mode", ["fixed", "rolling", "walk_forward"])
def test_future_mutation_cannot_change_past_entry_exit_or_execution(mode):
    data, _ = generate(999, steps=220)
    other = data.copy()
    other[170:, 1] += np.linspace(0, 8, len(other) - 170)
    a, b = backtest(data, rules=Rules(mode=mode)), backtest(other, rules=Rules(mode=mode))
    assert [d for d in a.decisions if d["t"] < 170] == [d for d in b.decisions if d["t"] < 170]
    assert [f for f in a.fills if f["t"] < 170] == [f for f in b.fills if f["t"] < 170]
    assert [p for p in a.path if p["t"] < 170] == [p for p in b.path if p["t"] < 170]


def test_n_asset_market_has_distinct_books_tapes_and_accounts():
    m = MultiMarket(["a", "b", "c"], [100, 80, 150], capture=False)
    m.venues["a"].command("order", side="buy", quantity=5, order_type="market")
    assert m.positions() == {"a": 5, "b": 0, "c": 0}
    assert not m.venues["b"].tape
    m.publish([101, 81, 149])
    m.check()
    assert portfolio(m).public()["pnl"] == pytest.approx(4.925)


def test_risk_consolidation_uses_actual_accounts():
    from quantlab.risk.analytics import FACTORS
    from quantlab.risk.session import RiskSession

    s = ready()
    s.command("pair", action="long")
    s.command("next_leg")
    base = RiskSession(capture=False)
    r = consolidated(base.portfolio(), FACTORS, base.settings.covariance(), s.market)
    assert {"SA-X", "SA-Y"} <= {p["instrument"] for p in r["portfolio"]["positions"]}
    assert r["portfolio"]["pnl"] == pytest.approx(s.metrics()["net_pnl"])
    assert r["linear"]["es"] >= r["linear"]["var"] > 0
    assert "zero" in r["assumption"]


def test_gross_guard_keeps_pending_limits_reserved():
    s = ready(rules={"max_gross": 1200, "notional": 1000})
    s.command("order", instrument="SA-X", side="buy", quantity=8, order_type="limit", price="1")
    r = s.command("order", instrument="SA-Y", side="buy", quantity=8)
    assert not r["ok"] and s.market.positions()["SA-Y"] == 0


@settings(max_examples=12, deadline=None)
@given(
    st.lists(
        st.sampled_from(["wait", "pair", "next", "step", "close", "cancel"]),
        min_size=1,
        max_size=20,
    )
)
def test_generated_mixed_operations_conserve_inventory_and_cash(operations):
    s = ready()
    for op in operations:
        if op == "pair":
            s.command("pair", action="long")
        elif op == "next":
            s.command("next_leg")
        elif op == "step":
            s.command("step", count=1)
        elif op == "cancel":
            s.command("liquidity", instrument="SA-X", depth=0)
        else:
            s.command(op)
        s.market.check()
        s._point()
    s.command("end")
    assert replay(s.journal()).audit() == s.audit()


def test_resting_limits_reserve_leg_imbalance_before_any_fill():
    s = ready(rules={"max_imbalance": 400})
    first = s.command(
        "order", instrument="SA-X", side="buy", quantity=3, order_type="limit", price="1"
    )
    second = s.command(
        "order", instrument="SA-X", side="buy", quantity=3, order_type="limit", price="1"
    )
    assert first["ok"] and not second["ok"]
    assert "leg imbalance" in second["message"]
    assert s.market.positions()["SA-X"] == 0
    assert sum(o.remaining_quantity for o in s.market.venues["SA-X"]._live("user")) == 3


def test_opposite_resting_legs_cannot_pretend_to_fill_atomically():
    s = ready(rules={"max_imbalance": 400})
    assert s.command(
        "order", instrument="SA-X", side="buy", quantity=3, order_type="limit", price="1"
    )["ok"]
    # Opposite directions do not cancel reservation risk: either leg may fill first.
    assert not s.command(
        "order", instrument="SA-Y", side="sell", quantity=5, order_type="limit", price="1000"
    )["ok"]
