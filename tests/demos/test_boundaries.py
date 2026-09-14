import copy
import json

import pytest

from quantlab.demos.annotations import CLASSIFICATIONS
from quantlab.demos.registry import FLAGSHIPS
from quantlab.research.codec import digest
from quantlab.trading.server import Controller


def call(h, kind, **p):
    return h.command({"kind": kind, "payload": p})


def finish(h):
    while not h.completed:
        call(h, "next")


@pytest.mark.parametrize("key", FLAGSHIPS)
def test_future_changes_do_not_change_before_response_or_explanation(key):
    h = Controller().demos
    h.start(key, "learn")
    before = copy.deepcopy(h.state())
    h.moment.after["future_canary"] = "NEVER BEFORE"
    h.evidence.private = {"private_canary": "NEVER BEFORE"}
    assert h.state() == before
    assert "NEVER BEFORE" not in json.dumps(call(h, "explain", concept=h.moment.concept))
    assert h.state()["active"]["question"]["solution"] is None


@pytest.mark.parametrize("key", ["picked-off", "synthetic-prices", "hidden-scenario"])
def test_hidden_inputs_only_available_after_completion_and_explicit_hindsight(key):
    h = Controller().demos
    h.start(key)
    with pytest.raises(ValueError):
        call(h, "hindsight", reveal=True)
    while not h.completed:
        serialized = json.dumps(h.state())
        for field in (
            "latent_before_ticks",
            "latent_after_ticks",
            "error_ticks",
            "signal_weight",
            "liquidity_shock",
        ):
            if key != "hidden-scenario" and field == "liquidity_shock":
                continue
            assert field not in serialized
        call(h, "next")
    assert h.state()["active"]["observer"] is None
    v = call(h, "hindsight", reveal=True)
    assert v["active"]["observer"]
    assert not v["active"]["question"] or not v["active"]["question"]["mastery_eligible"]


@pytest.mark.parametrize("mode", ["quick", "learn", "quant", "interview"])
def test_watching_never_changes_mastery_in_any_mode(mode):
    c = Controller()
    before = copy.deepcopy(c.learning.tutor.progress.data)
    h = c.demos
    h.start("order", mode)
    finish(h)
    assert c.learning.tutor.progress.data == before
    assert h.progress.public()["demos"]["order"] == {
        "viewed": 1,
        "completed": 1,
        "checkpoints_attempted": 0,
    }


@pytest.mark.parametrize("mode", ["quick", "quant", "interview"])
def test_showcase_answers_do_not_change_mastery_or_market_state(mode):
    c = Controller()
    h = c.demos
    h.start("order", mode)
    learner = copy.deepcopy(c.learning.tutor.progress.data)
    market = digest(c.session.evidence)
    call(h, "answer", question_id=h.qstate()["id"], answer="no")
    assert c.learning.tutor.progress.data == learner
    assert digest(c.session.evidence) == market
    assert h.progress.public()["demos"]["order"]["checkpoints_attempted"] == 1


def test_learn_answer_uses_existing_grader_and_records_first_attempt(tmp_path):
    c = Controller(learning_path=tmp_path / "learning.json")
    h = c.demos
    h.start("order", "learn")
    call(h, "answer", question_id=h.qstate()["id"], answer="no")
    row = c.learning.tutor.progress.data["recent"][-1]
    assert row["result"] == "correct_first" and row["credit"] == 1
    assert row["source"] == "demo:order"
    assert (tmp_path / "learning-demos.json").exists()


def test_hint_retry_and_reveal_follow_core_grading_rules():
    c = Controller()
    h = c.demos
    h.start("order", "learn")
    call(h, "answer", question_id=h.qstate()["id"], answer="yes")
    assert h.qstate()["closed"]
    call(h, "hint")
    call(h, "retry")
    call(h, "answer", question_id=h.qstate()["id"], answer="no")
    recent = c.learning.tutor.progress.data["recent"]
    assert [r["result"] for r in recent] == ["incorrect", "correct_after_hint"]
    assert recent[-1]["credit"] == 0.5
    with pytest.raises(ValueError):
        call(h, "answer", question_id=h.qstate()["id"], answer="no")
    call(h, "hint")
    with pytest.raises(ValueError):
        call(h, "hint")


def test_explain_answer_before_submission_never_earns_mastery():
    c = Controller()
    h = c.demos
    h.start("order", "learn")
    before = copy.deepcopy(c.learning.tutor.progress.data)
    call(h, "explain_answer")
    assert h.state()["active"]["question"]["solution"]["expected"] == "no"
    call(h, "answer", question_id=h.qstate()["id"], answer="no")
    assert c.learning.tutor.progress.data == before


def test_prior_showcase_reveal_blocks_credit_after_restart_and_across_server_restart(tmp_path):
    c = Controller(learning_path=tmp_path / "learning.json")
    h = c.demos
    h.start("order")
    call(h, "next")
    call(h, "restart")
    call(h, "mode", mode="learn")
    assert not h.state()["active"]["question"]["mastery_eligible"]
    new = Controller(learning_path=tmp_path / "learning.json").demos
    new.start("order", "learn")
    assert not new.state()["active"]["question"]["mastery_eligible"]


def test_disabled_tutor_leaves_answers_as_ungraded_practice():
    c = Controller()
    c.learning.tutor.progress.data["settings"]["enabled"] = False
    h = c.demos
    h.start("order", "learn")
    before = copy.deepcopy(c.learning.tutor.progress.data)
    call(h, "answer", question_id=h.qstate()["id"], answer="no")
    assert c.learning.tutor.progress.data == before


