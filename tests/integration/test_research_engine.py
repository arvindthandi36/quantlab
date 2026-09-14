import json
from dataclasses import replace

import pytest

from quantlab.research.adapters.control import GaussianControl
from quantlab.research.adapters.maker import MakerAdapter
from quantlab.research.analysis import analyse, extremes
from quantlab.research.cli import comparison_spec
from quantlab.research.codec import digest, plain, read_json
from quantlab.research.engine import execute, load_experiment
from quantlab.research.models import ExperimentSpec, Variant
from quantlab.research.registry import EvaluationReuseWarning
from quantlab.research.replay import reproduce_run, save_reproduced_maker
from quantlab.research.seeds import SeedPlan
from quantlab.research.sweeps import sweep_spec


def design(runs=5, pool="development"):
    return ExperimentSpec(
        "Does noise explain the difference?",
        "Both variants have equal expected payoff.",
        SeedPlan(50, pool, runs),
        tuple(Variant(name, {"variant_id": name, "mean": 0, "sd": 1}) for name in ("a", "b")),
        GaussianControl.name,
        bootstrap_resamples=30,
    )


def test_reproducibility_includes_statistics_bootstrap_and_metadata(tmp_path):
    first = execute(design(), GaussianControl(), tmp_path / "a")
    second = execute(design(), GaussianControl(), tmp_path / "b")
    assert first["runs"] == second["runs"]
    assert first["outcome_digest"] == second["outcome_digest"]
    assert first["analysis"] == second["analysis"]
    assert load_experiment(tmp_path / "a") == first
    assert len(first["runs"]) == 10
    from quantlab import __version__

    assert first["versions"]["quantlab"] == __version__
    assert first["registered_at"] <= first["finished_at"]
    assert first["analysis"] == plain(analyse(first))


def test_registration_and_evaluation_claim_exist_before_any_run(tmp_path):
    destination = tmp_path / "experiment"
    registry = tmp_path / "claims.jsonl"

    class Observer(GaussianControl):
        def run(self, *args, **kwargs):
            raw = read_json(destination / "registration.json")
            assert raw["spec"]["hypothesis"] == design().hypothesis
            assert registry.exists()
            return super().run(*args, **kwargs)

    first = execute(
        design(pool="evaluation"), Observer(), destination, evaluation_registry=registry
    )
    assert first["status"] == "complete"
    with pytest.warns(EvaluationReuseWarning):
        second = execute(
            design(pool="evaluation"),
            GaussianControl(),
            tmp_path / "again",
            evaluation_registry=registry,
        )
    assert second["warnings"] and first["runs"] == second["runs"]


def test_evaluation_requires_registry_and_immutable_destination(tmp_path):
    with pytest.raises(ValueError, match="registry"):
        execute(design(pool="evaluation"), GaussianControl(), tmp_path / "no")
    execute(design(), GaussianControl(), tmp_path / "used")
    with pytest.raises(FileExistsError):
        execute(
            replace(design(), hypothesis="rewrite prediction"),
            GaussianControl(),
            tmp_path / "used",
        )


def test_failures_retained_without_survivor_statistics(tmp_path):
    class FailOne(GaussianControl):
        def run(self, seed, *args, **kwargs):
            if seed == design().seeds.seeds()[1]:
                raise AssertionError("quantity does not reconcile")
            return super().run(seed, *args, **kwargs)

    result = execute(design(), FailOne(), tmp_path / "failed")
    assert result["status"] == "incomplete" and result["analysis"] is None
    assert len(result["runs"]) == 10
    assert sum(r["status"] == "failed" for r in result["runs"]) == 2
    assert len((tmp_path / "failed" / "runs.jsonl").read_text().splitlines()) == 10
    assert load_experiment(tmp_path / "failed") == result
    with pytest.raises(ValueError, match="survivor"):
        extremes(result, "a")


def test_crn_fingerprint_mismatch_fails_experiment(tmp_path):
    class Unfair(GaussianControl):
        def run(self, seed, configuration, **kwargs):
            outcome = super().run(seed, configuration, **kwargs)
            return replace(outcome, environment_fingerprint=digest(configuration["variant_id"]))

    result = execute(design(), Unfair(), tmp_path / "unfair")
    assert result["status"] == "incomplete"
    assert "fingerprint mismatch" in result["runs"][1]["error"]


