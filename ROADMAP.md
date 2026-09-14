# QuantLab roadmap

Owner: **Arvind Thandi**. Updated: 13 September 2026.

Build order: correctness → explainability → quantitative depth → testing → realism
→ visual polish. Completion refers to implemented and checked software, not to
demonstrated learning mastery.

| Phase | Deliverable | Status |
| --- | --- | --- |
| 0 — Engineering foundation | Installable Python package, isolated environment, type hints, validated domain types, named RNG streams, pytest/Hypothesis/Ruff, documentation | Complete |
| 1 — Matching engine | Price-time matching, partial fills, cancellation, always-on two-sided conservation, aggregated depth with optional FIFO expansion | Reviewed sufficiently to proceed; repetition requested |
| 2 — Event-driven market | Integer clock/queue, Gaussian latent walk, independent noise/liquidity arrivals, tape, seeded runs, verified JSON replay and explained timeline | Reviewed sufficiently to proceed |
| 3 — Informed flow | Explicit noisy signals, information boundaries, informed agents, adverse selection and 1/5/20-event markouts | Reviewed sufficiently to proceed |
| 4 — Market Making Lab | Manual/fixed/inventory-aware quotes, exact FIFO account, fees, inventory limits, reconciled attribution, diagnostics, teaching and small paired comparison | Reviewed sufficiently to proceed |
| 5 — Monte Carlo research | Reusable batch/distributional analysis, confidence intervals, bootstrap, paired comparisons, sweeps, seed discipline and hypothesis-first research | Implemented; verification and Arvind's review recorded in the Phase 5 report |
| 6 — Interactive application | Real manual market/limit trading, FIFO depth, accounts, charts, scenarios, time controls and verified action replay | Reviewed sufficiently to proceed |
| 7 — Quant Tutor | Integrated lessons, math-in-the-loop exercises, evidence-based mastery, spaced repetition, interview mode | Reviewed sufficiently to proceed |
| 8 — Options Lab | Black–Scholes, parity, Greeks verified numerically, robust IV solver and discrete delta hedging with costs | Approved to proceed |
| 9 — Risk and portfolio lab | Shared accounts, covariance/PSD, VaR/ES, option stress, limits, optimisation and tutor | Approved |
| 10 — Statistical arbitrage | Paired assets, causal regression/residuals and broken relationships | Approved |
| 11 — Research-grade refinement | Profiling, regression gates, forensic replay and release evidence | Core 1.0.0 approved |
| 12 — Explainability | Public traces, concept registry, isolated what-if and Tutor | Approved |
| 13 — Market environments | Synthetic, historical paper replay, known/hidden scenarios | Approved |
| 14 — Guided demonstrations | Annotated educational replay | Approved |
| 15 — Product release | Navigation, showcase, installation, documentation and feature freeze | Final quality gate |

## Phase 1 review gate

- [x] Show architecture before implementation.
- [x] Implement actual order matching; no decorative/generated price series.
- [x] Protect matching and quantity invariants with examples and generated sequences.
- [x] Provide a reproducible demonstration with explicit unmet liquidity.
- [x] Document financial conventions, storage complexity and limitations.
- [x] Record the starting learning level without awarding mastery.
- [ ] Revisit the five Phase 1 questions through repetition; answers are not claimed.
- [x] Arvind says he understands enough to proceed, while requesting repetition.
- [x] Arvind authorises beginning Phase 2.

## Phase 2 review gate

- [x] Implement a deliberately small autonomous market without informed agents.
- [x] Keep latent value out of both traders' information sets.
- [x] Preserve and strengthen the original matching rules and conservation tests.
- [x] Add aggregate price-level display while retaining FIFO internally.
- [x] Save/replay a short seeded session and verify all matching consequences.
- [x] Run all tests: 184 passed, including 5 statistical cases; lint/format checks pass.
- [x] Explain the actual 12-event seed-42 demo and new mathematics.
- [x] Arvind reviews Phase 2 as sufficient to proceed; formal questions remain repetition targets.
- [x] Arvind explicitly authorises Phase 3 only.

## Phase 3 review gate

