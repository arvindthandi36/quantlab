import math

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from quantlab.statarb.process import Asset, Link, Process, scenario
from quantlab.statarb.statistics import CausalModel, correlation, diagnostics, ols, zscore
from quantlab.statarb.strategy import Rules, decision, sizes


@pytest.mark.parametrize("alpha,beta", [(0, 1), (2, 3), (-5, 0.5), (100, -2), (1e5, 1e-3)])
def test_exact_ols(alpha, beta):
    x = np.arange(20.0)
    f = ols(x, alpha + beta * x)
    assert f.alpha == pytest.approx(alpha, abs=1e-8)
    assert f.beta == pytest.approx(beta, abs=1e-9)
    assert f.r_squared == pytest.approx(1)
    assert np.max(abs(f.residual(x, alpha + beta * x))) < 1e-7


@pytest.mark.parametrize(
    "x",
    [
        [1] * 6,
        [1 + 1e-12 * i for i in range(6)],
        [float("nan"), 1, 2],
        [1, 2],
        [1, float("inf"), 3],
    ],
)
def test_unidentified_regression_fails(x):
    with pytest.raises(ValueError):
        ols(x, np.arange(len(x)))


def test_ols_matches_scipy_standard_errors():
    from scipy.stats import linregress

    x = np.linspace(-3, 4, 60)
    y = 2 + 1.2 * x + np.random.default_rng(12).normal(0, 0.3, 60)
    a, b = ols(x, y), linregress(x, y)
    assert a.beta == pytest.approx(b.slope)
    assert a.alpha == pytest.approx(b.intercept)
    assert a.beta_se == pytest.approx(b.stderr)
    assert a.alpha_se == pytest.approx(b.intercept_stderr)


def test_constant_response_undefined_r_squared():
    assert ols(range(10), [5] * 10).r_squared is None


def test_outlier_warning_and_sensitivity():
    x = np.arange(100.0)
    y = x.copy()
    y[50] += 1000
    f = ols(x, y)
    assert any("outlier" in w for w in f.warnings)
    assert f.r_squared < 0.6


@pytest.mark.parametrize(
    "current,past,window,expected",
    [(3, [0, 1, 2], 3, 2), (0, [0, 1, 2], 3, -1), (3, [0, 1], 3, None), (5, [5] * 8, 6, None)],
)
def test_zscore_examples(current, past, window, expected):
    assert (
        zscore(current, past, window=window)["z"] == pytest.approx(expected)
        if expected is not None
        else zscore(current, past, window=window)["z"] is None
    )


@pytest.mark.parametrize("bad", [None, float("nan"), float("inf")])
def test_missing_z_rejected(bad):
    with pytest.raises(ValueError):
        zscore(1, [0, 1, bad], window=3)


def test_z_uses_only_selected_window():
    assert zscore(4, [float("nan"), 1, 2, 3], window=3)["z"] == 2


@pytest.mark.parametrize("mode", ["fixed", "rolling", "walk_forward"])
@pytest.mark.parametrize("t", [80, 99, 120])
def test_adversarial_future_changes_cannot_change_fit_mean_sd_z(mode, t):
    p = scenario(seed=912)
    data = [p.prices.tolist()] + [p.step() for _ in range(150)]
    changed = np.array(data)
    changed[t + 1 :] = np.random.default_rng(3).normal(500, 200, changed[t + 1 :].shape)
    a = CausalModel(mode=mode).at(data, t)
    b = CausalModel(mode=mode).at(changed, t)
    assert a == b
    assert a["fit"]["end"] <= t
    assert a["normalization_end"] == t


def test_current_row_excluded_from_fit_and_normalization():
    p = scenario(seed=44)
    data = np.array([p.prices.tolist()] + [p.step() for _ in range(100)])
    a = CausalModel(mode="rolling").at(data, 90)
    data[90, 1] += 8
    b = CausalModel(mode="rolling").at(data, 90)
    assert a["fit"] == b["fit"] and a["mean"] == b["mean"] and a["sd"] == b["sd"]
    assert b["spread"] - a["spread"] == pytest.approx(8)


def test_future_vintage_rejected():
    f = ols(range(10), range(10), end=100)
    with pytest.raises(ValueError, match="Future"):
        CausalModel().with_fit(np.ones((90, 2)), 80, f)


@pytest.mark.parametrize("phi", [0.2, 0.8, 0.97, 1.0])
def test_ar_diagnostics_interpretation(phi):
    z = np.random.default_rng(35).normal(size=10000)
    a = np.zeros(len(z))
    for i in range(1, len(a)):
        a[i] = phi * a[i - 1] + z[i]
    d = diagnostics(a)
    assert abs(d["phi"] - phi) < 0.04
    assert "not ADF" in d["label"]
    if phi < 1:
        assert d["half_life"] == pytest.approx(-math.log(2) / math.log(d["phi"]))


def test_constant_ar_has_no_half_life():
    assert diagnostics([4] * 30)["half_life"] is None


def test_explosive_ar_has_no_half_life():
    assert diagnostics(1.1 ** np.arange(50))["half_life"] is None


