"""Real execution, reservations, accounting, risk replay and information boundaries."""

import json
from dataclasses import asdict

import pytest

from quantlab.options.session import OptionsConfig, OptionsSession
from quantlab.research.codec import digest
from quantlab.risk.analytics import RiskSettings
from quantlab.risk.session import RiskSession, replay_risk
from quantlab.trading.server import Controller


@pytest.fixture
def session():
    return RiskSession(settings=RiskSettings(paths=300, sample_size=100))


def buy(s, n=1, side="buy"):
    return s.execute(
        "options",
        "option_order",
        contract_id=s.options.selected,
        side=side,
        quantity=n,
        quote_revision=s.options.quote_revision,
    )


def test_existing_accounts_consumed_not_copied(session):
    o = session.options
    o.command(
        "option_order",
        contract_id=o.selected,
        side="buy",
        quantity=1,
        quote_revision=o.quote_revision,
    )
    p = session.state()["report"]["portfolio"]
    assert p["positions"][0]["quantity"] == 1
    assert p["pnl"] == pytest.approx(o.metrics()["net_pnl"])
    assert p["equity"] == pytest.approx(p["cash"] + p["market_value"])
    assert p["pnl"] == pytest.approx(
        p["realised_gross"] + p["unrealised"] + p["financing"] - p["fees"]
    )


@pytest.mark.parametrize("side", ["buy", "sell"])
def test_real_hedge_changes_stock_and_delta(session, side):
    buy(session, side=side)
    before = session.portfolio().public()
    response = session.execute("options", "hedge")
    after = response["state"]["report"]["portfolio"]
    assert len(session.options.stock.account.fills) > 0
    assert after["greeks"]["vega"] == before["greeks"]["vega"]
    assert abs(after["greeks"]["delta"]) <= 0.5
    assert after["fees"] > before["fees"]
    session.options.stock.check_invariants()


@pytest.mark.parametrize(
    "metric,maximum",
    [
        ("gross", 10),
        ("net", 10),
        ("delta", 1),
        ("gamma", 0.01),
        ("vega", 1),
        ("position", 0),
        ("var", 1),
        ("drawdown", 0.001),
    ],
)
def test_hard_limit_blocks_actual_option_fill(session, metric, maximum):
    session.execute(
        "risk", "limits", limits=[dict(metric=metric, maximum=maximum, mode="hard")]
    )
    before = session.portfolio().public()
    r = buy(session)
    assert r["result"]["ok"] is False
    assert r["result"]["filled"] == 0
    assert session.portfolio().public() == before
    assert "hard limit" in r["result"]["message"]


@pytest.mark.parametrize("mode,filled", [("soft", True), ("hard", False)])
@pytest.mark.parametrize("target", ["options", "desk", "second"])
def test_trade_paths_obey_limits(session, mode, filled, target):
    session.execute("risk", "limits", limits=[dict(metric="delta", maximum=2, mode=mode)])
    r = session.execute(
        target,
        "stock_order" if target == "options" else "order",
        side="buy",
        quantity=3,
        order_type="market",
    )
    count = sum(len(v.account.fills) for v in session.venues().values())
    assert bool(count) == filled
    assert r["state"]["last_warnings"]


def test_existing_breach_can_be_reduced(session):
    buy(session)
    session.execute("risk", "limits", limits=[dict(metric="delta", maximum=1, mode="hard")])
    assert session.execute(
        "options", "stock_order", side="sell", quantity=25, order_type="market"
    )["result"]["ok"]
    assert not session.execute(
        "options", "stock_order", side="buy", quantity=1, order_type="market"
    )["result"]["ok"]


def test_pending_orders_reserve_capacity_and_cancel_frees_it(session):
    session.execute("risk", "limits", limits=[dict(metric="delta", maximum=10, mode="hard")])
    r = session.execute(
        "options", "stock_order", side="buy", quantity=8, order_type="limit", price="99"
    )
    oid = r["result"]["order_id"]
    assert session.options.stock.account.inventory == 0
    assert not session.execute(
        "options", "stock_order", side="buy", quantity=3, order_type="limit", price="98"
    )["result"]["ok"]
    session.execute("options", "cancel_stock", order_id=oid)
    assert session.execute(
        "options", "stock_order", side="buy", quantity=3, order_type="limit", price="98"
    )["result"]["ok"]


