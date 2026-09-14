import json
from dataclasses import asdict, replace

import pytest

from quantlab.research.codec import digest
from quantlab.research.engine import execute
from quantlab.research.registry import EvaluationReuseWarning
from quantlab.research.replay import reproduce_run
from quantlab.statarb.examples import teaching_cases
from quantlab.statarb.research import (
    BASE_RULES,
    StatArbAdapter,
    backtest,
    candidate_rules,
    evaluate_selection,
    experiment_spec,
    generate,
    invalid_lookahead,
    mining_universe,
    select_pair,
    sweep,
    walk_forward,
)
from quantlab.statarb.session import StatArbSession
from quantlab.trading.server import Controller
from quantlab.tutor.context import PublicContext
from quantlab.tutor.questions import question_for
from quantlab.tutor.statarb import LESSONS, statarb_context


@pytest.fixture(scope="module")
def public_state():
    s = StatArbSession(capture=False)
    s.command("step", count=80)
    return s.state()


@pytest.mark.parametrize("concept", list(LESSONS))
@pytest.mark.parametrize("level", [1, 4])
def test_causal_contextual_tutoring_for_each_topic(public_state, concept, level):
    c = statarb_context(public_state, "test")
    q = question_for(concept, c, level)
    assert (
        q.concept == concept
        and q.difficulty == level
        and q.intuition
        and q.maths
        and q.interview
    )
    assert "observed event" in q.quantlab
    assert "future" not in c.facts


def test_tutor_fact_allowlist_rejects_hidden_state(public_state):
    c = statarb_context(public_state, "test")
    with pytest.raises(ValueError):
        PublicContext(c.source, c.kind, c.event, c.time_us, dict(c.facts) | {"latent": 100})


def test_tutor_live_bridge_retains_no_generated_answers_and_clears_rewind():
    c = Controller()
    lab = c.statarb_lab
    lab.command({"kind": "step", "payload": {"count": 80}})
    assert c.learning.error is None
    assert c.learning.tutor.progress.data["recent"] == []
    lab.command({"kind": "end"})
    j = lab.journal()
    lab.command({"kind": "load_replay", "payload": {"journal_text": json.dumps(j)}})
    contexts = c.learning.tutor.contexts.values()
    assert all(x.event <= 0 for x in contexts if x.source == "statarb-session")
    assert c.learning.tutor.progress.data["recent"] == []


@pytest.mark.parametrize("mode", ["fixed", "rolling", "walk_forward"])
def test_causal_backtests_reproducible_without_capture_difference(mode):
    data, _ = generate(543, steps=180)
    rules = replace(BASE_RULES, mode=mode)
    a, b = backtest(data, rules=rules, capture=False), backtest(data, rules=rules, capture=True)
    assert a.metrics() == b.metrics() and a.decisions == b.decisions and a.fills == b.fills


def test_walk_forward_freezes_past_fit_for_each_block():
    data, _ = generate(874, steps=220)
    s, blocks = walk_forward(data, start=120)
    assert len(blocks) == 6
    for b in blocks:
        assert b["fit"]["end"] == b["start"] and b["fit"]["start"] == b["start"] - 60
        fitted = [d["estimation_fit"] for d in s.decisions if b["start"] <= d["t"] < b["end"]]
        assert all(f == b["fit"] for f in fitted)
    assert len({b["fit"]["beta"] for b in blocks}) > 1


def test_sweep_preserves_all_tried_settings_and_failure():
    data, _ = generate(543, steps=160)
    candidates = candidate_rules() + [asdict(BASE_RULES) | {"window": 2}]
    result = sweep(data, candidates=candidates)
    assert len(result["candidates"]) == 12
    assert result["candidates"][-1]["status"] == "failed"
    assert not result["evaluation_accessed"]
    assert {
        k
        for k in ("entry", "exit", "window", "z_window", "stop")
        if len({r["parameters"][k] for r in result["candidates"]}) > 1
    } == {"entry", "exit", "window", "z_window", "stop"}
    good = [x for x in result["candidates"] if x["status"] == "complete"]
    winner = result["candidates"][result["selected"]]
    assert winner["metrics"]["net_pnl"] == max(x["metrics"]["net_pnl"] for x in good)


def test_selection_persisted_before_holdout_and_reuse_recorded(tmp_path):
    data, _ = generate(623, steps=180)
    selection = sweep(data[:140], candidates=[asdict(BASE_RULES)])
    frozen = digest(selection)
    path = tmp_path / "study"
    result = evaluate_selection(
        data,
        selection,
        split=140,
        registry=tmp_path / "registry.jsonl",
        destination=path,
        seed=12,
    )
    assert result["status"] == "complete"
    assert json.loads((path / "selection.json").read_text())["evaluation_accessed"] is False
    assert digest(selection) == frozen
    assert json.loads((tmp_path / "registry.jsonl").read_text())["seeds"] == [12]
    with pytest.warns(EvaluationReuseWarning):
        second = evaluate_selection(
            data,
            selection,
            split=140,
            registry=tmp_path / "registry.jsonl",
            destination=tmp_path / "second",
            seed=12,
        )
    assert second["warnings"]


