# Phase 9 — Risk & Portfolio Lab

> Historical phase record. Current core conventions and release status are in the root README, ASSUMPTIONS and Phase 11 release report. Test counts and runtime labels below describe this phase.


Completed 12 September 2026. Phase 8 was approved; only Phase 9 was implemented. Phase 10 is not started.

## BUILD REPORT

QuantLab now measures portfolio risk from the existing Phase 6 stock and Phase 8 stock/options ledgers, plus a second controlled stock venue. It supports long/short positions, multiple calls and puts, cash, actual equity/P&L, exposure and concentration, covariance/correlation, variance decomposition, three VaR methods, exact-tail Expected Shortfall, full option stresses, Greek residuals, actual-trade limits and challenges, constrained allocation studies, research and tutoring.

The main sequence works: actual trade → portfolio exposure → stated risk assumptions → VaR/ES → stress drivers → actual hedge → changed risk → full-versus-Greek comparison → Monte Carlo → constrained allocation → actual-state tutoring. Risk calculations do not change account P&L. Python is the financial source of truth; browser code formats results and plots supplied values.

## TEST REPORT

**1,097 tests passed in 43.09 seconds. All 898 baseline test identifiers remain; zero were removed. 199 tests were added.**

New coverage: 90 mathematical tests; 44 execution/account/replay tests; 53 tutor/research tests; 12 HTTP integration tests. Properties include PSD variance nonnegativity and ES ≥ VaR. Independent checks cover integrated empirical quantiles, correlated-draw covariance, vector/scalar option prices, exact minimum-variance solutions, accounting identities, real hedge fills, resting-order reservations, atomic quote rejection, auto-hedge limits, horizon failures, replay integrity and public information boundaries.

The full suite includes existing conservation and generated mixed-operation tests. Ruff, browser JavaScript syntax and installed-dependency checks pass. Browser QA verified actual trades, rejection reasons, hedge fills, stress attribution, solver diagnostics, research, replay, no console errors and a 390-pixel layout with no page overflow. Demo answers were not credited to Arvind.

Evidence: [test output](phase_09/test-results.txt), [validation record](phase_09/validation.json).

## HOW TO OPEN THE RISK LAB

The upgraded application is running at **http://127.0.0.1:8766/risk** and is open in the existing browser. It starts with empty trading positions and the preserved learning profile. Stock and Options Lab navigation links lead to the same application.

To restart later from the project folder:

```bash
venv/bin/python -m quantlab.trading.server --port 8766 --learning-path runs/learning/progress.json
```

To reproduce the terminal demo and profile:

```bash
venv/bin/python -m quantlab.risk_demo --output runs/risk/demo --profile
```

## RISK DASHBOARD WALKTHROUGH

1. **Portfolio & trades:** equity, cash, realised/unrealised P&L, fees, positions, multipliers, factor Greeks and concentration. Buy/sell stocks or options; the hedge button submits an actual underlying order.
2. **Risk & tails:** choose confidence, calendar horizon, daily volatilities, correlation, return model, sample size and analysis seed. Compare parametric, empirical and MC estimates. Inspect histogram, VaR cutoff, exact ES tail and worst observations. Supply covariance or observed return rows with explicit missing-data handling.
3. **Stress & limits:** inspect the named scenario table, configure mixed shocks and see each instrument's contribution and approximation residual. Apply soft/hard limits or start a challenge.
4. **Allocation lab:** use the current factor covariance with explicit synthetic expected returns, budget, caps, shorting and cash constraints. Inspect feasibility, objective, residuals and target-return frontier points. This is an allocation study, not an unrecorded trade.
5. **Research:** register a hypothesis before independent runs. Inspect seed-level metric distributions, intervals and paired changes. Evaluation reuse is recorded.
6. **Report & replay:** end/save, export the journal and verify it before stepping through public frames. Cross-desk sessions are managed from the Risk Lab once attached.

## ONE MANUAL PORTFOLIO-RISK SESSION

The demo fixes market seed 42, analysis seed 99042 and independent synthetic-sample seed 77042 before observing results. Default VaR uses 95% confidence and a one-calendar-day horizon.

