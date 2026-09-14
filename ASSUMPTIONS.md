# QuantLab model assumptions — authoritative core register

Applies to release candidate 1.0.0 (Phases 0–11). This document supersedes the current-model claims in [the archived phase-by-phase register](docs/architecture/assumptions_phases_0_10.md). Exact units and identities live in [conventions](docs/conventions.md). A model being implemented correctly does not make its assumptions true in a real market.

| Model | WHAT IT ASSUMES | WHY WE USE IT | WHEN IT FAILS | WHAT QUANTLAB DOES NOT CLAIM |
|---|---|---|---|---|
| Exchange | One serial price/time-priority book per stock, integer ticks and whole positive units. Execution is at the resting price; market remainder cancels. | Every execution and FIFO priority can be explained. | Auctions, hidden/pegged orders, venue routing, latency and price bands matter. | Exchange certification or realistic queue-fill probabilities. |
| Latent value | Arithmetic Gaussian shocks in ticks on a fixed private clock; constant shock scale. Invalid nonpositive states fail. | Separate unobserved value from actual traded price. | Jumps, regime changes, positivity, volatility clustering and real information arrival. | A calibrated fair-value process or executable latent price. |
| Ordinary flow | Independent exponential waiting times, fixed rates; noise orders use public anchors, liquidity orders have exogenous side/size. | A small autonomous market without strategic complexity. | Order clustering, endogenous demand, feedback, queue incentives and session seasonality. | Representative real investor motives. |
| Informed flow | Current latent value plus independent Gaussian measurement error; a public-anchor Gaussian prior is reset at each decision. Positive prior and signal uncertainty. Trades require posterior edge above costs and uncertainty buffer. | Makes information asymmetry and adverse selection emerge through actual executions. | Biased/correlated signals, unknown precision, strategic signalling or learning across time. | A calibrated Bayesian filter, perfect information, or guaranteed informed profits. |
| Markouts | Signed reference change after specified horizons; public midpoint and observer latent benchmarks are separate. Missing/pending is unavailable. | Measure post-trade price movement by role. | Missing markets, benchmark manipulation, confounding common price moves, horizon selection. | Markout as extra booked P&L or causal proof of adverse selection from one trade. |
| Market making | Fixed or inventory-skewed quotes around a public reference; cancel/replace loses queue priority; fixed fees; reservations guard hard limits. | Isolate spread, inventory and adverse-selection effects. | Strategic competitors, financing, borrow, latency, endogenous liquidity and market impact. | Optimal quoting or profitability outside this model. |
| Accounts | Exact rational execution cash and FIFO lots; mark-to-reference for inventory; fees charged once; shorting allowed under explicit limits. | Reconcile independently computed ledger identities. | Real tax lots, clearing, margin, dividends, borrow recalls and broker accounting conventions. | Broker-equivalent account statements. |
| Option pricing | European cash-settled calls/puts; Black–Scholes–Merton constant annual volatility/rates/yield, lognormal diffusion and idealised replication. Scalar/array prices use one kernel. | A mathematically explicit baseline with testable bounds, parity and derivatives. | American exercise, jumps, stochastic volatility, discrete dividends and frictions. | Market prices or arbitrage-free dynamic smile calibration. |
| Option quote model | Finite synthetic dealer bid/ask sizes around model quotes, strike-dependent volatility, IOC. No option order book. | Distinguish theoretical value from execution and model finite fills. | Dealer competition, queue priority, real surfaces, endogenous spreads. | A complete options exchange or globally arbitrage-free surface. |
| Hedge process | Observed GBM stock path under physical drift, constant process volatility, discrete whole-stock hedges paying actual spreads/fees. Live dividend yield is zero. | Expose discrete hedge error, costs and changing delta. | Continuous rebalancing, jumps, liquidity gaps, dividends, transaction-dependent impact. | A riskless hedge; delta neutrality also does not remove gamma or vega. |
| IV | Monotone BSM inversion only within feasible bounds and sigma 0–5. Solver checks residual and sensitivity; unresolved values are null. | Explain prices as model-implied uncertainty with diagnostics. | Low vega, infeasible quotes, model misspecification, extreme floating-point tails. | A measured physical volatility or reliable answer at a numerical boundary. |
| Covariance | Synchronous finite simple-return samples; explicit N−1 or N scaling; symmetric PSD matrix. Only disclosed roundoff-level tolerance, no statistical repair. | Transparent quadratic exposures and joint shocks. | Changing dependence, bad timestamps, missing-data bias and unstable estimation. | Correlation stability or statistical regularisation. |
| VaR/ES | Loss = −P&L. Linear normal approximation, empirical inverse-CDF VaR and fractional-tail ES, or IID normal/Student joint daily scenarios with full option repricing. | Compare model-dependent loss estimates. | Fat tails not represented, clustering, crisis dependence, sparse tails, financing/liquidity gaps. | VaR as maximum loss, guaranteed coverage, or sufficient capital. |
| Risk repricing | Fixed-IV future revaluation unless explicitly shocked; frozen model/market basis; cash carry; horizon cannot cross a live expiry. | Avoid changing unexplained mark bases or silently extrapolating settlement. | Joint volatility/spot dynamics and actual future dealer prices. | The scenario is a future fact or a ledger transaction. |
| Stress | Explicit deterministic spot/IV/rate/time/haircut shocks; Greek approximation residual shown against full pricing. | Inspect assumptions and nonlinear consequences. | Missing crises, changing liquidity and omitted interactions. | Probability attached to a chosen shock. |
| Allocation | Synthetic mean/covariance inputs; constrained continuous weights with cash; feasibility checked before and after optimisation. | Study diversification and constraints. | Estimation error, turnover, integer lots, transaction costs and unstable means. | Recommended investments or automatic orders. |
| Stat Arb data | Published named synthetic stock prices; selectable correlated/common-factor shocks and specified AR residual relationships, including breaks. | Contrast correlation with stability and test causal fitting. | Real common trends, market structure, structural changes and nonlinear relationships. | Historical data or empirical cointegration evidence. |
| Stat Arb model | Centred/scaled OLS; conventional SE assumes IID homoskedastic errors. Fit ends before decision observation; z normalisation excludes current spread. Fixed, rolling and walk-forward schedules. | Make timing and regression inspectable. | Nonstationarity, outliers, serially correlated residuals, poor scale and near-constant predictors. | ADF/unit-root inference, mean reversion from correlation/R², or an optimal window. |
| Stat Arb execution | Separate actual stock legs, finite depth, costs, pending legs and imperfect integer hedge ratios; beta sizing supports 0.05–5. | Preserve leg risk and real inventory. | Simultaneous multi-venue execution, realistic latency, borrow and nonlinear impact. | Atomic pairs execution, guaranteed convergence or dollar/factor neutrality. |
| Combined labs | Distinct ledgers/underlyings; cross-lab covariance set to zero and one Stat Arb observation mapped to a risk day for the illustrative combined report. Limits retain their disclosed separate scopes. | Inspect the actual combined position without inventing hidden correlations. | The clocks, dependencies or limits require a unified calibrated model. | A joint global risk-limit engine or calibrated cross-lab VaR. |
| Research | Whole independent sessions conditional on one configuration; paired variants share verified exogenous paths; disjoint development/evaluation seed namespaces; pre-registration and evaluation exposure records. | Distinguish sampling uncertainty, paired effects, selection and failed runs. | Common model bias, repeatedly viewed holdouts, many hypotheses, small samples. | Out-of-model validity, untouched evaluation after reuse, or a confidence interval for model error. |
| Tutor | Deterministic local rules and questions from allowlisted public facts; answer evidence updates a practice indicator. | Teach observed mechanics without perturbing market RNG. | Ambiguous free reasoning, incomplete curriculum or treating practice scores as ability. | A calibrated competence assessment, external AI judgement or automatic mastery. |
| Local application | One user, one server per data directory, serialised financial requests. Separate submissions are separate orders. | Small inspectable state machine. | Untrusted network access, many clients, retries requiring exactly-once semantics or shared files across processes. | Internet hardening, distributed concurrency, durable exchange service or formal accessibility certification. |

