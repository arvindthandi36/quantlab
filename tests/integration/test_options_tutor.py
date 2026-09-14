import copy
from dataclasses import replace

import pytest

from quantlab.options.application import OptionsLab
from quantlab.options.session import OptionsSession
from quantlab.tutor.bridge import Learning
from quantlab.tutor.catalog import ACTIVE_CONCEPTS, OPTION_CONCEPTS
from quantlab.tutor.context import context_from_dict
from quantlab.tutor.derivatives import derivative_context
from quantlab.tutor.questions import question_for


@pytest.fixture
def lab(tmp_path):
    return OptionsLab(Learning(tmp_path / "learning.json"), directory=tmp_path / "sessions")


def buy(lab, side="buy", quantity=1):
    return lab.command(
        {
            "kind": "option_order",
            "payload": {
                "contract_id": lab.selected,
                "side": side,
                "quantity": quantity,
                "quote_revision": lab.session.quote_revision,
            },
        }
    )


@pytest.mark.parametrize("concept", OPTION_CONCEPTS)
def test_option_lessons_have_valid_distinct_tiered_questions(lab, concept):
    buy(lab)
    ctx = derivative_context(lab.session.snapshot(), "lesson", "option_order")
    assert ACTIVE_CONCEPTS[concept].implemented
    for level in (1, 2, 3, 4):
        q = question_for(concept, ctx, level)
        assert q.validate(list(q.expected) if isinstance(q.expected, tuple) else q.expected)
        assert q.intuition and q.maths and q.interview and q.quantlab
        assert "expected" not in q.public() and "layers" not in q.public()
        assert "£100" in q.quantlab and "1 × 100" in q.quantlab


@pytest.mark.parametrize("side,word", [("buy", "asset"), ("sell", "liability")])
def test_premium_lesson_uses_actual_side_and_cash_flow(lab, side, word):
    result = buy(lab, side)["result"]
    t = lab.learning.tutor
    assert t.active["concept"] == "premium"
    q = t._question()
    assert word in dict(q.options)[q.expected]
    assert f"{side} 1 × 100" in q.quantlab
    ctx = t.contexts["premium"]
    calc = question_for("premium", ctx, 2)
    assert float(calc.expected) == result["premium_cash_flow"]
    assert t.progress.record_for("premium")["attempts"] == 0
    t.hint()
    t.answer(t.active["id"], "mechanism")
    assert t.progress.data["recent"][-1]["result"] == "correct_after_hint"


def test_delta_and_manual_hedge_questions_use_all_positions_and_multiplier(lab):
    buy(lab, "sell", 5)
    lab.command({"kind": "stock_order", "payload": {"side": "buy", "quantity": 25}})
    ctx = derivative_context(lab.session.snapshot(), "actual")
    q = question_for("contract_multiplier", ctx, 2)
    assert float(q.expected) == pytest.approx(-5 * 100 * ctx.facts["delta"])
    hedge = question_for("delta_hedging", ctx, 2)
    assert float(hedge.expected) == round(-ctx.facts["option_delta"]) - 25


def test_pricing_analysis_and_tutor_never_consume_market_randomness(lab):
    baseline = OptionsSession()
    lab.command({"kind": "iv", "payload": {"initial": 0.001}})
    lab.command({"kind": "mc", "payload": {"paths": 1000, "seed": 991}})
    lab.command({"kind": "shock", "payload": {"spot_change": 2}})
    lab.learning.tutor.ask("delta")
    lab.learning.tutor.explain(deeper=True)
    for s in (baseline, lab.session):
        s.command("step", count=5)
        s.command("end")
    assert baseline.journal() == lab.session.journal()


def test_solver_and_mc_tutoring_uses_actual_diagnostics(lab):
    iv = lab.command({"kind": "iv", "payload": {"initial": 0.001}})["result"]["analysis"]
    c = lab.learning.tutor.contexts["newton_raphson"]
    assert c.facts["solver_method"] == iv["method"]
    assert c.facts["solver_residual"] == iv["residual"]
    mc = lab.command({"kind": "mc", "payload": {"paths": 1000}})["result"]["analysis"]
    c = lab.learning.tutor.contexts["monte_carlo_pricing"]
    assert c.facts["mc_estimate"] == mc["estimate"]
    assert float(question_for("monte_carlo_pricing", c, 2).expected) == mc["standard_error"] / 2


@pytest.mark.parametrize("field", ["seed", "next_spot", "innovations", "latent_value"])
def test_derivative_context_rejects_private_fields(lab, field):
    raw = derivative_context(lab.session.snapshot(), "public").public()
    raw["facts"][field] = 123
    with pytest.raises(ValueError, match="Non-public"):
        context_from_dict(raw)


def test_replay_clears_live_future_and_rewind_clears_same_revision_future(lab):
    buy(lab)
    lab.command({"kind": "step", "payload": {"count": 5}})
    lab.command({"kind": "end"})
    journal = lab.journal()
    lab.command({"kind": "load_replay", "payload": {"journal": journal}})
    assert lab.state()["step"] == 0 and not lab.state()["option_trades"]
    assert lab.learning.tutor.active is None
    assert all(
        c.time_us == 0 for c in lab.learning.tutor.contexts.values() if c.kind == "derivatives"
    )
    final = len(lab.frames) - 1
    lab.command({"kind": "replay_frame", "payload": {"index": final}})
    lab.learning.tutor.ask("delta")
    lab.command({"kind": "replay_frame", "payload": {"index": 0}})
    assert lab.learning.tutor.active is None
    assert all(
        c.time_us == 0 for c in lab.learning.tutor.contexts.values() if c.kind == "derivatives"
    )
    # A batched step can produce intermediate frames with one command revision.
    ctx = derivative_context(lab.state(), lab.source)
    future = replace(ctx, time_us=10_000_000)
    t = lab.learning.tutor
    t.observe_derivative(future)
    t.ask("delta", context=future)
    t.configure(enabled=False)
    t.observe_derivative(ctx)
    assert t.active is None
    assert all(c.time_us <= ctx.time_us for c in t.contexts.values() if c.source == ctx.source)


def test_replay_is_read_only_and_snapshot_is_detached(lab):
    lab.command({"kind": "end"})
    lab.command({"kind": "load_replay", "payload": {"journal": lab.journal()}})
    snapshot = lab.state()
    snapshot["accounts"]["total_pnl"] = 999
    assert lab.state()["accounts"]["total_pnl"] == 0
    with pytest.raises(ValueError, match="read-only"):
        buy(lab)
    with pytest.raises(ValueError, match="ended replay frame"):
        lab.journal()


def test_tutor_failure_and_disabled_state_do_not_prevent_options_execution(lab):
    lab.learning.tutor.configure(enabled=False)
    assert buy(lab)["result"]["filled"] == 1
    assert lab.learning.tutor.active is None
    lab.learning.error = "Injected learning storage failure"
    assert buy(lab)["result"]["filled"] == 1
    lab.session.portfolio.check(lab.session._marks())


def test_failed_automatic_save_preserves_ended_export(lab, tmp_path):
    path = tmp_path / "file-not-directory"
    path.write_text("keep")
    lab.directory = path
    buy(lab)
    result = lab.command({"kind": "end"})
    assert result["state"]["status"] == "ended"
    assert "saving failed" in result["state"]["save_warning"]
    assert lab.journal()["final"]["positions"][0]["quantity"] == 1


def test_new_session_invalid_config_preserves_original(lab):
    before = copy.deepcopy(lab.state())
    with pytest.raises(ValueError):
        lab.command({"kind": "new", "payload": {"implied_volatility": 20}})
    assert lab.state() == before
