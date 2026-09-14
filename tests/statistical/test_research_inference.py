import numpy as np

from quantlab.research.adapters.control import GaussianControl
from quantlab.research.seeds import SeedPlan
from quantlab.research.statistics import bootstrap, mean_interval, summarise


def test_gaussian_adapter_mean_variance_and_common_weather_correlation():
    adapter = GaussianControl()
    seeds = SeedPlan(909, "development", 4000).seeds()
    a = [
        adapter.run(seed, {"variant_id": "a", "mean": 0, "sd": 1}).metrics["net_pnl"]
        for seed in seeds
    ]
    b = [
        adapter.run(seed, {"variant_id": "b", "mean": 0, "sd": 1}).metrics["net_pnl"]
        for seed in seeds
    ]
    assert abs(np.mean(a)) < 0.06 and abs(np.mean(b)) < 0.06
    assert 0.9 < np.var(a, ddof=1) < 1.1
    assert 0.18 < np.corrcoef(a, b)[0, 1] < 0.32


def test_mean_t_interval_empirical_coverage():
    rng = np.random.default_rng(291)
    covered = 0
    for _ in range(400):
        ci = mean_interval(rng.normal(2, 3, 50))
        covered += ci.low <= 2 <= ci.high
    assert 0.90 < covered / 400 < 0.99


def test_bootstrap_uncertainty_tracks_analytic_se():
    rng = np.random.default_rng(192)
    values = rng.exponential(1, 600)
    result = bootstrap(values, seed=21, resamples=1500)
    expected = summarise(values).standard_error
    assert 0.85 < result.standard_error / expected < 1.15


def test_standard_error_square_root_scaling_without_shrinking_outcome_sd():
    rng = np.random.default_rng(918)
    values = rng.normal(0, 2, 1600)
    s = [summarise(values[:n]) for n in (100, 400, 1600)]
    assert 0.35 < s[1].standard_error / s[0].standard_error < 0.65
    assert 0.17 < s[2].standard_error / s[0].standard_error < 0.33
    assert all(1.6 < x.standard_deviation < 2.4 for x in s)


def test_selection_optimism_over_repeated_equal_skill_controls():
    rng = np.random.default_rng(377)
    differences = []
    for _ in range(150):
        development = rng.normal(0, 1, (50, 40)).mean(axis=1)
        winner = int(np.argmax(development))
        untouched = rng.normal(0, 1, (50, 200)).mean(axis=1)
        differences.append(development[winner] - untouched[winner])
    assert np.mean(differences) > 0.25
    assert np.mean(np.array(differences) > 0) > 0.85
