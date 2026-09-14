# Phase 10 — statistical arbitrage from first principles

Read this as a research lesson, not investment advice or a claim of real alpha. A price relationship is a hypothesis about a process. A profitable chart does not explain whether it survives new data, costs or execution failures.

The full chain is **data/process → relationship → model → signal → position → execution → P&L → risk → validation → failure analysis**. Each arrow can fail independently. The lab uses GBP per whole asset unit; one observation is a model step, not a calibrated trading day.

## 1. Correlation

### INTUITION

Two things can rise and fall together. Correlation describes the strength of a **linear** relationship in a particular sample. It does not say why they move together, whether their difference is stable, or whether anyone can profit from that relationship. Correlation of price levels and correlation of returns answer different questions.

### MATHEMATICS

First subtract each sample mean. Covariance averages the product of the two deviations: `cov(X,Y) = Σ(X−X̄)(Y−Ȳ)/(n−1)`. Dividing by both standard deviations gives `ρ = cov(X,Y)/(sX sY)`, between −1 and +1. Covariance retains units; correlation has no units. A zero standard deviation makes correlation undefined, not zero.

### QUANTLAB EXAMPLE

The completed stable and noncointegrated examples both have price correlation about 0.98. Inspect their residual paths rather than treating that number as a signal. The independently generated spurious example has nearly zero return correlation despite a high price-level correlation.

### ASSUMPTIONS

Observations are synchronized and finite. Sample correlation can be unstable, especially for wandering price levels. Correlation describes linear association, not all possible dependence.

### COMMON MISTAKES

Confusing levels with returns; confusing correlation with causation; assuming a high number proves cointegration; silently using a future sample to estimate today's correlation.

### INTERVIEW QUESTIONS

Why might a high price correlation coexist with an unstable spread? What happens to the correlation calculation when one asset never moves?

## 2. Regression

### INTUITION

Draw a line predicting Y from X. Each observation misses that line by some vertical amount. Ordinary least squares chooses the line that makes the sum of squared misses as small as possible. Squaring prevents positive and negative misses from cancelling and penalizes large misses strongly.

### MATHEMATICS

Minimise `L(α,β)=Σ(Yi−α−βXi)²`. Setting both first derivatives to zero gives `β̂ = Σ(Xi−X̄)(Yi−Ȳ)/Σ(Xi−X̄)²` and `α̂=Ȳ−β̂X̄`. This connects optimisation to covariance. `R²=1−SSE/SST` compares remaining squared errors with total variation in Y. Constant Y makes the denominator zero, so R² is unavailable.

In Quant Mode, let `A` be an `n×2` matrix with a column of ones and a column of X. Let `y` be `n×1`, and `θ=(α,β)` be `2×1`. For full column rank, `θ̂=(AᵀA)⁻¹Aᵀy`. This is a mathematical identity, **not the numerical implementation**: forming and inverting normal equations can magnify conditioning problems. QuantLab centers/scales X and calls NumPy's SVD-based least-squares solver, checks rank and rejects effectively constant predictors.

### QUANTLAB EXAMPLE

For X = 1,2,3,4,5 and Y = 5,8,11,14,17, the exact fit is α=2, β=3, R²=1. This arithmetic example is not a trading edge. The live fit at t=80 uses rows `[0,80)`, excluding row 80.

### ASSUMPTIONS

A line is a useful approximation; parameters remain relevant; observations are appropriate. Conventional SEs use residual variance `SSE/(n−2)` and assume IID homoskedastic errors. Autocorrelation, changing variance, outliers and nonstationary prices undermine the usual inferential interpretation. The interface discloses this instead of publishing spurious significance.

### COMMON MISTAKES

Calling the intercept investment alpha; using a high R² as evidence of profit; treating OLS standard errors on arbitrary prices as valid economic inference; returning huge coefficients when X barely varies.

### INTERVIEW QUESTIONS

Why square residuals? How can an outlier move the line? Why use a stable solver rather than explicit inversion?

## 3. Residuals

### INTUITION

A residual measures how far the observation is from the model's prediction. It is a model-relative error, not the true mispricing of an asset.

### MATHEMATICS

