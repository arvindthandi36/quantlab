# Phase 10 — Statistical Arbitrage & Systematic Research Lab

> Historical phase record. Current core conventions and release status are in the root README, ASSUMPTIONS and Phase 11 release report. Test counts and runtime labels below describe this phase.


Phase 10 is implemented. **Phase 11 has not started.** All numbers below come from the saved executions or registered experiments in `phase_10/`; defaults were not retuned after evaluation. Synthetic profits are not evidence of real-market alpha.

## BUILD REPORT

Added a six-screen Stat Arb Lab at **http://127.0.0.1:8766/statarb**, backed by a generic 2–30-asset market. Each instrument has its own price observation, FIFO book, tape and exact account. Valid covariance transforms and common-factor processes reuse Phase 9 infrastructure. Controlled links provide stable residuals, noncointegrated pairs and relationship breaks.

Models use centered/scaled least squares, explicit fitting vintages and past-only residual normalization. Frozen, rolling and walk-forward schedules are available. Manual pairs, individual market/limit orders and a prespecified systematic strategy execute through the existing Phase 6/1 pipeline. Pending second legs, cancelled remainders and partial closes remain visible.

The risk bridge reads actual ledgers. A consolidated card in Portfolio Risk includes the pair. Public tutor contexts, deterministic replay, candidate disclosure and Phase 5 registration/evaluation accounting are integrated. The AR(1) diagnostic is deliberately limited and **not ADF**. PCA is deferred.

## TEST REPORT

**1,294 passed in 67.35 seconds.** This preserves **all 1,097 original test IDs** and adds **197 tests**. None of the old tests was deleted or relaxed. The baseline itself passed in 41.51 seconds.

New coverage includes exact/SciPy-reference OLS, SEs and residual identities; singular/constant/missing inputs; covariance/factor structure; stable versus random-walk variance; signal timing; future-data mutation; sizing and stops; two-leg costs; no-fill/partial-fill/cancel/passive orders; generated mixed operations; ledger attribution; replay and tampering; research registration/selection/holdout access; tutor fact boundaries; and HTTP/security integration. The intentional old-context regression tutor behaviour was retained. Final review strengthened leg-imbalance reservations for unfilled limits and rejected invalid correlation even when zero volatility would mask it. Saved research extremes and demo journals were then verified unchanged.

Ruff passes across `src` and `tests`. Browser JavaScript parses successfully. Desktop/phone QA found and corrected low-contrast navigation; the final 390px page has no document overflow. All 288 registered evaluation runs completed; the worst run of each of ten variants was independently regenerated using the Phase 5 verifier.

Evidence: [validation.json](phase_10/validation.json), [test output](phase_10/test-results.txt).

## HOW TO OPEN THE STAT ARB LAB

