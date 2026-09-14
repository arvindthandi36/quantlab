"""Cross-cutting unit, precision, source-of-truth and resource-boundary regressions."""

import json
from dataclasses import replace
from fractions import Fraction

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from quantlab.execution import vwap
from quantlab.jsonio import loads
from quantlab.options.iv import implied_volatility
from quantlab.options.models import PricingInputs
from quantlab.options.pricing import bounds, greeks, parity_residual, price, price_many
from quantlab.risk.covariance import validate_covariance, variance_decomposition
from quantlab.risk.metrics import empirical_risk
from quantlab.risk.optimisation import optimise
from quantlab.risk.portfolio import Position
from quantlab.statarb.session import StatArbSession
from quantlab.statarb.statistics import CausalModel, ols, zscore


def test_one_vwap_authority_retains_exact_unit_and_empty_state():
    assert vwap([(10002, 3), (10005, 2)]) == Fraction(50016, 5)
    assert vwap([("100.02", 3), ("100.05", 2)]) == Fraction(50016, 500)
    assert vwap([]) is None
    with pytest.raises(ValueError):
        vwap([(100, 0)])


@pytest.mark.parametrize(
    "raw",
    [
        '{"a":1,"a":2}',
        '{"x":{"a":1,"a":2}}',
        "[NaN]",
        "[Infinity]",
        pytest.param("[" * 2000 + "]" * 2000, id="deep-nesting"),
    ],
)
def test_ambiguous_nonfinite_or_over_nested_upload_rejected(raw):
    with pytest.raises(ValueError):
        loads(raw)


def test_stock_contract_multiplier_ambiguity_rejected():
    with pytest.raises(ValueError, match="multiplier"):
        Position("S", "S", 3, 100, 100, 100)


def test_exhausted_action_budget_cannot_grow_and_still_allows_end():
    s = StatArbSession()
    s.actions = [{}] * 4000
    for _ in range(3):
        with pytest.raises(ValueError, match="end and export"):
            s.command("wait")
    assert len(s.actions) == 4000
    assert s.command("end")["ok"] and s.status == "ended"


@pytest.mark.parametrize(
    "t,sigma,rate,strike",
    [
        (1e-12, 0.2, 0, 100),
        (1e-6, 5, 1, 1e8),
        (50, 5, -1, 1e-8),
        (1, 0.000001, -1, 100),
        (50, 0.2, 1, 100),
        (0, 0.2, 0, 100),
        (1, 0, 0.05, 100),
    ],
)
def test_extreme_pricing_uses_same_kernel_parity_and_bounds(t, sigma, rate, strike):
    x = PricingInputs(100, strike, t, sigma, rate)
    values = {kind: price(kind, x) for kind in ["call", "put"]}
    assert parity_residual(values["call"], values["put"], x) == pytest.approx(
        0, abs=1e-12 * max(*values.values(), 100)
    )
    for kind in values:
        lo, hi = bounds(kind, x)
        assert lo <= values[kind] <= hi * (1 + 1e-12)
        assert price_many(kind, x, np.array([100.0]))[0] == pytest.approx(
            values[kind], rel=1e-12
        )


def test_subnormal_time_volatility_rejected_without_plausible_price():
    x = PricingInputs(100, 100, 1e-320, 1e-320)
    for f in (price, greeks):
        with pytest.raises(ValueError, match="precision"):
            f("call", x)


@pytest.mark.parametrize("scenario", ["impossible", "low_vega", "no_bracket", "iterations"])
def test_iv_failure_returns_no_invented_volatility(scenario):
    x = PricingInputs(100, 100, 1, 0.2)
    if scenario == "impossible":
        with pytest.raises(ValueError, match="feasibility"):
            implied_volatility("call", x, 100)
        return
    if scenario == "low_vega":
        x = replace(x, strike=1e8, time_years=1e-6)
        r = implied_volatility("call", x, 0)
    elif scenario == "no_bracket":
        r = implied_volatility("call", x, 99.99)
    else:
        r = implied_volatility(
            "call",
            x,
            price("call", replace(x, volatility=0.35)),
            max_iterations=1,
            newton_iterations=0,
        )
    assert not r.converged and r.volatility is None


