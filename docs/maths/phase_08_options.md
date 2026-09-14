# Phase 8: options, Greeks and hedging from first principles

Read this beside the Options Lab. Numbers come from its Python engines. The live
lab has one synthetic stock, European cash-settled options and zero dividends.
Standalone pricing and Monte Carlo additionally support a constant continuous
dividend yield. Synthetic results do not establish real-market profitability.

## 1. Options basics

**Intuition.** A call gives its holder the right to buy at a fixed **strike**. A put
gives the right to sell at that strike. The buyer pays a **premium** for the right;
the seller receives premium and accepts the corresponding obligation. **European**
means exercise occurs at expiry. Cash settlement pays the equivalent exercise
payoff without exchanging stock.

**Mathematics.** With expiry stock price $S_T$, strike $K$, signed contract count
$n$, and multiplier $m$:

- Call payoff per underlying unit: $\max(S_T-K,0)$.
- Put payoff per underlying unit: $\max(K-S_T,0)$.
- Signed position settlement: $nm\times\text{payoff}$.
- Premium cash flow: $-nm p$, with execution premium $p$ per underlying unit.

Positive $n$ means long, negative means short. Fees are separate. One contract
represents $m$ underlying units; one contract is not necessarily one share.
ACT/365 means 30 model days is exactly $30/365=6/73$ model years. Wall-clock dates
and local time zones do not change this simulated expiry.

**QuantLab example.** One call at strike £100, expiry day 30, multiplier 100 costs
£2.302151 per unit at the opening ask: premium £230.2151 plus £0.05 fee.
At expiry stock £100.77, settlement is $100(100.77-100)=£77$.
Receiving £77 is not £77 profit: the premium was paid earlier.

**Moneyness and time value.** A call is ITM when stock exceeds strike; a put is ITM
when stock is below strike. ATM means equal; OTM means immediate intrinsic payoff
is zero. Intrinsic value substitutes current $S$ for $S_T$. Time value is premium
minus current intrinsic. This difference can be negative for a European option
under some rates/dividends, because immediate exercise is unavailable. ITM does
not mean the purchaser has made a profit.

**Assumptions.** Cash settlement, fixed multiplier, no early exercise, assignment,
tax or margin. A short call can have very large losses; borrowing and position
limits here are not a realistic capital model.

**Common mistakes.** Calling premium immediate profit, forgetting the multiplier,
mixing days and years, or rewriting an expired payoff using a later stock price.
QuantLab records the expiry reference once.

**Interview questions.** Why can an ITM call lose money? How do the buyer's right
and seller's obligation differ? What changes under physical settlement?

## 2. Black–Scholes–Merton and parity

