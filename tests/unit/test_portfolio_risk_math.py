"""Small solvable portfolios, invariances and independently checked tail conventions."""

import math
from dataclasses import replace

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from quantlab.options.pricing import price
from quantlab.risk.analytics import diversification, tail_example
from quantlab.risk.covariance import (
    correlation,
    estimate_covariance,
    validate_covariance,
    variance_decomposition,
)
from quantlab.risk.metrics import empirical_risk, parametric_risk
from quantlab.risk.monte_carlo import (
    factor_matrix,
    historical_risk,
    joint_returns,
    monte_carlo_risk,
    revalue_returns,
    vector_option_prices,
)
from quantlab.risk.optimisation import optimise
from quantlab.risk.portfolio import Portfolio, Position
from quantlab.risk.scenarios import NAMED, Scenario, scenario_pnl


@pytest.mark.parametrize("ddof", [0, 1])
def test_exact_covariance(ddof):
    r = estimate_covariance([[1, 2], [2, 4], [3, 6]], ddof=ddof)
    assert np.allclose(r["covariance"], np.array([[2, 4], [4, 8]]) / (3 - ddof))
    assert r["mean"] == [2, 4]
    assert correlation(r["covariance"]) == [[1, 1], [1, 1]]


@pytest.mark.parametrize(
    "bad",
    [
        [[1, 2], [0, 1]],
        [[1, 2], [2, 1]],
        [[-1]],
        [[float("nan")]],
        [[1, 2]],
        [],
        [[0, 1], [1, 1]],
    ],
)
def test_invalid_covariance_fails(bad):
    with pytest.raises(ValueError):
        validate_covariance(bad)


def test_near_singular_diagnostic_and_no_regularisation():
    _, info = validate_covariance([[1, 1 - 1e-12], [1 - 1e-12, 1]])
    assert info["warnings"] and info["regularisation"] == "none"


def test_zero_variance_correlation_undefined():
    assert correlation([[0, 0], [0, 1]]) == [[None, None], [None, 1.0]]


def test_missing_policy_explicit():
    rows = [[1, 2], [None, 4], [3, 6]]
    with pytest.raises(ValueError):
        estimate_covariance(rows)
    r = estimate_covariance(rows, missing="listwise")
    assert r["dropped"] == 1 and r["n"] == 2
    assert r["covariance"] == [[2, 4], [4, 8]]


@pytest.mark.parametrize("rows", [[], [[1, 2]], [[None, 1], [2, None]]])
def test_insufficient_covariance(rows):
    with pytest.raises(ValueError):
        estimate_covariance(rows, missing="listwise")


@pytest.mark.parametrize("rho", [-1, -0.5, 0, 0.5, 1])
def test_two_asset_variance_decomposition(rho):
    c = [[0.01, 0.01 * rho], [0.01 * rho, 0.01]]
    d = variance_decomposition([0.5, 0.5], c)
    assert d["variance"] == pytest.approx(0.005 * (1 + rho))
    assert d["diagonal_total"] + d["cross_total"] == pytest.approx(d["variance"])
    if rho > -1:
        assert sum(d["component_volatility"]) == pytest.approx(d["volatility"])
    else:
        assert d["component_volatility"] is None


@given(
    st.lists(st.floats(-10, 10, allow_nan=False, allow_infinity=False), min_size=4, max_size=4),
    st.lists(st.floats(-5, 5, allow_nan=False, allow_infinity=False), min_size=2, max_size=2),
)
@settings(max_examples=60)
def test_psd_portfolio_variance_nonnegative(matrix, weights):
    a = np.array(matrix).reshape(2, 2)
    c = a @ a.T
    d = variance_decomposition(weights, c)
    assert d["variance"] >= 0
    assert d["variance"] == pytest.approx(float(np.linalg.norm(a.T @ weights) ** 2), abs=1e-9)


@pytest.mark.parametrize("alpha", [0.5, 0.8, 0.95, 0.99, 0.999])
def test_empirical_tail_against_integrated_quantile(alpha):
    losses = np.array([-5, 0, 1, 2, 2, 4, 7, 20, 20, 100])
    result = empirical_risk(losses, alpha)
    assert result["var"] == losses[math.ceil(alpha * len(losses)) - 1]
    # Independent finite probability-bin integration of inverse CDF.
    es = sum(
        max(0, (i + 1) / len(losses) - max(alpha, i / len(losses))) * loss
        for i, loss in enumerate(losses)
    ) / (1 - alpha)
    assert result["es"] == pytest.approx(es)
    assert result["es"] >= result["var"]