`e_t = Y_t−α̂−β̂X_t`. In an intercept OLS fit, training residuals sum to approximately zero and are orthogonal to the training X vector. These are fitting properties, not guarantees about future residuals.

### QUANTLAB EXAMPLE

At t=80 in the standard demo, Y−X is £0.26, while the fitted residual is about £0.3204. The two numbers differ because the fitted intercept and slope differ from zero and one.

### ASSUMPTIONS

The chosen Y/X ordering, units and line remain meaningful. Regressing X on Y generally does not produce the reciprocal of the Y-on-X slope.

### COMMON MISTAKES

Calling a residual fundamental mispricing; comparing residuals from different model vintages as if their definitions were unchanged; confusing an exactly zero training residual mean with future stability.

### INTERVIEW QUESTIONS

Why do training residuals often look better than future residuals? What changes when the model is re-estimated?

## 4. Hedge ratios

### INTUITION

If the fitted relationship says Y tends to move about twice as many pounds as X, one Y unit may be partially offset by two opposite X units. The word **may** matters: this is a model hedge, rounded into executable whole units.

### MATHEMATICS

For a long residual, `qY=q` and `qX≈−β̂q`. An ideal frozen unit hedge earns `q(ΔY−β̂ΔX)` before costs. Regression β here has units of X units per Y unit. Equal marked pounds instead require `qX X + qY Y = 0`. Factor neutrality requires `Σ qi Pi bi = 0` for specified return loadings `bi`. These are distinct equations.

### QUANTLAB EXAMPLE

With β≈0.9378, five Y units suggest 4.689 X units. The executable hedge rounds to five X units. The rounding and the estimated relationship leave measurable unit-hedge exposure. A near-zero dollar net can coexist with nonzero estimated X-proxy factor exposure.

### ASSUMPTIONS

Units are comparable spot asset units with multiplier one. The initial implementation restricts the unit-hedge β to `[0.05,5]`; unsupported negative or extreme estimates block entry visibly. That restriction is part of the strategy, not data cleaning.

### COMMON MISTAKES

Treating β as exact, permanent, dollar-neutral or market-neutral; ignoring whole-unit rounding; multiplying by the asset price twice.

### INTERVIEW QUESTIONS

How do you hedge one Y unit? Which neutrality does that create? What if the relationship changes?

## 5. Spreads

### INTUITION

A spread is a chosen combination of prices. Its definition determines what “long” and “short” mean. Here it is a regression residual, not the bid/ask spread of one order book.

### MATHEMATICS

`spread = Y−α̂−β̂X`. Holding the frozen combination earns `q Δspread` before execution costs. The intercept is not an instrument you buy; it cancels from changes when held fixed. Changing α or β changes the residual definition even if prices do not move.

### QUANTLAB EXAMPLE

Long spread buys Y and sells X. Short spread sells Y and buys X. The manual demo shorts a positive residual. Open trades retain their entry model and hedge so later fits cannot rewrite the original trade thesis.

### ASSUMPTIONS

The fitted relation is economically meaningful within this synthetic model. The lowest-level market supports multiple separate instruments; the teaching policy initially chooses the first two.

### COMMON MISTAKES

Using Y−X when scales differ; reversing the sign of a trade; treating a change caused by refitting as realized trading profit.

### INTERVIEW QUESTIONS

What exactly does a long spread own? Why doesn't a positive residual guarantee a short-spread profit?

## 6. Z-scores

### INTUITION

A z-score says how unusual the current residual is relative to its recent history. It expresses the distance from a mean in units of recent standard deviation.

### MATHEMATICS

`z_t=(s_t−mean(s[t−W:t]))/sd(s[t−W:t])`, with sample SD using `W−1`. The slice excludes t. All past residuals in that window are calculated using the **same available model vintage** as the current residual. Insufficient history gives “unavailable”; nonfinite observations fail; effectively zero SD gives “unavailable,” never a division by tiny volatility.

### QUANTLAB EXAMPLE

At t=80, spread≈£0.3204, past mean≈−£0.0221, past SD≈£0.1543, so z≈2.219. This clears the entry threshold of 2 but is below the stop threshold of 4.

### ASSUMPTIONS

The recent distribution is a useful scale. A normal probability interpretation would require additional distribution assumptions; the strategy does not make it.

### COMMON MISTAKES

