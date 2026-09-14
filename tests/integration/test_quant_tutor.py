import copy
import json
from dataclasses import replace

import pytest

from quantlab.maker_demo import manual_session
from quantlab.market.config import SimulationConfig
from quantlab.market_making.config import MakerConfig, Strategy
from quantlab.market_making.lab import MarketMakingLab
from quantlab.research.adapters.control import GaussianControl
from quantlab.research.codec import digest
from quantlab.research.engine import execute
from quantlab.trading.replay import dumps, loads
from quantlab.trading.server import Controller
from quantlab.tutor.adapters import maker_contexts, research_contexts
from quantlab.tutor.progress import Progress
from quantlab.tutor.service import Tutor
from tests.integration.test_research_engine import design
from tests.trading_helpers import order, scripted
from tests.unit.test_tutor_progress import Calendar, grade


def buy(controller, quantity=6):
    return controller.command(
        {
            "kind": "order",
            "payload": {"side": "buy", "order_type": "market", "quantity": quantity},
        }
    )


def tc(controller, kind, **payload):
    return controller.tutor_command({"kind": kind, "payload": payload})


@pytest.fixture
def desk(tmp_path):
    c = Controller(learning_path=tmp_path / "progress.json")
    buy(c)
    return c


def test_real_market_event_to_hint_explanation_history_and_restart(desk):
    current = desk.learning.state()["current"]
    assert current["question"]["concept"] == "vwap"
    assert "2 @ £100.01; 4 @ £100.02" in current["question"]["quantlab"]
    first = tc(desk, "answer", question_id=current["id"], answer="mid")["current"]
    assert "Treat each executed unit" in first["feedback"]
    assert "layers" not in first["question"] and not first["closed"]
    second = tc(desk, "answer", question_id=current["id"], answer="equal")["current"]
    assert "money exchanged" in second["feedback"]
    assert "layers" not in second["question"]
    third = tc(desk, "answer", question_id=current["id"], answer="weighted")["current"]
    assert third["learning_update"]["result"] == "correct_after_hint"
    assert "100.01667" in third["question"]["layers"]["maths"]
    restored = Controller(learning_path=desk.learning.path)
    history = restored.learning.dashboard()["recent"]
    assert [r["result"] for r in history] == ["incorrect", "incorrect", "correct_after_hint"]


def test_three_wrong_answers_then_reveal_and_no_copy_credit(desk):
    identifier = desk.learning.state()["current"]["id"]
    for index in range(3):
        current = tc(desk, "answer", question_id=identifier, answer="mid")["current"]
        assert ("layers" in current["question"]) == (index == 2)
    before = desk.learning.tutor.progress.status("vwap")
    later = tc(desk, "quiz", concept="vwap")["current"]
    answered = tc(desk, "answer", question_id=later["id"], answer="weighted")
    assert not answered["current"]["learning_update"]["credited"]
    assert desk.learning.tutor.progress.status("vwap") == before


def test_viewing_explain_and_go_deeper_give_no_mastery(desk):
    for action in ("explain", "deeper"):
        tc(desk, action)
    p = desk.learning.tutor.progress
    assert not p.data["recent"] and p.status("vwap")["score"] is None
    q = tc(desk, "quiz", concept="vwap")["current"]
    tc(desk, "answer", question_id=q["id"], answer="weighted")
    assert p.status("vwap")["score"] is None


def test_interview_delays_explanation_and_limits_hints(desk):
    t = desk.learning.tutor
    t.ask("liquidity")
    t.answer(t.active["id"], "orders")
    current = tc(desk, "quiz", concept="vwap", mode="interview")["current"]
    assert current["question"]["difficulty"] == 2
    tc(desk, "hint")
    with pytest.raises(ValueError, match="No more hints"):
        tc(desk, "hint")
    answered = tc(desk, "answer", question_id=current["id"], answer="100.01667")["current"]
    assert answered["stage"] == "debrief"
    assert answered["learning_update"] is None and "layers" not in answered["question"]
    assert "layers" in tc(desk, "explain")["current"]["question"]