- [x] Define observations, signal generation/accuracy, estimate, costs and imperfect information before implementation.
- [x] Add informed buy/sell/hold decisions using current noisy signals and executable quotes.
- [x] Preserve the matching engine and verify all conservation tests.
- [x] Add provider-signed midpoint/latent markouts with pending/missing states and exact event maturity.
- [x] Separate public types/output from observer diagnostics, seeds and private-event timing.
- [x] Verify causal prefixes, signal decisions and deterministic replay, including old journals.
- [x] Run the full suite: 248 passed, including 10 statistical cases; lint/format checks pass.
- [x] Explain the actual seed-42 demo, controlled mirrored examples and first-principles mathematics.
- [x] Arvind reviews Phase 3 as sufficient to proceed; question answers remain repetition targets.
- [x] Arvind explicitly authorises Phase 4 only.

## Phase 4 review gate

- [x] Document public reference, FIFO accounting, fee treatment, attribution and limits before implementation.
- [x] Add fixed and inventory-aware public-input strategies, passive exact-price quotes and soft/hard controls.
- [x] Cancel/replace quotes safely; reserve capacity for all resting units and detect stale orders.
- [x] Reconcile cash/inventory, realised/unrealised P&L and additive path attribution without markout double counting.
- [x] Add public manual observations, editable distances/sizes and delayed teaching explanations with hint/retry.
- [x] Add inventory, drawdown, spread, fill-rate and public-event markout diagnostics; private counterparty labels remain debug-only.
- [x] Replay complete quote, exchange and account histories without RNG draws; preserve old simulations/journals.
- [x] Run all tests: 372 passed; lint/format/dependency checks pass.
- [x] Capture seed-42 demo and retain all 20 predeclared paired strategy comparisons, including unfavourable results.
- [x] Arvind reviews Phase 4 as sufficient to proceed; formal question answers remain repetition targets.
- [x] Arvind explicitly authorises Phase 5 only.

## Phase 5 review gate

- [x] Register hypotheses, counts, configurations, inference conventions and seed pools before experiments.
- [x] Add an asset-independent adapter protocol and deterministic session seed allocation.
- [x] Verify common exogenous weather while allowing endogenous market consequences to differ.
- [x] Add full distributions, paired differences, t intervals/tests, bootstrap, tails and correlations.
- [x] Keep losing/no-fill/failed sessions visible; incomplete experiments cannot infer from survivors.
- [x] Add reusable one-dimensional sweeps, evaluation-access warnings and selection-bias teaching.
- [x] Profile full/lightweight modes and preserve accounting/conservation in both.
- [x] Run the 1,600-pair development study, five-value sweep and 1,000 fresh evaluation pairs.
- [x] Connect extreme-run addresses to full regeneration and verified event journals.
- [x] Run the full suite: 486 passed, preserving all 372 prior cases; lint/format/dependency checks pass.
- [x] Arvind reviews Phase 5 as sufficient to proceed; learning checks remain repetition targets.
- [x] Arvind explicitly authorises Phase 6 only.

## Planned modelling decisions

Phase 2 uses a zero-drift Gaussian latent walk at fixed intervals, exponential
interarrival times on an integer-microsecond clock and scheduling-order ties.
These baseline choices and their limitations are documented in
[Phase 2 mathematics](docs/maths/phase_02_market.md). Phase 3's
[information contract](docs/maths/phase_03_information.md) defines who observes what,
when and with what signal noise. Phase 4's [accounting contract](docs/maths/phase_04_accounting.md)
defines exact FIFO P&L, fees, public marking, resting capacity and path attribution.
Phase 5's [research contract](docs/architecture/phase_05_design.md) defines hypotheses,
seed pools, sample sizes, uncertainty estimates and coverage conventions. Its
generic engine supports later directional/options/portfolio research adapters;
market making is the first trading application, not the project's permanent scope.

Phase 6 remains the proper interactive trading application: manual BUY/SELL,
market/limit orders, user-selected size/price, cash/positions/realised and unrealised
P&L, live book/tape/open orders/cancels, execution price, partial fills, VWAP and
basic risk. Later labs should plug into the same underlying market infrastructure.
These Phase 6 controls are implemented through the existing exchange. Phase 8 option
trades use finite dealer quotes; their stock hedges use the same Phase 1 / Phase 6
execution and accounting. Phases 9–10 were subsequently implemented and approved.

Regimes must alter parameters, not labels. Develop and validate normal liquid,
high-volatility, low-liquidity, informed-buying, informed-selling, trending,
mean-reverting, news-shock, widening-spread and temporary-dislocation scenarios
across Phases 2–6. Hidden-regime views must exclude latent information.

