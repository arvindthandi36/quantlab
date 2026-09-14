import copy
import json

import pytest

from quantlab.environments.contract import MarketEnvironment
from quantlab.environments.explanation import what_if
from quantlab.environments.scenarios import SPECS, ScenarioSession, replay_scenario
from quantlab.research.codec import digest
from quantlab.trading.server import Controller


@pytest.mark.parametrize("key", list(SPECS))
def test_scenarios_are_real_core_inputs_and_reproduce(key):
    s = ScenarioSession(key, seed=73, steps=20)
    assert isinstance(s, MarketEnvironment)
    cfg = s.configuration()
    assert cfg["configuration"] and cfg["mechanism"]
    s.command("step", count=20)
    r, frames = replay_scenario(s.journal())
    assert digest(s.public()) == digest(r.public()) and len(frames) == 2
    assert s.challenge()["complete"]
    assert s.reveal()["configuration"] == cfg


@pytest.mark.parametrize("key", list(SPECS))
def test_hidden_scenarios_privacy_explain_tutor_and_reveal(key):
    c = Controller()
    h = c.environments
    s = ScenarioSession(key, seed=913142, hidden=True, steps=20)
    h.active = s
    for count in (0, 9, 2):
        if count:
            h.act("step", count=count)
        p = h.state()
        assert p["configuration"] is None
        assert p["environment"]["title"] == "Scenario Session"
        assert "913142" not in json.dumps(p)
        for concept in ("current_price", "pnl", "var", "z_score"):
            out = h.explain(concept)
            assert "913142" not in json.dumps(out) and "scheduled_input" not in json.dumps(out)
        q = h.tutor.ask(p)
        assert SPECS[key]["title"] not in json.dumps(q)
        with pytest.raises(ValueError):
            h.reveal()
        with pytest.raises(ValueError):
            h.journal()
    h.act("end")
    assert h.state()["configuration"] is None
    assert h.reveal()["configuration"]["scenario"] == key
    assert not h.explain("current_price", mode="observer", reveal=True)["quiz_allowed"]
    journal = h.journal()
    h.load_replay(journal)
    with pytest.raises(ValueError):
        h.reveal()
    with pytest.raises(ValueError):
        h.act("step")
    h.command({"kind": "replay_frame", "payload": {"index": len(h.frames) - 1}})
    assert h.reveal()["configuration"]["scenario"] == key


def test_real_parameter_differences_and_scheduled_shocks():
    normal = ScenarioSession("normal")
    vol = ScenarioSession("high_volatility")
    assert normal.session.scenario.market.latent_sigma_ticks == 2
    assert vol.session.scenario.market.latent_sigma_ticks == 8
    liq = ScenarioSession("liquidity_shock", steps=20)
    liq.command("step", count=9)
    assert all(m["depth"] == 40 for m in liq.public_core()["markets"])
    liq.command("step")
    assert all(m["depth"] == 2 for m in liq.public_core()["markets"])
    corr = ScenarioSession("correlation_breakdown", steps=20)
    before = copy.deepcopy(corr.session.process.factor)
    corr.command("step", count=10)
    assert not (before == corr.session.process.factor).all()
    opt = ScenarioSession("option_volatility_shock", steps=20)
    opt.command("step", count=9)
    assert opt.session.current_iv == 0.2
    opt.command("step")
    assert opt.session.current_iv == 0.4


def test_delta_objective_tracks_trade_between_observations():
    s = ScenarioSession("option_volatility_shock", steps=20)
    q = s.public_core()["selected"]
    s.command(
        "option_order",
        contract_id=q["id"],
        side="buy",
        quantity=1,
        quote_revision=q["revision"],
    )
    assert s.max_abs_delta > 10
    s.command("hedge")
    s.command("step", count=20)
    assert not s.challenge()["success"]


def test_drawdown_objective_can_succeed_while_losing_and_fail_while_profitable():
    s = ScenarioSession("normal", steps=20)
    s.command("order", side="buy", quantity=1, order_type="market")
    s.command("order", side="sell", quantity=1, order_type="market")
    s.command("step", count=20)
    assert s.challenge()["pnl"] < 0 and s.challenge()["success"]
    # Challenge reads independently recorded maximum drawdown, not the sign of terminal P&L.
    p = ScenarioSession("normal", steps=20)
    p.command("step", count=20)
    from unittest.mock import patch

    core = p.public_core()
    core["account"].update(total_pnl="2", max_drawdown="3")
    with patch.object(p, "public_core", return_value=core):
        assert p.challenge()["pnl"] > 0 and not p.challenge()["success"]


@pytest.mark.parametrize(
    "key,kind,inputs",
    [
        ("normal", "order_size", {"quantity": 20}),
        ("normal", "inventory", {"inventory": 3}),
        ("option_volatility_shock", "volatility", {"volatility": 0.3}),
        ("mean_reverting", "entry_threshold", {"entry": 2.5}),
    ],
)
def test_scenario_public_whatif_is_detached(key, kind, inputs):
    s = ScenarioSession(key, hidden=True)
    before = digest(s.public())
    what_if(s.public(), kind, inputs)
    assert digest(s.public()) == before and not s.actions


@pytest.mark.parametrize(
    "bad",
    [{"key": "missing"}, {"seed": True}, {"steps": 0}, {"hidden": "true"}, {"mode": "auto"}],
)
def test_reject_invalid_scenario_setup(bad):
    with pytest.raises(ValueError):
        ScenarioSession(**bad)


@pytest.mark.parametrize("key", ["normal", "mean_reverting", "option_volatility_shock"])
def test_rejected_actions_do_not_create_unjournalled_core_transitions(key):
    s = ScenarioSession(key, steps=20)
    s.command("step")
    before = digest(s.public())
    args = {"side": "invalid", "quantity": 2, "order_type": "market"}
    if s.engine == "statarb":
        args["instrument"] = "SA-X"
    with pytest.raises(ValueError):
        s.command("stock_order" if s.engine == "options" else "order", **args)
    assert digest(s.public()) == before
    s.command("end")
    r, _ = replay_scenario(s.journal())
    assert digest(s.public()) == digest(r.public())


def test_manual_paired_engine_order_after_past_only_warmup_replays():
    s = ScenarioSession("mean_reverting", steps=60)
    s.command("step", count=40)
    s.command("order", instrument="SA-X", side="buy", quantity=5, order_type="market")
    assert s.public_core()["markets"][0]["position"] == 5
    s.command("end")
    r, _ = replay_scenario(s.journal())
    assert digest(s.public()) == digest(r.public())


@pytest.mark.parametrize("field", ["model_configuration", "source", "timestamp_range"])
def test_scenario_replay_rejects_forged_provenance(field):
    s = ScenarioSession("normal", steps=20)
    s.command("end")
    j = s.journal()
    j[field] = {}
    with pytest.raises(ValueError, match="provenance"):
        replay_scenario(j)
