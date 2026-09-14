import copy
import json
import time

import pytest

from quantlab.demos.annotations import classify, select, teach
from quantlab.demos.builders import build
from quantlab.demos.projections import point
from quantlab.demos.replays import verified
from quantlab.research.codec import digest
from quantlab.risk.analytics import RiskSettings
from quantlab.risk.session import RiskSession
from quantlab.trading.server import Controller
from tests.demos.test_boundaries import call, finish


@pytest.mark.parametrize(
    "key", ["order", "picked-off", "delta-hedge", "leg-risk", "historical", "hidden-scenario"]
)
def test_teach_loads_saved_json_without_original_live_session_and_exact_action_alignment(key):
    e = build(key)
    saved = json.dumps(e.journal)
    frames, actions, _, proof = verified(saved)
    assert len(frames) == len(actions) + 1
    h = Controller().demos
    h.command({"kind": "load_journal", "payload": {"journal_text": saved}})
    assert h.evidence.verification == proof
    for m in h.evidence.moments:
        i = int(m.id.split("-")[-1])
        assert m.before == frames[i - 1] and m.after == frames[i]
        assert actions[i - 1]["kind"].replace("_", " ") in m.action
    finish(h)
    summary = h.state()["active"]["summary"]
    assert len(summary["three_review_questions"]) == 3
    assert summary["one_interview_question"] and summary["biggest_risk"]
    assert not h.controller.learning.tutor.progress.data["recent"]
    assert all("journal_text" not in a["payload"] for a in h.path_journal()["actions"])


def test_option_replay_step_intermediate_frames_are_not_misattributed_to_next_hedge():
    e = build("delta-hedge")
    frames, actions, _, _ = verified(e.journal)
    assert [f["core"]["revision"] for f in frames] == list(range(len(actions) + 1))
    i = next(i for i, a in enumerate(actions) if a["kind"] == "step")
    assert frames[i]["core"]["step"] == 0 and frames[i + 1]["core"]["step"] == 1
    assert actions[i + 1]["kind"] == "hedge"


def test_completed_risk_journal_uses_original_verifier_and_teaches_real_risk_change():
    s = RiskSession(settings=RiskSettings(paths=100, sample_size=40))
    s.execute("desk", "order", side="buy", quantity=2, order_type="market")
    s.execute(
        "options",
        "option_order",
        contract_id=s.options.selected,
        side="buy",
        quantity=1,
        quote_revision=s.options.quote_revision,
    )
    s.execute("risk", "end")
    e = teach(s.journal())
    assert e.verification["verified"]
    assert any(m.after["engine"] == "risk" for m in e.moments)


def test_loaded_replay_before_metadata_does_not_disclose_future_tags_summary_or_concepts():
    h = Controller().demos
    call(h, "load_journal", journal=build("picked-off").journal)
    v = h.state()["active"]
    assert not v["spec"]["concepts"] and not v["moment"]["tags"]
    assert v["summary"] is None and v["observer"] is None and v["journey"] is None
    assert v["moment"]["concept"] == "model_risk"
    before = copy.deepcopy(h.state())
    h.moment.after["unseen_canary"] = "future only"
    h.moment.tags = ("future surprise",)
    h.moment.concept = "markouts"
    assert h.state() == before


def test_hidden_scenario_saved_replay_reveals_no_configuration_before_opt_in():
    h = Controller().demos
    call(h, "load_journal", journal=build("hidden-scenario").journal)
    while not h.completed:
        text = json.dumps(h.state())
        for hidden in ("liquidity_shock", "model_configuration", "break_at", "seed"):
            assert hidden not in text
        call(h, "next")
    assert h.state()["active"]["observer"] is None
    assert call(h, "hindsight", reveal=True)["active"]["observer"]["configuration"]