@pytest.mark.parametrize("bad", [None, "", "not-a-choice", [], True, 1, {"answer": "no"}])
def test_invalid_answers_do_not_record_attempts(bad):
    h = Controller().demos
    h.start("order", "learn")
    before = copy.deepcopy(h.progress.data)
    with pytest.raises(ValueError):
        call(h, "answer", question_id=h.qstate()["id"], answer=bad)
    assert h.qstate()["attempt"] == 0 and h.progress.data == before


def test_stale_question_rejected_after_advancing():
    h = Controller().demos
    h.start("delta-hedge", "learn")
    old = h.qstate()["id"]
    call(h, "next")
    call(h, "next")
    with pytest.raises(ValueError):
        call(h, "answer", question_id=old, answer="no")


@pytest.mark.parametrize("bad", ["NaN", "Infinity", "1e999", "£51", False, [], {}, "1/0"])
def test_numeric_hedge_validator_rejects_nonfinite_or_malformed_inputs(bad):
    h = Controller().demos
    h.start("delta-hedge", "learn")
    call(h, "next")
    call(h, "next")
    with pytest.raises(ValueError):
        call(h, "answer", question_id=h.qstate()["id"], answer=bad)
    assert h.qstate()["attempt"] == 0


@pytest.mark.parametrize("key", FLAGSHIPS)
def test_demo_modes_hints_and_explanation_do_not_consume_market_rng_or_change_personal_session(
    key,
):
    c = Controller()
    h = c.demos
    evidence = copy.deepcopy(c.session.evidence)
    rng = c.session.environment._latent_rng.getstate()
    signal_rng = c.session.environment._signal_rng.getstate()
    h.start(key, "learn")
    outcomes = copy.deepcopy([m.after for m in h.evidence.moments])
    call(h, "hint")
    call(h, "mode", mode="interview")
    call(h, "explain", concept=h.moment.concept)
    assert c.session.evidence == evidence
    assert c.session.environment._latent_rng.getstate() == rng
    assert c.session.environment._signal_rng.getstate() == signal_rng
    assert outcomes == [m.after for m in h.evidence.moments]


def test_historical_explanation_cannot_claim_latent_cause():
    h = Controller().demos
    h.start("historical")
    while not h.completed:
        d = call(h, "explain", concept="historical_replay")
        assert "cause" in json.dumps(d).lower() or "why" in json.dumps(d).lower()
        assert not d["quiz_allowed"]
        assert "latent_before_ticks" not in json.dumps(d)
        assert "ARTIFICIAL" in d["environment"]["badge"]
        call(h, "next")


@pytest.mark.parametrize("classification", CLASSIFICATIONS)
def test_process_classification_is_explicit_user_reflection_only(classification):
    c = Controller()
    h = c.demos
    h.start("order")
    call(h, "next")
    before = copy.deepcopy(c.learning.tutor.progress.data)
    v = call(
        h,
        "reflect",
        classification=classification,
        reason="My declared size limit was ten units.",
    )
    assert v["active"]["reflection"]["classification"] == classification
    assert "unknown" in v["active"]["process_assessment"].lower()
    assert c.learning.tutor.progress.data == before
    assert "not an automatic" in v["active"]["reflection"]["label"]


def test_reflection_does_not_accept_an_automatic_profit_grade_or_missing_reason():
    h = Controller().demos
    h.start("order")
    with pytest.raises(ValueError):
        call(h, "reflect", classification=CLASSIFICATIONS[0], reason="Rule")
    call(h, "next")
    with pytest.raises(ValueError):
        call(h, "reflect", classification="Excellent trade", reason="Made money")
    with pytest.raises(ValueError):
        call(h, "reflect", classification=CLASSIFICATIONS[0], reason="")


def test_capture_requires_explicit_showcase_and_disables_all_question_credit():
    h = Controller().demos
    h.start("order", "learn")
    with pytest.raises(ValueError):
        call(h, "capture", name="order-after-multifill")
    v = call(h, "capture", name="order-before-submit", showcase=True)
    assert v["active"]["showcase"] and not v["active"]["question"]["mastery_eligible"]
    call(h, "restart")
    assert not h.state()["active"]["question"]["mastery_eligible"]


def test_script_and_path_export_gated_and_branch_path_recorded():
    h = Controller().demos
    h.start("delta-hedge")
    with pytest.raises(ValueError):
        h.export()
    with pytest.raises(ValueError):
        h.path_journal()
    call(h, "next")
    call(h, "next")
    call(h, "branch", choice="partial")
    finish(h)
    assert h.path_journal()["branch"] == "partial"
    assert any(a["kind"] == "branch" for a in h.path_journal()["actions"])
    for heading in (
        "SETUP",
        "WHAT USER DOES",
        "WHAT QUANTLAB SHOWS",
        "KEY EXPLANATION",
        "MATHS",
        "REAL-FINANCE USE",
        "LIMITATIONS",
    ):
        assert heading in h.export()


def test_public_responses_are_detached_from_private_evidence():
    h = Controller().demos
    h.start("order")
    v = h.state()
    v["active"]["point"]["core"]["account"]["cash"] = "999999"
    assert h.state()["active"]["point"]["core"]["account"]["cash"] == "10000.00000"


@pytest.mark.parametrize("answer", ["yes", "no"])
def test_showcase_answer_feedback_cannot_be_relabelled_as_fresh_learning(answer):
    c = Controller()
    h = c.demos
    h.start("order", "quick")
    before = copy.deepcopy(c.learning.tutor.progress.data)
    call(h, "answer", question_id=h.qstate()["id"], answer=answer)
    call(h, "restart")
    call(h, "mode", mode="learn")
    assert not h.state()["active"]["question"]["mastery_eligible"]
    assert h.state()["active"]["question"]["solution"] is None
    call(h, "answer", question_id=h.qstate()["id"], answer="no")
    assert c.learning.tutor.progress.data == before
