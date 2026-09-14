# Concept registry

The authoritative definitions live in `src/quantlab/explainability/registry.py`. The browser, API, search, relationship maps and tutor bridge read that one registry. This document is a coverage index, not a second definition store.

There are **70 concepts across 12 domains**. Every concept supports Beginner, Maths, Quant and Interview. Maths defines symbols when a formula applies; a mechanism without its own scalar formula links to its calculated dependencies.

## Metadata contract

`id`, `name`, `domain`, `definition`, `matters`, `changes`, `limitation`, `prerequisites`, `related`, `affected_by`, `affects`, `maths` (equation and variables), `uses`, `locations`, `assumptions`, `depths`, `misconception`, and `interview`. IDs are stable API keys. Registry validation rejects broken prerequisite/related/assumption links and cycles in prerequisites. Dependency graphs may have feedback relationships; they are not asserted to be prerequisite DAGs.

## Coverage audit

| Lab | Count | Important concepts / actions |
|---|---:|---|
| Trading | 20 | Bid, Ask, Spread, Midpoint, Market depth, FIFO priority, Market order, Limit order, Partial fill, VWAP, Position, Realised P&L, Unrealised P&L, P&L and its changes, Fees, Markout, Drawdown, Order size, Slippage, Execution cost |
| Maker | 14 | Inventory, Inventory quote skew, Spread capture, Adverse selection, Order flow, Market depth, Spread, Markout, Position, P&L and its changes, Fees, Exposure, FIFO priority, Limit order |
| Options | 14 | Option model value, Black–Scholes model, Delta, Gamma, Vega, Theta, Rho, Implied volatility, Volatility, Delta hedge, Contract multiplier, P&L and its changes, Root finding, Monte Carlo |
| Risk | 13 | Value at Risk (VaR), Expected Shortfall, Covariance, Correlation, Covariance matrix, Portfolio variance, Diversification, Exposure, Stress P&L, Portfolio optimisation, Drawdown, P&L and its changes, Model risk |
| Statarb | 13 | Regression fit, Regression beta, Residual / spread, Z-score, Stat-arb decision, Correlation, Incomplete pair risk, Look-ahead bias, Position, P&L and its changes, Execution cost, Winner's curse, Standard deviation |
| Research | 12 | Sample mean, Standard deviation, Standard error, Confidence interval, Expected value, Variance, Monte Carlo, Common random numbers, Winner's curse, Look-ahead bias, Verified replay, Model risk |
| Learning | 12 | Learning evidence, UI / engine separation, Integer ticks, Event-driven clock, Deterministic seeds, Verified replay, Common random numbers, Model risk, Expected value, Standard error, Confidence interval, Look-ahead bias |

Coverage means a meaningful definition, drivers, limitations and relevant public evidence. Some mechanisms have a structured trace instead of a number. Unrecorded slippage benchmarks and standalone spread capture stay unavailable; no substitute result is invented.

## Domain index

### Derivatives

`option_pricing`, `black_scholes`, `delta`, `gamma`, `vega`, `theta`, `rho`, `volatility`, `delta_hedging`, `contract_multiplier`

### Engineering / reproducibility

`randomness`, `reproducibility`, `integer_ticks`, `event_driven`, `architecture`, `mastery`

### Market mechanics

`bid`, `ask`, `spread`, `midpoint`, `depth`, `queue_priority`

### Market microstructure

`markouts`, `inventory`, `quote_skew`, `spread_capture`, `adverse_selection`, `order_flow`

### Numerical methods

`implied_volatility`, `monte_carlo`, `root_finding`

### Portfolio theory

`correlation`, `covariance`, `covariance_matrices`, `portfolio_variance`, `diversification`, `portfolio_optimisation`

### Probability

`expectation`, `variance`

### Research methods

`lookahead_bias`, `selection_bias`, `common_random_numbers`, `model_risk`

### Risk

`var`, `expected_shortfall`, `stress_testing`, `drawdown`, `exposure`

### Statistical arbitrage

`regression`, `regression_beta`, `residual`, `z_score`, `stat_arb_signal`, `leg_risk`

### Statistics

`sample_mean`, `standard_deviation`, `standard_error`, `confidence_intervals`

### Trading / execution

`limit_orders`, `market_orders`, `partial_fills`, `order_size`, `vwap`, `slippage`, `execution_cost`, `position`, `realised_pnl`, `unrealised_pnl`, `pnl_attribution`, `fees`

## Search and relationships

Search tokenises local names, IDs, definitions, aliases and driver metadata. Examples include “Why did VaR rise?”, “gamma”, “look-ahead bias”, “what does correlation affect?” and “P&L”. This is keyword ranking, not unrestricted semantic understanding. Six short maps distinguish model dependencies from conceptual relationships. Every node opens its concept and selects a relevant lab if necessary. Opening an uninitialised lab concept shows a definition and an explicit missing-evidence message. It does not create a financial account.

## Extending safely

Add one metadata record, valid relationships and an allowlisted public evidence projection if the existing engine exposes the relevant output. Reuse a validated API for calculations or isolated examples. Supply a variable definition for every new mathematical symbol and a plain-language limitation. Add current-state, privacy and replay tests for a new projection. Do not alter frozen financial behaviour as part of an explanation change.
