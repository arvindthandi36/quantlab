import math
from dataclasses import replace
from fractions import Fraction

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from quantlab.options.analytics import shock
from quantlab.options.iv import implied_volatility
from quantlab.options.models import OptionContract, PricingInputs, years_from_days
from quantlab.options.pricing import (
    bounds,
    finite_differences,
    greeks,
    parity_residual,
    payoff,
    price,
)


@pytest.mark.parametrize(
    "kind,s,k,q,r,t,v,value",
    [
        ("call", 60, 65, 0, 0.08, 0.25, 0.30, 2.1334),
        ("put", 100, 95, 0.05, 0.10, 0.50, 0.20, 2.4648),
        ("put", 19, 19, 0.10, 0.10, 0.75, 0.28, 1.7011),
        ("call", 19, 19, 0.10, 0.10, 0.75, 0.28, 1.7011),
        ("call", 1.56, 1.60, 0.08, 0.06, 0.5, 0.12, 0.0291),
        ("put", 75, 70, 0.05, 0.10, 0.5, 0.35, 4.0870),
    ],
)
def test_published_quantlib_haug_benchmarks(kind, s, k, q, r, t, v, value):
    # https://github.com/lballabio/QuantLib/blob/master/test-suite/europeanoption.cpp
    # Numerical facts only. Input t is already a year fraction, not calendar days.
    assert price(kind, PricingInputs(s, k, t, v, r, q)) == pytest.approx(value, abs=1e-4)


@pytest.mark.parametrize(
    "kind,expected", [("call", 10.450583572185565), ("put", 5.573526022256971)]
)
def test_reproducible_atm_benchmark(kind, expected):
    assert price(kind, PricingInputs(100, 100, 1, 0.2, 0.05)) == pytest.approx(
        expected, abs=1e-12
    )


@pytest.mark.parametrize("kind", ["call", "put"])
@pytest.mark.parametrize(
    "x",
    [
        PricingInputs(100, 100, 1, 0.2, 0.05),
        PricingInputs(80, 100, 0.1, 0.4, -0.02, 0.01),
        PricingInputs(130, 100, 2, 0.6, 0.07, 0.03),
    ],
)
def test_all_analytic_greeks_against_independent_finite_differences(kind, x):
    analytic, numerical = greeks(kind, x), finite_differences(kind, x)
    for name in ("delta", "gamma", "vega", "theta", "rho"):
        assert getattr(analytic, name) == pytest.approx(
            getattr(numerical, name), rel=3e-5, abs=2e-7
        )


@given(
    s=st.floats(5, 500),
    k=st.floats(5, 500),
    t=st.floats(0.0001, 5),
    v=st.floats(0.01, 2),
    r=st.floats(-0.1, 0.2),
    q=st.floats(0, 0.15),
)
@settings(max_examples=150)
def test_parity_bounds_and_monotonicity_properties(s, k, t, v, r, q):
    x = PricingInputs(s, k, t, v, r, q)
    c, p = price("call", x), price("put", x)
    assert abs(parity_residual(c, p, x)) < 1e-10 * max(s, k)
    for kind in ("call", "put"):
        lo, hi = bounds(kind, x)
        value = price(kind, x)
        assert lo - 1e-10 <= value <= hi + 1e-10
        up = price(kind, replace(x, spot=s * 1.001))
        assert up >= value - 1e-10 if kind == "call" else up <= value + 1e-10
        assert price(kind, replace(x, volatility=v + 0.001)) >= value - 1e-10


@pytest.mark.parametrize(
    "kind,spot,expected", [("call", 110, 10), ("call", 90, 0), ("put", 90, 10), ("put", 110, 0)]
)
def test_exact_expiry_and_zero_time_value(kind, spot, expected):
    assert price(kind, PricingInputs(spot, 100, 0, 0.6, 0.07, 0.03)) == expected
    assert payoff(kind, spot, 100) == expected


def test_expiry_kink_is_not_fabricated_gamma():
    g = greeks("call", PricingInputs(100, 100, 0, 0.2))
    assert g.delta is None and g.gamma is None and g.theta is None


@pytest.mark.parametrize("kind", ["call", "put"])
def test_zero_volatility_discounted_bound(kind):
    x = PricingInputs(100, 90, 1, 0, 0.1, 0.03)
    assert price(kind, x) == bounds(kind, x)[0]
    assert greeks(kind, x).gamma == 0


def test_theta_is_calendar_decay_and_can_be_positive_for_a_put():
    x = PricingInputs(50, 100, 1, 0.05, 0.1)
    assert greeks("put", x).theta > 0
    short = replace(x, time_years=1 - 1 / 365)
    assert price("put", short) > price("put", x)
    assert greeks("put", x).public()["theta_per_day"] == greeks("put", x).theta / 365


