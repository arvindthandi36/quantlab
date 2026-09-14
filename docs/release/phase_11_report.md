# Phase 11 — core hardening and release report

**QuantLab 1.0.0 release candidate. Original core feature-complete for review. Phase 12 has not begun.**

## BUILD / HARDENING REPORT

The complete Phases 0–10 system was audited, hardened and validated without adding a financial domain. The principal fixes are:

- One BSM pricing kernel now serves scalar pricing and vector risk repricing; one exact VWAP function serves exchange reports, desk reports and tutor calculations.
- Stock risk positions reject option-style multipliers. Overflowing covariance, variance, regression, spread statistics and research estimates cannot escape as plausible answers. A proposed risk covariance is analysed before replacing usable settings.
- Stat Arb's action limit no longer prevents ending/export, and repeated over-budget requests cannot grow the journal. An order before usable model history now explains the missing input.
- All HTTP financial reads and writes follow the same controller lock. Uploaded JSON rejects duplicate keys, nonfinite values and excessive nesting. Early replay frames cannot export later private evidence. Public save/research paths omit the user's directory.
- Visual replay has a 64 MB serialized-frame budget and fails explicitly rather than retaining arbitrarily large repeated snapshots or truncating evidence.
- `quantlab` and `quantlab serve` launch all labs. Shared navigation, a research entry page, keyboard tabs/skip focus, and shared Risk reset back to manual market making are implemented.
- The complete platform declares its runtime dependencies. The installer was updated after advisory findings. A portable Git source bundle accompanies the clean-install evidence.

No accounting discrepancies or silent critical numerical failures remain known from this audit. That is a bounded engineering finding, not a proof covering all possible inputs or real-market conditions.

## TEST REPORT

**1,346 passed, 0 failed, 0 skipped.** All **1,294 original test IDs remain**; 52 targeted checks were added. Final development run: **74.05 s**. Final genuinely cloned, newly installed environment: **1,346 passed in 97.93 s**. Static checks pass, and all 184 Python files pass the formatter check.

Evidence: [test output](phase_11/test-results.txt), [exact counts](phase_11/test_counts.json), [clean-install verification](phase_11/clean_install.json). The original baseline was 1,294 passed in 67.54 s. The different total suite times include changed coverage and environment startup; they are not a performance-regression comparison.

New coverage targets actual bugs and cross-module disagreements: exact unit scaling, full financial workflows, overflow, missing history, exhausted action limits, PSD quadratic identities, sparse tails, causal future poisoning, public snapshots, concurrent mutations/reads, strict uploads and replay memory limits. Existing generated matching/manual/Stat Arb sequences remain. Statistical tests use fixed seeds; no thresholds were relaxed to obtain a pass.

The slowest existing tests are Stat Arb pair mining/sweeps and complete generated execution sequences. Many HTTP fixtures each spend ~0.5 s shutting down their server. Some domains intentionally repeat account/replay assertions at different integration boundaries; these protect distinct failure modes. No tests were deleted merely because they appeared similar. Tests that independently calculate expected identities or finite differences remain deliberate validation oracles.

## TESTS BY DOMAIN

Each collected instance is assigned once by its owning filename; some integration cases span more than one domain.

| Domain | Tests |
|---|---:|
| Matching, domain and conservation | 96 |
| Market, events and replay | 100 |
| Information and adverse selection | 52 |
| Market making and accounting | 124 |
| Manual trading | 113 |
| Research and statistical inference | 114 |
| Tutor | 148 |
| Options and hedging | 151 |
| Risk and portfolio | 199 |
| Stat Arb | 197 |
| Cross-core release checks | 52 |
| **Total** | **1,346** |

By test-directory type: **753 unit, 578 integration, 15 statistical**. Property-based tests are included in their owning directory, not counted as an additional category or as one test per generated example.

## ACCOUNTING AUDIT

