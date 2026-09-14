# Phase 9 — Portfolio risk from first principles

The examples use actual QuantLab positions. Risk estimates describe hypothetical outcomes conditional on a model; they are not forecasts, maximum losses or regulatory capital. A precise number can be precisely wrong about the real world.

## PORTFOLIO EXPOSURE

### INTUITION

A portfolio is the collection of what you own and owe. Cash and a purchased option are different assets: paying premium exchanges cash for a contract, rather than immediately losing the entire premium. A short position is a negative holding. It benefits from a fall in that instrument's price and loses from a rise, all else equal.

Position size answers “how many?” Market value answers “what is it marked at now?” Risk exposure asks “how does that value respond to a change?” None substitutes for the others.

### MATHEMATICS

For quantity q, contract multiplier m and current unit mark P, position value is V=q*m*P. Stock has m=1. Equity=cash+sum(V). Gross exposure=sum(abs(V)); net exposure=sum(V). Long exposure=sum(max(V,0)); short exposure=sum(max(-V,0)), so gross=long+short and net=long-short. Cash is reported separately.

Net P&L=realised gross trading P&L+unrealised P&L+financing-fees. It also equals equity-initial capital. Both identities are checked against the existing accounts. Delta in stock units is q*m*per-unit delta. Delta exposure in pounds is delta*stock spot. Greeks add by underlying; offsetting delta on a different stock is not the same hedge.

### QUANTLAB EXAMPLE

One 30-day £100 call costs £230.2151 plus a £0.05 fee. Its midpoint value is £228.71505. It has delta 51.143575 stock units and vega £1,143.26204 per 1.00 change in annual volatility. A small premium can therefore represent much larger stock-equivalent exposure. The manual desk starts with £10,000 cash; adding that account increases initial capital and equity equally, not trading profit.

### ASSUMPTIONS

Marks are the existing option midpoint and public stock reference, not guaranteed liquidation prices. All instruments and liquidity are synthetic. QL-STOCK, QL-DESK and QL-SECOND are separate instruments. Underlying identities are retained by the reusable portfolio model. Risk-session drawdown starts at attachment because the previously independent desks did not share a historical clock.

### COMMON MISTAKES

Counting premium paid as both an immediate loss and an asset; forgetting the multiplier; cancelling different stocks' delta and claiming a hedge; adding cash to gross risky position value; comparing mixed-unit quantities as though one contract equalled one share.

### INTERVIEW QUESTIONS

Why can a £200 option carry £5,000 of delta exposure? How do you reconcile cash, equity and P&L? Which mark would you use to estimate an executable exit?

## COVARIANCE

### INTUITION

First measure each return's deviation from its own average. Multiply two deviations from the same observation. Two positive deviations or two negative deviations give a positive product: the assets moved together relative to their averages. Opposite signs give a negative product. Average those products.

### MATHEMATICS

For synchronised observations x_t and y_t, sample covariance is sum((x_t-mean(x))*(y_t-mean(y)))/(N-1). Sample variance is the same calculation with x=y. The N-1 denominator reflects estimating the mean from the same observations. Population covariance uses N when those observations define the entire population of interest. Covariance has squared-return units when both inputs are returns.

### QUANTLAB EXAMPLE

Returns A=[0.01,-0.01,0], B=[0.02,-0.02,0] have means zero. Their sample covariance is 0.0002. A's sample variance is 0.0001 and B's is 0.0004. The covariance matrix is [[0.0001,0.0002],[0.0002,0.0004]]. Its diagonal is individual variance; its off-diagonal is co-movement. Symmetry follows because x*y=y*x.

### ASSUMPTIONS

Rows must refer to the same time interval. QuantLab uses one-day simple returns, N-1 by default, explicit N when requested, and rejects missing rows unless listwise deletion is explicitly chosen. Listwise means dropping an entire incomplete row across all assets. It avoids mixing different observation sets across matrix entries, but can bias the sample if missingness is systematic. Two complete rows are the minimum, not evidence of a reliable estimate.