@pytest.mark.parametrize(
    "concept",
    [
        "architecture",
        "queue_priority",
        "sample_mean",
        "randomness",
        "model_criticism",
        "research_integrity",
    ],
)
def test_project_defence_uses_implemented_topics_and_records_struggle(desk, concept):
    current = tc(desk, "quiz", concept=concept, mode="defence")["current"]
    q = desk.learning.tutor._question()
    wrong = next(key for key, _ in q.options if key != q.expected)
    tc(desk, "answer", question_id=current["id"], answer=wrong)
    history = desk.learning.dashboard()["recent"][-1]
    assert history["mode"] == "defence" and not history["correct"]
    assert "layers" not in desk.learning.state()["current"]["question"]


def test_no_duplicate_questions_or_progress_writes_on_unchanged_observation(desk, monkeypatch):
    before = copy.deepcopy(desk.learning.tutor.progress.data)

    def unexpected():
        raise AssertionError("unchanged snapshot should not write storage")

    monkeypatch.setattr(desk.learning.tutor.progress, "save", unexpected)
    for _ in range(15):
        desk.learning.observe(desk.state(), desk.learning_source)
    assert desk.learning.tutor.progress.data == before
    assert desk.learning.error is None


def test_frequency_and_unanswered_question_are_respected(desk):
    t = desk.learning.tutor
    t.configure(event_gap=100)
    first = t.active["id"]
    for _ in range(3):
        desk.command(
            {
                "kind": "order",
                "payload": {
                    "side": "sell",
                    "order_type": "limit",
                    "quantity": 1,
                    "price": "100.10",
                },
            }
        )
    assert t.active["id"] == first
    tc(desk, "explain")
    desk.command({"kind": "cancel_all"})
    assert t.active["id"] == first


def test_question_is_frozen_when_new_prices_arrive(desk):
    before = copy.deepcopy(desk.learning.state()["current"]["question"])
    desk.command({"kind": "step_interval", "payload": {"delta_us": 1_000_000}})
    after = desk.learning.state()["current"]["question"]
    assert before == after
    assert desk.learning.tutor.active["context"]["time_us"] == 0


def test_tutor_disabled_has_no_questions_or_new_answer_evidence(desk):
    tc(desk, "configure", enabled=False)
    before = copy.deepcopy(desk.learning.tutor.progress.data["concepts"])
    desk.command({"kind": "step_event"})
    buy(desk, 1)
    assert desk.learning.state()["current"] is None
    assert desk.learning.tutor.progress.data["concepts"] == before
    with pytest.raises(ValueError, match="disabled"):
        tc(desk, "quiz")


def test_optional_prediction_then_real_decision_and_result():
    c = Controller()
    prediction = tc(c, "predict")["current"]
    answer = tc(c, "answer", question_id=prediction["id"], answer="no")["current"]
    assert answer["stage"] == "decide" and "layers" not in answer["question"]
    buy(c, 1)
    result = c.learning.state()["current"]
    assert result["stage"] == "explain" and "1 filled" in result["result"]
    assert c.session.actions[0]["kind"] == "order"
    assert len(c.session.actions) == 1


def test_selling_and_resting_limit_triggers_are_real():
    c = Controller()
    c.command(
        {
            "kind": "order",
            "payload": {
                "side": "sell",
                "quantity": 2,
                "order_type": "limit",
                "price": "100.05",
            },
        }
    )
    assert c.learning.state()["current"]["question"]["concept"] == "limit_orders"
    assert "queue_priority" in c.learning.state()["encountered"]
    c.command({"kind": "cancel_all"})
    c.command(
        {"kind": "order", "payload": {"side": "sell", "quantity": 4, "order_type": "market"}}
    )
    assert c.learning.tutor.contexts["exposure"].facts["position"] == -4


