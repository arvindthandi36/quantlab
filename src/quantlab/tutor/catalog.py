"""Small prerequisite graph; unencountered and future material stays unassessed."""

from dataclasses import dataclass

from quantlab.tutor.risk import LESSONS as RISK_LESSONS
from quantlab.tutor.statarb import LESSONS as STATARB_LESSONS


@dataclass(frozen=True)
class Concept:
    id: str
    domain: str
    title: str
    prerequisites: tuple[str, ...] = ()
    implemented: bool = True


DOMAINS = {
    "Market mechanics": "bid ask spread midpoint market_orders limit_orders liquidity depth "
    "queue_priority partial_fills vwap slippage",
    "Market microstructure": "order_flow adverse_selection informed_trading markouts inventory "
    "spread_capture toxic_flow quote_skew pnl_attribution",
    "Probability": "random_variables expectation variance conditional_probability "
    "distributions "
    "poisson_arrivals normal_distributions law_of_large_numbers",
    "Statistics": "sample_mean standard_deviation standard_error confidence_intervals "
    "bootstrap "
    "correlation hypothesis_testing selection_bias multiple_testing",
    "Calculus": "derivatives optimisation_calculus continuous_time",
    "Linear algebra": "covariance_matrices portfolio_linear_algebra factor_models regression",
    "Optimisation": "portfolio_optimisation execution_optimisation inventory_control",
    "Derivatives": "option_pricing greeks volatility hedging",
    "Risk": "drawdown var expected_shortfall stress_testing exposure tail_outcomes",
    "Numerical methods": "root_finding monte_carlo finite_differences numerical_optimisation",
    "Python / implementation": "data_structures testing randomness reproducibility algorithms "
    "numerical_correctness architecture model_criticism research_integrity decision_quality",
}
FUTURE_DOMAINS = {"Calculus", "Linear algebra", "Optimisation", "Derivatives"}
FUTURE = {
    "var",
    "expected_shortfall",
    "stress_testing",
    "root_finding",
    "finite_differences",
    "numerical_optimisation",
}
PREREQUISITES = {
    "spread": ("bid", "ask"),
    "midpoint": ("bid", "ask"),
    "liquidity": ("spread",),
    "market_orders": ("bid", "ask"),
    "queue_priority": ("limit_orders",),
    "partial_fills": ("market_orders",),
    "vwap": ("liquidity",),
    "slippage": ("vwap",),
    "markouts": ("midpoint",),
    "adverse_selection": ("markouts",),
    "informed_trading": ("expectation",),
    "spread_capture": ("spread", "inventory"),
    "toxic_flow": ("markouts",),
    "exposure": ("inventory",),
    "drawdown": ("exposure",),
    "pnl_attribution": ("inventory",),
    "quote_skew": ("spread", "inventory"),
    "expectation": ("random_variables",),
    "variance": ("expectation",),
    "standard_deviation": ("variance",),
    "standard_error": ("sample_mean", "standard_deviation"),
    "confidence_intervals": ("standard_error",),
    "bootstrap": ("sample_mean",),
    "hypothesis_testing": ("standard_error",),
    "selection_bias": ("sample_mean",),
    "multiple_testing": ("hypothesis_testing",),
    "law_of_large_numbers": ("expectation",),
    "monte_carlo": ("randomness",),
    "reproducibility": ("randomness",),
}
CONCEPTS = {
    key: Concept(
        key,
        domain,
        key.replace("_", " ").capitalize(),
        PREREQUISITES.get(key, ()),
        domain not in FUTURE_DOMAINS and key not in FUTURE,
    )
    for domain, names in DOMAINS.items()
    for key in names.split()
}


def prerequisites_for(key):
    return ACTIVE_CONCEPTS[key].prerequisites


# Preserve the Phase 7 catalog API for stock-only callers and saved regression cases.
# Application services use the complete versioned catalog below. Derivative questions
# additionally require a real derivatives context; availability is not permission to
# manufacture an options lesson from an old stock-only observation.
OPTION_PREREQUISITES = {
    "call": (),
    "put": (),
    "strike": (),
    "expiry": (),
    "premium": ("call",),
    "intrinsic_value": ("strike",),
    "time_value": ("intrinsic_value",),
    "moneyness": ("strike",),
    "black_scholes": ("call", "expectation"),
    "put_call_parity": ("call", "put"),
    "delta": ("call",),
    "gamma": ("delta",),
    "vega": ("volatility",),
    "theta": ("expiry",),
    "rho": ("premium",),
    "implied_volatility": ("black_scholes",),
    "realised_volatility": ("standard_deviation",),
    "delta_hedging": ("delta", "contract_multiplier"),
    "contract_multiplier": ("premium",),
    "newton_raphson": ("root_finding", "vega"),
    "monte_carlo_pricing": ("expectation",),
    "option_pricing": ("call", "put"),
    "greeks": ("delta",),
    "volatility": (),
    "hedging": ("delta",),
    "root_finding": (),
    "finite_differences": ("delta",),
    "derivatives": ("delta",),
}
OPTION_CONCEPTS = {
    key: Concept(
        key,
        "Numerical methods"
        if key
        in ("root_finding", "newton_raphson", "finite_differences", "monte_carlo_pricing")
        else "Calculus"
        if key == "derivatives"
        else "Derivatives",
        key.replace("_", " ").capitalize(),
        parents,
        True,
    )
    for key, parents in OPTION_PREREQUISITES.items()
}
ACTIVE_CONCEPTS = CONCEPTS | OPTION_CONCEPTS

# Phase 9 runtime concepts retain the original stock-only catalog contract.

RISK_CONCEPTS = {
    key: Concept(
        key,
        "Risk" if key not in ("minimum_variance", "portfolio_optimisation") else "Optimisation",
        key.replace("_", " ").capitalize(),
        (),
        True,
    )
    for key in RISK_LESSONS
}
ACTIVE_CONCEPTS = ACTIVE_CONCEPTS | RISK_CONCEPTS

# Phase 10 concepts are runtime-only and require observed stat-arb facts.

STATARB_CONCEPTS = {
    k: Concept(k, "Statistics", k.replace("_", " ").capitalize()) for k in STATARB_LESSONS
}
ACTIVE_CONCEPTS = ACTIVE_CONCEPTS | STATARB_CONCEPTS