### COMMON MISTAKES

Using price levels instead of returns without saying so; mixing daily and annual moments; treating an estimated covariance as fixed truth; filling missing values with zero; allowing an asymmetric matrix to pass silently.

### INTERVIEW QUESTIONS

Why centre returns? Why N-1? What can change when observations are missing? Why must a covariance matrix be symmetric?

## CORRELATION

### INTUITION

Covariance depends on how volatile the individual assets are. Correlation removes that scale so you can compare the strength and direction of linear co-movement.

### MATHEMATICS

rho_ij=Sigma_ij/(sigma_i*sigma_j). Here sigma is the square root of variance. With positive variances, correlation lies in [-1,1] and its diagonal is one. If a variance is zero, correlation is undefined; QuantLab displays a dash. Covariance can be recovered as Sigma_ij=rho_ij*sigma_i*sigma_j.

### QUANTLAB EXAMPLE

A's daily volatility is 1.2%, the second stock's is 0.8%, and assumed correlation is 0.25. Their covariance is 0.012*0.008*0.25=0.000024. The dashboard displays both quantities, with their different units.

### ASSUMPTIONS

Correlation describes linear co-movement over a particular model or sample. It can change. Zero correlation does not generally imply independence; for example, a common heavy-tail scaling can generate dependence in extreme outcomes.

### COMMON MISTAKES

Calling covariance correlation; treating zero correlation as proof of independence; saying correlations always go to one in crises.

### INTERVIEW QUESTIONS

Why can covariance change even if correlation stays fixed? What does a crisis correlation scenario test?

## PORTFOLIO VARIANCE

### INTUITION

The portfolio moves when its components move. Squaring their combined movement creates individual squared terms and cross terms. Those cross terms are where diversification appears.

### MATHEMATICS

Variance=w^T*Sigma*w. For two assets this is w1²*sigma1²+w2²*sigma2²+2*w1*w2*cov12. Volatility is sqrt(variance). Fractional equity weights produce return variance. QuantLab's live risk report instead uses current delta exposure in pounds as w, so variance is GBP² and volatility is GBP. It does not divide by possibly small or negative equity.

When volatility is safely positive, marginal volatility_i=(Sigma*w)_i/volatility. Component volatility_i=w_i*marginal_i. Components sum to total volatility; an offset can have a negative contribution. At zero or nearly cancelled variance, the division is unstable, so contributions are unavailable with an explanation.

### QUANTLAB EXAMPLE

After the demo adds two actual stock exposures, its linear variance is 5,220.704529 individual terms +1,203.445808 cross terms=6,424.150337 GBP². Volatility is £80.150797. The two nonzero component-volatility contributions are £52.681041 and £27.469757.

### ASSUMPTIONS

This decomposition describes current linear delta risk under the selected covariance. It does not capture option curvature, volatility changes, funding costs or future trading decisions.

### COMMON MISTAKES

Adding standard deviations rather than variances and covariance terms; omitting the factor of two; confusing fractional weights with pound exposures; presenting contributions near zero variance as stable.

### INTERVIEW QUESTIONS

Derive the two-asset formula by squaring w1*R1+w2*R2. Why can a risk contribution be negative?

## DIVERSIFICATION

### INTUITION

A second position helps only if its movements offset or do not fully reinforce the first position's movements. The number of names is not a risk metric by itself.

### MATHEMATICS

For equal weights and equal individual volatility sigma, portfolio variance is sigma²*(1+rho)/2. With rho=1 the equal-weight portfolio is as volatile as either asset. With rho=-1 it cancels exactly under this ideal linear model.

Concentration is separate: position share_i=abs(V_i)/gross. Largest share identifies a dominant holding. HHI=sum(share_i²), with 1 for a single position and 1/N for N equal absolute values. Delta-value concentration is separately reported because option premiums can understate sensitivity.

### QUANTLAB EXAMPLE