def test_partial_fill_and_matured_negative_provider_mark_from_real_engine():
    session = scripted([(100_000, "buy", 18), (200_000, "sell", 5)])
    order(session, side="sell", quantity=5, price="100.03")
    t = Tutor()
    t.observe(session.public_snapshot(), "script")
    session.command("step_event")
    t.observe(session.public_snapshot(), "script")
    assert t.contexts["partial_fills"].facts["filled"] == 3
    session.command("step_event")
    t.observe(session.public_snapshot(), "script")
    # The queue and trades, not the tutor, determine whether and when marks mature.
    actual = session.public_snapshot()["markouts"]
    assert actual
    for context in t.contexts.values():
        if context.kind == "markout":
            assert context.facts["observed_time_us"] <= session.now_us
    session.check_invariants()


@pytest.mark.parametrize("seed", [0, 42, 91])
def test_tutor_interactions_leave_all_market_evidence_and_rng_paths_identical(seed):
    plain = Controller()
    tutored = Controller()
    for c in (plain, tutored):
        c.command({"kind": "new", "payload": {"seed": seed, "duration_seconds": 5}})
    tc(plain, "configure", enabled=False)
    for c in (plain, tutored):
        buy(c)
    current = tutored.learning.state()["current"]
    tc(tutored, "answer", question_id=current["id"], answer="mid")
    tc(tutored, "hint")
    tc(tutored, "explain")
    tc(tutored, "deeper")
    tutored.learning.dashboard()
    tutored.learning.exports(True)
    for _ in range(8):
        for c in (plain, tutored):
            c.command({"kind": "step_event"})
        if (
            not tutored.learning.state()["current"]
            or tutored.learning.state()["current"]["closed"]
        ):
            tc(tutored, "quiz", concept="exposure")
            tc(tutored, "explain")
    for c in (plain, tutored):
        c.command({"kind": "end"})
    assert plain.session.actions == tutored.session.actions
    assert plain.session.evidence == tutored.session.evidence
    assert dumps(plain.session) == dumps(tutored.session)
    assert loads(dumps(tutored.session)).evidence == plain.session.evidence


def test_live_observer_and_review_rejected_then_separately_revealed(desk):
    for kind, payload in (("observer", {"reveal": True}), ("review", {})):
        with pytest.raises(ValueError):
            tc(desk, kind, **payload)
    desk.command({"kind": "step_interval", "payload": {"delta_us": 1_000_000}})
    desk.command({"kind": "end"})
    with pytest.raises(ValueError):
        tc(desk, "observer", reveal=False)
    before = copy.deepcopy(desk.learning.tutor.progress.data)
    hidden = tc(desk, "observer", reveal=True)
    assert hidden["observer_only"] and "latent_after_ticks" in hidden["observer_only"][0]
    assert desk.learning.tutor.progress.data == before
    public = json.dumps([desk.state(), desk.learning.state(), desk.learning.exports()])
    for forbidden in (
        "latent_after_ticks",
        "signal_error_ticks",
        "informed_arrival",
        "next_event_time_us",
    ):
        assert forbidden not in public


def test_post_session_review_does_not_grade_by_profit_or_lose_known_then(desk):
    before = copy.deepcopy(desk.learning.tutor.progress.data["recent"])
    desk.command({"kind": "step_interval", "payload": {"delta_us": 1_000_000}})
    desk.command({"kind": "end"})
    review = tc(desk, "review")["review"]
    assert len(review["three_questions"]) == 3 and review["interview"]
    assert review["known_then"][0]["observed"]["best_ask"] == "100.01000"
    assert len(review["decision_vs_outcome"]) == 4
    assert "without contemporaneous reasoning" in review["assessment"]
    assert desk.learning.tutor.progress.data["recent"] == before
    assert review["mastery_updates"] == []
    assert "No reasoning-based assessment" in review["what_you_did_well"][0]


def test_replay_gates_observer_until_ended_frame(desk):
    desk.command({"kind": "step_interval", "payload": {"delta_us": 1_000_000}})
    desk.command({"kind": "end"})
    payload = dumps(desk.session)
    desk.command({"kind": "load_replay", "payload": {"journal_text": payload}})
    with pytest.raises(ValueError):
        tc(desk, "observer", reveal=True)
    desk.command({"kind": "replay_step", "payload": {"index": len(desk.frames) - 1}})
    assert tc(desk, "observer", reveal=True)["observer_only"]


