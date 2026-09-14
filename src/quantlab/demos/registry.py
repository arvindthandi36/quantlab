"""Catalogue metadata; each focus uses a shared, bounded existing-engine walkthrough."""

from quantlab.demos.models import Spec
from quantlab.explainability.registry import CONCEPTS

# id | title | central concept(s) | evidence builder
GROUPS = {
    "Trading": """
order|How an order becomes a trade|market_orders,depth,vwap,execution_cost|order
walk-book|Market order walking the book|order_size,depth,slippage|order
vwap|VWAP from multiple fills|vwap,partial_fills,execution_cost|order
queue|Limit order resting and queue priority|limit_orders,queue_priority|queue
partial|Partial fills|partial_fills,depth|partial
long-short|Going long and short|position,unrealised_pnl|long_short
""",
    "Market Making": """
spread-liquidity|Spread and liquidity|spread,depth|order
adverse-selection|Adverse selection|adverse_selection,markouts|picked_off
picked-off|Getting picked off|adverse_selection,markouts,spread_capture|picked_off
markouts|Markouts|markouts,adverse_selection|picked_off
inventory|Inventory risk|inventory,drawdown|long_short
quote-skew|Inventory-aware quote skew|quote_skew,inventory|skew
""",
    "Research": """
one-run|Why one profitable run proves little|sample_mean,standard_error|precision
monte-carlo|Monte Carlo distributions|monte_carlo,variance|precision
sd-se|Standard deviation vs standard error|standard_deviation,standard_error|precision
confidence|Confidence intervals|confidence_intervals,standard_error|precision
winner|Winner’s curse / multiple testing|selection_bias,sample_mean,confidence_intervals|winner
crn|Common random numbers|common_random_numbers,variance|crn
""",
    "Options": """
call-put|What a call and put are|option_pricing,contract_multiplier|option_inputs
black-scholes|Black-Scholes inputs|black_scholes,option_pricing|option_inputs
delta|Delta|delta,contract_multiplier|delta
gamma|Gamma|gamma,delta|delta
vega|Vega|vega,volatility|delta
theta|Theta|theta,option_pricing|delta
iv|Implied volatility|implied_volatility,volatility|option_inputs
newton|Newton-Raphson + fallback|root_finding,implied_volatility|solver
delta-hedge|Delta hedging|option_pricing,delta,gamma,delta_hedging,vega|delta
residual-risk|Delta-neutral does not mean risk-free|delta_hedging,vega,model_risk|delta
realised-implied|Realised vs implied volatility|volatility,implied_volatility|delta
""",
    "Risk": """
covariance|Covariance and correlation|covariance,correlation|diversification
diversification|Diversification|diversification,portfolio_variance|diversification
portfolio-variance|Portfolio variance|portfolio_variance,covariance_matrices|diversification
var|VaR|var,model_risk|tails
es|Expected Shortfall|expected_shortfall,var|tails
tails|VaR vs ES|var,expected_shortfall,model_risk|tails
stress|Stress testing|stress_testing,model_risk|stress
reprice|Greek approximation vs full repricing|stress_testing,gamma,vega|stress
correlation-stress|Correlation stress|correlation,diversification|diversification
model-risk|Model risk|model_risk,stress_testing|stress
""",
    "Stat Arb": """
regression|Regression|regression,regression_beta|regression
residual|Residual spread|residual,regression|pairs
z-score|Z-score|z_score,residual|pairs
pairs|Correlation vs cointegration|correlation,regression,residual,z_score,model_risk|pairs
spurious|Spurious correlation|correlation,selection_bias|mining
leg-risk|Leg risk|leg_risk,partial_fills|leg
walk-forward|Walk-forward testing|lookahead_bias,regression|lookahead
relationship-break|Relationship breakdown|model_risk,residual|pairs
lookahead|Look-ahead bias|lookahead_bias,regression|lookahead
pair-mining|Pair-mining / multiple testing|selection_bias,correlation|mining
""",
    "Markets": (
        "\nsynthetic-prices|Synthetic market: how prices "
        "emerge|current_price,order_flow,market_orders,randomness|syntheti"
        "c\nhistorical|Historical replay: what is real and what is "
        "simulated|historical_replay,current_price,vwap|historical\nscenari"
        "o|Scenario market|market_environments,model_risk|scenario\nhidden-"
        "scenario|Hidden scenario "
        "inference|market_environments,model_risk|hidden\n"
    ),
    "Engineering": """
ticks|Why integer ticks|integer_ticks,reproducibility|order
seeds|Why deterministic seeds|randomness,reproducibility|synthetic
fifo|Why price-time priority|queue_priority,event_driven|queue
separation|Why UI and engine are separated|architecture,event_driven|order
fingerprints|Why replay fingerprints matter|reproducibility,architecture|historical
""",
}
FLAGSHIPS = (
    "order",
    "picked-off",
    "delta-hedge",
    "tails",
    "pairs",
    "winner",
    "synthetic-prices",
    "historical",
)
REGISTRY = {}
for domain, rows in GROUPS.items():
    for row in rows.strip().splitlines():
        key, title, concept_ids, builder = row.split("|")
        concepts = tuple(concept_ids.split(","))
        env = (
            "SIMULATED HISTORICAL EXECUTION · ARTIFICIAL FIXTURE"
            if builder == "historical"
            else "SCENARIO"
            if builder in ("scenario", "hidden")
            else "SYNTHETIC STATISTICAL CONTROL"
            if builder in ("precision", "winner", "crn")
            else "SYNTHETIC"
        )
        REGISTRY[key] = Spec(
            key,
            title,
            CONCEPTS[concepts[0]].public()["matters"],
            domain,
            concepts,
            builder,
            difficulty="Build on the basics"
            if domain in ("Research", "Stat Arb", "Risk")
            else "First principles",
            duration_minutes=6 if key in FLAGSHIPS else 3,
            prerequisites=tuple(
                dict.fromkeys(
                    p for c in concepts for p in CONCEPTS[c].public()["prerequisites"]
                )
            ),
            environment=env,
            flagship=key in FLAGSHIPS,
        )


def catalogue():
    return [s.public() for s in REGISTRY.values()]