Calling z=2 a 95% probability of convergence; including future observations; mixing residual definitions from different fits; dividing by effectively zero SD.

### INTERVIEW QUESTIONS

What does z=+2.5 tell you? What does it not tell you? Which rows define today's mean?

## 7. Mean reversion

### INTUITION

Under a mean-reverting model, the expected deviation shrinks over time. Random shocks can still push the deviation further away before it returns, and a particular sample may never return during your holding period.

### MATHEMATICS

` s[t]=μ+φ(s[t−1]−μ)+ση[t]`, with independent standard-normal η. For `|φ|<1`, long-run variance is `σ²/(1−φ²)` under the stationary model. Conditional expected deviation after h observations is `φ^h(s[t]−μ)`. For `0<φ<1`, half-life is `−ln(2)/ln(φ)`. It describes expected decay, not a promised waiting time.

### QUANTLAB EXAMPLE

The controlled stable link uses φ=.92 and innovation SD £.16. Its ideal stationary residual SD is about £.408 and model half-life about 8.31 observations. A short finite-window estimate can differ markedly. The live model does not receive true φ or the hidden residual.

### ASSUMPTIONS

Constant parameters, independent shocks and an unbounded mathematical process. The executable simulator rejects nonpositive price paths instead of clipping them; at extreme horizons this failure boundary limits the ideal stochastic model.

### COMMON MISTAKES

Thinking “mean reverting” means guaranteed return; interpreting half-life as a stop timer guaranteed to work; ignoring a changing mean or volatility.

### INTERVIEW QUESTIONS

Can a mean-reverting spread get worse after entry? Why can a strategy lose even when the generating process is stationary?

## 8. Stationarity

### INTUITION

A stationary process behaves statistically in a stable way over time. A chart looking flat is not enough. A process may have a stable mean but growing variance, or an apparently stable recent window followed by a break.

### MATHEMATICS

Weak stationarity requires constant mean and variance and a covariance depending only on lag, not the calendar location. For a random walk `s[t]=s[t−1]+η[t]`, variance accumulates with t. It has a unit root: φ=1. QuantLab estimates descriptive AR(1) persistence and half-window means/SDs, but performs **no ADF hypothesis test and supplies no p-value**.

### QUANTLAB EXAMPLE

Inspect residual mean, SD, lag-one autocorrelation, fitted φ, histogram and first/second-half statistics. A half-life is reported only for 0<estimated φ<1. An unrelated random walk can still produce φ̂<1 in a finite sample; the number does not certify stationarity.

### ASSUMPTIONS

The AR fit is a limited descriptive summary. Residuals estimated from a prior regression require special critical values for formal cointegration inference; ordinary coefficient p-values would be misleading.

### COMMON MISTAKES

Calling this AR tool ADF; turning φ̂<1 into a pass/fail trading certificate; equating a short quiet period with a stable long-run distribution.

### INTERVIEW QUESTIONS

What is the null hypothesis of a genuine unit-root test? Why does rejecting a unit root still not establish net profitability?

## 9. Cointegration

### INTUITION

Two prices may each wander while a particular combination remains stable. This is closer to the hypothesis a residual strategy needs than simple correlation, but costs, timing and estimation can still make it unprofitable.

### MATHEMATICS

In the teaching construction, X is a random walk. Let `Y=α+βX+s`. If s is stationary, X and Y share a stationary linear combination. If s is an independent random walk with nonzero innovation variance, no nonzero combination removes both independent stochastic trends. Y can nevertheless be highly correlated with X.

### QUANTLAB EXAMPLE

Completed seed 101001 gives price correlations approximately .9828 (stable residual) and .9808 (random-walk residual). Their future residual paths differ. The ground truth comes from the generating equations, not from a chart or the limited AR diagnostic.

### ASSUMPTIONS

The ideal unbounded processes have the stated integration orders and constant parameters. QuantLab's finite, tick-rounded, positive-price realization is an educational approximation. Real assets require independent economic and statistical investigation.

### COMMON MISTAKES

Using correlation as a cointegration test; using a residual AR estimate with ordinary regression critical values; assuming cointegration proves exploitable alpha.

### INTERVIEW QUESTIONS

Why can highly correlated prices be noncointegrated? What additional evidence would you seek for real securities?

