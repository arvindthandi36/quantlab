from dataclasses import asdict

import pytest

from quantlab.options.models import PricingInputs
from quantlab.options.monte_carlo import monte_carlo_price
from quantlab.options.research import OptionsAdapter
from quantlab.options.session import OptionsConfig
from quantlab.research.engine import execute, load_experiment
from quantlab.research.models import ExperimentSpec, Variant
from quantlab.research.seeds import SeedPlan


def config(frequency=1, vol=0.2):
    return {
        "market": asdict(
            OptionsConfig(
                strikes=(100,),
                expiries_days=(5,),
                steps=5,
                process_volatility=vol,
                skew=0,
                curvature=0,
            )
        ),
        "option_type": "call",
        "strike": 100,
        "expiry_days": 5,
        "quantity": 1,
        "hedge_frequency": frequency,
    }


@pytest.mark.parametrize("kind", ["call", "put"])
def test_deterministic_risk_neutral_monte_carlo_matches_analytic_statistically(kind):
    x = PricingInputs(100, 100, 1, 0.2, 0.05, 0.02)
    a = monte_carlo_price(kind, x, paths=200_000, seed=42)
    b = monte_carlo_price(kind, x, paths=200_000, seed=42)
    assert a == b
    assert abs(a["error"]) < 4 * a["standard_error"]
    assert a["confidence_interval"]["method"] == "Student t mean"


def test_more_mc_paths_reduce_standard_error_not_individual_dispersion():
    x = PricingInputs(100, 100, 1, 0.2, 0.05)
    a = monte_carlo_price("call", x, paths=10_000, seed=91)
    b = monte_carlo_price("call", x, paths=160_000, seed=91)
    assert b["standard_error"] == pytest.approx(a["standard_error"] / 4, rel=0.04)


def test_zero_vol_and_expiry_mc_are_deterministic_payoffs():
    for t in (0, 1):
        result = monte_carlo_price(
            "call", PricingInputs(110, 100, t, 0, 0.03), paths=1000, seed=0
        )
        assert result["estimate"] == pytest.approx(result["analytic"], abs=1e-12)
        assert result["standard_error"] < 1e-12


def test_common_innovations_and_distinct_hedge_consequences():
    a = OptionsAdapter()
    first = a.run(42, config(1), full=True)
    sparse = a.run(42, config(5), full=True)
    volatile = a.run(42, config(1, 0.3))
    assert (
        first.environment_fingerprint
        == sparse.environment_fingerprint
        == volatile.environment_fingerprint
    )
    assert first.trajectory_fingerprint != sparse.trajectory_fingerprint
    assert first.metrics["turnover"] != sparse.metrics["turnover"]
    assert a.run(42, config(1)).metrics == first.metrics


def test_actual_phase5_engine_runs_derivatives_paired_experiment(tmp_path):
    adapter = OptionsAdapter()
    spec = ExperimentSpec(
        "Does hedge frequency alter costs and residual exposure?",
        "More frequent hedging is expected to reduce interval delta exposure but add costs.",
        SeedPlan(root=88042, pool="development", runs=8),
        (Variant("daily", config(1)), Variant("five", config(5))),
        adapter.name,
        bootstrap_resamples=50,
    )
    result = execute(spec, adapter, tmp_path / "study")
    assert result["status"] == "complete", result["warnings"]
    assert len(result["runs"]) == 16
    assert load_experiment(tmp_path / "study") == result
    assert result["metric_units"]["daily"]["net_pnl"] == "GBP"
    assert result["analysis"]["paired"]