Open **[Stat Arb Lab](http://127.0.0.1:8766/statarb)**. The existing local server has been updated. Before restarting it, the original stock, options and risk accounts were verified to be at event zero with no orders or positions. Existing learner answer history was preserved; browser exercises used a separate temporary learning profile.

For a later restart from the project directory:

```bash
venv/bin/python -m quantlab.trading.server --port 8766
```

Then open `/statarb`. The other desks remain at `/`, `/options`, `/risk`, and `/learning`.

## STAT ARB SCREEN WALKTHROUGH

1. **Market & trade:** click **Observe next prices** with 80 selected. The initial fit becomes available. Inspect separate aggregated books and the current residual/z-score. Choose Long spread, Short spread or Wait. The first order executes; **Execute next queued leg** submits the second.
2. **Relationship:** inspect α, β, R², both price and return correlation, residual, past mean/SD, causal z, limited AR diagnostics and actual-account risk. Quant Mode explains the matrix formula and its units.
3. **Research lab:** register repeated train/test, walk-forward, cost, break or pair-mining studies. Inspect every parameter/pair candidate and the holdout. The invalid future-data demo is clearly rejected.
4. **Challenge correlation:** compare completed independent teaching datasets. Their revealed generating assumptions do not reveal the active market's future.
5. **Trades & replay:** inspect each episode's entry model, during-trade exposure/P&L path, actual fills, exit reason and attribution. End, download the journal, and load it for verified replay.
6. **Market & rules:** configure a new process and commit thresholds, windows, sizing, execution order, limits and costs. End the existing session first so its history is not silently discarded.

For a leg-risk exercise, withdraw X external liquidity, submit a pair and execute its second leg. Y can fill while X remains zero. A request is not a fill.

## CORRELATED-ASSET DEMO

Positive and negative examples apply a valid covariance factor to independent Gaussian shocks. The independent example uses zero correlation. Statistical tests verify the increment correlations near −.9, 0 and +.9 over 7,000 observations. Every asset keeps a separate book.

Correlation is a description of joint behaviour. There is no rule saying “high correlation means enter a trade.”

## COMMON-FACTOR DEMO

The model uses `Ri = bi F + εi`: a shared return shock plus each asset's own independent movement. The completed example includes three assets with loadings 1, 1.5 and −.5, showing a negative loading as well as positive ones. It displays the common component, idiosyncratic component and their sum.

Live risk estimates loadings from the **observed X-return proxy**. It never supplies the true hidden process loadings to the trading agent. The proxy is not a complete market-factor model.

## REGRESSION DEMO

The analytical example X=[1,2,3,4,5], Y=[5,8,11,14,17] recovers **α=2, β=3, R²=1**. Independent tests compare noisy-sample coefficients and conventional SEs with SciPy.

OLS means choosing the line with the smallest sum of squared prediction errors. The line's intercept is not investment alpha. A perfect sample fit does not establish a profitable strategy. The implementation uses [NumPy's stable least-squares solver](https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html), not explicit inversion of normal equations.

## SPREAD / RESIDUAL DEMO

At t=80 in the manual demo, X=£97.38 and Y=£97.64. Raw Y−X is **£0.26**. The available fit is α≈5.99709 and β≈.937795, so `Y−α−βX≈£0.320407`.

A residual is a deviation from a fitted line, not proof of true mispricing. Its definition changes if the line changes. Open trades retain their entry hedge and model.

## Z-SCORE DEMO

At that same event, the current residual is about **2.219 recent standard deviations above its past mean**. The fit uses `[0,80)`; normalization uses `[40,80)`. Current observation 80 enters only the current residual, not either fitted window.

A z-score measures relative unusualness. It does not give the probability of profitable convergence. Insufficient or effectively zero residual volatility makes the signal unavailable.

## CORRELATION VS COINTEGRATION DEMO

| Completed construction | Price correlation | Future residual SD | Descriptive AR(1) φ |
|---|---:|---:|---:|
| Stable residual, φ=.92 by construction | .98284 | £.39089 | .92168 |
| Independent random-walk residual, φ=1 | .98081 | £.82567 | .99903 |

Both prices can look very closely related while their residual processes differ. Ground truth comes from the generating equations. The AR fit is descriptive, not a formal cointegration test. The finite tick-rounded executable simulation is an approximation to those ideal processes.

## SPURIOUS-CORRELATION DEMO

The disclosed search considers all 28 pairs among eight unrelated random walks and chooses the largest absolute training price correlation. Its selected example has training R²≈.869; across the completed path, price correlation≈.839 but return correlation≈.006.