## 10. Look-ahead bias

### INTUITION

A historical simulation cheats if a decision uses something the trader did not yet know. The result may look excellent precisely because the impossible information removes uncertainty.

### MATHEMATICS

Information at t contains only the published prefix through t. The model fit satisfies `fit_end≤t`; normalization uses rows strictly before t. Future-data mutation tests replace every row after t while holding the prefix fixed; fits, means, SDs, z-scores, decisions and executions through t must stay identical.

### QUANTLAB EXAMPLE

The isolated INVALID oracle takes a position from the sign of `spread[t+1]−spread[t]`. It still pays actual book spreads and fees, yet appears much better than the causal strategy. This intentionally impossible rule is never exposed as a live strategy option.

### ASSUMPTIONS

Synchronized public quotes are already observed when the signal is formed. Trades use the existing current book, not a future closing price. Latency is simplified but represented by separate leg events.

### COMMON MISTAKES

Full-sample β used early in the sample; full-sample z normalization; “today's signal” filled at tomorrow's close while timestamped today; looking at the final test before choosing defaults.

### INTERVIEW QUESTIONS

How can a model leak information without explicitly referencing t+1? What would an adversarial test change?

## 11. Pairs trading

### INTUITION

A pairs policy turns a relationship hypothesis into two actual orders. It needs a decision rule, size, exit rule, failure rule and accounting. These choices matter as much as the fitted line.

### MATHEMATICS

Entry: short residual if `z≥entry`, long if `z≤−entry`, provided `|z|<stop`. Exit near the recent mean if `|z|≤exit`, or on a holding/loss/exposure stop. Default entry/exit/stop are 2/.4/4. Beta-adjusted size uses `qY=floor(notional/(Y+|β|X))`, `qX=−round(βqY)`. Equal-notional sizing divides marked pounds across legs. Volatility sizing also caps `qY` by `volatility_budget/past_residual_SD`.

### QUANTLAB EXAMPLE

At t=81, the standard automated demo sees z≈3.558 and sells five Y. At t=82, it buys five X. A near-mean signal at t=92 requests closure; the last leg fills at t=93. This trade nets only £0.05 after actual execution.

### ASSUMPTIONS

Rules are committed before trading. New entries use the current available fit; open trades retain their entry fit and hedge. Stops can request liquidation but do not supply liquidity.

### COMMON MISTAKES

Changing thresholds after seeing the path; calling every profitable trade correct; forgetting unsupported estimates can cause no-trade outcomes; hiding marked residual inventory at the sample boundary.

### INTERVIEW QUESTIONS

Why distinguish a signal from an execution? What happens when the strategy wants to close but the book is empty?

## 12. Leg risk

### INTUITION

A pair is a plan involving two instruments. The exchange sees two independent orders. Between them, the first fill creates a position that may be largely unhedged. The second can fill partially or fail completely.

### MATHEMATICS

Unit-hedge mismatch is `qX+β_entry qY`; the displayed GBP imbalance is its absolute value times X. Gross exposure is `|qX X|+|qY Y|`. Net marked value and factor exposure are separate quantities. Imbalance-observations accumulate the mismatch over the observation intervals in which it was actually held.

### QUANTLAB EXAMPLE

Set X depth to one: one unit is available at the best price, four at the next. A larger pair can buy all requested Y while selling only five X. The remainder of that market order cancels. Set X depth to zero to produce no hedge fill at all. The Risk Lab reads those exact resulting positions.

### ASSUMPTIONS

The two requests are sequential. Clicking “next queued leg” without advancing prices still creates a separate execution event; advancing a price between them exposes temporal risk. External liquidity refreshes once per observation.

### COMMON MISTAKES

Assuming simultaneous perfect fills; computing P&L from desired instead of actual quantities; counting rounding mismatch and temporary exposure twice.

### INTERVIEW QUESTIONS

What is the exposure after only the first fill? How should a partial close appear in the accounts?

## 13. Transaction costs

### INTUITION

Buying usually pays an ask and selling receives a bid. Both legs also pay fees. A small theoretical convergence can disappear when four executions are needed for entry and exit.

### MATHEMATICS

