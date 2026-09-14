import copy
import json
import random
from dataclasses import replace
from fractions import Fraction

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from quantlab.market.events import EventKind
from quantlab.market.simulation import MarketEnvironment
from quantlab.research.codec import digest
from quantlab.trading.replay import dumps, journal, loads, replay
from quantlab.trading.scenarios import select_scenario
from quantlab.trading.server import Controller
from quantlab.trading.session import TradingSession
from tests.trading_helpers import order, quiet, scripted


def completed():
    s = TradingSession(select_scenario(duration_seconds=5))
    order(s, quantity=6)
    order(s, quantity=5, price="99.98")
    s.command("step_interval", delta_us=2_000_000)
    s.command("cancel_all")
    order(s, "sell", 8)
    s.command("step_interval", delta_us=3_000_000)
    return s


def test_complete_manual_session_both_replay_paths():
    s = completed()
    assert s.status == "ended"
    assert not s._live("user") and not s._live("auto")
    payload = journal(s)
    assert replay(payload).public_snapshot() == s.public_snapshot()
    assert replay(payload, regenerate_seed=True).evidence == s.evidence
    assert loads(dumps(s)).public_snapshot() == s.public_snapshot()


def test_replay_partial_then_cancellation_and_second_passive_order():
    s = scripted(
        [(100, "sell", 7), (200, "sell", 4)],
        initial_book=(("buy", 9998, 5), ("sell", 10002, 5)),
    )
    order(s, quantity=5, price="99.98")
    order(s, quantity=2, price="99.98")
    s.command("step_event")
    s.command("cancel", order_id="user-1")
    s.command("step_event")
    s.command("end")
    assert s.orders["user-1"].filled == 2
    assert replay(journal(s)).evidence == s.evidence


def test_replay_does_not_draw_randomness(monkeypatch):
    payload = journal(completed())

    def forbidden(*args, **kwargs):
        raise AssertionError("random draw in recorded replay")

    monkeypatch.setattr(random.Random, "random", forbidden)
    monkeypatch.setattr(random.Random, "gauss", forbidden)
    monkeypatch.setattr(random.Random, "getrandbits", forbidden)
    assert replay(payload).status == "ended"


@pytest.mark.parametrize(
    "tamper", ["fill", "cash", "action", "public", "background", "timestamp"]
)
def test_replay_rejects_inconsistent_evidence_even_with_new_checksum(tamper):
    data = copy.deepcopy(journal(completed()))
    if tamper == "fill":
        next(e for e in data["evidence"] if e["kind"] == "order")["report"]["trades"][0][
            "quantity"
        ] += 1
    elif tamper == "cash":
        data["evidence"][-1]["accounts"]["user"]["cash_ticks"] = "0/1"
    elif tamper == "action":
        data["actions"][0]["payload"]["quantity"] += 1
    elif tamper == "public":
        data["final_public"]["account"]["position"] += 1
    elif tamper == "timestamp":
        data["actions"][0]["at_us"] += 1
    else:
        data["evidence"] = [
            e
            for e in data["evidence"]
            if not (e["kind"] == "market" and e["market"]["event"]["kind"] == "latent_update")
        ]
    data["sha256"] = digest({k: v for k, v in data.items() if k != "sha256"})
    with pytest.raises((ValueError, AssertionError)):
        replay(data)


def test_export_blocked_before_end_and_checksum_detects_damage():
    s = TradingSession(quiet())
    with pytest.raises(ValueError, match="End"):
        journal(s)
    s.command("end")
    data = journal(s)
    data["end_time_us"] = 123
    with pytest.raises(ValueError, match="checksum"):
        replay(data)