The controlled £10,000 allocation study uses 1% daily asset volatility and equal zero expected return. One concentrated asset has £100 daily volatility. Two half-sized positions have £79.06 at correlation 0.25, £98.74 at 0.95, and £50 at -0.5. Identical perfectly correlated exposure stays at £100.

### ASSUMPTIONS

The comparison fixes individual volatility, budget and means. It is a hypothetical allocation study, not an unrecorded rebalance of the trading account. Small option-mark shares can coexist with substantial gamma or vega.

### COMMON MISTAKES

Claiming many names guarantee safety; ignoring shorts or leverage; assuming low estimated volatility proves low concentration.

### INTERVIEW QUESTIONS

Can a portfolio be less volatile than each of its assets? Why can a concentrated portfolio appear quiet in a short sample?

## VALUE AT RISK

### INTUITION

Arrange hypothetical losses from best to worst. VaR identifies a threshold far along that list. Outcomes beyond that threshold remain possible. It answers where the tail begins, not how far the tail extends.

### MATHEMATICS

Loss L=-P&L. VaR_alpha=inf{x:F_L(x)>=alpha}. For normal linear P&L, mean loss m=-w^T*mu*h and standard deviation s=sqrt(h*w^T*Sigma*w), giving VaR=m+z_alpha*s. At 95%, z is approximately 1.64485. This horizon scaling assumes IID daily moments and linear exposure; it is not applied to nonlinear option P&L.

Empirical VaR sorts N loss observations and selects one-based rank ceil(alpha*N). Full historical revaluation compounds non-overlapping daily return blocks, ages options and reprices the current portfolio. Full Monte Carlo draws joint daily returns, compounds them, and does the same repricing. Neither multiplies a one-day option VaR by sqrt(h).

### QUANTLAB EXAMPLE

After buying the call and selling 51 actual shares, 95% one-day delta-normal VaR is £0.2834. Historical full revaluation gives £3.8203; 5,000-path Monte Carlo gives £3.8233. The small delta-normal number omits theta and gamma. Full repricing remains conditional on unchanged IV in these ordinary return scenarios.

### ASSUMPTIONS

A negative VaR is allowed: it is a gain threshold under the specified model. The default historical sample is explicitly synthetic, separately seeded and not the live market's future. A user can supply synchronised observations. Sample coverage, omitted crises, dependence and nonstationarity matter. Horizons crossing an unsettled expiry are unavailable because a terminal-only scenario does not identify the earlier settlement price.

### COMMON MISTAKES

“VaR is maximum loss”; selecting the best-profit tail; silently flooring every negative VaR at zero; treating historical VaR as assumption-free; applying square-root time scaling to arbitrary option portfolios. The order-entry VaR limit explicitly uses nonnegative delta-normal risk, not the full-revaluation dashboard measure.

### INTERVIEW QUESTIONS

Why can a loss exceed VaR? Why may the three methods disagree without any implementation being wrong? What does delta-normal leave out?

## EXPECTED SHORTFALL

### INTUITION

Once you identify the bad tail, ask how severe its losses are on average. Two portfolios can cross the same VaR threshold yet behave very differently in the worst outcomes.

### MATHEMATICS

ES_alpha=(1/(1-alpha))*integral_alpha^1 VaR_u du. In an empirical sample, average exactly the worst (1-alpha)*N observations, taking a fractional observation at the boundary when necessary. This handles probability mass at the VaR cutoff. It is not always equal to averaging only losses strictly greater than VaR. Under this convention ES>=VaR.

For a normal loss variable, ES=m+s*phi(z_alpha)/(1-alpha), where phi is the standard normal density. This density measures how concentrated normal probability is near z; it is not a probability at a single point.

### QUANTLAB EXAMPLE

Two 100-observation samples both have 94 zero losses and five £10 losses. Their final losses are £20 and £200. Both have 95% VaR £10. The worst five losses average £12 in the first sample and £48 in the second. QuantLab shades histogram bins touching the tail but calculates the exact tail from individual observations, never histogram bins.