def test_storage_failure_does_not_fail_exchange(desk, monkeypatch):
    def fail():
        raise OSError("disk full")

    monkeypatch.setattr(desk.learning.tutor.progress, "save", fail)
    before = desk.session.account.inventory
    result = buy(desk, 1)
    assert result["result"]["ok"]
    assert desk.session.account.inventory == before + 1
    assert desk.session.status != "failed"
    assert desk.learning.state()["error"]
    desk.session.check_invariants()


def test_corrupt_progress_only_blocks_learning_and_explicit_reset_preserves_file(tmp_path):
    path = tmp_path / "progress.json"
    path.write_text("{broken")
    c = Controller(learning_path=path)
    assert c.learning.state()["error"]
    assert buy(c, 1)["result"]["ok"]
    with pytest.raises(ValueError):
        tc(c, "reset", confirmation="yes")
    tc(c, "reset", confirmation="RESET LEARNING")
    assert path.with_suffix(".json.unreadable").read_text() == "{broken"
    assert Progress(path).data["recent"] == []
    assert c.session.account.inventory == 1


def test_spaced_revisit_uses_saved_actual_context_after_calendar_advances(desk):
    clock = Calendar()
    t = desk.learning.tutor
    t.progress.clock = clock
    identifier = t.active["id"]
    tc(desk, "answer", question_id=identifier, answer="mid")
    tc(desk, "explain")
    score = t.progress.status("vwap")
    clock.advance(2)
    assert "vwap" in [r["concept"] for r in t.progress.due()]
    revisited = tc(desk, "quiz")["current"]
    assert revisited["question"]["concept"] == "vwap"
    assert "2 @ £100.01; 4 @ £100.02" in revisited["question"]["quantlab"]
    assert t.progress.status("vwap") == score


def test_phase5_actual_experiment_values_and_pairing(tmp_path):
    record = execute(design(runs=8), GaussianControl(), tmp_path / "experiment")
    contexts = research_contexts(tmp_path / "experiment")
    t = Tutor()
    t.study(contexts)
    assert t.view()["current"]["question"]["concept"] == "standard_error"
    first, second = contexts
    mean = sum(r["metrics"]["net_pnl"] for r in record["runs"] if r["variant"] == "a") / 8
    assert first.facts["mean"] == pytest.approx(mean)
    assert second.facts["paired"] and second.facts["paired_se"] is not None
    assert "correlation" in t.contexts and "tail_outcomes" in t.contexts
    assert "simulation_seed" not in json.dumps(t.progress.export())


def test_failed_experiment_is_not_reduced_to_its_successful_runs(tmp_path):
    class Broken(GaussianControl):
        def run(self, *args, **kwargs):
            raise ValueError("test failure")

    execute(design(), Broken(), tmp_path / "failed")
    with pytest.raises(ValueError, match="Incomplete"):
        research_contexts(tmp_path / "failed")


def test_adapter_recomputes_analysis_from_verified_rows(tmp_path):
    execute(design(), GaussianControl(), tmp_path / "experiment")
    path = tmp_path / "experiment" / "experiment.json"
    before = research_contexts(path)
    raw = json.loads(path.read_text())
    raw["analysis"]["variants"]["a"]["distributions"]["net_pnl"]["mean"] = 999999
    raw.pop("record_digest")
    raw["record_digest"] = digest(raw)
    path.write_text(json.dumps(raw))
    after = research_contexts(path)
    assert before == after


def test_phase4_public_observation_adapter_and_manual_tutor_preserve_lab():
    market = SimulationConfig(duration_us=2_000_000, informed_rate_per_second=1)
    maker = MakerConfig(strategy=Strategy.MANUAL)
    lab = MarketMakingLab(market, maker)
    observation = lab.advance_to_decision()
    contexts = maker_contexts(observation, source="lab", event=0, hard_limit=maker.hard_limit)
    assert all("latent" not in str(c.public()) for c in contexts)
    output = []
    t = Tutor()

    def read(prompt):
        return ""  # skip tutoring / repeat existing quotes

    baseline = manual_session(market, maker, read=read, write=lambda _: None)
    taught = manual_session(market, maker, adaptive_tutor=t, read=read, write=output.append)
    assert baseline == taught
    assert any("QUANT TUTOR:" in line for line in output)
    assert not t.progress.data["recent"]


