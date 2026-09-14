import json
from dataclasses import replace

import pytest

from quantlab.randomness import RandomStreams
from quantlab.research.adapters.control import GaussianControl
from quantlab.research.adapters.maker import MakerAdapter, maker_configuration
from quantlab.research.codec import canonical, digest, plain, read_json, write_new
from quantlab.research.models import ExperimentSpec, SimulationOutcome, Variant, spec_from_dict
from quantlab.research.registry import EvaluationReuseWarning, claim_evaluation
from quantlab.research.seeds import SeedPlan, derived_seed
from quantlab.research.sweeps import sweep_spec


def test_seed_prefixes_determinism_unique_and_disjoint():
    dev = SeedPlan(10, "development", 1600).seeds()
    test = SeedPlan(10, "evaluation", 1600).seeds()
    assert len(set(dev)) == 1600 and len(set(test)) == 1600
    assert not set(dev) & set(test)
    assert dev[:100] == SeedPlan(10, "development", 100).seeds()
    assert dev[100:400] == SeedPlan(10, "development", 300, start=100).seeds()
    assert dev != SeedPlan(11, "development", 1600).seeds()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"root": True},
        {"root": -1},
        {"pool": "test"},
        {"runs": 0},
        {"runs": True},
        {"start": -1},
    ],
)
def test_seedplan_rejects_invalid(kwargs):
    with pytest.raises((ValueError, TypeError)):
        SeedPlan(**{"root": 1, "pool": "development", "runs": 2, **kwargs})


def test_research_rng_and_unrelated_streams_do_not_perturb_market():
    seed = derived_seed(1, "a")
    baseline = RandomStreams(seed).create("market.latent")
    unrelated = RandomStreams(seed).create("bootstrap")
    for _ in range(100):
        unrelated.gauss(0, 1)
    actual = RandomStreams(seed).create("market.latent")
    assert [baseline.random() for _ in range(20)] == [actual.random() for _ in range(20)]
    assert derived_seed(1, "a") != derived_seed(1, "b") != derived_seed(1, "a", 1)


def test_codec_exact_finite_and_exclusive(tmp_path):
    from fractions import Fraction

    value = {"x": Fraction(1, 3), "y": [1, 2]}
    assert plain(value) == {"x": "1/3", "y": [1, 2]}
    assert digest({"a": 1, "b": 2}) == digest({"b": 2, "a": 1})
    write_new(tmp_path / "a.json", value)
    assert read_json(tmp_path / "a.json") == plain(value)
    with pytest.raises(FileExistsError):
        write_new(tmp_path / "a.json", {})
    with pytest.raises(ValueError):
        canonical(float("nan"))
    (tmp_path / "bad.json").write_text('{"x": NaN}')
    with pytest.raises(ValueError):
        read_json(tmp_path / "bad.json")


def test_registration_requires_question_and_prior_hypothesis():
    spec = ExperimentSpec(
        "question", "prior", SeedPlan(1, "development", 2), (Variant("a", {}),), "adapter"
    )
    assert spec_from_dict(plain(spec)) == spec
    with pytest.raises(ValueError):
        replace(spec, hypothesis=" ")
    with pytest.raises(ValueError):
        replace(spec, variants=(Variant("a", {}), Variant("a", {})))


def test_evaluation_registry_logs_before_access_and_warns_overlap(tmp_path):
    path = tmp_path / "claims.jsonl"
    seeds = SeedPlan(9, "evaluation", 3).seeds()
    assert claim_evaluation(path, design_digest="first", seeds=seeds) == []
    with pytest.warns(EvaluationReuseWarning, match="2 seeds"):
        messages = claim_evaluation(path, design_digest="new-design", seeds=seeds[1:])
    assert "not a fresh holdout" in messages[0]
    assert len([json.loads(s) for s in path.read_text().splitlines()]) == 2
    assert (
        claim_evaluation(
            path, design_digest="fresh", seeds=SeedPlan(9, "evaluation", 2, start=3).seeds()
        )
        == []
    )


def test_sweep_changes_one_field_with_shared_seed_plan():
    base = maker_configuration(strategy="inventory")
    spec = sweep_spec(
        question="q",
        hypothesis="h",
        seeds=SeedPlan(3, "development", 100),
        adapter=MakerAdapter(),
        base_configuration=base,
        parameter=("strategy", "inventory_skew_ticks"),
        values=("0", "1/2", "1"),
    )
    assert spec.paired
    for v, value in zip(spec.variants, ("0", "1/2", "1"), strict=True):
        expected = plain(base)
        expected["strategy"]["inventory_skew_ticks"] = value
        assert v.configuration == expected
    assert base["strategy"]["inventory_skew_ticks"] == "1/2"


def test_market_parameter_sweep_does_not_claim_identical_paths():
    spec = sweep_spec(
        question="q",
        hypothesis="h",
        seeds=SeedPlan(3, "development", 2),
        adapter=MakerAdapter(),
        base_configuration=maker_configuration(),
        parameter=("market", "latent_sigma_ticks"),
        values=(1, 2, 4),
    )
    assert not spec.paired


@pytest.mark.parametrize(
    "path,values",
    [
        (("missing",), (1, 2)),
        (("strategy", "bad"), (1, 2)),
        ((), (1, 2)),
        (("strategy", "inventory_skew_ticks"), (1, 1)),
        (("strategy", "inventory_skew_ticks"), ()),
    ],
)
def test_invalid_sweeps(path, values):
    with pytest.raises(ValueError):
        sweep_spec(
            question="q",
            hypothesis="h",
            seeds=SeedPlan(3, "development", 2),
            adapter=MakerAdapter(),
            base_configuration=maker_configuration(),
            parameter=path,
            values=values,
        )


@pytest.mark.parametrize("metric", [True, float("nan"), float("inf"), "1"])
def test_outcomes_cannot_hide_nonfinite_or_invalid_metrics(metric):
    with pytest.raises(ValueError):
        SimulationOutcome({"metric": metric}, digest("env"), digest("history"))


def test_control_is_asset_independent_adapter():
    a = GaussianControl()
    c = {"variant_id": "a", "mean": 0, "sd": 1}
    x = a.run(10, c)
    assert x == a.run(10, c)
    y = a.run(10, {**c, "variant_id": "b"})
    assert x.environment_fingerprint == y.environment_fingerprint
    assert x.metrics != y.metrics