For a fill, signed shortfall is `side_sign × quantity × (execution_price−current_public_reference)`, positive when costly. Net P&L equals marked price movement minus signed shortfall minus fees. A passive limit can have negative shortfall relative to the contemporaneous reference; that is disclosed rather than clamped to zero. Deeper-book slippage is included in the actual execution price.

### QUANTLAB EXAMPLE

The manual round trip earns £0.60 from marked movement, spends £0.20 on execution shortfall and £0.10 in fees, leaving £0.30. The same selected fixed-strategy path makes £6.55 with low costs and loses £0.25 with the larger spread/fee setting.

### ASSUMPTIONS

Fees are per executed unit; no fee is charged for cancelled remainder. Borrow costs, funding, queue competition, dynamic impact and forced margin liquidation are omitted and listed as model limitations.

### COMMON MISTAKES

Using mid-price fills; omitting the second leg's fees; charging fees on unfilled requests; adding spread costs twice after using actual bid/ask fills.

### INTERVIEW QUESTIONS

How do you reconcile P&L without double counting spread costs? Why can high turnover consume a small signal?

## 14. Walk-forward testing

### INTUITION

Pretend you deploy repeatedly through history: fit on the past, use that model on a block you have not yet seen, then move forward. This more closely resembles deployment than one full-sample fit, but still depends on the researcher's choices.

### MATHEMATICS

At a block boundary t, fit `[t−W,t)` and trade `[t,t+B)`. Fixed models retain their initial training vintage. Rolling models refit each observation. Walk-forward models refit only at block boundaries. The report distinguishes the latest fitted model from an open trade's retained entry model.

### QUANTLAB EXAMPLE

The registered comparison uses W=60, z-window=30 and B=20. It reports coefficient drift, incremental block P&L, turnover, peak-relative drawdown, closed-trade hit rate and residual range. A single completed seed improves under refitting; repeated evaluation measures whether that survives across seeds.

### ASSUMPTIONS

Training and test rows are chronological and no evaluation outcome changes the rules. In the generalisation/mining study, both scored blocks have equal lengths; the selected specification is refitted on past data at deployment. This is disclosed, so the difference is not attributed solely to overfitting.

### COMMON MISTAKES

Refitting with the next block included; overwriting old signals; comparing different time spans without disclosure; interpreting walk-forward as immunity to selection bias.

### INTERVIEW QUESTIONS

What is frozen within a block? Why might frequent refitting increase instability and costs?

## 15. Regime breakdown

### INTUITION

A relationship is a description of a process, not a law. Its slope, mean, volatility or persistence can change. A policy trained on an old relationship may then trade against a continuing divergence.

### MATHEMATICS

Controlled breaks can shift β by .15, move μ by £2, multiply residual innovation SD by four, replace φ with one, or add an idiosyncratic £.06 drift per observation. These are synthetic interventions, not estimated real-market probabilities.

### QUANTLAB EXAMPLE

The completed drift example loses £24.25 while its stable counterpart gains £5.35 under the specified old-fit policy. Other break paths can still profit. The report retains them rather than pretending every structural change must cause a loss.

### ASSUMPTIONS

The researcher knows the construction in completed observer examples. Live agents and snapshots do not receive the future break time or true changed parameters. The live warning uses observed z and exposure, not a secret regime flag.

### COMMON MISTAKES

Hard-coding losses after a break; using the hidden break time to stop before trouble; letting aggregate positive P&L hide damaged assumptions.

### INTERVIEW QUESTIONS

What would a historical relationship failure look like in live observations? Why can a stop fail to close the position?

## 16. Multiple testing

### INTUITION

Trying many hypotheses gives chance more opportunities to produce an impressive result. If you show only the winner, the audience cannot assess how much searching produced it.

### MATHEMATICS

For m independent tests, each with false-rejection probability a, the probability of at least one false rejection is `1−(1−a)^m`. At a=.05 and m=20 this is about .642. This is an intuition exercise, **not a p-value for the pair-mining leaderboard**. Candidate pairs share assets and are dependent; their outcome distribution must not use that independent-test formula mechanically.

### QUANTLAB EXAMPLE

The parameter study retains all 11 one-at-a-time candidates. The mining study retains all 28 pairs from eight unrelated assets. No Sharpe ranking or p-value claim is used; selection uses training net P&L with a declared tie-break.

