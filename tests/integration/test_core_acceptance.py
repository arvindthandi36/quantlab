"""Release gates spanning lab boundaries, rather than additional isolated examples."""

from tests.core_workflows import maker_workflow, pair_workflow, portfolio_workflow


def test_stock_option_hedge_risk_stress_close_and_replay():
    assert portfolio_workflow()["replay"]


def test_maker_research_and_tutor_share_verified_results(tmp_path):
    assert maker_workflow(tmp_path / "study")["full_light_identical"]


def test_incomplete_pair_consolidated_risk_close_and_replay():
    assert pair_workflow()["replay"]


def test_missing_pair_history_explains_recovery_without_an_order():
    from quantlab.statarb.session import StatArbSession

    s = StatArbSession()
    r = s.command("pair", action="long")
    assert not r["ok"] and "past observations" in r["message"]
    assert not s.fills and s.active is None and s.status == "active"


def test_shared_risk_reset_can_return_to_manual_market_making(tmp_path, monkeypatch):
    from quantlab.trading.server import Controller

    monkeypatch.chdir(tmp_path)
    c = Controller()
    lab = c.risk_lab
    lab.command({"kind": "end"})
    lab.command({"kind": "new", "payload": {"desk_mode": "manual_maker"}})
    assert c.session.mode == "manual_maker"
    result = c.command(
        {
            "kind": "quotes",
            "payload": dict(bid_distance=2, ask_distance=2, bid_size=1, ask_size=1, shift=0),
        }
    )
    assert result["result"]["ok"]
    c.session.check_invariants()