def test_pair_mining_discloses_fixed_universe_every_candidate_and_selection():
    data, _ = mining_universe(201042, assets=5, steps=180)
    selection = select_pair(data[:160])
    changed = data.copy()
    changed[160:] += 1000
    again = select_pair(changed[:160])
    assert selection == again and len(selection["candidates"]) == 10
    assert selection["universe"] == [f"NULL-{i}" for i in range(5)]
    assert not selection["evaluation_accessed"]
    assert "training" in selection["criterion"]


def test_bad_evaluation_visible_and_selection_unchanged(tmp_path):
    data, _ = generate(234, steps=180)
    sel = sweep(data[:140], candidates=[asdict(BASE_RULES)])
    bad = data.copy()
    bad[150, 1] = float("nan")
    out = evaluate_selection(
        bad,
        sel,
        split=140,
        registry=tmp_path / "registry",
        destination=tmp_path / "result",
        seed=13,
    )
    assert out["status"] == "failed" and (tmp_path / "result/evaluation.json").exists()
    assert (tmp_path / "registry").exists()


def test_phase5_adapter_registered_execution_and_reproduction(tmp_path):
    spec = experiment_spec("walk_forward", runs=2, steps=220, split=120, pool="evaluation")
    record = execute(
        spec, StatArbAdapter(), tmp_path / "study", evaluation_registry=tmp_path / "registry"
    )
    assert record["status"] == "complete"
    assert (tmp_path / "study/registration.json").exists() and (tmp_path / "registry").exists()
    # Verify full regeneration against Phase 5 stored evidence, not a separate implementation.
    result = reproduce_run(record, StatArbAdapter(), spec.variants[0].name, 0)
    assert result


@pytest.mark.parametrize(
    "experiment", ["generalisation", "walk_forward", "costs", "regime", "mining"]
)
def test_research_design_registers_prior_hypothesis_and_all_variants(experiment):
    spec = experiment_spec(experiment, runs=2)
    assert len(spec.variants) == 2 and spec.question and spec.hypothesis
    assert spec.paired == (experiment != "regime")
    assert spec.seeds.pool == "development"
    for v in spec.variants:
        StatArbAdapter().validate(v.configuration)


def test_same_environment_full_summary_have_identical_fingerprints():
    config = (
        experiment_spec("walk_forward", runs=2, steps=200, split=120).variants[0].configuration
    )
    a = StatArbAdapter().run(34, config)
    b = StatArbAdapter().run(34, config, full=True)
    assert a.metrics == b.metrics and a.trajectory_fingerprint == b.trajectory_fingerprint
    assert a.environment_fingerprint == b.environment_fingerprint


def test_cost_increase_reduces_same_immediate_roundtrip():
    outputs = []
    for fee in (0, 0.05):
        s = StatArbSession(fee=fee, capture=False)
        s.command("step", count=80)
        s.command("pair", action="long")
        s.command("next_leg")
        s.command("close")
        s.command("next_leg")
        outputs.append(s.metrics())
    assert outputs[1]["net_pnl"] < outputs[0]["net_pnl"]
    assert outputs[1]["turnover"] == outputs[0]["turnover"]


def test_invalid_oracle_explicitly_rejected_despite_apparent_gain():
    data, _ = generate(201042, steps=180)
    bad = invalid_lookahead(data)
    assert not bad["deployable"] and "INVALID" in bad["label"]
    assert bad["net_pnl"] > backtest(data).metrics()["net_pnl"]


def test_teaching_cases_distinguish_dgp_claims_and_disclose_spurious_selection():
    cases = teaching_cases()
    assert "phi=1" in cases["process_claims"]["noncointegrated"]
    assert len(cases["cases"]["spurious"]["all_candidates"]) == 28
    assert "deliberately selected" in cases["cases"]["spurious"]["selection"]
    assert cases["cases"]["exact_regression"]["alpha"] == pytest.approx(2)
    assert cases["cases"]["exact_regression"]["beta"] == pytest.approx(3)


def test_risk_application_shows_actual_linked_pair_and_hides_during_replay():
    c = Controller()
    lab = c.statarb_lab
    lab.command({"kind": "step", "payload": {"count": 80}})
    lab.command({"kind": "pair", "payload": {"action": "long"}})
    report = c.risk_lab.state()["linked_statarb"]
    assert any(p["instrument"] == "SA-Y" for p in report["portfolio"]["positions"])
    assert report["portfolio"]["gross"] > 0
    lab.command({"kind": "end"})
    j = lab.journal()
    lab.command({"kind": "load_replay", "payload": {"journal_text": json.dumps(j)}})
    assert c.risk_lab.state()["linked_statarb"] is None