### ASSUMPTIONS

The tested universe and selection criterion are recorded before opening the holdout. Formal Bonferroni/FDR procedures are not implemented in this phase.

### COMMON MISTAKES

Presenting the best result as a typical result; omitting failed parameter choices; treating dependent searches as independent tests; presenting a post-selection interval as unbiased evidence of alpha.

### INTERVIEW QUESTIONS

What information do you need about the search before trusting one excellent backtest? Why is the winner's estimate often optimistic?

## 17. Pair mining

### INTUITION

Pair mining makes the selection problem tangible. Start with many assets that have no true relationship. Search their historical combinations. Some will look appealing by chance, especially when using persistent price levels.

### MATHEMATICS

Eight assets generate `8×7/2=28` unordered pairs. Select the maximum **training** net P&L; break ties in declared index order. Save all candidates and the choice. Only then claim evaluation access and measure the selected specification on future rows. The selector's API does not accept the evaluation block.

### QUANTLAB EXAMPLE

The separately registered single-seed winner earns £12.92 in training but £0 on the holdout: its newly estimated positive-unit hedge is unsupported, so the strategy makes no entry. This is a failure to reproduce the historical opportunity, **not an executed trading loss**. Repeated Phase 5 evaluation also retains losing executed holdouts and reports their frequency. No evaluation seed is searched until a desired story appears.

### ASSUMPTIONS

The synthetic universe is fixed, so there is no silent delisting/survivorship filter. Real equity universes would need point-in-time membership, corporate actions and missing/delisted assets. Training selection is biased even when execution is perfectly simulated.

### COMMON MISTAKES

Quietly discarding zero-trade or losing winners; searching evaluation seeds for a persuasive example; reusing the test as a new training set while still calling it untouched.

### INTERVIEW QUESTIONS

What exactly was selected? When was the evaluation block accessed? Which failed and discarded candidates remain visible?

## 18. Model risk

### INTUITION

Every number in this lab is conditional on choices about prices, relationships, execution and risk. Reproducibility helps find errors; it does not make those choices true.

### MATHEMATICS

For actual inventories during an interval, exact marked movement is
`qY Δ(Y−β_entry X) + (qX+β_entry qY)ΔX`, plus other assets' movements if present.
The second component is a unit-hedge directional term, not automatically a true common-factor term. After signed execution shortfall and actual fees, the total must equal the Phase 6 ledger P&L. The reconciliation fails loudly beyond numerical tolerance. Temporary directional P&L is a **subset**, not another additive term.

Portfolio risk reuses Phase 9: current dollar exposures w and past sample return covariance Σ give linear variance `wᵀΣw`. A normal 95% VaR/ES describes one observation under that model. Linked cross-lab risk explicitly assumes zero cross-lab covariance and maps one stat-arb step to a risk day; this is a crude joint illustration, not a calibrated portfolio forecast.

### QUANTLAB EXAMPLE

An almost dollar-neutral pair still has nonzero unit-hedge exposure, estimated factor exposure and VaR. A profitable trade can exit before its residual reaches the near-mean criterion. A stop can leave residual inventory when liquidity is absent.

### ASSUMPTIONS

Exogenous prices; finite externally refreshed depth; no feedback impact; Gaussian innovations; no borrow/funding constraints; fixed capital definition; uncertainty conditional on the chosen process. Existing Risk Lab limits cover the original desks; Stat Arb safeguards have their own explicit scope.

### COMMON MISTAKES

Synthetic profit described as real alpha; false precision; browser code silently recomputing regressions; total P&L interpreted as evidence that the original reasoning was correct.

### INTERVIEW QUESTIONS

Which conclusions survive changing the process? What does a deterministic replay prove? Which important risks remain outside the model?

## Sources and implementation references

Numerical least squares and rank diagnostics follow [NumPy's least-squares documentation](https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html). The danger of regressions on wandering series is discussed in [Forecasting: Principles and Practice, regression evaluation](https://otexts.com/fpp3/regression-evaluation.html). A real formal cointegration test has specific hypotheses and critical values; see [statsmodels' Engle–Granger documentation](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.coint.html). QuantLab intentionally does not label its simpler descriptive AR tool as that test.