Reproducibility metadata, statistical validation, learning notes and honest
limitations accompany each relevant phase; they are not deferred cleanup tasks.

## Deferred advanced ideas

Hawkes arrivals, explicit queue/latency effects, Almgren–Chriss execution,
volatility surfaces, local/stochastic volatility, Heston, PCA, Kalman filtering,
hierarchical Bayesian models, regime detection, reinforcement learning, execution
algorithms, multi-asset books and market-impact models require a clear educational
or research purpose and reliable earlier foundations. None is currently implemented.


## Phase 6 review gate

- [x] Document account endowments, risk reservations, public time and information boundaries.
- [x] Connect local browser buy/sell and market/limit orders to the Phase 1 engine.
- [x] Preserve FIFO and conservation; show real partial fills, cumulative VWAP and cancellations.
- [x] Separate manual and automated accounts; support longs, shorts, FIFO P&L and fees.
- [x] Add pause/resume/step controls, public charts and five reusable scenario configurations.
- [x] Add Beginner/Quant views, an optional checkpoint and completed-session decision review.
- [x] Save manual actions and verify both recorded-event replay and seed regeneration.
- [x] Exercise a complete browser trading session, including partial passive fills and short covering.
- [x] Arvind explicitly approves Phase 6 as sufficient to proceed; unanswered questions remain repetition targets.
- [x] Arvind explicitly authorises Phase 7 only.


## Phase 7 review gate

- [x] Define information boundaries and the teaching/scoring contract before implementation.
- [x] Connect actual Phase 4 observations, Phase 5 results and Phase 6 manual events.
- [x] Add local hints, structured answers, transparent evidence, misconceptions and spaced review.
- [x] Add a collapsible/disabled panel, learning dashboard, prerequisites and research view.
- [x] Separate live inputs, public post-session review and explicitly revealed observer information.
- [x] Add interview/project defence, persistence, reset and readable exports.
- [x] Verify identical market journals with/without tutoring and deterministic replay.
- [x] Preserve all 599 existing tests; full suite 747 passed.
- [x] Run a separate deterministic teaching demo and browser acceptance flow.
- [x] Arvind approves Phase 7 as sufficient to proceed; question answers are not assumed.
- [x] Arvind explicitly authorises Phase 8 only.

## Phase 8 review gate

- [x] Define contracts, time, units, model/execution separation and information boundaries.
- [x] Price European calls/puts, parity and five Greeks; independently verify finite differences.
- [x] Add diagnosed safeguarded Newton/bisection IV and seeded Monte Carlo uncertainty.
- [x] Trade finite synthetic option quotes; reconcile exact premium, FIFO lots and settlement.
- [x] Execute manual and automatic stock hedges through Phase 6 and Phase 1.
- [x] Show chains, positions, Greeks, shocks, curves, reports and public verified replay.
- [x] Connect actual derivatives facts to the tutor without changing market randomness.
- [x] Run 1,000-pair frequency and volatility studies and reproduce extreme sessions.
- [x] Preserve every original test; final counts and browser evidence are in the Phase 8 report.
- [x] Arvind approved Phase 8 as sufficient to proceed; mastery is not inferred.
- [x] Explicit authorisation for Phase 9 was received.


## Phase 9 review gate

- [x] Preserve all 898 prior tests and add independent risk, execution, replay and privacy checks.
- [x] Reuse actual Phase 6 and Phase 8 ledgers and transaction paths.
- [x] Define losses, empirical quantile/tail mass, covariance units and horizon conventions.
- [x] Demonstrate delta-neutral but positive-vega exposure and explicit approximation residuals.
- [x] Run four registered evaluation studies and retain unsuccessful model assumptions visibly.
- [x] Profile options-heavy revaluation; validate public risk contexts and replay.
- [x] Arvind approves Phase 9 as sufficient to proceed; no quiz mastery is inferred.
- [x] Explicit authorisation for Phase 10 only.


## Phase 10 review gate

- [x] Generic named-asset markets, covariance/factor shocks and controlled residual regimes.
- [x] Stable OLS, causal model vintages, residuals, z-scores and limited AR diagnostics.
- [x] Manual/systematic actual FIFO pairs execution, partial fills and delayed leg risk.
- [x] Exact-ledger attribution, explicit costs, limits, capital, positions and risk linkage.
- [x] Phase 5 registered train/test and walk-forward studies, disclosed parameter search,
  pair-mining selection and evaluation-access registry; losing/failed outcomes retained.
