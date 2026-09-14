"""New lessons use actual risk facts; studies use Phase 5 registration and seed discipline."""

import json
from dataclasses import asdict

import pytest

from quantlab.research.engine import execute, load_experiment
from quantlab.research.registry import EvaluationReuseWarning
from quantlab.research.replay import reproduce_run
from quantlab.risk.analytics import RiskSettings
from quantlab.risk.research import RiskAdapter, experiment_spec
from quantlab.risk.session import RiskSession
from quantlab.trading.server import Controller
from quantlab.tutor.catalog import RISK_CONCEPTS
from quantlab.tutor.context import PublicContext
from quantlab.tutor.questions import question_for
from quantlab.tutor.risk import risk_context


@pytest.fixture(scope="module")
def risk_state():
    s = RiskSession(settings=RiskSettings(paths=300, sample_size=100))
    s.execute(
        "options",
        "option_order",
        contract_id=s.options.selected,
        side="buy",
        quantity=1,
        quote_revision=s.options.quote_revision,
    )
    s.execute("options", "hedge")
    s.execute("risk", "scenario", stock_return=-0.08, volatility_change=0.12)
    s.execute("risk", "optimise", max_cash=0)
    return s.state()


@pytest.mark.parametrize("concept", list(RISK_CONCEPTS))
@pytest.mark.parametrize("level", [1, 3])
def test_risk_concepts_have_distinct_current_lessons(risk_state, concept, level):
    c = risk_context(risk_state, "risk-test")
    q = question_for(concept, c, level)
    assert q.concept == concept and q.maths and q.interview
    assert "risk-test" in q.quantlab
    assert q.difficulty == level


@pytest.mark.parametrize(
    "concept", ["var", "tail_risk", "portfolio_variance", "scenario_analysis", "concentration"]
)
def test_first_principles_numeric_check(risk_state, concept):
    q = question_for(concept, risk_context(risk_state, "actual"), 2)
    assert q.answer_type == "number" and q.difficulty == 2


def test_risk_context_allowlist_rejects_hidden_facts(risk_state):
    c = risk_context(risk_state, "risk")
    with pytest.raises(ValueError):
        PublicContext(c.source, c.kind, c.event, c.time_us, dict(c.facts) | {"latent": 100})
    raw = json.dumps(c.public())
    for key in ("signal", "innovation", "seed", "future_price"):
        assert key not in raw


def test_tutor_rewind_clears_future_risk_state():
    c = Controller()
    r = c.risk_lab
    s = r.session
    r.command({"kind": "scenario", "payload": {"stock_return": -0.1}})
    first = s.state()
    r.command(
        {
            "kind": "trade",
            "payload": {
                "target": "options",
                "command": "stock_order",
                "fields": dict(side="buy", quantity=10, order_type="market"),
            },
        }
    )
    assert c.learning.tutor.contexts["var"].event > first["revision"]
    c.learning.observe_risk(first, "risk-session")
    assert c.learning.tutor.contexts["var"].event == first["revision"]
    assert c.learning.error is None


def test_tutor_never_credits_an_encounter_as_mastery():
    c = Controller()
    c.risk_lab.command({"kind": "scenario", "payload": {"stock_return": -0.1}})
    assert not c.learning.tutor.progress.data["recent"]


@pytest.mark.parametrize("experiment", ["correlation", "tails", "nonlinearity", "sample_size"])
def test_registered_research_runs_and_reproduction(tmp_path, experiment):
    spec = experiment_spec(experiment, runs=3, paths=300)
    r = execute(spec, RiskAdapter(), tmp_path / experiment)
    assert r["status"] == "complete"
    assert len(r["runs"]) == 6
    assert (
        load_experiment(tmp_path / experiment / "experiment.json")["design_digest"]
        == r["design_digest"]
    )
    name = spec.variants[0].name
    full = reproduce_run(r, RiskAdapter(), variant=name, run_index=0)
    row = next(x for x in r["runs"] if x["variant"] == name and x["run_index"] == 0)
    assert full.metrics == row["metrics"]
    assert full.journal["portfolio"]["positions"]


def test_evaluation_reuse_is_durable_and_explicit(tmp_path):
    spec = experiment_spec("correlation", runs=2, pool="evaluation", paths=100)
    a = RiskAdapter()
    reg = tmp_path / "evaluations.jsonl"
    first = execute(spec, a, tmp_path / "first", evaluation_registry=reg)
    assert not first["warnings"]
    with pytest.warns(EvaluationReuseWarning):
        second = execute(spec, a, tmp_path / "second", evaluation_registry=reg)
    assert second["warnings"] and len(reg.read_text().splitlines()) == 2


def test_full_lightweight_same_risk_numbers():
    a = RiskAdapter()
    c = {"settings": asdict(RiskSettings(paths=200)), "portfolio": "hedged_call"}
    light = a.run(456, c)
    full = a.run(456, c, full=True)
    assert full.metrics == light.metrics
    assert full.environment_fingerprint == light.environment_fingerprint
    assert full.trajectory_fingerprint == light.trajectory_fingerprint


def test_new_risk_replay_clears_other_desk_future_contexts(tmp_path):
    c = Controller(learning_path=tmp_path / "learning.json")
    o = c.options_lab
    o.command(
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
    assert any(x.kind == "derivatives" for x in c.learning.tutor.contexts.values())
    r = c.risk_lab
    r.command({"kind": "end"})
    original = json.dumps(r.journal())
    r.command({"kind": "load_replay", "payload": {"journal_text": original}})
    assert all(x.kind == "risk" for x in c.learning.tutor.contexts.values())
    assert c.learning.tutor.progress.data["recent"] == []