@pytest.mark.parametrize("rho", [-0.9, 0, 0.9])
def test_multivariate_shocks_match_covariance(rho):
    p = Process(
        seed=993, correlation=rho, assets=[Asset("a", initial=1000), Asset("b", initial=1000)]
    )
    rows = np.array([p.step() for _ in range(7000)])
    changes = np.diff(rows, axis=0)
    assert correlation(*changes.T) == pytest.approx(rho, abs=0.04)
    assert np.std(changes[:, 0]) == pytest.approx(0.25, abs=0.015)


def test_three_asset_factor_identity():
    p = Process(
        seed=123,
        common_factor=True,
        assets=[Asset("a", loading=1), Asset("b", loading=-1), Asset("c", loading=2)],
    )
    before = p.prices.copy()
    p.step()
    e = p.evidence[-1]
    for i, a in enumerate(p.assets):
        assert p.prices[i] / before[i] - 1 == pytest.approx(
            a.loading * e["common_factor_return"]
            + a.volatility / a.initial * e["innovations"][i]
        )


@pytest.mark.parametrize(
    "name",
    [
        "independent",
        "positive",
        "negative",
        "common_factor",
        "noncointegrated",
        "stable",
        "beta",
        "mean",
        "volatility",
        "decouple",
        "drift",
    ],
)
def test_deterministic_processes_and_private_breaks(name):
    p, q = scenario(name, seed=928, steps=200), scenario(name, seed=928, steps=200)
    assert [p.step() for _ in range(150)] == [q.step() for _ in range(150)]
    assert p.evidence == q.evidence


def test_cointegration_by_construction_and_unit_root_variance_growth():
    # Across independent repetitions, stable residual variance saturates; unit-root grows.
    terminal = {}
    for phi in (0.9, 1):
        values = []
        for seed in range(120):
            p = Process(seed=seed, links=[Link(phi=phi)])
            for _ in range(150):
                p.step()
            values.append(p.spreads[1])
        terminal[phi] = np.var(values)
    assert terminal[1] > 10 * terminal[0.9]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"correlation": 1.1},
        {"assets": [Asset("x"), Asset("x")]},
        {"links": [Link(x=0, y=3)]},
        {"seed": True},
        {"seed": -1},
    ],
)
def test_invalid_process_parameters(kwargs):
    with pytest.raises(ValueError):
        Process(**kwargs)


def test_generic_multiple_links():
    p = Process(
        assets=[Asset("a"), Asset("b"), Asset("c")],
        links=[Link(), Link(x=1, y=2, alpha=10, beta=0.5)],
    )
    p.step()
    assert p.prices[2] == pytest.approx(10 + 0.5 * p.prices[1] + p.spreads[2])


@pytest.mark.parametrize("sizing", ["hedge_ratio", "fixed_notional", "volatility_scaled"])
def test_sizing_has_correct_units(sizing):
    qx, qy = sizes(Rules(notional=2000, sizing=sizing), [50, 100], 2, 0.3)
    assert qx < 0 < qy
    if sizing != "fixed_notional":
        assert qx == -2 * qy
    else:
        assert abs(qx) * 50 == qy * 100


@pytest.mark.parametrize(
    "z,held,want",
    [
        (2.1, False, "short"),
        (-2.1, False, "long"),
        (0.1, False, "wait"),
        (0.1, True, "close"),
        (4.2, True, "close"),
        (4.2, False, "wait"),
        (1, True, "wait"),
    ],
)
def test_strategy_entry_exit_signs(z, held, want):
    assert decision(Rules(), dict(available=True, z=z), held=held)[0] == want


@pytest.mark.parametrize(
    "kw", [{"age": 41}, {"pnl": -51}, {"gross": 10001}, {"imbalance": 2001}]
)
def test_safeguards_do_not_need_available_signal(kw):
    assert decision(Rules(), dict(available=False), held=True, **kw)[0] == "close"


@pytest.mark.parametrize(
    "kw",
    [
        {"exit": 2},
        {"entry": 4},
        {"stop": 1},
        {"window": 2},
        {"z_window": False},
        {"mode": "future"},
        {"sizing": "kelly"},
        {"notional": 1e6},
        {"max_loss": float("nan")},
    ],
)
def test_invalid_rules_fail(kw):
    with pytest.raises(ValueError):
        Rules(**kw)


@settings(max_examples=30)
@given(
    st.floats(-100, 100, allow_nan=False, allow_infinity=False),
    st.floats(0.1, 4, allow_nan=False, allow_infinity=False),
)
def test_generated_ols_residual_orthogonality(alpha, beta):
    x = np.arange(1.0, 31.0)
    y = alpha + beta * x + np.sin(x)
    f = ols(x, y)
    e = f.residual(x, y)
    assert abs(sum(e)) < 1e-8 and abs(e @ x) < 1e-7


@pytest.mark.parametrize("rho", [-2, 2])
def test_zero_volatility_cannot_mask_invalid_correlation(rho):
    with pytest.raises(ValueError, match="correlation"):
        Process(assets=[Asset("x", volatility=0), Asset("y", volatility=0)], correlation=rho)