@given(
    st.lists(
        st.floats(-1e4, 1e4, allow_nan=False, allow_infinity=False), min_size=2, max_size=100
    )
)
@settings(max_examples=70)
def test_es_never_better_than_var(losses):
    r = empirical_risk(losses, 0.95)
    assert r["es"] >= r["var"] - 1e-8


def test_same_var_different_es():
    r = tail_example()
    assert r["mild"]["var"] == r["severe"]["var"] == 10
    assert r["mild"]["es"] == pytest.approx(12)
    assert r["severe"]["es"] == pytest.approx(48)


@pytest.mark.parametrize("scale", [-2, 0, 1, 3])
def test_parametric_linear_normal_analytic(scale):
    r = parametric_risk([1000 * scale], [[0.0001]], [0.001], alpha=0.95, days=4)
    assert r["mean_loss"] == pytest.approx(-4 * scale)
    assert r["loss_sd"] == pytest.approx(abs(scale) * 20)
    assert r["var"] == pytest.approx(-4 * scale + 1.6448536269514722 * abs(scale) * 20)
    assert r["es"] >= r["var"]


def test_gain_threshold_not_clamped():
    r = empirical_risk([-5, -4, -3])
    assert r["var"] < 0 and r["es"] < 0
    r = parametric_risk([100], [[0]], [0.01])
    assert r["var"] == r["es"] == -1


@pytest.mark.parametrize("cov", [[[1, 0.4], [0.4, 2]], [[1, 1], [1, 1]], [[0, 0], [0, 0]]])
def test_matrix_factor_reconstructs(cov):
    f, info = factor_matrix(cov)
    assert np.allclose(f @ f.T, cov)
    assert info["factor_method"]


@pytest.mark.parametrize("distribution", ["normal", "student"])
def test_correlated_draws_statistics(distribution):
    c = np.array([[0.0001, 0.00005], [0.00005, 0.0004]])
    r, _ = joint_returns(c, [0.0002, -0.0001], paths=100000, seed=19, distribution=distribution)
    assert np.allclose(np.cov(r, rowvar=False), c, atol=1e-5)
    assert np.allclose(r.mean(axis=0), [0.0002, -0.0001], atol=0.0002)


def test_correlated_draws_replay_prefix_and_seed_separation():
    a, _ = joint_returns([[0.0001]], [0], paths=250, seed=99, days=3)
    b, _ = joint_returns([[0.0001]], [0], paths=1000, seed=99, days=3)
    assert np.array_equal(a, b[:250])
    assert not np.array_equal(a, joint_returns([[0.0001]], [0], paths=250, seed=100, days=3)[0])


@pytest.mark.parametrize("kind", ["call", "put"])
@pytest.mark.parametrize("years", [0, 0.001, 0.1, 2])
@pytest.mark.parametrize("sigma", [0, 0.2, 1.5])
def test_vector_repricing_matches_scalar_bsm(kind, years, sigma):
    p = Position("option", "S", -2, 100, 10, 100, kind, 100, years, sigma, 0.03)
    spots = np.array([1, 30, 90, 100, 110, 200, 1000])
    v = vector_option_prices(p, spots, years)
    expected = [price(kind, replace(p.inputs(), spot=float(s))) for s in spots]
    assert v == pytest.approx(expected, abs=1e-10)


def test_stock_historical_losses_and_sign():
    p = Portfolio((Position("S", "S", 10, 1, 100, 100),), -1000)
    r = historical_risk(
        p, ["S"], [[-0.10], [0.02], [0.05], [-0.02]], alpha=0.75, days=1, full=True
    )
    assert r["full"]["losses"] == pytest.approx([100, -20, -50, 20])
    assert r["full"]["var"] == pytest.approx(20)
    assert r["full"]["es"] == pytest.approx(100)


def test_historical_blocks_compound_not_sqrt_scaling():
    p = Portfolio((Position("S", "S", 1, 1, 100, 100),), 0)
    r = historical_risk(p, ["S"], [[0.1], [0.1], [-0.1], [-0.1], [0.5]], days=2, full=True)
    assert r["full"]["losses"] == pytest.approx([-21, 19])
    assert r["unused_rows"] == 1