Core hard failures are not repaired. Bounded floating-point roundoff handling is local, disclosed and separate from exact accounting. Platform/libm/BLAS differences can change floating-point evidence; replay compatibility is deliberately conservative.


## Phase 12 explanation and hypothetical interpretation

The approved core assumptions above are unchanged. Explanation panels link to the
Phase 11 [model-risk map](docs/release/model_risk.md) and group its applicable risks.

| Interpretation | Assumption / limitation |
|---|---|
| Actual explanation | Public engine snapshots are evidence for recorded calculations, not proof of real-market validity. Missing evidence is reported as unavailable. |
| Why did this change? | Compares two retained public observations. Changed inputs may interact; reported differences are not additive causal shares. |
| Order-size hypothesis | Frozen displayed FIFO depth; includes displayed own orders. It omits live self-trade controls, account constraints, fees and later market reaction. |
| Volatility hypothesis | Existing option model with other selected inputs held fixed. Attached portfolio analysis is detached model repricing and delta-normal risk, not a new live Monte Carlo report. |
| Correlation hypothesis | One common correlation across three named factors, with configured daily volatilities fixed. Replaces a custom covariance matrix in the detached hypothesis. |
| Inventory hypothesis | Existing nonlinear inventory quoting policy and planner, with soft/hard limits disclosed. It does not claim manual desk quotes automatically follow that policy. |
| Threshold hypothesis | Published Stat Arb prefix only; independent flat-position qualification at each point. It is not an executed strategy backtest or a new registered evaluation. |
| Teaching examples | Independent core-engine or explicitly qualitative examples, never invented user-session values. |
| Observability | Current public information for live/replay; hidden synthetic evidence requires explicit reveal after the stock session ends and is excluded from quizzes. |
| Reading and mastery | Reading records no assessment. Only the established tutor’s answer evidence can affect mastery. |