def test_independent_buy_sell_reservations_not_netting(session):
    session.execute("risk", "limits", limits=[dict(metric="delta", maximum=10, mode="hard")])
    session.execute("second", "order", side="buy", quantity=10, order_type="limit", price="99")
    session.execute(
        "second", "order", side="sell", quantity=10, order_type="limit", price="101"
    )
    assert not session.execute(
        "second", "order", side="buy", quantity=1, order_type="limit", price="98"
    )["result"]["ok"]


def test_option_quote_partial_fill_not_requested_size(session):
    session.execute("risk", "limits", limits=[dict(metric="position", maximum=20, mode="hard")])
    r = buy(session, 100)
    assert r["result"]["filled"] == 20 and r["result"]["cancelled"] == 80


def test_analysis_never_consumes_market_randomness(session):
    reference = OptionsSession(session.options.config)
    for _ in range(3):
        session.execute("risk", "scenario", stock_return=-0.08, volatility_change=0.12)
        session.state()
    session.execute("options", "step", count=3)
    reference.command("step", count=3)
    assert session.options._innovations == reference._innovations
    assert session.options.spots == reference.spots


def test_replay_reconstructs_trades_limits_stresses_optimisation(session):
    buy(session)
    session.execute("risk", "limits", limits=[dict(metric="delta", maximum=55, mode="hard")])
    session.execute("options", "stock_order", side="buy", quantity=10, order_type="market")
    session.execute("options", "hedge")
    session.execute(
        "risk", "scenario", stock_return=-0.08, volatility_change=0.12, rate_change=0.005
    )
    session.execute("risk", "optimise", max_cash=0, max_weight=0.4, means=[0.001, 0.002, 0.003])
    session.execute("options", "step", count=2)
    session.execute("risk", "end")
    j = session.journal()
    verified, frames = replay_risk(json.loads(json.dumps(j)), frames=True)
    assert verified.journal() == j and len(frames) == len(session.actions) + 1
    assert frames[1]["report"]["portfolio"]["positions"][0]["quantity"] == 1


def test_replay_integrity_and_recomputed_frame(session):
    session.execute("risk", "end")
    j = session.journal()
    j["final"]["report"]["portfolio"]["cash"] += 1
    with pytest.raises(ValueError):
        replay_risk(j)
    j["digest"] = digest({k: v for k, v in j.items() if k != "digest"})
    with pytest.raises(ValueError):
        replay_risk(j)


def test_public_view_excludes_latent_rng_and_market_seed(session):
    raw = json.dumps(session.state()).lower()
    for forbidden in [
        "latent",
        "signal",
        "_rng",
        "innovations",
        "options_config",
        "desk_scenario",
        "physical_drift",
    ]:
        assert forbidden not in raw
    with pytest.raises(ValueError, match="End"):
        session.journal()


def test_public_reports_are_detached(session):
    a = session.state()
    a["report"]["covariance"][0][0] = 99
    assert session.state()["report"]["covariance"][0][0] < 1


def test_settings_validation_is_atomic(session):
    before = asdict(session.settings)
    with pytest.raises(ValueError):
        session.execute("risk", "settings", correlation=-0.9)
    assert asdict(session.settings) == before


def test_stress_never_changes_realised_pnl(session):
    buy(session)
    before = session.options.accounts()
    session.execute(
        "risk", "scenario", stock_return=-0.10, volatility_change=0.20, liquidation_bps=100
    )
    assert session.options.accounts() == before


def test_api_desks_use_same_risk_policy():
    c = Controller()
    lab = c.risk_lab
    lab.command(
        {
            "kind": "limits",
            "payload": {"limits": [dict(metric="delta", maximum=0, mode="hard")]},
        }
    )
    r = c.command(
        {"kind": "order", "payload": dict(side="buy", quantity=1, order_type="market")}
    )
    assert not r["result"]["ok"]
    o = c.options_lab
    r = o.command(
        {
            "kind": "option_order",
            "payload": dict(
                contract_id=o.selected,
                side="buy",
                quantity=1,
                quote_revision=o.session.quote_revision,
            ),
        }
    )
    assert not r["result"]["ok"]
    assert c.learning.error is None


