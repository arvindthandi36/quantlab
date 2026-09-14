# Core architecture, public interfaces and reproducibility

Release candidate 1.0.0. These are reusable Python contracts; underscore-prefixed helpers, controller wiring, caches and raw private observations are internal. DTO/schema changes require version review and regression tests. No promise of perpetual binary or cross-version compatibility is made.

## Source of truth and main interfaces

| Domain | Authoritative implementation / supported use | Boundary |
|---|---|---|
| Matching | `OrderBook.submit(LimitOrder/MarketOrder)`, `cancel`, `snapshot`, `check_invariants` | Exact integer ticks, FIFO and conservation. No HTTP/agent dependency. |
| Executions | `execution.vwap((price, quantity)...)` | One exact calculation used by book reports, desk reports and tutor. Fees separate. |
| Market | `MarketEnvironment.step`, `observation`; `MarketSimulation.run` | Agent inputs public; private process and signal state held by environment. |
| Events | `EventQueue`, validated `SimulationConfig` | Stable ordering by time/sequence; independently seeded named streams. |
| Stock accounting | `MakerAccount.apply`, `snapshot`, `check_invariants` | Exact tick cash/FIFO; `TradingSession.command/public_snapshot` wraps manual activity. |
| Market making | `MarketMakingLab.advance_to_decision`, `observation`, `decide`, `run` | `environment_factory` admits recorded-event environments; strategies receive public observations. |
| Options | `PricingInputs`, `price`, `price_many`, `greeks`, `implied_volatility`, `monte_carlo_price` | Scalar and array BSM use `_price_kernel`; risk's vector function is a compatibility adapter. IV uses this price/vega. |
| Option accounts | `OptionPortfolio.apply/snapshot/check`; `OptionsSession.command/snapshot/journal` | Per-contract premium/multiplier, exact ledger, real stock hedge venue. |
| Portfolio/risk | `Position`, `Portfolio`, `from_accounts`, covariance validation, `parametric_risk`, `monte_carlo_risk`, `scenario_pnl`, `optimise` | Detached risk inputs; no independent trade P&L ledger. Scenario P&L is explicitly hypothetical. |
| Research | `SimulationAdapter`, `ExperimentSpec`, `SeedPlan`, `execute`, `load_experiment`, `reproduce_run` | Registration before runs; complete rows including failures; private evidence separate from summaries. |
| Tutor | `PublicContext`, `Tutor.observe/study/ask`, local `Progress` | Strict public fact allowlists, deterministic questions, no exchange/RNG mutation. |
| Stat Arb | `MultiMarket.publish`, `ols`, `zscore`, `CausalModel.at`, `StatArbSession.command/state`, `backtest` | Published price prefixes; model vintage precedes action; actual separate stock legs. |
| Browser | `Controller`, `TradingServer`; one `quantlab serve` process | Same lock order for GET/POST financial state. UI formats returned numbers and plots geometry. |
| Replay | Domain journal/replay functions; `ReplayFrames` only for visual capture | Complete reconstruction, comparison, version policies, bounded visual retention. |

The JS audit found display conversions (percent formatting, currency, chart geometry, clocks and frame indices), not matching, Greeks, IV, VaR, covariance, OLS, z-score or P&L implementations. Python tutor worked examples retain elementary arithmetic for explanation; VWAP was a duplicated execution formula and now delegates to the same function. The old options performance demonstration deliberately compares scalar/vector implementations of a fixed Monte Carlo payoff as a **validation oracle**, not live pricing. Tests and finite differences intentionally provide independent checks; they are not competing production authorities.

The numeric BSM implementation was consolidated because the risk vector code had its own expiry approximation and tail path. Backend operations differ (`math.erfc` versus SciPy `ndtr`), so comparisons are tolerance-based and runtime versions remain relevant. The new shared kernel has explicit precision rejection. Covariance/OLS/research statistics now reject overflow before emitting plausible summaries.

## Architecture review

The largest modules are the trading session (~840 lines), tutor questions (~820), Stat Arb session (~690), options session (~675), and tutor service (~605). These concentrate state transitions or lesson content. Splitting their transactions across files simply for size would increase regression risk; no broad rewrite was performed. The focused extractions are execution statistics, numeric boundary handling, strict JSON, replay frame budgeting, shared navigation and public job-path presentation.

Dependencies point from UI/application adapters toward domain code. Risk needs actual option/stock accounts; Stat Arb uses generic stock venues and risk functions. Controller-to-lab imports are deliberately deferred. Optional pre-trade guard callbacks create runtime relationships between risk and venues; the pure pricing/exchange code does not import controllers. Existing imports and every test also run from the non-editable clean installation, exposing reliance on source-only package data or path hacks.