def test_disabled_tutor_rejects_stale_answer_submission(desk):
    identifier = desk.learning.tutor.active["id"]
    tc(desk, "configure", enabled=False)
    with pytest.raises(ValueError, match="disabled"):
        tc(desk, "answer", question_id=identifier, answer="weighted")
    assert desk.learning.tutor.progress.data["recent"] == []


def test_actual_research_units_are_preserved(tmp_path):
    raw = execute(design(), GaussianControl(), tmp_path / "experiment")
    for context in research_contexts(tmp_path / "experiment"):
        assert context.facts["unit"] == raw["metric_units"][context.facts["variant"]]["net_pnl"]


def test_saved_history_cannot_smuggle_unknown_observer_fields(tmp_path):
    path = tmp_path / "learning.json"
    p = Progress(path)
    grade(p)
    data = json.loads(path.read_text())
    data["recent"][0]["latent_ticks"] = 99999
    path.write_text(json.dumps(data))
    c = Controller(learning_path=path)
    assert c.learning.state()["error"]
    with pytest.raises(ValueError):
        c.learning.exports()
    assert buy(c, 1)["result"]["ok"]


def test_due_review_can_return_at_automatic_event_cadence(desk):
    t = desk.learning.tutor
    clock = Calendar()
    t.progress.clock = clock
    t.configure(event_gap=1)
    t.answer(t.active["id"], "mid")
    t.explain()
    clock.advance(2)
    desk.command({"kind": "step_event"})
    assert t.active["concept"] == "vwap"
    assert not t.active["closed"]


def test_research_sweep_triggers_selection_without_claiming_drawdown_from_minimum(tmp_path):
    from quantlab.research.models import Variant

    spec = replace(
        design(),
        variants=tuple(
            Variant(name, {"variant_id": name, "mean": 0, "sd": 1}) for name in ("a", "b", "c")
        ),
    )
    execute(spec, GaussianControl(), tmp_path / "sweep")
    t = Tutor()
    t.study(research_contexts(tmp_path / "sweep"))
    assert "selection_bias" in t.contexts and "tail_outcomes" in t.contexts
    assert "drawdown" not in t.contexts


def test_adverse_selection_trigger_never_requires_private_identity():
    from quantlab.tutor.context import PublicContext

    t = Tutor()
    context = PublicContext(
        "recorded-public",
        "markout",
        8,
        3_000_000,
        {
            "trade_id": 1,
            "role": "provider",
            "horizon": 5,
            "value": "-0.03",
            "observed_time_us": 3_000_000,
        },
    )
    t.study([context])
    assert t.active["concept"] == "adverse_selection"
    assert "counterparty" not in context.facts
    assert "informed" not in t.active["context"]["facts"]


def test_newer_question_cannot_be_answered_using_a_stale_identifier(desk):
    previous = desk.learning.tutor.active["id"]
    tc(desk, "quiz", concept="liquidity")
    with pytest.raises(ValueError, match="changed"):
        tc(desk, "answer", question_id=previous, answer="orders")
    assert desk.learning.tutor.progress.data["recent"] == []