def test_unfair_market_configuration_rejected_before_registration(tmp_path):
    spec = comparison_spec(runs=2, hypothesis="h")
    c = plain(spec.variants[1].configuration)
    c["market"]["latent_sigma_ticks"] = 4
    spec = replace(spec, variants=(spec.variants[0], Variant("inventory", c)))
    with pytest.raises(ValueError, match="exogenous"):
        execute(spec, MakerAdapter(), tmp_path / "bad")
    assert not (tmp_path / "bad").exists()


@pytest.mark.parametrize("kind", ["metric", "hypothesis", "seed", "row", "analysis"])
def test_serialisation_detects_tampering(tmp_path, kind):
    result = execute(design(), GaussianControl(), tmp_path / "record")
    if kind == "metric":
        result["runs"][0]["metrics"]["net_pnl"] = 900
    elif kind == "hypothesis":
        result["spec"]["hypothesis"] = "retroactive"
    elif kind == "seed":
        result["simulation_seeds"][0] = 1
    elif kind == "row":
        result["runs"].pop()
    else:
        result["analysis"]["paired"] = {}
    p = tmp_path / "tampered.json"
    p.write_text(json.dumps(result))
    with pytest.raises(ValueError, match="integrity"):
        load_experiment(p)


def test_extremes_keep_losers_and_break_ties_by_run_address(tmp_path):
    result = execute(design(), GaussianControl(), tmp_path / "record")
    for row in result["runs"]:
        row["metrics"]["net_pnl"] = 0
    assert [r["run_index"] for r in extremes(result, "a")] == [0, 1, 2]
    result["runs"][6]["metrics"]["net_pnl"] = -100
    assert extremes(result, "a", count=1)[0]["run_index"] == 3
    assert extremes(result, "a", largest=True, count=1)[0]["run_index"] == 0


def test_extreme_run_full_regeneration_and_existing_journal_replay(tmp_path):
    from quantlab.market_making.journal import load_lab, replay_lab

    spec = comparison_spec(runs=6, duration_us=5_000_000, hypothesis="h", resamples=20)
    result = execute(spec, MakerAdapter(), tmp_path / "maker")
    worst = extremes(result, "inventory", count=1)[0]
    lab = save_reproduced_maker(
        result, "inventory", worst["run_index"], tmp_path / "worst.json"
    )
    assert load_lab(tmp_path / "worst.json") == lab == replay_lab(lab)
    assert plain(lab.market_config.seed) == worst["simulation_seed"]
    assert (tmp_path / "worst.provenance.json").exists()
    damaged = plain(result)
    next(
        r
        for r in damaged["runs"]
        if r["variant"] == "inventory" and r["run_index"] == worst["run_index"]
    )["metrics"]["net_pnl"] = 1234
    with pytest.raises(ValueError, match="differs"):
        reproduce_run(damaged, MakerAdapter(), "inventory", worst["run_index"])


def test_replay_rejects_other_versions_and_wrong_run(tmp_path):
    result = execute(design(), GaussianControl(), tmp_path / "data")
    with pytest.raises(ValueError, match="exactly one"):
        reproduce_run(result, GaussianControl(), "a", 999)
    result["versions"]["quantlab"] = "0.0.0"
    with pytest.raises(ValueError, match="versions"):
        reproduce_run(result, GaussianControl(), "a", 0)


def test_engine_supports_thousand_sessions_without_market_assumptions(tmp_path):
    result = execute(
        replace(design(1000), variants=design().variants[:1]),
        GaussianControl(),
        tmp_path / "many",
    )
    assert result["status"] == "complete" and len(result["runs"]) == 1000
    assert result["analysis"]["variants"]["a"]["distributions"]["net_pnl"]["available"] == 1000


def test_reusable_sweep_runs_each_value_and_records_all_variants(tmp_path):
    spec = sweep_spec(
        question="q",
        hypothesis="mean should change by specified amount",
        seeds=SeedPlan(1, "development", 4),
        adapter=GaussianControl(),
        base_configuration={"variant_id": "same", "mean": 0, "sd": 1},
        parameter=("mean",),
        values=(0, 1, 2),
        bootstrap_resamples=20,
    )
    result = execute(spec, GaussianControl(), tmp_path / "sweep")
    assert result["status"] == "complete" and len(result["runs"]) == 12
    groups = result["analysis"]["variants"]
    means = [groups[v.name]["distributions"]["net_pnl"]["mean"] for v in spec.variants]
    assert means[1] - means[0] == pytest.approx(1)
    assert means[2] - means[0] == pytest.approx(2)