def test_paused_reads_and_timer_ticks_do_not_advance():
    controller = Controller()
    before = controller.state()
    for _ in range(5):
        controller.tick()
        assert controller.state() == before
    controller.command({"kind": "start"})
    controller.tick()
    assert controller.state()["time_us"] == 250_000
    controller.command({"kind": "pause"})
    before = controller.state()
    controller.tick()
    assert controller.state() == before
    controller.command({"kind": "resume"})
    controller.tick()
    assert controller.state()["time_us"] == 500_000


def test_explicit_steps_are_deterministic_and_refused_while_running():
    a, b = TradingSession(select_scenario()), TradingSession(select_scenario())
    for _ in range(8):
        previous = a.public_number
        a.command("step_event")
        b.command("step_event")
        assert a.public_number == previous + 1
        assert a.evidence == b.evidence
    a.command("start")
    before = a.now_us
    assert not a.command("step_event")["ok"]
    assert a.now_us == before


def test_step_with_only_private_events_jumps_to_declared_end():
    s = TradingSession(quiet())
    s.command("step_event")
    assert s.status == "ended" and s.now_us == 10_000_000
    assert all("latent" not in item["message"] for item in s.timeline)


def test_manual_executions_update_background_public_last_price_without_rng_draw():
    a, b = TradingSession(select_scenario()), TradingSession(select_scenario())
    first_arrival = a.environment.next_event_time_us
    order(a, quantity=6)
    assert a.environment.observation().last_trade_ticks == 10002
    assert b.environment.observation().last_trade_ticks is None
    assert a.environment.next_event_time_us == first_arrival
    a.command("step_interval", delta_us=2_000_000)
    b.command("step_interval", delta_us=2_000_000)
    latent_a = [
        e["market"]
        for e in a.evidence
        if e["kind"] == "market" and e["market"]["event"]["kind"] == "latent_update"
    ]
    latent_b = [
        e["market"]
        for e in b.evidence
        if e["kind"] == "market" and e["market"]["event"]["kind"] == "latent_update"
    ]
    assert [x["latent_after_ticks"] for x in latent_a] == [
        x["latent_after_ticks"] for x in latent_b
    ]

    def times(session):
        return [
            (e["market"]["event"]["kind"], e["time_us"])
            for e in session.evidence
            if e["kind"] == "market"
        ]

    assert times(a) == times(b)


@pytest.mark.parametrize("mode", TradingSession.MODES)
def test_public_state_allowlist_hides_observer_data_even_after_end(mode):
    s = TradingSession(select_scenario("toxic", duration_seconds=3), mode)
    order(s, quantity=2)
    s.command("step_interval", delta_us=3_000_000)
    text = json.dumps(s.public_snapshot())
    for forbidden in (
        "latent_",
        "signal",
        "informed_arrival",
        "noise_arrival",
        "liquidity_arrival",
        "next_event",
        "environment",
        "auto-",
        "opening-",
        "due_event",
    ):
        assert forbidden not in text
    assert any(e.get("market", {}).get("informed") for e in s.evidence if e["kind"] == "market")


def test_ordinary_agent_inputs_contain_only_public_observations():
    s = TradingSession(select_scenario("toxic"))
    observation = s.environment.observation()
    assert set(observation.__dataclass_fields__) == {
        "best_bid",
        "best_ask",
        "last_trade_ticks",
        "opening_reference_ticks",
    }
    assert not hasattr(observation, "latent_ticks")


def test_private_value_changes_alone_do_not_change_public_state_at_fixed_time():
    base = quiet()
    a = TradingSession(base)
    b = TradingSession(replace(base, market=replace(base.market, initial_latent_ticks=12345)))
    a.command("step_interval", delta_us=1_000_000)
    b.command("step_interval", delta_us=1_000_000)
    assert a.public_snapshot() == b.public_snapshot()