- [x] Public-context tutoring, deterministic replay and dedicated future-mutation tests.
- [x] First-principles lessons, browser acceptance checks and measured profiles.
- [x] Arvind approved Phase 10; quiz mastery is not inferred.
- [x] Explicit authorisation for Phase 11 only.

Optional later research: formal ADF/cointegration inference with suitable critical values;
PCA; realistic borrowing/funding, market impact and cross-asset latency. These are not
implemented or implied by the present results.


## Phase 11 core release gate

- [x] Accounting, units, signs, numerical boundaries, public information and RNG audited.
- [x] Shared calculations, resource limits, concurrent reads and errors hardened.
- [x] Original tests preserved; new system workflows and adversarial regressions added.
- [x] Clean Git snapshot clone, isolated non-editable installation and full suite validated.
- [x] One application, consistent navigation, browser and keyboard/mobile checks.
- [x] Benchmarks, extended sessions, dependency advisory audit and assumptions register.
- [x] Arvind approved QuantLab 1.0.0 core and authorised Phase 12 only.

## Phase 12 explanation and learning gate

- [x] Preserve the original 1,346 tests and frozen financial implementations.
- [x] Trace actual VWAP, accounting, Greeks, risk, z-scores, quotes and public markouts.
- [x] Add a central 70-concept registry, four depths, search and six connection maps.
- [x] Add five bounded, isolated what-if interfaces over approved core APIs.
- [x] Explain changed public inputs without invented causal percentages.
- [x] Verify replay-point, live, post-session and explicit observer boundaries.
- [x] Integrate public-context quizzes without awarding mastery for reading.
- [x] Document architecture, assumptions, reproducible examples and measured performance.
- [x] Arvind approved Phase 12; approval does not imply quiz mastery.

## Phase 13 market environments

- [x] Preserve the 1,507 existing tests and approved financial workflow fingerprints.
- [x] One selector/contract for Synthetic, Historical and Scenario environments.
- [x] Strict local OHLCV import, provenance, next-close paper execution and causal chart/risk/signals.
- [x] Adversarial mutation of all future observations; public Explain/Tutor and isolated hypotheses.
- [x] Twelve genuine scenario presets, hidden-mode boundaries, explicit reveal and independent objectives.
- [x] Dataset-verified replay, causal paired historical research and labelled scenario comparisons.
- [x] Browser/mobile checks, measured profiles, limitations and reproducible evidence.
- [x] Arvind approved Phase 13; approval is not a mastery grade.

## Phase 14 guided demonstrations and annotated replay

- [x] Preserve all 1,732 prior tests, financial sources and representative Phase 13 fingerprints.
- [x] Add 58 catalogue topics and eight reproducible genuine-engine flagships.
- [x] Add four depths, prospective questions, isolated activity and existing tutor grading.
- [x] Teach saved verified sessions with bounded moment selection and strict public replay points.
- [x] Distinguish user process reflection from realised outcome; explicit hindsight only.
- [x] Reuse Phase 12 concepts/Explain; retain Phase 13 source and hidden-state boundaries.
- [x] Add recording layout, named captures, Markdown scripts and a demo path audit.
- [x] Test browser/mobile workflows, performance and all existing regressions.
- [x] Arvind approves Phase 14.

Phase 14 approved. Phase 15 release preparation is recorded below; external videos remain planned.

Later optional adapters: genuinely observed quotes/trades/depth; controlled corporate-action and
currency handling; historical option chains; a separate live-paper extension with explicit approval.
No live broker execution is implemented.


## Final product release · Phase 15

Phase 14 is approved. Phase 15 completed product 1.1.0: common navigation, Home and system pages,
real showcase captures, reviewer documentation, MIT licensing, clean installation and feature freeze.
The 1,910-test baseline and financial replay core remain preserved. Final results are in
[the release report](docs/release/PHASE15_REPORT.md). No further implementation phase is begun.
Optional research directions are non-commitments in [FEATURE_FREEZE.md](FEATURE_FREEZE.md).

Final gate: 1,933 tests pass in both environments; product 1.1.0 is feature frozen.