def test_vega_scales_per_absolute_decimal_and_per_percentage_point():
    x = PricingInputs(100, 100, 1, 0.2, 0.05)
    g = greeks("call", x)
    assert price("call", replace(x, volatility=0.2001)) - price("call", x) == pytest.approx(
        g.vega * 0.0001, rel=1e-4
    )
    assert g.scaled(-5 * 100).vega == -500 * g.vega
    assert g.public()["vega_per_vol_point"] == g.vega / 100


def test_days_years_and_contract_multiplier_are_explicit():
    contract = OptionContract("call", 100, years_from_days(30), 100)
    assert contract.expiry_years == Fraction(6, 73)
    assert contract.remaining(years_from_days(30)) == 0
    assert contract.public()["remaining_days"] == 30


@pytest.mark.parametrize(
    "field,value",
    [
        ("spot", 0),
        ("strike", -1),
        ("volatility", 20),
        ("volatility", -0.1),
        ("time_years", -1),
        ("rate", math.inf),
        ("spot", True),
        ("dividend_yield", float("nan")),
    ],
)
def test_invalid_and_ambiguous_pricing_inputs_reject(field, value):
    with pytest.raises(ValueError):
        replace(PricingInputs(100, 100, 1, 0.2), **{field: value})


@pytest.mark.parametrize("kind", ["call", "put"])
@pytest.mark.parametrize(
    "spot,time,vol",
    [
        (100, 1, 0.2),
        (70, 1, 0.6),
        (150, 1, 0.5),
        (100, 1e-5, 0.3),
        (100, 2, 0.001),
        (100, 1, 3.5),
    ],
)
def test_iv_recovers_known_price(kind, spot, time, vol):
    x = PricingInputs(spot, 100, time, vol, 0.01, 0.01 if vol == 0.001 else 0)
    solved = implied_volatility(kind, x, price(kind, x))
    assert solved.converged, solved
    assert solved.volatility == pytest.approx(vol, abs=2e-7)
    assert abs(solved.residual) <= 1e-10


@pytest.mark.parametrize("kind", ["call", "put"])
def test_iv_impossible_price_rejects(kind):
    x = PricingInputs(120, 100, 1, 0.2, 0.05)
    lo, hi = bounds(kind, x)
    for premium in (lo - 0.01, hi, hi + 1):
        with pytest.raises(ValueError):
            implied_volatility(kind, x, premium)


def test_newton_and_bad_initial_guess_fallback_are_explicit():
    x = PricingInputs(100, 100, 1, 0.3, 0.05)
    target = price("call", x)
    primary = implied_volatility("call", x, target)
    fallback = implied_volatility("call", x, target, initial=0.00001)
    assert primary.converged and primary.newton_steps > 0
    assert fallback.converged and fallback.bisection_steps > 0
    assert fallback.volatility == pytest.approx(0.3, abs=1e-7)


def test_iteration_limit_never_returns_plausible_success():
    x = PricingInputs(100, 100, 1, 0.6, 0.05)
    result = implied_volatility(
        "call", x, price("call", x), max_iterations=1, newton_iterations=0
    )
    assert not result.converged and result.volatility is None


def test_unidentifiable_low_vega_and_expiry_are_explicit():
    x = PricingInputs(1, 100, 0.0001, 0.2)
    result = implied_volatility("call", x, price("call", x))
    assert not result.converged and result.volatility is None
    assert "bound" in result.status
    with pytest.raises(ValueError, match="expiry"):
        implied_volatility("call", replace(x, time_years=0), 0)


def test_greek_shock_approximation_is_local_and_includes_time_sign():
    x = PricingInputs(100, 100, 1, 0.2, 0.05)
    small = shock("call", x, spot_change=0.1)
    large = shock("call", x, spot_change=30)
    assert abs(small["approximation_error"]) < 1e-5
    assert abs(large["approximation_error"]) > abs(small["approximation_error"])
    assert shock("call", x, elapsed_days=1)["exact_change"] < 0


def test_synthetic_quote_at_saturated_upper_bound_is_explicitly_unidentifiable():
    from quantlab.options.quotes import make_quote

    c = OptionContract("call", 100, years_from_days(30), 100)
    q = make_quote(c, 100, 0, 0.2, 0, revision=1)
    saturated = replace(q, bid=Fraction(100), ask=Fraction(100), model_value=100)
    state = saturated.public()
    assert state["iv"]["volatility"] is None and not state["iv"]["converged"]
    assert "upper bound" in state["iv"]["status"]


@pytest.mark.parametrize(
    "kind,spot,moneyness,intrinsic",
    [
        ("call", 110, "ITM", 10),
        ("put", 110, "OTM", 0),
        ("call", 100, "ATM", 0),
        ("put", 90, "ITM", 10),
    ],
)
def test_quote_moneyness_and_time_value_units(kind, spot, moneyness, intrinsic):
    from quantlab.options.quotes import make_quote

    q = make_quote(
        OptionContract(kind, 100, years_from_days(30)), spot, 0, 0.2, 0, revision=1
    ).public()
    assert q["moneyness"] == moneyness and q["intrinsic"] == intrinsic
    assert q["time_value"] == q["midpoint"] - intrinsic
