# Core units, signs and mathematical invariants

Authoritative for QuantLab 1.0.0. Models and limitations: [assumptions](../ASSUMPTIONS.md).

## Units and scaling

| Quantity | Canonical unit / conversion | Boundary protection |
|---|---|---|
| Book price | Positive integer ticks. Default one tick = £0.01. | `PriceGrid` converts exact decimal GBP; off-grid and nonpositive prices rejected. |
| Execution quantity | Whole positive units, side separate. | Domain validation rejects bool, zero, fractions and negative quantities. |
| Signed inventory | Positive long, negative short. Stock multiplier = 1. | Risk `Position` rejects stock contract-multiplier ambiguity. |
| Maker account | Exact rational **ticks**, including fractional-tick fees. | GBP = ticks × exact tick size; independent cash/lot checks. |
| Options and portfolio account | GBP, exact rational execution ledgers; public/risk calculations use checked floats. | No intermediate rounded pennies in premium accounting. |
| Option premium | GBP **per underlying unit**. | Cash = −signed contracts × multiplier × premium − fee. |
| Contract multiplier | Underlying units per option contract; positive integer. Default 100. | Applied once to premium and per-unit Greeks. |
| Fees | Stock GBP per filled unit; option GBP per filled contract. | Charged on actual fills only; no extra fee at model cash settlement. |
| Annual volatility | Decimal standard deviation per square-root model year: 20% = 0.20. | Pricing inputs label decimals; one volatility point = 0.01. |
| One-day return volatility | Decimal standard deviation per model day, **not** annual option sigma. | Risk settings/covariance have explicit daily meaning. No automatic equivalence. |
| Covariance | Return² per observation/day if built from returns; price covariance would be GBP². | Synchronous columns, dimensional checks, finite/symmetric/PSD validation. |
| Risk exposure vector | GBP delta exposure = units of delta × spot; allocation weights are dimensionless. | `variance_decomposition` documents which vector is supplied. |
| Portfolio variance | GBP² for GBP exposures; return² for weights. | Volatility is the square root, GBP or return respectively. |
| Rates/yield | Annual continuously compounded decimals. 5% = 0.05. | Pricing bounds −1…1; live account settings narrower. |
| Basis points | 1 bp = 0.0001 of the base amount. | Stress liquidation haircut is explicitly bps. |
| Time | Market clock integer microseconds; 1 second = 1,000,000 µs. Options ACT/365: years = calendar model days / 365. | Event order uses time and sequence; expiries align with configured steps. |
| Risk horizon | Whole IID calendar model days; option repricing uses days/365. | No silent crossing of first live option expiry. |
| Markout horizon | Number of eligible public exchange actions, or explicitly labelled observer events. | Not interchangeable with seconds/days. Pending/missing remains null. |
| Delta | Change in GBP value per £1 change in own underlying. | Per-unit Greek × signed contracts × multiplier; stock delta = signed units. |
| Gamma | Delta change per £1 underlying move. | Aggregate as above; no multiplication by spot except a labelled transformation. |
| Vega/rho | GBP change per **1.00** volatility/rate change. | Display per percentage point = raw / 100. |
| Theta | GBP value change per year as time passes. | Display per calendar model day = raw / 365. |
| Simple/log return | P[t]/P[t−1]−1 versus log(P[t]/P[t−1]); dimensionless, distinct. | Risk uses simple returns; desk realised-volatility display uses log returns. |
| Stat Arb spread | Y−alpha−beta X in Y price units (GBP here). Beta has Y-price/X-price units. | Supported sizing range stated; tiny residual SD makes z unavailable. |
| z-score | (Current spread−past mean)/past sample SD; dimensionless. | Current observation excluded from normalisation; all terms use one fit vintage. |
| Stock VWAP | Same unit as supplied fill prices; fees excluded. | One exact `execution.vwap` function serves exchange, desk and tutor. |

Annualising IID daily return volatility by √365 would be a *model assumption*, not a unit identity for observed market data. QuantLab does not silently use √252 in one lab and √365 in another. Stat Arb's combined-risk clock mapping is explicitly an approximation.

## Sign reference

| Quantity | Positive | Negative / caveat |
|---|---|---|
| Signed execution/inventory | Buy / long | Sell / short |
| Execution cash flow | Sell proceeds | Buy payment; fees always reduce cash |
| Realised gross P&L | Closing long above entry or closing short below entry | Opposite price movement |
| Unrealised P&L | Signed open lot × (mark−entry) | A mark is not a liquidation fill |
| Net P&L | Realised gross + unrealised + financing − fees | Stock maker `realised_pnl_ticks` is already net of fees; risk bridge adds fees back only when producing `realised_gross` |
| Provider markout | Provider side sign × (later reference−execution price) > 0 favours provider | <0 harms provider; seller sign is −1, buyer +1 |
| Aggressor markout | Same own-side sign rule, separately labelled role | Never pool roles silently |
| Call/put delta | Long call generally positive | Long put generally negative; short reverses |
| Gamma/vega | Long vanilla option generally nonnegative | Short reverses; kinks/degenerate cases can be undefined |
| Theta/rho | Derivative under stated carry/time convention | Do not assume theta always negative or put rho always determines P&L with other inputs changing |
| Loss / VaR / ES | Loss = −P&L; positive threshold is a loss | Negative VaR/ES is permitted if model outcomes are gains |
| Stress P&L | Hypothetical value increases | Negative is hypothetical damage, never a ledger debit |
| Long spread | Buy Y, sell approximately beta units of X per Y | Benefits from spread rising, conditional on held hedge and costs |
| Short spread | Sell Y, buy approximately beta units of X | Benefits from spread falling; no convergence guarantee |
| Execution shortfall | Signed quantity × (execution−reference), normally a cost | Can be negative with price improvement; not clipped to a loss |

## Identities versus expectations

**Identities checked mechanically:** every execution's buyer reduction = seller reduction = trade quantity; totals reconcile across each match; submitted quantity partitions into both filled sides, live remainder and cancelled remainder. Cash equals initial cash plus actual flows less fees plus financing. Equity equals cash plus signed marked positions; P&L equals equity less initial capital and also realised gross plus unrealised plus financing less fees. Total option Greeks equal signed quantity × multiplier × per-unit Greek summed by underlying. Stat Arb's spread plus directional price attribution minus signed shortfall minus fees equals actual marked P&L; temporary-leg directional attribution is a subset, not an additional term. Replay compares actual reconstructed transitions.

**Conditional mathematical properties:** BSM bounds/parity and finite derivatives depend on the model and numerical domain. A valid PSD covariance gives nonnegative quadratic variance up to disclosed roundoff tolerance. ES ≥ VaR follows the specified upper-loss-tail definition, including fractional boundary mass. Future-data mutation must not alter a past causal signal. Exact floating replay is restricted by recorded versions.

**Model expectations, never invariants:** cleaner signals may improve estimated decisions over distributions; informed flow may adversely select a maker; an AR residual may converge; more data may improve estimates. Profits, convergence, monotone realised P&L with information quality, and precise VaR coverage are not correctness tests.