@pytest.mark.parametrize(
    "function",
    [
        lambda: variance_decomposition([1e200], [[1.0]]),
        lambda: ols([1, 2, 3, 4], [1e200, 2e200, 3e200, 4e200]),
        lambda: zscore(1e308, [1e308] * 3, window=3),
    ],
)
def test_overflow_never_escapes_as_infinite_or_finite_summary(function):
    with pytest.raises(ValueError, match="no estimate"):
        function()


def test_large_finite_covariance_average_does_not_overflow():
    c, metadata = validate_covariance([[1e308, 0], [0, 1e308]])
    assert np.isfinite(c).all() and np.isfinite(metadata["eigenvalues"]).all()


@given(
    st.lists(st.integers(-20, 20), min_size=4, max_size=4),
    st.lists(st.integers(-100, 100), min_size=2, max_size=2),
)
@settings(max_examples=40, derandomize=True)
def test_psd_quadratic_identity_including_singular_directions(entries, weights):
    a = np.array(entries, dtype=float).reshape(2, 2) / 100
    covariance = a.T @ a
    result = variance_decomposition(weights, covariance)
    expected = float(np.sum((a @ weights) ** 2))
    assert result["variance"] == pytest.approx(expected, abs=1e-8)
    assert result["variance"] >= 0


@pytest.mark.parametrize("alpha", [0.51, 0.95, 0.999])
def test_sparse_loss_tail_es_is_at_least_var_including_profitable_paths(alpha):
    r = empirical_risk([-10, -8, -2, 20], alpha)
    assert r["es"] >= r["var"]


def test_singular_optimizer_boundary_and_infeasibility():
    r = optimise([[0.01, 0.01], [0.01, 0.01]], [0.001, 0.001], max_cash=0, max_weight=0.5)
    assert r["weights"] == pytest.approx([0.5, 0.5, 0])
    with pytest.raises(ValueError, match="infeasible"):
        optimise([[0.01, 0.01], [0.01, 0.01]], [0.001, 0.001], max_cash=0, max_weight=0.4)


@pytest.mark.parametrize("mode", ["fixed", "rolling", "walk_forward"])
def test_future_poisoned_values_do_not_even_enter_validation(mode):
    rng = np.random.default_rng(111042)
    x = 100 + np.cumsum(rng.normal(0, 0.1, 150))
    y = 2 + 1.02 * x + rng.normal(0, 0.05, 150)
    a = np.column_stack((x, y))
    changed = a.copy()
    changed[101:] = np.nan
    args = dict(window=40, z_window=20, mode=mode)
    first = CausalModel(**args).at(a, 100)
    second = CausalModel(**args).at(changed, 100)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_visual_replay_budget_rejects_before_retaining_extra_frame():
    from quantlab.replay_support import ReplayFrames

    frames = ReplayFrames(byte_limit=20)
    frames.append({"x": 1})
    with pytest.raises(ValueError, match="No frames were truncated"):
        frames.append({"x": "a" * 30})
    assert frames == [{"x": 1}]


def test_failed_risk_covariance_proposal_preserves_usable_current_settings():
    from quantlab.risk.analytics import RiskSettings
    from quantlab.risk.session import RiskSession

    session = RiskSession(settings=RiskSettings(paths=100, sample_size=20))
    before = session.state()
    with pytest.raises(ValueError):
        session.execute("risk", "covariance", matrix=[[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    assert session.covariance is None
    assert session.state()["report"] == before["report"]


def test_research_summary_overflow_is_not_a_confidence_interval():
    from quantlab.research.statistics import summarise

    with pytest.raises(ValueError, match="no estimate"):
        summarise([1e308, -1e308, 1e308])