The selection itself is the lesson: persistence and searching can produce an impressive chart without a causal or stationary relationship. Every candidate is shown. [Forecasting: Principles and Practice](https://otexts.com/fpp3/regression-evaluation.html) discusses this danger of regressions on nonstationary series.

## ONE MANUAL PAIRS TRADE

The preserved journal is [manual-session.json](phase_10/manual-session.json).

| Event | What happened and why |
|---|---|
| t=80, training completed | Positive residual z≈2.219; no future convergence is known. |
| First manual short-spread leg | Sell 5 Y at its actual £97.63 bid; fee £.025. X has not filled. Unit-hedge imbalance≈£456.61. |
| Separate second execution event | Buy 5 X at its actual £97.39 ask; fee £.025. Gross exposure £975.10; net marked exposure −£1.30; remaining unit-hedge mismatch≈£30.29. |
| t=81–83 | Published prices move. Actual holdings earn both residual and remaining directional movement. |
| t=83, manual close | Buy back Y and sell X through their current books. Final net P&L **£.30** after **£.30 total costs**. |

Marked movement £.60 consists of about £.385394 residual movement plus £.214606 remaining unit-hedge directional movement. Execution shortfall is £.20 and fees £.10. The residual has **not** met the near-mean exit criterion: exit z≈1.144. A profitable outcome does not prove the original reasoning correct.

## ONE SYSTEMATIC PAIRS TRADE

At t=81, z≈3.558 clears entry 2 and remains below stop 4. The prespecified policy sells 5 Y at **£98.30**. At t=82 the queued hedge buys 5 X at **£97.89**. The t=92 near-mean exit signal buys Y at **£98.67**; t=93 sells X at **£98.29**. After four real executions and fees, the episode earns only **£.05**.

Across the standard short run, four episodes net **£.45**, with **£4.45 maximum drawdown**, **£1.20 costs**, and a worst episode of **−£.65**. Those losing and low-profit episodes are retained in [systematic-session.json](phase_10/systematic-session.json).

## LEG-RISK DEMO

With a £4,000 target and X depth one, the first leg buys **21 Y**, but X can sell only **5 units** across two price levels. Gross exposure is **£2,537.34**, net marked exposure **£1,563.54**, and unit-hedge imbalance about **£1,430.87**. The unfilled market remainder cancels; no synthetic hedge is added.

The next two observations change P&L while the mismatch is held. In this particular preserved path, the eventual episode profits £9.03. That does not make leg risk beneficial: the direction happened to help. The zero-depth browser exercise also verified Y=5, X=0, and Portfolio Risk showed precisely those positions. [Partial-fill journal](phase_10/partial-session.json).

## TRANSACTION-COST DEMO

On the fixed single path, low execution costs yield **£6.55**; larger spreads and fees yield **−£.25**. Across 32 registered paired seeds, mean P&L changes from **£4.9753** to **−£4.4809**. Mean paired difference: **−£9.4563**, 95% interval **[−£10.2602, −£8.6523]**.

Both cases execute through actual books. Costs are neither omitted nor subtracted twice from P&L already using bid/ask prices.

## IN-SAMPLE VS OUT-OF-SAMPLE DEMO

Three prespecified entry thresholds are ranked using training net P&L only. The chosen specification is then refitted using past rows at deployment and evaluated on an equal-length untouched trading block. Selection, re-estimation and sampling can all contribute to the difference.

Across 32 seeds, mean training-selected P&L is **£4.9778** versus **£1.5172** out of sample. Paired difference **−£3.4606**, 95% interval **[−£5.4017, −£1.5196]**. Test results never select the threshold.

## WALK-FORWARD DEMO

Fit the last 60 past observations, freeze that model for the next 20, then repeat. The report tracks each fitting vintage, β/α drift, block P&L, turnover, drawdown, hit rate and spread range.

One completed seed earns £6.55 fixed versus £9.55 walk-forward. Across 32 registered seeds, the mean advantage is only **£.1434**, with 95% paired interval **[−£2.5050, £2.7919]**. This study does **not** establish that refitting is better.

## REGIME-BREAKDOWN DEMO

The controlled cases change slope, mean, innovation volatility, persistence or residual drift. The live policy sees observed prices and z-scores, not the hidden break flag.

One old-fit path earns **£5.35** under the stable construction and loses **£24.25** when the residual acquires drift. Some other breaks profit; none are hidden. In the separate 32-seed study, stable mean P&L is **£6.3972** and drift-case mean is **−£28.9497**. The drift range is **−£52.80 to −£9.14**, despite the safeguards. Stops request actual orders; they do not repair the model or manufacture liquidity.

## PARAMETER-SWEEP DEMO

The 11-candidate one-at-a-time design varies entry, exit, regression window, z window and stop. All parameters, training results, failures and selection criteria are saved.

On the registered single case, candidate 8—the z-window variant—wins training with **£4.95**, then earns **£7.30** in the holdout. This successful holdout is retained too. It is one selected synthetic path, not proof of robustness. [Selection and evaluation](phase_10/parameter-sweep/selection.json).

## PAIR-MINING / MULTIPLE-TESTING DEMO

Every run creates eight unrelated assets, tests all **28** pairs on training only, saves every candidate and applies the declared training-P&L ranking. The selector never receives evaluation rows.

Across 16 registered seeds, historical winners average **£14.7606** in training and **−£.0188** out of sample. The paired drop is **−£14.7794**, 95% interval **[−£19.5554, −£10.0034]**. There are **5 negative, 7 positive and 4 zero-P&L holdouts**. The out-of-sample mean interval is wide: approximately **[−£6.22, £6.18]**. This is evidence of strong selection optimism in the construction, not proof every winner loses.

For a transparent adverse example, **registered run index 11 is the worst holdout, selected explicitly for failure analysis after the entire study**: its training winner earns **£1.57**, then loses **£23.34** out of sample. It is not presented as representative or as a seed chosen before evaluation. The full sample above supplies context.

The separately prespecified single-seed demo instead falls from £12.92 to £0: its deployment β estimate turns negative, outside this policy's supported positive-unit hedge range. That is a **no-trade failure of persistence, not a realized loss**. Both outcomes remain visible. No seed search was used to replace the zero result with a dramatic loss.

## LOOK-AHEAD-BIAS DEMO

The deliberately invalid oracle uses the next observation's residual movement to choose today's position. It pays real costs, but still appears to make **£117.05** where the causal baseline on the same completed teaching data loses **£4.43**.

The advantage is impossible information, so the methodology is explicitly rejected and cannot drive live orders. Dedicated adversarial tests change future observations and require earlier fits, means, SDs, z-scores, entries, exits and fills to remain unchanged.

## PHASE 5 RESEARCH INTEGRATION

Five studies were registered before outcomes: generalisation, walk-forward, costs, regime and mining. There are **288 completed variant-runs, zero failed runs**, with development/evaluation namespaces and a durable pre-access registry. All 11 sweep candidates and all 28 mining candidates are retained. Failures are tested and saved rather than replaced by zero returns.

Ten worst variant-runs were regenerated against exact saved metrics, coverage, environment and trajectory fingerprints. Environments hash the actual process evidence. The regime study is unpaired because its paths differ; shared-path studies are paired. [Design registration](phase_10/design-registration.json), [evaluation registry](phase_10/evaluation-registry.jsonl), [research records](phase_10/research).

## PHASE 9 RISK INTEGRATION

The executed manual short pair has only **−£1.30 net marked exposure**, yet estimated X-proxy factor exposure is about **−£8.32**, with one-observation 95% linear VaR **£1.2425** and ES **£1.5581**. Net pounds are not the same as eliminated risk.

The Risk Lab displays a consolidated linked-account card, including actual pair positions, gross/net, proxy factor exposure, VaR/ES and stress P&L. It makes the assumptions visible: zero cross-lab covariance and a crude mapping from a stat-arb observation to a risk day. Existing original-desk risk limits and Stat Arb safeguards keep explicit separate scopes; a linked view is not a claim of unified global limit enforcement.

## PHASE 7 TUTOR INTEGRATION

Added 22 contextual topics: covariance, correlation, regression, α, β, residuals, R², hedge ratios, z-scores, mean reversion, stationarity, unit roots, cointegration, look-ahead, walk-forward, instability, leg risk, dollar/factor neutrality, multiple testing, data snooping and transaction costs.

Questions use an allowlisted public schema. Numeric exercises use the current displayed facts; higher levels ask for assumptions and project defence. Replay rewind clears later contexts. No demo answer has been credited to Arvind. The [maths lesson](../maths/phase_10_statistical_arbitrage.md) gives all 18 requested topics the six requested learning sections.

## PERFORMANCE REPORT

Unprofiled timings were measured after tests finished on this local machine:

| Workload | Wall time | Instrumented peak memory |
|---|---:|---:|
| 1,000 rolling regressions/signals | .328 s | 1.43 MB |
| 10 separate assets × 1,000 market steps | 2.421 s | 10.46 MB |
| 321-row walk-forward experiment | .408 s | 1.96 MB |
| Mine all 28 training pairs with real execution | 4.634 s | 1.98 MB |

Memory figures use tracemalloc and do not include every native allocation. The separate cProfile/tracemalloc timings include heavy instrumentation and initially overlapped tests; they are not quoted as normal throughput. Most instrumented time is in book refresh and exact invariant checking. OLS, covariance and residual operations use NumPy; model fits are reused within frozen blocks. Sequential execution remains sequential to preserve its meaning. No financial logic was duplicated in browser JavaScript. [Profile and timings](phase_10/performance.json).

## FILES CHANGED

- New `src/quantlab/statarb/`: `process.py`, `market.py`, `statistics.py`, `strategy.py`, `session.py`, `risk.py`, `research.py`, `examples.py`, `application.py`, and package initializer.
- New `src/quantlab/statarb_demo.py`: saved deterministic demonstrations, registered studies and profiling entry point.
- Updated `src/quantlab/trading/server.py`: static/API routes, shared lock, lazy Stat Arb controller.
- New `src/quantlab/trading/static/statarb.html`, `.css`, `.js`; updated navigation in stock/options/risk/learning screens, Risk Lab linked-account card and `tutor.js` routing.
- Updated `src/quantlab/risk/application.py`: read-only consolidated actual-account reporting.
- New `src/quantlab/tutor/statarb.py`; updated tutor catalog, fact allowlist, bridge, relevance/questions and service.
- Four new test files: `tests/unit/test_statarb_statistics.py`, and integration `test_statarb_sessions.py`, `test_statarb_research_tutor.py`, `test_statarb_http.py`. Existing tests were preserved.
- New architecture, maths, report and `docs/learning/phase_10/` evidence. Updated README, ROADMAP, ASSUMPTIONS, LEARNING_LOG and CHANGELOG.

This is an unreleased feature increment. Saved evidence truthfully retains runtime version 0.9.0, along with the distinct stat-arb journal schema and adapter. Prior artifacts were not relabelled or rewritten.

## RED TEAM

- **Statistical claims:** high correlation/R² is never a trading certificate. Finite-sample AR persistence is not ADF. Half-life may be misleading on a unit-root realization; no p-value is invented.
- **Time boundaries:** model/normalization use past rows only; no future closing prices fill historical orders. The intentionally invalid oracle is isolated. Repeated evaluation is marked as reuse.
- **Selection:** every candidate, failed run and zero-trade outcome is retained. Mining pairs share assets; the independent-testing formula is only an intuition lesson. The worst holdout example is explicitly selected after evaluation and shown alongside all results.
- **Execution:** books are real but external quotes refresh exogenously. There is no feedback impact, realistic competition, correlated venue latency or atomic pair fill. Gross/leg controls are conservative preflights, not a complete margin system.
- **Economics:** borrow constraints, short financing, capital haircuts, taxes and corporate actions are absent. Synthetic asset universes simplify survivorship rather than solve it for real data.
- **Model/risk:** true factor loadings and break timing stay private. X is only an observable proxy. Cross-lab covariance/time mapping is crude; global shared risk-limit enforcement is not claimed. A stop can leave positions exposed when the book is empty.
- **Accounting:** the exact ledgers remain authoritative. Attribution has a checked identity; the temporary directional component is a subset and is never added twice. Profitable trades can fail their original convergence thesis.
- **Scope:** formal unit-root/cointegration inference and PCA are deferred. No Phase 11, live-market trading or claim of real alpha is included.

## 3-QUESTION ARVIND CHECK

1. Two prices have correlation .98. What extra question about their **residual** matters before considering a pairs trade?
2. Your Y order fills but X does not. Do you already have the intended hedge, and what exposure would you inspect?
3. You try 28 unrelated pairs and report only the historical winner. Why is an untouched test necessary, and why must the other 27 results remain visible?