def test_mc_linear_portfolio_normal_benchmark():
    p = Portfolio((Position("S", "S", 100, 1, 100, 100),), -10000)
    r = monte_carlo_risk(p, ["S"], [[0.0001]], [0], paths=100000, seed=80)
    assert r["full"]["var"] == pytest.approx(164.48536, abs=2)
    assert r["full"] == r["delta"]


def test_option_horizon_rejects_unobservable_settlement():
    p = Portfolio((Position("C", "S", 1, 100, 2, 100, "call", 100, 1 / 365, 0.2),), 0)
    with pytest.raises(ValueError, match="expiry"):
        revalue_returns(p, ["S"], [[0]], days=2)


@pytest.mark.parametrize("name", list(NAMED))
def test_named_scenarios_have_no_account_mutation(name):
    p = Portfolio((Position("S", "S", 20, 1, 100, 100),), -1000)
    before = p.public()
    r = scenario_pnl(p, NAMED[name])
    assert p.public() == before
    assert r["loss"] == -r["full_pnl"]
    assert r["full_pnl"] == pytest.approx(r["approximate_pnl"] + r["residual"])


def test_delta_neutral_vega_and_taylor_error():
    c = Position("C", "S", 1, 100, 2, 100, "call", 100, 30 / 365, 0.2)
    h = Position("S", "S", round(-c.sensitivities()["delta"]), 1, 100, 100)
    p = Portfolio((c, h), 0)
    assert abs(p.public()["greeks"]["delta"]) < 0.5
    r = scenario_pnl(p, Scenario(volatility_change=0.2))
    assert r["full_pnl"] > 200 and r["contributions"]["vega"] > 200
    zero = scenario_pnl(p, Scenario())
    assert zero["full_pnl"] == 0
    small = scenario_pnl(p, Scenario(stock_return=0.001))
    large = scenario_pnl(p, Scenario(stock_return=0.2))
    assert abs(large["residual"]) > abs(small["residual"])


def test_exposure_concentration_and_greek_units():
    p = Portfolio(
        (Position("A", "A", 10, 1, 100, 100), Position("B", "B", -5, 1, 100, 100)), 500
    )
    r = p.public()
    assert (r["gross"], r["net"], r["long"], r["short"], r["equity"]) == (
        1500,
        500,
        1000,
        500,
        1000,
    )
    assert r["largest_position_share"] == pytest.approx(2 / 3)
    assert r["hhi"] == pytest.approx(5 / 9)
    assert r["gross_delta_gbp"] == 1500


def test_diversification_identical_no_false_gain():
    d = diversification()["rows"]
    assert d[0]["volatility_gbp"] == d[-1]["volatility_gbp"]
    assert d[3]["volatility_gbp"] < d[1]["volatility_gbp"] < d[2]["volatility_gbp"]


def test_minimum_variance_analytic_inverse_variance_weights():
    r = optimise([[0.01, 0], [0, 0.04]], [0.001, 0.001], max_cash=0)
    assert r["success"] and r["weights"] == pytest.approx([0.8, 0.2, 0], abs=1e-6)
    assert r["variance"] == pytest.approx(0.008)


@pytest.mark.parametrize("long_only", [True, False])
@pytest.mark.parametrize("cash", [0, 0.2, 0.5])
def test_optimisation_constraints(long_only, cash):
    r = optimise(
        np.diag([0.01, 0.02, 0.03]),
        [0.001, 0.002, 0.003],
        long_only=long_only,
        min_cash=cash,
        max_cash=cash,
        max_weight=0.4,
        risk_aversion=10,
    )
    assert sum(r["weights"]) == pytest.approx(1)
    assert r["weights"][-1] == pytest.approx(cash)
    assert max(r["weights"][:-1]) <= 0.4 + 1e-8
    assert r["bound_violation"] < 1e-8


def test_cash_only_is_legitimate_minimum():
    r = optimise([[0.01]], [0.002])
    assert r["cash_weight"] == pytest.approx(1)
    assert r["variance"] == pytest.approx(0, abs=1e-12)


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(max_weight=0.4, max_cash=0),
        dict(min_cash=0.5, max_cash=0.1),
        dict(target_return=100),
        dict(long_only="yes"),
    ],
)
def test_infeasible_or_invalid_optimisation(kwargs):
    with pytest.raises(ValueError):
        optimise([[0.01, 0.0], [0, 0.02]], [0.001, 0.001], **kwargs)