### ASSUMPTIONS

Tail estimates need tail data. With 100 observations at 99%, only one observation carries the empirical tail average. QuantLab warns below 20 effective tail observations; this threshold is a diagnostic, not proof of reliability above it.

### COMMON MISTAKES

Averaging the wrong tail, dropping all observations equal to VaR, counting an entire boundary atom when only part belongs in the worst tail, claiming more simulations eliminate model risk.

### INTERVIEW QUESTIONS

Why report ES beside VaR? How should ties at the cutoff be handled? What uncertainty remains with only five tail observations?

## STRESS TESTING

### INTUITION

Choose explicit adverse conditions and ask how today's held portfolio would respond. A stress is a what-if, not a realised transaction and not necessarily a likely forecast.

### MATHEMATICS

Stock change=q*S*r_scenario. Option change=q*m*(new BSM value-current BSM value). Cash carry=C*(exp(r*h/365)-1). An optional liquidation haircut subtracts basis_points/10000 times absolute current marked value. Attribution sums instrument changes plus cash carry. No stress result is posted to the realised-P&L ledger.

### QUANTLAB EXAMPLE

Named scenarios: NORMAL ages one day with unchanged spot/IV; EQUITY SELL-OFF moves all underlyings -10%; VOLATILITY SPIKE adds 20 volatility points; CORRELATION BREAKDOWN changes pair correlation to 0.9; LIQUIDITY SHOCK charges a 100-basis-point hypothetical haircut. COMBINED STRESS combines -10% spot, +20 vol points, +50 rate basis points, 100-bp haircut and correlation 0.9. Additional -5% equity and +5-point vol shocks are supplied. All unnamed parameters are zero. The UI also accepts custom shocks.

### ASSUMPTIONS

These are synthetic scenarios, not calibrated historical or regulatory stresses. A pure correlation change affects the distribution, not the deterministic current mark. The haircut is not a market-impact or order-book depletion model. Model-price changes freeze the existing midpoint/model basis, giving exactly zero scenario P&L at zero shock and zero time.

### COMMON MISTAKES

Treating a stress loss as already realised; confusing 20 vol points with a 20% relative increase; assuming a scenario is exhaustive; adding a correlation shock as an invented cash loss.

### INTERVIEW QUESTIONS

Which positions drive the loss? Which combinations were omitted? Why can a nominally adverse scenario benefit a particular portfolio?

## OPTIONS RISK

### INTUITION

Delta hedging removes a local slope. It does not flatten every curve or remove sensitivity to volatility and time. You can have almost no first-order stock exposure and still own valuable or dangerous option exposure.

### MATHEMATICS

Portfolio delta=sum(q*m*delta_option)+stock quantity. Gamma describes how that slope changes as spot moves. Vega describes response to a change in annual volatility; vega per one volatility point is vega/100. Theta describes calendar-time passage; daily theta uses annual theta/365. Rho describes response to the annual interest-rate input. Units matter before any addition or multiplication.

### QUANTLAB EXAMPLE

The hedged one-call portfolio has delta 0.143575, gamma 6.954844 and vega £1,143.26204 per 1.00. A +20-point volatility shock means dvol=0.20. Full repricing gains £228.527168 while actual trading P&L stays -£2.11105. A short option portfolio can lose under the same volatility shock. This is a consequence of positions and repricing, not a hard-coded reward or penalty.

### ASSUMPTIONS

The exercise uses European cash-settled vanilla options, ACT/365, sticky strike IV and BSM. It does not model stochastic volatility, jumps, early exercise, margin or transaction-dependent implied volatility. Different-underlying exposure is retained separately.

### COMMON MISTAKES

“Delta-neutral means risk-free”; forgetting the multiplier; using vega per 1.00 as though it were per one point; assuming the hedge remains neutral after spot changes.

### INTERVIEW QUESTIONS