def test_markouts_mature_only_at_horizon_and_use_observed_mid():
    s = scripted(
        [(100, "sell", 2), (200, "buy", 1)], initial_book=(("buy", 9998, 5), ("sell", 10002, 5))
    )
    order(s, quantity=2, price="99.99")
    s.command("step_event")
    assert s.own_trades[0]["role"] == "provider"
    assert all(m["status"] == "pending" for m in s.markouts)
    s.command("step_interval", delta_us=50)
    assert all(m["status"] == "pending" for m in s.markouts)
    s.command("step_event")
    m = s.markouts[0]
    assert m["status"] == "matured" and m["observed_time_us"] == 200
    assert m["value_ticks"] == 1  # midpoint 10000 minus buy execution 9999
    assert s.markouts[1]["status"] == "pending"


def test_one_sided_markout_is_missing_not_zero():
    s = scripted([(100, "buy", 3)], initial_book=(("buy", 9998, 5), ("sell", 10002, 3)))
    order(s, quantity=1)
    s.command("step_event")
    assert s.markouts[0]["status"] == "missing midpoint"
    assert s.markouts[0]["value_ticks"] is None


def test_marks_never_add_to_pnl():
    s = completed()
    before = s.account.snapshot()
    s.markouts.clear()
    assert s.account.snapshot() == before


def test_manual_quotes_reuse_planner_cancel_all_and_keep_separate_auto_account():
    s = TradingSession(select_scenario(), "manual_maker")
    order(s, quantity=2, price="99.97")
    response = s.command("quotes", bid_distance="2", ask_distance="2", bid_size=2, ask_size=2)
    assert response["ok"] and s.orders["user-1"].cancelled == 2
    first_ids = {o.order_id for o in s._live("user")}
    s.command("quotes", bid_distance="3", ask_distance="3", bid_size=3, ask_size=3)
    assert not first_ids & {o.order_id for o in s._live("user")}
    assert len(s._live("user")) == 2
    s.command("step_interval", delta_us=2_000_000)
    assert s.accounts["auto"] is not s.account
    assert s._owned("auto") and not s._owned("auto") & s._owned("user")
    s.command("end")
    assert replay(journal(s), regenerate_seed=True).evidence == s.evidence


def test_quotes_rejected_in_free_mode_and_bad_request_does_not_cancel():
    s = TradingSession(quiet())
    assert not s.command("quotes")["ok"]
    s = TradingSession(quiet(), "manual_maker")
    order(s, quantity=1, price="99.98")
    assert not s.command("quotes", bid_distance="-2", ask_distance="2", bid_size=2, ask_size=2)[
        "ok"
    ]
    assert len(s._live("user")) == 1


def test_report_exposure_is_time_weighted_and_fees_reconcile():
    s = TradingSession(quiet())
    order(s, quantity=2)
    s.command("step_interval", delta_us=2_000_000)
    order(s, "sell", 1)
    s.command("step_interval", delta_us=2_000_000)
    s.command("end")
    r = s.report()
    assert r["average_absolute_position"] == 1.5
    assert (r["max_long_units"], r["max_short_units"]) == (2, 0)
    assert r["fees"] == "0.00300" and r["trade_count"] == 2
    assert Fraction(r["final_pnl"]) == Fraction(r["realised_pnl"]) + Fraction(
        r["unrealised_pnl"]
    )


@pytest.mark.parametrize("initial", [-8, 8])
def test_position_management_challenge_endowed_position_and_target(initial):
    s = TradingSession(
        select_scenario("position", initial_position=initial, duration_seconds=1), "challenge"
    )
    order(s, "sell" if initial > 0 else "buy", abs(initial))
    s.command("step_interval", delta_us=1_000_000)
    assert s.report()["challenge"]["completed_duration"]
    assert s.report()["challenge"]["target_met"]
    assert replay(journal(s)).account.snapshot() == s.account.snapshot()