def test_no_wrong_underlying_hedge(session):
    buy(session)
    session.execute("second", "order", side="sell", quantity=51, order_type="market")
    factors = session.portfolio().public()["factors"]
    assert factors["QL-STOCK"]["delta"] > 50 and factors["QL-SECOND"]["delta"] == -51
    assert session.state()["reserved_risk"]["delta"] > 100


@pytest.mark.parametrize(
    "kind,target", [("var", 0), ("delta", 0.5), ("concentration", 0.4), ("volatility", 0)]
)
def test_challenges_depend_on_actual_positions(session, kind, target):
    buy(session, side="sell")
    r = session.execute(
        "risk", "challenge", kind=kind, target=target, vega_max=0, minimum_delta_gbp=10000
    )
    assert not r["state"]["challenge"]["passed"]


def test_account_failure_is_not_hidden(session):
    buy(session)
    session.options.portfolio.cash += 1
    with pytest.raises(AssertionError):
        session.state()


def test_quote_replacement_rejected_before_any_cancel_or_fill(session):
    session.execute("risk", "limits", limits=[dict(metric="delta", maximum=1, mode="hard")])
    before = session.desk.book.snapshot()
    result = session.execute(
        "desk", "quotes", bid_distance=1, ask_distance=1, bid_size=2, ask_size=2, shift=0
    )
    assert not result["result"]["ok"]
    assert session.desk.book.snapshot() == before
    assert not session.desk.account.fills


def test_risk_uses_estimated_matrix_for_limit_too(session):
    session.execute("risk", "covariance", matrix=[[0.01, 0, 0], [0, 0.01, 0], [0, 0, 0.01]])
    session.execute("risk", "limits", limits=[dict(metric="var", maximum=10, mode="hard")])
    assert not session.execute(
        "options", "stock_order", side="buy", quantity=1, order_type="market"
    )["result"]["ok"]


def test_short_expiry_risk_unavailable_does_not_break_actual_trade():
    o = OptionsSession(OptionsConfig(expiries_days=(0.5,), step_days=0.5, steps=2))
    s = RiskSession(o, settings=RiskSettings(paths=100, sample_size=20))
    r = buy(s)
    assert r["result"]["filled"] == 1
    assert r["state"]["report"]["monte_carlo"]["full"]["var"] is None
    assert r["state"]["report"]["monte_carlo"]["full"]["warnings"]
    s.execute("options", "step", count=1)
    assert s.state()["report"]["monte_carlo"]["full"]["var"] is not None


def test_custom_scenario_reprices_after_real_hedge(session):
    buy(session)
    session.execute("risk", "scenario", stock_return=-0.1)
    before = session.state()["scenario"]["full_pnl"]
    session.execute("options", "hedge")
    assert session.state()["scenario"]["full_pnl"] > before + 500


def test_horizon_scenario_becomes_unavailable_after_time_passes(session):
    buy(session)
    session.execute("risk", "scenario", days=30)
    session.execute("options", "step", count=1)
    assert session.state()["scenario"]["full_pnl"] is None


def test_attach_existing_accounts_replays_history():
    o = OptionsSession()
    o.command("stock_order", side="buy", quantity=12, order_type="market")
    s = RiskSession(o, settings=RiskSettings(paths=100, sample_size=20))
    s.execute("options", "stock_order", side="sell", quantity=3, order_type="market")
    s.execute("risk", "end")
    r, _ = replay_risk(s.journal())
    assert r.options.stock.account.inventory == 9


def test_automatic_hedge_obeys_risk_limit(session):
    buy(session)
    session.execute("risk", "limits", limits=[dict(metric="position", maximum=2, mode="hard")])
    session.execute("options", "set_auto", frequency=1)
    session.execute("options", "step", count=1)
    assert session.options.stock.account.inventory == 0
    assert session.state()["last_warnings"]


def test_active_financial_command_replay_stays_deterministic(session):
    session.execute("desk", "start")
    session.execute("desk", "advance", delta_us=250000)
    session.execute("desk", "pause")
    session.execute("risk", "end")
    assert replay_risk(session.journal())[0].journal() == session.journal()


def test_cash_rate_shock_is_hypothetical_and_consistent(session):
    before = session.portfolio().cash
    r = session.execute("risk", "scenario", days=1, rate_change=0.01)["state"]["scenario"]
    assert r["full_pnl"] > 0 and r["full_pnl"] == r["contributions"]["cash_carry"]
    assert session.portfolio().cash == before