| Event | What happened and why |
| --- | --- |
| Buy one ATM call | One real dealer fill at £2.302151 per unit ×100, plus £0.05 fee. Cash falls and an option asset appears. Initial net P&L is -£1.55005 because the midpoint is below the paid ask. |
| Set hard delta maximum 55 | The current call delta is 51.143575. |
| Try buying 10 stock units | Rejected before execution: proposed delta 61.143575 exceeds 55. No accounting repair or invented fill. |
| Set full-MC VaR target £20 | The current £89.698948 VaR fails the target. |
| Sell 51 QL-STOCK units | Actual FIFO fill at £99.99 with £0.051 fee. Delta becomes 0.143575; full-MC VaR £3.823316 now meets the challenge. Actual net P&L is -£2.11105. |
| Apply volatility and mixed stresses | Hypothetical repricing reveals remaining vega/gamma. Actual P&L remains unchanged. |
| Clear delta limit and add 50 units of each of two stocks | Both purchases are actual trades. Risk rises and the earlier £20 challenge fails again; success is not ensured. |
| Stress correlation | The current joint-risk estimate changes, without inventing an immediate cash loss. |
| Solve allocation constraints | Validated hypothetical weights; no account mutation. |
| Observe one real model day | Stock and option marks update causally. Actual P&L becomes £3.69865. |
| End and replay | Resting orders are cancelled, holdings remain marked, and all 16 public frames verify against regenerated trades, warnings, risk and evidence. |

The saved [demo data](phase_09/demo.json) and [risk journal](phase_09/manual-session.json) preserve the complete details. The browser independently exercised an actual call purchase, prohibited buy, 51-share hedge, custom shock, allocation solve and challenge, then loaded this journal and verified frames 1–16.

## COVARIANCE / CORRELATION DEMO

Variance measures one return's dispersion. Covariance measures whether two returns are above/below their own averages together. Correlation divides covariance by their two standard deviations.

For daily volatilities 1.2% and 0.8% and correlation 0.25: covariance=0.012×0.008×0.25=0.000024. The correlation is 0.25; these are not interchangeable numbers. The estimator uses N−1 by default and rejects missing rows unless complete-row deletion is explicitly requested.

## PORTFOLIO-VARIANCE DEMO

For actual delta exposure in pounds, variance=wᵀΣw has units GBP². The expanded demo book has individual variance terms 5,220.704529 plus cross terms 1,203.445808, giving 6,424.150337 GBP². Square-rooting gives £80.150797 daily linear volatility. Component volatilities £52.681041 and £27.469757 sum to that total.

This is a linear delta decomposition. Options retain nonlinear and volatility risks beyond it.

## DIVERSIFICATION DEMO

Hold budget £10,000, means zero and each asset's daily volatility 1% fixed. One asset has £100 volatility. Equal weights have £79.06 at correlation 0.25, £98.74 at 0.95, and £50 at -0.5. At perfect positive correlation they retain £100 volatility. More names alone do not ensure safety.

## PARAMETRIC VAR DEMO

Normal linear loss uses VaR=mean loss+z×loss standard deviation, with z≈1.64485 at 95%. After the actual hedge, delta-normal VaR is **£0.283392** and ES **£0.355386**. The apparently tiny number omits option decay, curvature and IV changes. It is explicitly labelled an approximation.

## HISTORICAL VAR DEMO

Reprice the current hedged portfolio under 500 synchronised, independently generated synthetic return observations. Full empirical VaR is **£3.820306**, ES **£3.837454**. The default sample is labelled synthetic, not observed live history. Uploaded observations can replace it; history is not assumption-free and may omit future crises.

## MONTE CARLO VAR DEMO

Joint normal daily returns, 5,000 paths and analysis seed 99042 give full VaR **£3.823316**, ES **£3.837264**. The same scenarios under delta-only approximation give much smaller losses. Full risk compounds multi-day daily returns and reprices options; it does not multiply option VaR by √time. Analysis never consumes the market RNG.

## VAR VS EXPECTED SHORTFALL DEMO

Both teaching samples have 95% VaR £10. One has ES £12; the other ES £48. Their most extreme loss changes from £20 to £200 while the 95th loss remains £10. VaR identifies a threshold. ES measures severity in the worst tail. Neither is maximum loss.

## TAIL-RISK DEMO

The histogram shows loss increasing to the right, a VaR cutoff and bins touching the tail in amber. Worst observations are listed. ES is computed from exact observations, averaging exactly the worst (1−alpha) probability mass with fractional boundary weight. It is not approximated by bin averages or by dropping all observations tied at VaR. Small effective tail samples produce explicit warnings.

## STRESS-TEST DEMO

Named synthetic stresses include unchanged prices with one day of decay, -5%/-10% equity, +5/+20 volatility points, correlation 0.9, a 100-bp hypothetical liquidation haircut and combined stress with +50 rate basis points. The custom -8% stock/+12-vol-point/+50-bp-rate scenario on the hedged call gains **£266.874419** under full repricing. A scenario can benefit a particular portfolio; no loss is hard-coded. The instrument table attributes -£141.125581 to the call and +£408 to the short stock.

## DELTA-NEUTRAL-BUT-NOT-RISK-FREE DEMO

Delta is 0.143575 stock units after hedging, but vega is £1,143.26204 per 1.00 volatility. Raising IV from 20% to 40% changes value by **+£228.527168**. The first-order vega estimate is +£228.652408. A reverse exposure would react differently. Near-zero delta removes a local stock slope, not all risks.