def test_tutor_hint_retry_then_trade_then_explain_no_future_answer():
    s = TradingSession(quiet())
    s.command("learn")
    assert s.tutor["stage"] == "predict" and "explanation" not in s.tutor
    s.command("predict", answer="yes")
    assert s.tutor["stage"] == "predict" and "hint" in s.tutor
    s.command("predict", answer="no")
    assert s.tutor["stage"] == "trade"
    order(s, quantity=1, price="99.98")
    assert s.tutor["stage"] == "explain" and "0 filled" in s.tutor["result"]
    assert s.now_us == 0


def test_controller_replay_readonly_and_does_not_tick():
    controller = Controller()
    result = controller.command({"kind": "load_replay", "payload": journal(completed())})
    assert result["state"]["replay"]
    before = controller.state()
    controller.tick()
    assert controller.state() == before
    with pytest.raises(ValueError, match="read-only"):
        controller.command({"kind": "order"})
    controller.command(
        {"kind": "replay_step", "payload": {"index": len(controller.frames) - 1}}
    )
    assert controller.state()["report"] is not None


def test_active_session_cannot_be_silently_replaced():
    c = Controller()
    c.command({"kind": "step_interval", "payload": {"delta_us": 1}})
    with pytest.raises(ValueError, match="End"):
        c.command({"kind": "new"})


def test_end_completes_equal_time_events_without_advancing_to_future():
    def factory(config, book):
        source = MarketEnvironment(config, book)
        source._queue.schedule(2_000_000, EventKind.LIQUIDITY)
        return source

    s = TradingSession(quiet(), environment_factory=factory)
    s.command("step_event")
    assert s.now_us == 2_000_000
    assert s.environment.next_event_time_us == 2_000_000
    s.command("end")
    assert s.now_us == 2_000_000
    assert s.environment.next_event_time_us == 3_000_000
    assert replay(journal(s)).evidence == s.evidence


def test_decision_review_retains_public_state_before_order():
    s = TradingSession(quiet())
    order(s, quantity=6)
    decision = s.timeline[-1]
    assert decision["observed_before"]["position"] == 0
    assert decision["observed_before"]["best_ask"] == "100.01000"
    assert decision["position"] == 6
    assert decision["reference"] == "100.00500"


def test_action_budget_closes_session_without_applying_extra_order(monkeypatch):
    monkeypatch.setattr(TradingSession, "MAX_ACTIONS", 3)
    s = TradingSession(quiet())
    order(s, quantity=1, price="99.98")
    s.command("pause")
    result = order(s, quantity=1)
    assert not result["ok"] and s.status == "ended"
    assert not s.account.fills and not s._live("user")
    assert len(s.actions) == 3
    assert not order(s)["ok"] and len(s.actions) == 3
    assert replay(journal(s)).evidence == s.evidence


def test_save_failure_is_visible_and_download_evidence_survives(tmp_path):
    blocked = tmp_path / "not-a-directory"
    blocked.write_text("occupied")
    c = Controller(blocked)
    response = c.command({"kind": "end"})
    assert response["state"]["status"] == "ended"
    assert "saving failed" in response["state"]["server_error"]
    assert loads(dumps(c.session)).status == "ended"


@settings(max_examples=25, deadline=None)
@given(
    st.lists(
        st.tuples(
            st.sampled_from(["buy", "sell", "cancel", "step"]),
            st.integers(1, 12),
            st.integers(9995, 10005),
        ),
        min_size=1,
        max_size=30,
    )
)
def test_generated_mixed_manual_and_background_sequences(operations):
    s = TradingSession(select_scenario(duration_seconds=3))
    for kind, qty, price in operations:
        if s.status == "ended":
            break
        if kind == "cancel":
            s.command("cancel_all")
        elif kind == "step":
            s.command("step_interval", delta_us=100_000)
        else:
            order(s, kind, qty, f"{price // 100}.{price % 100:02d}" if qty % 2 else None)
        s.check_invariants()
    if s.status != "ended":
        s.command("end")
    assert replay(journal(s)).evidence == s.evidence
    assert replay(journal(s), regenerate_seed=True).evidence == s.evidence