See [what-if contracts](docs/explainability/WHAT_IF_MODE.md) and
[information boundaries](docs/explainability/INFORMATION_BOUNDARIES.md).


## Phase 13 environment assumptions

The approved financial kernels above remain unchanged. Their environment adapters add:

- Historical **recorded prices are observations, not known true values or causal explanations**.
  Provenance and adjustment policies are declarations that QuantLab cannot independently certify.
- Bar timestamps are end/availability times. Next-close candidate prices, shared volume fractions,
  fixed adverse slippage and fees are explicit paper conventions, not actual historical execution.
  No queue, historical spread/depth or option chain is inferred from OHLCV.
- GBP only, exact tick prices, controlled corporate actions, at most two aligned series. Gaps are
  not interpolated; risk across gaps can mix interval lengths. No funding/margin/borrow model.
- Live risk uses at most 250 revealed past returns and existing revaluation/empirical tails. A
  calculable two-return VaR is statistically fragile. It is neither a maximum loss nor a forecast.
- Historical pair qualification uses causal fits. Research fixes training/evaluation boundaries,
  uses one actual dataset path and makes no independent-path/alpha claim. Simple one-unit legs
  do not hedge regression beta or guarantee both executions.
- Scenarios change real existing inputs. Their conditional outcomes are not market predictions.
  Hidden mode removes direct configuration, not a user's ability to infer or inspect local files.
- No real market data is bundled. Artificial fixtures remain labelled. Full source fingerprints
  are withheld in live state, then checked on replay. Restart resets accounts, not human knowledge.

See [the detailed execution contract](docs/markets/HISTORICAL_EXECUTION.md) and
[information boundaries](docs/markets/INFORMATION_BOUNDARIES.md).

## Phase 14 teaching assumptions

- Demonstrations prepare genuine bounded engine evidence and reveal it in sequence. The displayed
  narrative is not a replacement financial model. User hedge branches rerun actual core actions.
- Fixed demo configurations illustrate mechanisms, not representative performance or real-world alpha.
  Seed 140042 was declared before inspection; the winner's control is not seed-searched.
- Public checkpoint responses exclude later outcomes and private signals. Hidden synthetic truth needs
  explicit ended-demo hindsight. This is a cooperative local information boundary, not tamper resistance.
- Annotation chooses a few moments and can miss context. Its risk proxy is not a full audit. Profit or
  loss does not grade process; declared objectives and decision rules are usually unavailable.
- Quick/showcase/replay viewing never earns mastery. Learn answers use existing validators and grading;
  prior answer exposure persists separately, so restarting cannot erase what the learner has seen.
- Capture mode retains simulated-execution, artificial-data and limitation labels. No recording or final
  marketing assets were generated. See [the boundary contract](docs/demos/INFORMATION_BOUNDARIES.md).


## Product 1.1.0 presentation

Phase 15 changes presentation and release preparation, not financial assumptions. The new
[limitations guide](docs/LIMITATIONS.md) organises existing simplifications and failure modes.
The product version differs from the frozen core replay version; [versioning](docs/release/VERSIONING.md)
explains why old journals retain their existing checks. Real screenshots are selected educational
states, not evidence of real-world performance. No dark theme or formal accessibility certification
is claimed. The planned feature set is frozen.