## GREEK APPROXIMATION VS FULL REPRICING

For a +0.1% spot move, full P&L is £0.0491135 versus approximation £0.0491318: residual about -£0.0000183. For the large mixed shock, full P&L is £266.874419 versus £360.605651: residual **-£93.731233**. Delta, gamma, vega, theta and rho contributions are shown individually. Residual is neither hidden nor posted to realised P&L.

## CORRELATION-STRESS DEMO

For the expanded actual book, raising assumed correlation from 0.25 to 0.9 raises linear volatility from **£80.150797 to £97.740009** and delta-normal VaR from **£131.836330 to £160.768009**. The cross term increases while individual variances stay fixed. A pure correlation change gives zero deterministic spot-shock P&L; its effect is distributional. This is a scenario, not a claim that correlations always rise.

## RISK-LIMIT CHALLENGE

The hard delta limit prohibits the proposed extra purchase with the named metric, observed proposed value and limit in its explanation. It permits the actual hedge that reduces risk. Pending buy/sell orders reserve separate endpoints instead of cancelling each other algebraically. Whole manual quote replacements are checked before cancellation or the first fill. Auto-hedges also pass the guard.

Limits can warn softly or prohibit a newly breached/worsening action. A trade that reduces an existing breach remains allowed. The VaR limit specifically uses nonnegative delta-normal risk, while the VaR challenge uses full-MC risk. Market moves can breach limits after entry. Challenge alternatives cover delta with a vega cap, concentration with a preserved exposure floor, and a volatility-shock loss cap.

## PORTFOLIO-OPTIMISATION DEMO

Minimise wᵀΣw with risky weights capped at 40% and cash fixed at 20%. The demo solution is **14.347826%, 25.652174%, 40%, 20% cash**, with variance **0.000028852174**. The solver succeeds and budget/bound residuals pass validation. Expected returns are synthetic assumptions. Allowing unrestricted cash can produce an all-cash minimum-variance solution; requiring too much investment under tight caps can be infeasible. Failed/infeasible answers are not accepted as portfolios.

The optional mean–variance objective adds expected return and risk aversion. Target-return frontier points show feasible and infeasible targets. No allocation automatically changes account holdings.

## PHASE 5 RESEARCH INTEGRATION

Four hypotheses were fixed in code before outcomes, each with 128 distinct evaluation seed addresses and two variants: **1,024 complete runs, zero failures**. The persistent evaluation registry reported no reused seed addresses. Every study's worst primary-metric observation was regenerated with full evidence and matched its recorded metrics/fingerprint. The studies are conditional synthetic evaluations, not evidence of real trading returns.

| Study | Outcome |
| --- | --- |
| Correlation 0 → 0.9, two actual long stock positions | Mean VaR £118.5695 → £160.3142. Paired mean increase £41.7447; 95% Student-t interval £41.2974–£42.1921. |
| Normal → covariance-matched t(5), executed short straddle | Mean ES £239.2451 → £360.6008. Paired increase £121.3558; 95% interval £117.5045–£125.2070. |
| One → five days, executed delta-hedged five-call position | Mean full-minus-delta VaR £18.5604 → £97.8298. Different horizons are explicitly unpaired. |
| 250 → 5,000 nested MC paths | Across-seed SD of VaR £11.0065 → £2.3898. More paths reduce sampling variation, not model error. |

Registration, raw runs, estimates, intervals, registry and worst-case evidence are in [the research directory](phase_09/research). The browser also completed a separate 32-address development study and rendered its paired interval. Reuse checks are automated and disclose later inspections rather than relabelling them fresh holdouts.

## PHASE 7 TUTOR INTEGRATION

Nineteen risk topics use strictly allowlisted current portfolio facts. Lessons cover covariance, correlation, matrices, variance, diversification, VaR, ES, tails, stresses, concentration, contributions, delta-normal/full revaluation, scenarios, model risk, optimisation, PSD and correlated simulation. Structured numeric questions and interview/project-defence questions are available.

Replay rewind clears future risk contexts. Loading a consolidated new session/replay also clears other live desk contexts, while retaining historical answer evidence and learning progress. There is no market RNG, latent value, private signal or future realised price in risk tutor inputs. An encounter or profitable result earns no mastery credit.

## PERFORMANCE REPORT

Profiling used an actually executed portfolio with **20 option contracts and a real stock hedge**, with tracing and profiling enabled:

| Joint paths | Summary mode | Retain every loss |
| --- | --- | --- |
| 5,000 | 0.0141 s | 0.0281 s |
| 100,000 | 0.1221 s | 0.4106 s |