@pytest.mark.parametrize(
    "resting,flow,price,deeper,sweep",
    [
        ("sell", "buy", "100.03", "100.10", 18),
        ("buy", "sell", "99.97", "99.90", 21),
    ],
)
def test_actual_adverse_provider_marks_in_both_directions(resting, flow, price, deeper, sweep):
    from fractions import Fraction

    session = scripted([(100_000, flow, sweep), (200_000, flow, 2)])
    order(session, side=resting, quantity=5, price=price)
    order(session, side=resting, quantity=2, price=deeper)
    t = Tutor()
    t.observe(session.public_snapshot(), "provider-example")
    session.command("step_event")
    t.observe(session.public_snapshot(), "provider-example")
    assert "adverse_selection" not in t.contexts
    assert any(m["status"] == "pending" for m in session.public_snapshot()["markouts"])
    session.command("step_event")
    t.observe(session.public_snapshot(), "provider-example")
    context = t.contexts["adverse_selection"]
    assert Fraction(context.facts["value"]) == Fraction("-0.015")
    assert context.facts["role"] == "provider"
    assert session.account.inventory == (5 if resting == "buy" else -5)
    session.check_invariants()


def test_short_demo_is_reproducible_without_touching_personal_progress():
    from quantlab.tutor_demo import demonstrate

    first = demonstrate()
    second = demonstrate()
    assert first == second
    assert first["market_independence"]["identical_journals"]
    assert first["interview"]["question"]["difficulty"] == 2
    assert first["session_review"]["what_happened"]["final_pnl"] == "0.04400"


def test_known_then_contains_no_post_execution_result(desk):
    desk.command({"kind": "end"})
    review = tc(desk, "review")["review"]
    assert "VWAP" not in review["known_then"][0]["order"]
    assert "filled" not in review["known_then"][0]["order"]
    assert review["known_then"][0]["observed"]["position"] == 0


def test_phase4_tutor_failure_cannot_stop_manual_trading(monkeypatch):
    market = SimulationConfig(duration_us=1_000_000)
    maker = MakerConfig(strategy=Strategy.MANUAL)
    tutor = Tutor()

    def fail(*args, **kwargs):
        raise OSError("test storage failure")

    monkeypatch.setattr(tutor, "study", fail)
    output = []
    actual = manual_session(
        market, maker, adaptive_tutor=tutor, read=lambda _: "", write=output.append
    )
    assert actual == manual_session(market, maker, read=lambda _: "", write=lambda _: None)
    assert any("Tutor stopped" in text for text in output)


def test_go_deeper_for_qualitative_concept_changes_level_without_credit(desk):
    tc(desk, "quiz", concept="architecture", mode="defence")
    before = desk.learning.tutor.progress.status("architecture")
    deeper = tc(desk, "deeper")["current"]["deeper"]
    assert deeper["difficulty"] == 3
    assert deeper["answer_type"] == "choices"
    assert desk.learning.tutor.progress.status("architecture") == before


def test_rewinding_replay_discards_later_frame_tutor_contexts(desk):
    desk.command({"kind": "step_interval", "payload": {"delta_us": 2_000_000}})
    desk.command({"kind": "end"})
    desk.command({"kind": "load_replay", "payload": {"journal_text": dumps(desk.session)}})
    desk.command({"kind": "replay_step", "payload": {"index": len(desk.frames) - 1}})
    tc(desk, "quiz", concept="markouts")
    assert desk.learning.tutor.active["context"]["event"] > 0
    desk.command({"kind": "replay_step", "payload": {"index": 0}})
    assert desk.learning.state()["current"] is None
    for context in desk.learning.tutor.contexts.values():
        if context.source == desk.learning_source:
            assert context.event <= desk.state()["public_event"]
            assert context.time_us <= desk.state()["time_us"]
    with pytest.raises(ValueError):
        tc(desk, "quiz", concept="markouts")


def test_rewind_boundary_applies_while_tutor_is_disabled(desk):
    desk.command({"kind": "step_interval", "payload": {"delta_us": 2_000_000}})
    desk.command({"kind": "end"})
    desk.command({"kind": "load_replay", "payload": {"journal_text": dumps(desk.session)}})
    desk.command({"kind": "replay_step", "payload": {"index": len(desk.frames) - 1}})
    tc(desk, "quiz", concept="markouts")
    tc(desk, "configure", enabled=False)
    desk.command({"kind": "replay_step", "payload": {"index": 0}})
    assert tc(desk, "configure", enabled=True)["current"] is None
    with pytest.raises(ValueError):
        tc(desk, "quiz", concept="markouts")