**Intuition.** An option pays different amounts in different future states. The
model values that contingent payoff through idealised replication and discounting.
It does not reveal which state will happen. Risk-neutral pricing is a valuation
construction, not a forecast that people are indifferent to risk. The primary
[MIT option-pricing lecture](https://ocw.mit.edu/courses/15-450-analytics-of-finance-fall-2010/0d1260b891a96241316d883d4f5bfaec_MIT15_450F10_lec02.pdf)
develops the replication argument.

**Mathematics.** $S$ is current stock, $K$ strike, $T$ remaining years, $\sigma$
annual decimal volatility, $r$ continuously compounded rate, and $q_d$ continuous
dividend yield. $N$ is the standard normal cumulative probability; $\phi$ its density.
For positive $T,\sigma$:

$$
d_1=\frac{\log(S/K)+(r-q_d+\sigma^2/2)T}{\sigma\sqrt T},
\qquad d_2=d_1-\sigma\sqrt T.
$$
$$
C=Se^{-q_dT}N(d_1)-Ke^{-rT}N(d_2),\qquad
P=Ke^{-rT}N(-d_2)-Se^{-q_dT}N(-d_1).
$$

The discount factor $e^{-rT}$ converts a future amount to present value. Logarithms
measure proportional stock/strike distance. Dividing by $\sigma\sqrt T$ scales
that distance by the model's uncertainty. Prices are per underlying unit.
The code evaluates the out-of-the-money tail first, then uses parity for the
in-the-money side to reduce cancellation error. Expiry and zero volatility have
explicit limiting formulas.

Put-call parity:

$$ C-P=Se^{-q_dT}-Ke^{-rT}. $$

Call plus discounted strike and put plus discounted stock have matching expiry
payoffs under the same assumptions, supporting equal model prices.

**QuantLab example.** $S=K=100,T=1,\sigma=.20,r=.05,q_d=0$ gives call £10.45058357
and put £5.57352602. Difference £4.87705755 equals $100-100e^{-.05}$.
Six additional numerical benchmarks, including dividend-paying cases, come from
the primary [QuantLib European-option tests](https://github.com/lballabio/QuantLib/blob/master/test-suite/europeanoption.cpp).

**Assumptions.** European exercise, constant rate/volatility/yield, lognormal stock,
no arbitrage and frictionless continuous replication. The synthetic market adds
spreads, finite depth, fees, whole shares and discrete hedging. The theoretical
assumptions are not claims about real markets.

**Common mistakes.** Entering 20 instead of .20 for 20%; using physical expected
return in pricing; calling every rounded midpoint parity gap free arbitrage.
Check identical contracts, settlement, dividends, executable bid/ask, fees,
funding, shorting and available quantity.

**Interview questions.** Why does high physical expected return not simply raise
the Black–Scholes price? Why does parity require matching contracts?

## 3. Greeks and finite differences

**Intuition.** Change one input slightly while holding others fixed. Delta is the
slope of option value as stock changes; gamma is how quickly that slope changes.
Vega, theta and rho describe volatility, elapsed time and rate sensitivities.
They are local measurements, not guaranteed profits or complete risk measures.

**Mathematics.**

| Greek | Definition | Call | Put |
|---|---|---|---|
| Delta | $\partial V/\partial S$ | $e^{-q_dT}N(d_1)$ | $e^{-q_dT}(N(d_1)-1)$ |
| Gamma | $\partial^2V/\partial S^2$ | $e^{-q_dT}\phi(d_1)/(S\sigma\sqrt T)$ | Same |
| Vega | $\partial V/\partial\sigma$ | $Se^{-q_dT}\phi(d_1)\sqrt T$ | Same |
| Theta | $-\partial V/\partial T$ | Calendar-time convention | Calendar-time convention |
| Rho | $\partial V/\partial r$ | $KTe^{-rT}N(d_2)$ | $-KTe^{-rT}N(-d_2)$ |

Writing $A=-Se^{-q_dT}\phi(d_1)\sigma/(2\sqrt T)$:

$$
\Theta_C=A-rKe^{-rT}N(d_2)+q_dSe^{-q_dT}N(d_1),
$$
$$
\Theta_P=A+rKe^{-rT}N(-d_2)-q_dSe^{-q_dT}N(-d_1).
$$

Vega/rho are per **1.00 absolute annual decimal** change. Divide by 100 for one
percentage point: .20 to .21 is .01. Theta is per model year; daily display divides
by 365. This daily convention is a local rate, not exact one-day repricing.
Multiply by signed quantity and multiplier for position Greeks; sum across options.
Stock contributes one delta per unit, zero option gamma/vega/theta.

**QuantLab example.** The one-year call has delta .63683065, gamma .01876202,
vega 37.52403469, theta −6.41402755/year and rho 53.23248155. For one 100-unit
contract, a £.10 stock rise gives first-order change about £6.3683; one volatility
percentage point gives about £37.5240; daily theta is about −£1.7573.
These are separate small-input thought experiments, not forecasts of one day.

Finite differences independently reprice nearby inputs:

$$
\Delta_{FD}\approx\frac{V(S+h)-V(S-h)}{2h},\qquad
\Gamma_{FD}\approx\frac{V(S+h)-2V(S)+V(S-h)}{h^2}.
$$

Vega/rho change their own inputs; theta negates the remaining-time derivative.
Too large a step introduces approximation error; too small amplifies floating-point
roundoff. Tests use sensible absolute/relative tolerances, not exact equality.

**Assumptions.** These are fixed-volatility partial derivatives. As the synthetic
smile moves with moneyness, actual value changes may also contain vega effects.
Expiry at strike is a payoff kink: undefined derivatives are labelled.

**Common mistakes.** Call delta is not literally real-world ITM probability.
$N(d_2)$ has a risk-neutral terminal-event interpretation in this model; delta uses
$N(d_1)$ and dividend discounting. Neither gives a literal real-world forecast.
Long gamma is normally positive; signed short quantity reverses it. Theta can be
positive, especially for puts with carry effects. Do not mix daily and annual
theta, or per-unit and per-contract vega.

**Interview questions.** Why can a delta-neutral short-gamma position lose?
Why can theta be positive? What does a finite-difference mismatch suggest?

## 4. IV and numerical root finding

**Intuition.** Turn the pricing model around: which volatility reproduces an
observed premium? That is implied volatility, conditional on all other inputs.
It is neither future realised volatility nor proof that the model is correct.
Here it is inferred from a **synthetic** quote midpoint.

**Mathematics.** Solve

$$ f(\sigma)=V(\sigma)-p_{target}=0. $$

Newton follows the local slope:

$$ \sigma_{new}=\sigma-\frac{f(\sigma)}{\operatorname{vega}(\sigma)}. $$

Vega is the derivative of price with respect to volatility. Tiny vega can turn a
small price error into an enormous suggested volatility move. A poor guess can
jump outside the allowed interval.

The solver first checks discounted bounds. Calls lie between
$\max(Se^{-q_dT}-Ke^{-rT},0)$ and $Se^{-q_dT}$; puts use the reversed lower
difference and upper $Ke^{-rT}$. Finite IV requires separation from the upper
bound. Prices numerically indistinguishable from the zero-volatility lower bound
cannot identify IV reliably. Expiry has no IV; impossible prices reject explicitly.

A bracket has model prices on opposite sides of the target. Bisection halves the
interval while retaining the root. QuantLab brackets within [0,5], uses safe Newton
steps, and otherwise bisects. Price residual and volatility convergence are checked.
Boundary ambiguity, no bracket or iteration exhaustion returns no reliable IV;
the latest iterate is never labelled a successful answer merely because time ran out.

**QuantLab example.** For $S=100,K=120,T=.25,r=.05,\sigma=.30$, call value is
£1.04916322. Starting at .001 gives numerically zero vega. One bracket step then
four Newton steps converge in six evaluated iterations to .3000000000000035,
with residual about $3.73\times10^{-14}$.

**Assumptions.** Contract inputs are known, the target has enough precision, and the
model's monotone price-volatility relationship applies. Numerical accuracy does
not remove quote noise. A tiny premium change can imply a large IV change when
vega is low. Solver tolerance is not an economic confidence interval.

**Common mistakes.** Treating nonconvergence as an answer; solving impossible prices;
calling synthetic IV real-market IV; equating printed decimals with information.
A midpoint may contain seven decimals when bid and ask have six.

**Interview questions.** Why is bisection safer but often slower? Why can a small
pricing residual coexist with an uncertain volatility estimate?

## 5. Delta hedging, gamma, theta and local approximations

**Intuition.** If options gain about £51 for a £1 stock rise, shorting 51 stock
units offsets that immediate sensitivity. Stock and time then change, changing
delta. The original hedge is no longer necessarily appropriate.

**Mathematics.** Portfolio delta is $D=\sum_i n_i m_i\Delta_i+H$, with signed stock
holding $H$. Nearest whole-stock target:
$H^*=\operatorname{round}(-\sum_i n_i m_i\Delta_i)$; trade $H^*-H$.
Rounding uses nearest integer, ties to even. Short 10 contracts, delta .60,
multiplier 100 gives −600 option delta, requiring +600 stock units.

Taylor's local approximation:

$$
\Delta V\approx\Delta\,\Delta S+\tfrac12\Gamma(\Delta S)^2+
\operatorname{vega}\,\Delta\sigma+\Theta\,\Delta t+\rho\,\Delta r.
$$

Here $\Delta t$ is elapsed years, so calendar theta has the correct sign. Curvature
comes from the second-order stock term. Cross terms and higher orders are omitted.
The shock lab compares this with exact repricing and shows the error. Large shocks
should not be expected to fit a local approximation.

**QuantLab example.** Buy the day-30 call: delta +51.1436. A real market sale of 51
stock units at £99.99 leaves +.1436. Day 1 stock £100.21 gives option delta +52.6071:
the old hedge leaves +1.6071. Sell two more units at £100.20, leaving −.3929.
The demo deliberately leaves that hedge unchanged until expiry; it illustrates
sparse manual hedging, not an optimal policy.

Long options conventionally have positive gamma and often negative theta. A delta
hedge removes the local linear term, leaving curvature, time, volatility, funding
and execution effects. “Gamma good, theta bad” overlooks the cost of convexity and
the realised path.

**Assumptions.** Stock shorting/borrowing are available. Actual fills depend on the
book; partial fills, position limits and self-trade prevention can leave exposure.
The benchmark submits genuine stock orders. Ending a session marks remaining
holdings; it does not invent closing trades.

**Common mistakes.** Directly setting holdings to a target; ignoring fees/spread;
double-counting premiums and profit; assuming delta neutrality means no risk.
Stock acquired for a hedge is an asset financed by a cash outflow.

**Interview questions.** How does discrete trading break continuous replication?
Why does more frequent hedging not guarantee higher net P&L?

## 6. Realised versus implied volatility and research

**Intuition.** IV is inferred from today's price. RV summarises past movements.
Process volatility is a simulation parameter, not a promise about a finite sample.

**Mathematics.** Log returns $u_j=\log(S_j/S_{j-1})$ give close-to-close quadratic
variation:

$$ \widehat\sigma_{RV}=\sqrt{\frac{\sum_j u_j^2}{N\Delta t}}. $$

The sample mean is not subtracted. Drift, sampling frequency and tick rounding
affect a finite sample. Twenty observations give a noisy estimate.
Under restrictive continuous-hedging assumptions, the intuition for a long option
includes $\tfrac12\Gamma S^2(\sigma_{realised}^2-\sigma_{implied}^2)dt$.
This is not the simulator's P&L rule: actual premiums, fills, settlement and funding
produce the reported P&L.

**QuantLab example.** At fixed 20% quote volatility, 1,000 daily-hedged twenty-day
long-call paths with process settings 15%, 20%, 30% realised mean RV 14.898%,
19.864%, 29.797%; mean net P&L was −£50.98, −£3.89, +£90.92.
These are conditional averages, not guaranteed per-path orderings.

The frequency study uses exactly matched stock paths for every-1, every-5,
every-20 and no hedge. Volatility variants share standard-normal innovations,
scaled differently. Phase 5 registers hypotheses before execution, retains every
run, calculates distributions/paired uncertainty and reproduces extreme sessions
with full execution evidence. These are development seeds, not untouched evaluation.

**Assumptions.** Constant drift/volatility within each scenario, no jumps, and no
trading impact on the future exogenous process. Dealer liquidity is synthetic.
The frequency experiment uses a flat smile to isolate hedge frequency. General
live smile parameters are not a calibrated or arbitrage-free volatility surface.

**Common mistakes.** “Buy whenever RV exceeds IV” ignores unknown future RV,
gamma weighting, discrete hedges, costs and model error. Complete sessions,
not correlated fills, are independent observations. Explicit fees are separate;
bid/ask concessions already enter fill prices and P&L. Subtracting them again
double-counts costs. Interval RMS delta is a grid-based exposure measure, not a
continuous intraday risk estimate; daily hedging still has gap and gamma risk.

**Interview questions.** Why use common random numbers? Why can similar RV values
produce different hedging P&L?

## 7. Monte Carlo pricing

**Intuition.** Draw many possible terminal stock prices, calculate their payoffs,
discount and average. More samples stabilise the average but do not remove model error.

**Mathematics.** Under the risk-neutral pricing measure:

$$ S_T=S\exp((r-q_d-\tfrac12\sigma^2)T+\sigma\sqrt T Z),\quad Z\sim N(0,1). $$

The $-\sigma^2/2$ correction gives the lognormal process its intended mean growth.
IID means independent draws from the same distribution. For discounted payoffs
$X_i$, estimate $\bar X$, with standard error $s_X/\sqrt N$ using sample standard
deviation $s_X$. Phase 5 supplies a Student-t mean interval. For nonnormal payoffs
this is a large-sample approximation, not a guarantee for every run.

**QuantLab example.** For the one-year call, seed 42 gives £10.473643 with 100,000
paths (SE £.046701), then £10.451306 with 1,000,000 (SE £.014734), against analytical
£10.450584. Identical seeds reproduce results. The pricing random stream is
independent of the live stock stream and cannot consume or reveal its future.

**Assumptions.** Same payoff, yield, volatility, risk-neutral drift and discounting
as analytical pricing. Physical drift for trading experiments is a separate input.
Intervals measure sampling uncertainty, not model error. When a stochastic sample
has no payoff variation, a warning explains that a zero-width interval cannot
resolve unsampled rare tails.

**Common mistakes.** Standard deviation describes payoff dispersion; standard
error describes uncertainty in the mean. Halving SE needs roughly four times
as many paths. Analytical pricing is faster for these vanilla European options;
simulation here is a teaching and validation tool.

**Interview questions.** Why is pricing drift $r-q_d$? Why does Monte Carlo converge
slowly? What uncertainty remains after a million paths?