What can hurt a delta-neutral short straddle? Why might a volatility increase help a hedged long call? How does time change the hedge?

## FULL REPRICING

### INTUITION

A Greek approximation is a local sketch of the pricing surface. Full repricing evaluates the chosen model at the new point. The difference between them tells you about approximation error, not necessarily real-world forecast accuracy.

### MATHEMATICS

Approximate option P&L=delta*dS+0.5*gamma*dS²+vega*dvol+theta*dt+rho*dr. Residual=full model change-approximate change. Cross derivatives and higher-order terms are omitted. The residual is displayed; it is never repaired away or forced into realised P&L.

### QUANTLAB EXAMPLE

For a +0.1% spot move in the hedged call book, full change is £0.0491135, approximation £0.0491318 and residual about -£0.0000183. For spot -8%, vol +12 points and rates +50 bps, full change is £266.8744, approximation £360.6057 and residual -£93.7312. Large mixed shocks make the local approximation less accurate in this example; that ordering is not a universal theorem for every portfolio.

### ASSUMPTIONS

“Full” means full evaluation of BSM under stated inputs, not an exact market outcome. Quote basis, liquidity, pricing model, horizon and exercise rules remain assumptions.

### COMMON MISTAKES

Calling model repricing an exact forecast; assuming gamma alone captures every nonlinearity; assigning the residual to unexplained realised losses.

### INTERVIEW QUESTIONS

What terms were omitted from the Taylor expansion? Why can two individually small shocks interact? What model risk survives full repricing?

## MODEL RISK

### INTUITION

Risk depends on the lens you use. Changing the return sample, tail shape, volatility, correlation or option model can change the answer even with the same current portfolio.

### MATHEMATICS

Write the estimate as Risk(positions, model, parameters, data, horizon, confidence). Monte Carlo sampling error shrinks with larger samples under suitable assumptions; model misspecification does not. A confidence interval across independent seed addresses measures simulation variation conditional on the registered design.

### QUANTLAB EXAMPLE

Across 128 pre-registered evaluation seeds, the executed short-straddle study has normal-shock mean ES £239.2451 and covariance-matched t(5) mean ES £360.6008. The tail model changes risk while keeping second moments fixed. In the sample-size study, the SD of estimated VaR across seeds falls from £11.0065 at 250 paths to £2.3898 at 5,000 paths. Neither result establishes a real-world forecast.

### ASSUMPTIONS

Studies register hypotheses before outcomes, retain all runs, use separate evaluation roots, track seed reuse, and regenerate worst observations. Pairing means shared Gaussian scenario innovations where the horizon agrees; transformed scenarios can differ. Horizon comparisons are explicitly unpaired. The stream-identity fingerprint records seed and generation contract rather than hashing every scenario draw.

### COMMON MISTAKES

Choosing the favourable seed after seeing outcomes; calling an inspected evaluation pool untouched; mistaking numerical precision or narrow conditional intervals for realism.

### INTERVIEW QUESTIONS

Which assumption matters most for this portfolio? How could you discover omitted risk? Why does reproducibility not prove validity?

## PORTFOLIO OPTIMISATION

### INTUITION

Optimisation finds weights that best answer a specified mathematical question under specified restrictions. Change the covariance, expected returns or restrictions and you change the answer.

### MATHEMATICS

Minimum variance minimises w^T*Sigma*w subject to sum(w)=1 and chosen bounds. Mean–variance minimises (lambda/2)*w^T*Sigma*w-mu^T*w, with risk-aversion lambda>0. Cash is an explicit zero-return, zero-variance asset in this teaching model. The solver first checks feasibility, then reports success, objective, budget residual, bound violation and constraints. It never returns failed weights as a successful portfolio.

### QUANTLAB EXAMPLE

With uncorrelated variances 0.01 and 0.04 and no cash allocation, the minimum-variance weights are 80% and 20%, yielding variance 0.008. In the actual three-factor demo's allocation study, a 40% risky-asset cap and exactly 20% cash give weights 14.347826%, 25.652174%, 40%, 20%. Budget=100%; variance=0.000028852174. A fully invested two-asset long-only portfolio with a 40% cap on each asset is infeasible, rather than secretly given weights that violate the cap.