Mixed command DTOs remain: a successful option order returns an execution record (`filled`, `cancelled`, premium); other commands return `ok/message`. The HTTP adapter wraps each as `result/state`. This is documented rather than changing old journal output merely for cosmetic uniformity. Consumers must check the relevant execution fields. A rejected request may be recorded in the journal and advance revision, while financial state remains unchanged.

## RNG map

| Source | Stream derivation | Lifetime / purpose |
|---|---|---|
| Latent shocks | `RandomStreams(seed).create('market.latent')` | One retained generator per environment. |
| Arrivals | `market.noise.arrivals`, `market.liquidity.arrivals`, `market.informed.arrivals` | Distinct exponential arrival streams. |
| Ordinary decisions | `market.noise.decisions`, `market.liquidity.decisions` | Separate from arrivals and latent shocks. |
| Signal error | `market.informed.signals` | Noisy current measurement, never future information. |
| Option stock path | `options.stock.innovations-v1` | Physical GBM observations. |
| Option pricing MC | `options.pricing.terminal-v1` → 128-bit seed → NumPy PCG64 | Independent risk-neutral terminal paths. |
| Risk scenarios | `SeedSequence([seed,9009])` → PCG64; Student radial stream `[seed,9010]` | Independent of live market paths. |
| Stat Arb process | `SeedSequence([seed,1010])` → PCG64 | Named-asset public-price generation and private evidence. |
| Research sessions | SHA-256 canonical root/name/index, then parity-separated development/evaluation addresses | Child seeds unique within design, evaluation access durably recorded. |
| Bootstrap | Experiment-derived labelled child seed → PCG64; complete-session resampling | Never a market generator. |
| Controls | `control.weather`, `control.variant:<id>` | Explicit statistical controls, not execution P&L. |
| Teaching/examples | Fixed recorded seeds; deterministic question permutations | No shared live stream. |
| Server/session tokens | Standard-library `secrets` | Security/source identifiers only, never financial outcomes. |

`RandomStreams.create(name)` returns a generator at its **start**, so clients retain it rather than recreate it each event. Duplicate names intentionally reproduce the same stream; modules use disjoint names. Production research is sequential, not a parallel scheduler. Common random numbers deliberately share exogenous paths across paired variants and verify actual environment fingerprints. Independently changing model regimes is labelled unpaired when those paths differ.

Full versus light capture, repeated public reads, tutor enabled/disabled, analysis-before-step, and cross-lab replay tests preserve intended results. Exact bitwise equality is not a claim across arbitrary Python/NumPy/SciPy/libm/BLAS versions.

## Error and resource contracts

| Failure | User meaning / recovery |
|---|---|
| Stale/invalid option quote, hard position limit | Order rejected or zero/partial fill explicitly reported. Inspect current quote/exposure; the session remains usable. |
| Singular PSD covariance | Valid with a visible warning/eigenfactor when supported; indefinite covariance rejected. Proposed risk covariance is analysed before commit. |
| IV failure | Infeasible inputs raise a clear error; unresolved root returns `converged=false, volatility=null` and diagnostic status. |
| Insufficient or tiny spread history | Signal unavailable, not z=0. Collect more observations or inspect model validity. |
| Pair leg has no liquidity | Actual remainder cancels; inventory already filled remains. Restore liquidity or manually reduce it. |
| Numeric overflow | No estimate returned; input magnitude/precision problem. Not a repaired matrix or fabricated value. |
| Reconciliation/invariant failure | Fail loudly; do not continue that session. Normal browser does not receive traceback; `--debug` emits local traces. |
| Incompatible or corrupted replay | Reject before replacing active UI state. Preserve journal and use the recorded version if supported. |
| Action limit | Desk 5,000; options/risk 3,000 plus permitted end; Stat Arb 4,000 plus permitted end. Ending/export remains possible. |
| Visual replay too large | 64 MB cumulative serialized-frame budget, additional Python overhead. Fail explicitly; verify without capture using Python. No partial/truncated financial evidence. |

Stock/account journals deliberately grow during a bounded session. They are not tick databases. Market events, session horizons, analysis path counts, draw budgets, command sizes and visual replay retention have separate caps. Multiple concurrent clients and hostile resource exhaustion remain outside the local single-user design.

## Future compatibility without new features

Current contract identifiers, units, model configuration, source labels, event/revision times, scenario labels and fit vintages already supply explainability hooks. `LABS` centralises navigation metadata. There is no Phase 12 explanation engine. The generic research adapter, market `environment_factory`, and public multi-asset `publish` boundary accept observed data independently of how it is produced; no historical feed, adapter or Phase 13 functionality has been added.