At 100,000 paths, traced peak allocation was about 12.1 MB. Both modes gave identical VaR **£40.628947** and ES **£40.765870**. Timings are one local measured profile, not a universal benchmark. The default dashboard uses 5,000 paths and caches unchanged portfolio/assumption reports. Pure pricing is vectorised and independently checked against scalar BSM. See [performance data](phase_09/performance.json) and [profile](phase_09/profile.txt).

## FILES CHANGED

- New `src/quantlab/risk/`: public portfolio adapter; covariance validation; loss metrics; scenarios; correlated simulation/full repricing; optimisation; analytics; execution limits; session/replay; research and application adapter.
- New `src/quantlab/risk_demo.py`: deterministic actual-trade demo and profile.
- `src/quantlab/trading/session.py`, `server.py`: optional execution guards, atomic quote preflight, shared risk routes/lock, managed-session exports.
- `src/quantlab/options/session.py`, `application.py`: option guards and shared risk-managed commands without duplicate accounting.
- New risk HTML/CSS/JS; navigation links in existing pages; shared tutor JavaScript supports Risk Lab contexts.
- New `src/quantlab/tutor/risk.py`; catalog/context/questions/service/bridge extend the existing tutor and preserve the original stock-only catalog API.
- Four new test files named in `validation.json`.
- Package version 0.9.0 and demo entry point; local-run ignore rule; README, ROADMAP, ASSUMPTIONS, LEARNING_LOG, CHANGELOG, architecture contract, first-principles maths and this evidence report.

## RED TEAM

- Ordinary return VaR holds IV fixed. The delta-hedged long-call tail can look tightly bounded by decay under that narrow model, while omitted IV jumps, execution costs or basis changes can dominate. Stress analysis is essential.
- Full repricing is full **BSM** repricing, not exact market repricing. The current midpoint/model basis is frozen. Sticky strike IV, cash funding and synthetic liquidity are assumptions.
- Default empirical observations are synthetic. IID normal/t daily returns exclude changing regimes and serial dependence. An invalid ≤−100% arithmetic draw fails explicitly rather than being clipped.
- Three stock identities exist, but only QL-STOCK has the Phase 8 daily process. QL-DESK has its separate microstructure clock; QL-SECOND is a controlled static venue. Assumed joint risk scenarios are not a calibrated multi-asset market process.
- Options are currently written only on QL-STOCK. The portfolio/matrix/repricing layers retain underlying identities and support additional mappings; a new option venue would still need execution and settlement integration.
- The hard VaR limit is delta-normal. A delta-neutral short-gamma/short-vega book can evade that one metric; gamma/vega limits and stresses address different dimensions. A combination of limits remains incomplete risk control.
- Pending-order checks reserve present-price endpoints. They do not prevent future mark moves from creating breaches or guarantee solvency. Drawdown measures the consolidated session since attachment, not a reconstructed pre-attachment joint history.
- Maximum position quantity is in each instrument's native units. One contract and one share are not comparable economic sizes; value and Greeks must be read alongside it.
- Empirical tail conventions matter. ES here integrates exactly the worst mass, including fractional ties; other conventions can give different finite-sample estimates.
- Near-singular covariance can destabilise allocations and contributions. Warnings and explicit numerical tolerances are not a cure for poor data. No statistical regularisation is automatic.
- Cash has zero return/variance in allocation studies. Expected returns are synthetic. Frontier points are illustrative and not guaranteed future opportunities; allocations do not enforce transaction costs or lots.
- Liquidity stress is a stated haircut, not endogenous market impact, margin, funding stress, borrow recall or default. Those remain limitations, not silently completed features.
- Research fingerprints bind seed and stream identity, not every exogenous draw. Full results and worst-case regeneration provide additional checks. Exact replay is version-bound, and a checksum detects alteration but is not a digital signature.
- Browser demo work used a temporary profile. No learner answer, profit or approval was converted into a mastery claim.

## 3-QUESTION ARVIND CHECK

1. Your 95% VaR is £10,000. Can a loss exceed £10,000, and what extra question does Expected Shortfall answer?
2. The portfolio's delta is almost zero but vega is strongly positive. What change can still move its value substantially?
3. Two long assets keep the same individual volatilities, but their correlation rises. Which term of portfolio variance changes, and why can diversification weaken?

Answers are not recorded until Arvind supplies them. **Do not start Phase 10 before review.**

For the full first-principles explanations, formulas, examples, assumptions, mistakes and interview questions, read [the Phase 9 maths lesson](../maths/phase_09_portfolio_risk.md). Conventions were checked against primary [NumPy covariance](https://numpy.org/doc/stable/reference/generated/numpy.cov.html), [NumPy Cholesky](https://numpy.org/doc/stable/reference/generated/numpy.linalg.cholesky.html) and [SciPy SLSQP](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html) documentation; these document numerical methods, not the realism of QuantLab's risk assumptions.