### ASSUMPTIONS

Expected returns are synthetic daily inputs, not reliable forecasts. Shorting is bounded when allowed. Minimum variance can legitimately choose all cash if allowed; maximum cash can require investment. The frontier lists constrained synthetic risk/return targets, including infeasible targets. It is not an investment opportunity guaranteed by the future. Allocation weights do not transfer cash or rebalance accounts; actual trades are separate.

### COMMON MISTAKES

Trusting the solver flag without checking constraints; hiding covariance regularisation; using unstable inverse matrices; claiming historical mean returns are facts about the future.

### INTERVIEW QUESTIONS

What changes when shorting is disallowed? Why can small expected-return errors move weights sharply? Why is all cash sometimes the correct mathematical answer?

## CORRELATED MONTE CARLO

### INTUITION

Start with independent random shocks. Mix them with a matrix so that shared movements have the intended strength. Reprice the held portfolio under every joint scenario, then calculate losses and their tail.

### MATHEMATICS

Independent standard-normal Z has mean zero and identity covariance. If Sigma=L*L^T, then LZ has covariance Sigma. For positive definite matrices, Cholesky supplies a triangular L. For singular positive semidefinite matrices, an eigenfactor V*sqrt(D) works, with zero eigenvalues representing redundant directions. A genuinely indefinite matrix is rejected because it would imply negative variance in some direction.

Daily arithmetic returns are mu+LZ. Multi-day terminal return is product(1+daily_return)-1. For a covariance-matched multivariate Student t with degrees of freedom nu>2, multiply the common Gaussian vector by sqrt((nu-2)/U), where U is an independent chi-square draw with nu degrees of freedom. The shared scale produces heavier tails while preserving covariance. QuantLab uses nu=5 in the UI comparison.

### QUANTLAB EXAMPLE

The default three-factor model uses daily volatilities 1.2%, 1%, 0.8% and pair correlation 0.25. Each scenario moves all three factors together, so the actual stock and option positions see a coherent joint state. Tests recover the target sample covariance from 100,000 draws within statistical tolerances and check full vector option prices against the existing scalar BSM implementation.

### ASSUMPTIONS

Daily draws are IID under this model. Arithmetic returns at or below -100% are rejected, never clipped or resampled silently. Negative covariance eigenvalues within numerical tolerance may be truncated only in the disclosed singular-factor fallback; no statistical regularisation is automatic. Analysis and historical-sample seeds are independent of market RNG. Summary and retained-loss modes produce identical risk numbers. Replay requires the recorded QuantLab, Python, NumPy and SciPy versions.

### COMMON MISTAKES

Independent draws with a nonzero correlation label; assuming any symmetric matrix is valid; silently fixing negative eigenvalues; reusing the live market RNG for analysis; treating simulated price paths as privileged knowledge of the actual future.

### INTERVIEW QUESTIONS

Why does LZ have covariance Sigma? What is a PSD matrix? Why can Cholesky fail on a valid but singular covariance? How do you validate the simulated dependence statistically?

## Primary references

The covariance denominator and orientation conventions are checked against [NumPy covariance documentation](https://numpy.org/doc/stable/reference/generated/numpy.cov.html). Positive-definite factorisation requirements are documented in [NumPy Cholesky](https://numpy.org/doc/stable/reference/generated/numpy.linalg.cholesky.html). The constrained solver and stopping controls are documented in [SciPy SLSQP](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html). The discrete-tail distinction follows the distribution-aware definition discussed by [Rockafellar and Uryasev, Conditional Value-at-Risk for General Loss Distributions](https://www.sciencedirect.com/science/article/pii/S0378426602002716). QuantLab's specific finite-sample convention is stated and independently tested above; these sources do not validate its synthetic market assumptions.