@pytest.mark.parametrize(
    "key", ["order", "delta-hedge", "historical", "hidden-scenario", "leg-risk"]
)
def test_corrupt_saved_journal_rejected_without_changing_current_demo(key):
    raw = copy.deepcopy(build(key).journal)
    raw["actions"][0]["payload"]["quantity"] = 9999
    h = Controller().demos
    h.start("order")
    old = copy.deepcopy(h.state())
    with pytest.raises((ValueError, TypeError, KeyError)):
        call(h, "load_journal", journal=raw)
    assert h.state() == old


def test_historical_requires_exact_original_data_even_when_instrument_name_matches():
    raw = copy.deepcopy(build("historical").journal)
    raw["datasets"][0]["fingerprint"] = "0" * 64
    with pytest.raises(ValueError, match="exact original"):
        verified(raw)


def test_no_unverified_frames_or_future_payloads_accepted():
    with pytest.raises(ValueError):
        verified({"frames": [], "actions": []})
    h = Controller().demos
    h.start("order")
    with pytest.raises(ValueError):
        call(h, "next", future={"cash": 1})


def test_teach_current_completed_session_and_synthetic_environment_wrapper():
    c = Controller()
    c.command(
        {"kind": "order", "payload": {"side": "buy", "quantity": 6, "order_type": "market"}}
    )
    with pytest.raises(ValueError):
        call(c.demos, "teach_current", lab="trading")
    c.command({"kind": "end"})
    public = digest(c.state())
    evidence = digest(c.session.evidence)
    call(c.demos, "teach_current", lab="trading")
    assert digest(c.state()) == public and digest(c.session.evidence) == evidence
    verified(c.environments.journal())


def test_selector_keeps_large_profit_and_large_loss_with_no_praise():
    frames = []
    for i, pnl in enumerate((0, 25, -30, 1, -1, 40, -50)):
        frames.append(
            point(
                {
                    "revision": i,
                    "account": {"position": i, "total_pnl": str(pnl)},
                    "trades": [],
                    "orders": [],
                }
            )
        )
    actions = [
        {"kind": "order", "payload": {"side": "buy", "quantity": 1}}
        for _ in range(len(frames) - 1)
    ]
    moments = select(frames, actions, limit=4)
    assert any(float(m.after["core"]["account"]["total_pnl"]) > 0 for m in moments)
    assert any(float(m.after["core"]["account"]["total_pnl"]) < 0 for m in moments)
    assert [int(m.id.split("-")[1]) for m in moments] == sorted(
        int(m.id.split("-")[1]) for m in moments
    )
    assert all(
        "Profit alone" in m.result_note and "Excellent" not in m.result_note for m in moments
    )


def test_event_rank_magnitude_is_symmetric_for_profit_and_loss():
    before = point({"account": {"total_pnl": "0", "position": 2}})
    plus = point({"account": {"total_pnl": "100", "position": 2}})
    minus = point({"account": {"total_pnl": "-100", "position": 2}})
    assert classify(before, plus, {}) == classify(before, minus, {})


def test_long_public_journal_selection_is_bounded_and_fast():
    frames = [
        point(
            {
                "revision": i,
                "account": {"total_pnl": str(i % 17 - 8), "position": i % 10},
                "orders": [],
            }
        )
        for i in range(10001)
    ]
    actions = [{"kind": "step", "payload": {"count": 1}}] * 10000
    start = time.perf_counter()
    moments = select(frames, actions)
    elapsed = time.perf_counter() - start
    assert len(moments) == 6 and elapsed < 2


def test_long_genuine_saved_journal_verifies_without_original_session():
    from quantlab.demos.build_trading import act, order_session
    from quantlab.trading.replay import journal

    s = order_session()
    for _ in range(250):
        act(s, "pause")
    act(s, "order", side="buy", quantity=10, order_type="market")
    act(s, "end")
    raw = journal(s)
    start = time.perf_counter()
    e = teach(raw)
    elapsed = time.perf_counter() - start
    assert len(e.moments) <= 6 and elapsed < 10
    assert any("multiple fills" in m.tags for m in e.moments)
