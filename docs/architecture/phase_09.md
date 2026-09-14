# Phase 9 — Risk & Portfolio Lab contract

> Historical phase record. Current core conventions and release status are in the root README, ASSUMPTIONS and Phase 11 release report. Test counts and runtime labels below describe this phase.


Only Phase 9 is authorised. All 898 prior tests remain part of the acceptance suite.

## Account and information boundary

The Risk Lab reads the existing Phase 8 option/stock accounts and Phase 6 manual account. These are separate synthetic instruments: QL-STOCK is the option underlying; QL-DESK is the manual microstructure instrument. They are not interchangeable hedges. An optional QL-SECOND exchange supplies a second controlled teaching instrument. All stock transactions use TradingSession and the FIFO matching engine. All option transactions use the finite Phase 8 dealer quotes. Cash, realised/unrealised P&L, fees and equity come from those accounts, never reconstructed by a risk calculator. Aggregation checks equity minus initial capital equals accounted P&L. No funding is transferred between accounts.

Risk inputs are detached current positions and public quotes. No market RNG, latent value, private signal or future realised observation enters a risk model. Analysis seeds generate hypothetical scenarios in an independent stream. A synthetic return sample is explicitly labelled, never passed off as observed history. Uploaded empirical observations represent synchronised one-day simple returns, complete cases only; missing rows are rejected unless explicit listwise deletion is requested.

## Valuation and time

Current equity uses executable-venue public marks (option midpoint), not a second accounting mark. Scenario P&L uses model-price CHANGES from the current model price, plus stock changes and cash funding. Thus zero shock at zero horizon has zero scenario P&L even when quote midpoint differs slightly from model value. This freezes the current quote/model basis. It is an assumption, not an executable price guarantee. Options use sticky strike volatility, parallel absolute volatility-point shocks and ACT/365 elapsed calendar days. Cash accrues at the stated scenario rate; stock cash from other desks follows the same hypothetical risk funding assumption. No scenario is posted to an account. Horizons beyond the first live option expiry are rejected: terminal-only sampling cannot infer an earlier cash-settlement price.

## Loss, covariance and model conventions

Loss = minus hypothetical P&L, in GBP. Negative VaR is allowed (a gain threshold). Empirical VaR is the inverse empirical CDF, ordered loss index ceil(alpha*N)-1. ES averages exactly the worst (1-alpha)*N observations, with a fractional weight at the boundary. This includes a boundary atom only to the required tail mass. ES >= VaR; VaR is never a maximum-loss claim. Normal VaR uses mean loss plus z_alpha standard deviation; options are explicitly delta-normal. IID one-day arithmetic-return moments scale mean and covariance by horizon only for this LINEAR approximation. Full revaluation compounds sampled daily returns and ages options; no square-root scaling of nonlinear P&L.

Covariance estimation uses N-1 sample denominator by default (population N is explicit). Matrices must be finite, symmetric and positive semidefinite. Zero-variance correlations are undefined, not zero. Near singularity is reported. Positive definite draws use Cholesky; singular PSD draws use an explicitly reported eigenfactor. Tiny numerical negative eigenvalues within relative tolerance are disclosed if truncated; genuinely indefinite matrices fail. No statistical regularisation is automatic.

## Execution limits and replay

Limits operate at order ingress on an isolated copy of the actual exchange/account state. They inspect actual proposed fills and reservations for outstanding limit orders, at current marks. Soft limits warn; hard limits prohibit a newly breached or worsening exposure. Reducing an existing breach is allowed (and still warned). Market moves can breach limits after submission; limits do not promise continuous solvency. Existing orders reserve buy-only/sell-only exposure endpoints independently by instrument. A manual quote replacement is also tested before its real orders are submitted. Drawdown is irreversible: a breach cannot be erased by a trade.

Risk sessions record financial commands, assumptions, limits, custom scenarios and analytical results in order. Ended exports include baseline seed/configuration and account evidence; active public views never include market seeds. Replay reconstructs actual trades and compares every result and risk frame. Research pricing/analysis randomness never advances market time.

## Optimisation

The optimisation panel is a synthetic allocation study tied to the current factor model, not an automatic trade or expected-return forecast. It solves a budgeted minimum variance or mean-variance problem with optional long-only, risky-asset caps and minimum cash. All cash is explicitly a zero-variance asset. Solver status, objective, feasibility residuals and constraints are returned. Infeasible or failed solutions are rejected. Exact zero-risk cash solutions are legitimate and explained. Implemented dollar allocations are a teaching budget, not invented funds in the trading account.