Matching retains the per-execution and operation-wide identity: buyer reduction = seller reduction = recorded trade quantity. Cancellations remove remainder without creating fills. Exact rational ledgers independently reconcile cash, signed inventory, FIFO lots, fees and marked P&L; discrepancies raise rather than repair.

The cross-lab workflows independently check cash + market value = equity and realised gross + unrealised + financing − fees = P&L, plus aggregate position Greeks. Option premium is a cash flow multiplied by contract size, not an immediate loss. Stock hedge proceeds are balanced by a short liability. Closing uses real executions. Settlement closes the option exactly once and does not erase a stock hedge. Stat Arb attribution reconciles actual separate-leg holdings and does not add the temporary-leg subset twice.

The consolidated report consumes actual ledgers; it does not create another P&L account. Public reports use floats after exact accounting, so identity comparisons allow £1e−7 reporting tolerance. See [central conventions](../conventions.md) and [workflow evidence](phase_11/cross_lab_demo.json).

## UNITS AUDIT

The [formal unit table](../conventions.md#units-and-scaling) covers GBP/ticks, per-unit/per-contract prices, multipliers, annual decimals and percentage points, theta years/days, rates/basis points, microseconds/seconds/ACT365 years, simple/log returns, weights and covariance.

The concrete ambiguity found was a stock `Position` accepting multiplier 100 while stock delta still used quantity alone. Stock multiplier is now required to be one. Options retain explicit multipliers. Numeric limits already validate annual decimal volatility and whole quantities. No annual-to-daily conversion is silently shared across the options, risk and Stat Arb clocks.

## SIGN-CONVENTION AUDIT

The [sign table](../conventions.md#sign-reference) defines long/short, buy/sell cash flows, gross/net P&L, own-side/provider markout, Greeks, positive losses, VaR/ES, spread direction and hypothetical stress P&L. Stock maker realised P&L already includes fees; the risk bridge converts it to a gross field before subtracting consolidated fees once.

Positive provider markout favours the provider. A resting seller has sign −1: if the later reference rises above its sale price, its markout is negative. A long spread buys Y and sells approximately beta units of X per Y; a short spread reverses that. A positive VaR is a loss threshold; negative VaR is permitted when the relevant model quantile is a gain.

## SOURCE-OF-TRUTH AUDIT

Python remains authoritative for matching, accounts, pricing, Greeks, IV, risk, covariance, OLS, z-scores and VWAP. The JS audit found formatting, chart geometry, percentages, clocks and frame selection, not duplicate financial engines. Scalar and vector BSM now share one algorithm; the risk vector entry point delegates to it. Tutor VWAP questions use the exact execution helper.

Tests, finite differences and an explicitly labelled fixed-payoff performance demonstration intentionally retain independent validation calculations. They are not live financial authorities. Elementary arithmetic in teaching explanations is derived from public facts. Full mapping: [architecture and APIs](architecture.md#source-of-truth-and-main-interfaces).

## RNG / REPRODUCIBILITY AUDIT

The [RNG map](architecture.md#rng-map) documents every production stream: latent shocks, each arrival/decision family, signal error, option stock observations, risk-neutral pricing MC, portfolio scenarios and Student radial shocks, Stat Arb, bootstrap, controls and examples. Security tokens use separate system randomness and never determine financial outcomes.

Named generators are retained across events. Research child seeds use deterministic root/namespace/index addressing with disjoint development/evaluation parity; paired paths are checked by actual exogenous fingerprints. Research execution is sequential. Logging modes, repeated public reads, tutor enabled/disabled and risk inspection do not perturb live market draws. All four cross-lab workflows verify replay. Reproducibility is conditional on the recorded rules/runtime, not proof that those rules model reality.

## INFORMATION-LEAKAGE AUDIT

Public trading/option/risk/Stat Arb inputs, tutor allowlists, ordinary snapshots and replay frames exclude latent value, private measurements, innovations, process configuration and future observations. Current hypothetical risk scenarios are labelled assumptions, not future observations. Observed option chains contain current quotes. Stat Arb fits and normalisation use recorded past windows; tests poison later data with NaNs and verify unchanged past signals. Existing tests mutate future prices across all three estimation schedules and check complete trading decisions/fills.

Market seeds/private observer journals require an ended session. The stock replay export gate was strengthened to inspect the displayed frame, matching the other labs. Tutor rewind removes contexts/questions from later frames. Research summaries are made available after completed registered studies and keep failed/tried candidates visible; evaluation reuse remains recorded. Counterparty queue aliases do not disclose informed/noise identity in ordinary trading views.

This is an application information boundary, not a sandbox against malicious Python code running in the same interpreter. A complete uploaded/ended journal intentionally contains observer evidence; its owner already possesses that information.

## NUMERICAL EDGE-CASE AUDIT

Tests exercise near-zero time, extreme strike/rates/volatility, zero volatility, parity, bounds, low vega, impossible IV and failed brackets/iteration budgets. Subnormal time × volatility below representable precision raises explicitly. The risk vector path no longer has a separate “near-zero means expired” pricing rule.

Covariance tests cover PSD, singular/near-singular matrices, extreme correlations, tiny variance and scaling. Averaging a large finite matrix no longer overflows by adding it to itself first. Overflow in quadratic variance, OLS summaries, z normalisation or research uncertainty fails with no estimate. Sparse-loss tails preserve ES ≥ VaR under fractional-tail weighting. Optimisation tests retain infeasible and boundary/singular cases; missing/regression-degenerate observations are rejected or explicitly unavailable.

The audit does not promise reliable estimates for arbitrarily large dynamic ranges or numerically invisible option tails. Boundary nulls/warnings and local roundoff tolerances are documented, not disguised as precise values.

## CROSS-LAB INTEGRATION DEMOS

Run `python -m tests.core_workflows` from an installed checkout. The full [event-by-event JSON](phase_11/cross_lab_demo.json) contains the reconciliations.

**A — manual stock → option → stock hedge → risk/stress → close.** Starting capital is £10,000.

| Event | Cash | Marked equity | Net P&L |
|---|---:|---:|---:|
| Buy 3 manual-desk units | £9,699.9570 | £9,999.9720 | −£0.0280 |
| Buy one call, multiplier 100 | £9,469.6919 | £9,998.4220 | −£1.5781 |
| Execute short stock delta hedge | £14,569.1309 | £9,997.8610 | −£2.1391 |
| Inspect hypothetical stress | unchanged | unchanged | unchanged |
| Observe one actual model day | £14,569.1309 | £9,994.2707 | −£5.7293 |
| Close option at bid | £14,803.4156 | £9,992.7206 | −£7.2794 |
| Close both stock positions through their own books | £9,992.1116 | £9,992.1116 | **−£7.8884** |

All positions are then flat, fees total £0.2080, and replay reconstructs the same result. Cash rises during the short hedge because shares are sold; the short position is a liability. Only cash **plus** positions represents equity.

**B — maker → research → tutor.** A seeded maker session produces identical metrics/fingerprints with full or light logging. A registered four-run batch completes and its verified outcome rows create a public standard-error tutor context. No learner answer is fabricated.

**C — incomplete pair → consolidated risk/stress → close.** X liquidity is withdrawn. The long-Y leg fills and X remains zero. Consolidated equity is £19,999.94 from £20,000 explicit combined capital; the actual remaining exposure enters risk/stress. Restoring liquidity and closing through real books leaves zero inventory and net −£0.12 from costs. Replay agrees. No artificial leg-risk loss was inserted.

**D — option → delta hedge → IV/spot shock → VaR/ES/full repricing.** In A's actual held portfolio, a hypothetical −5% stock move plus +0.10 IV change gives full stress P&L **+£153.4446**, while its ordinary fixed-IV Monte Carlo VaR/ES are **£7.0893 / £8.2364**. These answer different questions. The stress does not alter cash or realised P&L; higher IV and convexity can benefit a hedged long option. No result is forced to be a loss.

## ARCHITECTURE REVIEW

The [review](architecture.md) identifies large session/tutor modules, deferred controller imports, shared risk guard relationships and mixed legacy command DTOs. Stable state transitions were not rewritten for style. Focused extractions reduce genuinely duplicated formulas and boundary handling.

The reusable market factory, generic research adapter and `MultiMarket.publish` boundary do not require that observations originate from a particular synthetic generator. Existing event/fit/source/unit metadata supplies small future explainability hooks. There is no new explanation engine, historical feed or additional financial domain.

## CLEAN-INSTALL DEMO

The original worktree had no commits or remote history. A **temporary local Git release repository** was therefore created from an explicit source manifest and genuinely cloned with `git clone --no-local`. The original Git index was untouched. A new venv installed upgraded pip and declared `.[dev]` with isolated/no-cache pip, using no developer path overrides. Installation is **non-editable**; an assertion verifies imports come from site-packages. `pip check` passes.

The final clone runs **1,346 tests successfully**, reports QuantLab 1.0.0, and launches one server. Trading/market making, research, learning, options, risk and Stat Arb were opened; real simulated orders, registered research, tutoring and JSON replay were exercised. Source/tests/package metadata in the workspace were hash-compared with the tested clone. Evidence: [clean-install record](phase_11/clean_install.json).

The portable `quantlab-core-1.0.0.bundle` can be cloned without inventing a remote URL. Follow the root README's venv/install/test/launch commands. Validation was on Python 3.14.0/macOS; other platform/interpreter combinations need their own gate.

## DEPENDENCY AUDIT

Runtime dependencies are NumPy, SciPy and Matplotlib; pytest, Hypothesis and Ruff are development tools. Transitives and licences are inventoried. The full platform now declares its numerical dependencies instead of requiring an undocumented extra at launch. The old `research` extra remains compatible.

The initial scan found 12 pip-25.2 advisory rows (six distinct IDs). Pip was upgraded to 26.2.1; the final scan reports **no known vulnerabilities**. This is a dated advisory-database finding, not an absence guarantee. See [dependency/security review](security_dependencies.md), [inventory](phase_11/dependencies.json), and [final scan](phase_11/dependency_audit_final.json). No open-source licence was selected on the owner's behalf.

## REPOSITORY HYGIENE REPORT

Environments/caches/builds, `runs/` data and credential-file patterns are ignored. High-confidence credential scans found no private keys/API tokens; values were never printed. Four historical text/profile files had local paths made portable. Current root documentation replaces outdated instructions; historical phase reports are labelled as such and retain old test counts/financial evidence honestly.

The archive includes historical reproducibility evidence, so its source tree is larger than a minimal runtime wheel. Private learning progress and developer environments are excluded from the release snapshot. The original repository remains uncommitted; the portable bundle supplies a real, independently clonable release snapshot without changing that history.

## PERFORMANCE BENCHMARKS

Sequential local measurements with fixed seeds and explicit workloads; not isolated-machine or production-throughput guarantees. Full details and profiles: [benchmarks](phase_11/benchmarks.json).

| Workload | Time |
|---|---:|
| 20,000 matching submissions; 10,000 actual trades, conservation enabled | 0.090 s |
| 300 simulated seconds, 5,347 market events | 0.733 s |
| **1,000 independent maker research runs**, one variant, 2 s simulated per run, registration/output/analysis | 2.397 s |
| **1,000,000 option MC paths**, estimate/uncertainty | 0.162 s |
| **100,000 risk scenarios**, 11 option positions with full revaluation | 0.060 s |
| 1,920 rolling fits over 2,000 published Stat Arb observations | 0.947 s |
| 751-command manual soak, including journal and replay checks | 16.714 s |
| 252-step option/hedge soak, including replay and final serialization measurement | 12.707 s |

The maker CPU profile is dominated by repeated exact accounting checks and rational arithmetic. These were retained for correctness. No broad speed optimisation is claimed. The BSM source-consolidation comparison over 100,000 varying spots measured median **4.747 ms before / 5.469 ms after**; the extra validation costs work and these small local samples are not a statistically established regression estimate.

Twelve sequential reads per installed endpoint gave median/p95 milliseconds: stock **0.62/9.82**, options **4.64/5.15**, risk **6.98/10.04**, Stat Arb **2.84/3.39**, learning **1.30/1.51**. These include transfer and first-request overhead, not browser rendering or large replay-upload latency. [HTTP measurements](phase_11/http_latency.json).

## MEMORY / SOAK TEST REPORT

For the same 30-second maker workload, full versus light capture had identical outcomes. Traced retained memory was **430,566 / 15,823 bytes**; peaks **471,552 / 79,624 bytes**. Native allocations outside tracemalloc are not fully measured. Timing was essentially equal in this small sample; the benefit is retained evidence size, not a claimed speedup.

The long market journal was ~9.35 MB. The manual soak produced 1,537 evidence records, a ~3.21 MB journal and ~545 KB final public state; invariants/replay held. The option soak ran all 252 steps with 195 hedge decisions/fills, ~2.34 MB journal and ~537 KB final public state. State grew with retained history at four measured checkpoints; the horizon caps bound it. Final snapshot serialization peaked at ~1.90 MB traced allocation; this is not the whole process's peak RSS.

Repeated rolling fits and the 1,000-run lightweight research batch completed without numerical instability or missing requested runs. Explicit action/horizon/path/draw limits and the new visual-frame budget prevent obvious unlimited retention. None of these profitability outcomes is treated as strategy validation.

## BROWSER / ACCESSIBILITY REPORT

Every main route was checked at **1440×1000** and **390×844**. No document-wide horizontal overflow was found; dense tables remain internally scrollable. Main form controls had labels. The practical pass checked headings, semantic buttons/forms/tables, chart descriptions, visible focus, empty/error states, disabled controls, refresh, research running/completed states and local replay.

Verified interactions include option execution and −51 stock hedge; 32 seeded paths across four registered research variants; research tutoring; causal Stat Arb fit and separate legs; manual quotes/cancellation/buy; shared Risk reset to maker mode; uploaded replay and first/ended frames; keyboard End/arrow navigation and skip link focusing MAIN. No console errors were observed after fresh navigation. Test learning activity was isolated; no Arvind answers were entered. Evidence: [browser checks](phase_11/browser_checks.json).

This is not screen-reader testing, formal WCAG certification or exhaustive contrast/device coverage. Existing older header links remain alongside the consistent platform navigation; a full redesign belongs outside Phase 11.

## REPLAY / VERSIONING POLICY

[The policy](replay_policy.md) distinguishes recorded-event verification from seeded regeneration. Older market/maker/stock instructions may be verified only by reconstructing and comparing all recorded transitions. Exact seeded stock regeneration requires package/Python versions; options, risk and Stat Arb fail incompatible runtime metadata explicitly. Research reads verify saved evidence, while reproduction also checks actual outcomes/fingerprints.

Schemas, seeds, configurations, instruments/scenarios and action histories remain recorded. A checksum is not authentication. No historical 0.9.0 option/risk/Stat Arb evidence has been relabelled as 1.0.0. No silent financial-rule migration is provided.

## MODEL-ASSUMPTIONS REGISTER

[ASSUMPTIONS.md](../../ASSUMPTIONS.md) is now authoritative. Every major model records **what it assumes, why it is used, when it fails, and what QuantLab does not claim**. The old cumulative register is archived. The register covers execution, latent/ordinary/informed flow, making, marks/accounts, BSM/dealer quotes/hedging/IV, covariance/tails/stress/allocation, Stat Arb, combined labs, research and tutoring.

## MODEL-RISK MAP

The [dependency diagram](model_risk.md) shows how volatility assumptions propagate through prices, Greeks, hedges and VaR; dependence assumptions through covariance, tails and allocation; and synthetic relationships through causal fitting, orders and research. Exact accounts can reconcile perfectly while the model supplying their marks or forecast remains wrong.

## SECURITY / PRIVACY REVIEW

Default application behaviour is local with no external service/API key. The server has loopback Host/Origin/token checks and a self-only content policy. Uploads are data, not executable code. Learning remains local; private synthetic journals are explicit ended-session exports. Public path minimisation and replay frame gating were strengthened.

A hostile local process, deliberate resource exhaustion, shared-process introspection, public tunnelling, multi-process data-directory races and untrusted internet clients are not secured by this design. `--debug` traces may include local details. Review: [security and dependencies](security_dependencies.md).

## FILES CHANGED

- Package/launch: `pyproject.toml`, `requirements-dev.lock`, `.gitignore`, `quantlab/__init__.py`, new `quantlab/__main__.py`.
- Shared correctness boundaries: new `execution.py`, `jsonio.py`, `numerics.py`, `replay_support.py`; `orderbook/models.py`, `trading/session.py`, `trading/replay.py`, `tutor/questions.py`, `research/statistics.py`.
- Pricing/risk: `options/pricing.py`, `options/session.py`, `options/application.py`; `risk/monte_carlo.py`, `covariance.py`, `metrics.py`, `optimisation.py`, `portfolio.py`, `session.py`, `application.py`.
- Stat Arb: `statarb/statistics.py`, `session.py`, `application.py`.
- Browser: `trading/server.py`, new `trading/navigation.py` and `trading/public.py`; new `static/navigation.js`, `static/research.html`; `static/style.css`, `static/risk.html`, `static/risk.js`.
- Verification: `tests/core_workflows.py`, `tests/unit/test_core_hardening.py`, `tests/integration/test_core_acceptance.py`, `tests/integration/test_core_http.py`; `scripts/core_benchmark.py`, `scripts/clean_install.py`.
- Documentation: root README/ASSUMPTIONS/ROADMAP/CHANGELOG; central conventions; release architecture/replay/security/model-risk documents and evidence; archived assumptions; historical banners and four path-only report/profile cleanups.

Source/tests/package metadata match the final tested clone. Historical numerical evidence was not re-run under a new label or silently changed.

## REMAINING LIMITATIONS

Only Python 3.14.0/macOS received the clean-install gate. Exact replay needs the documented runtime. Journals grow within session caps; large visual replay may require non-capturing verification. Some session/tutor modules remain large, and command DTOs retain documented historical differences.

The model remains deliberately synthetic: no calibration, realistic borrowing/margin/impact, genuine multi-venue execution, globally calibrated cross-lab covariance, American options or formal cointegration inference. QuantLab has no owner-selected open-source licence or remote release publication. The portable Git bundle is a private release candidate.

## FINAL CORE RED TEAM

A correctly matched and reconciled loss forecast can still be a poor forecast. Fixed IV, stable dependence, IID sessions and synthetic relationships are substantial assumptions; changing them can overwhelm sampling confidence intervals. Reusing evaluation data or selecting among many variants weakens apparent out-of-sample evidence even when the seed registry is correct.

Exact ledgers do not make marks executable. Delta neutrality does not remove gamma/vega or separate-leg exposure. Missing tail observations cannot be replaced by reassuring estimates. Adverse markout is descriptive, not automatic causal proof. Finite-size toy liquidity and no real borrow/funding/latency remain major realism limits.

Determinism helps find bugs; it does not establish alpha, safety or truth. The release is suitable for inspectable local teaching and synthetic research within its stated limits. It is not approved for real-money trading or regulatory risk reporting. The original core is complete for Arvind's review; work stops here.

## 3-QUESTION ARVIND CHECK

1. Selling stock for a hedge increases cash. Why is that increase not automatically profit?
2. If only tomorrow's prices change, which parts of today's fitted signal and order should remain unchanged, and why?
3. If accounting reconciles and replay is exact, what important uncertainty still remains in the portfolio's VaR estimate?
