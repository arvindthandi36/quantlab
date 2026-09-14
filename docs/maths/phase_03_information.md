# Phase 3 model contract — defined before implementation

Owner: **Arvind Thandi**. Scope: informed flow and markouts only; no Phase 4 accounts,
market-making strategies, inventory management or P&L engine.

## Intuition and information boundaries

Normal agents receive only `PublicObservation`: best bid, best ask, last transaction
and configured opening reference. They receive neither the observer journal nor
the seed, latent state, signal, signal error, private estimate or future events.

At each informed arrival the signal service samples a **fresh noisy measurement
of the current latent value**. The informed agent receives that measurement, its
timestamp and stated noise level, plus ordinary public observations. It cannot
see the actual error or latent value. The observer debug log can show both.
No signals forecast, sample or read the future. Equal-time events follow the
existing scheduling-order convention; only updates already processed can be sensed.

Public output exposes submitted orders and executions, with anonymous order IDs.
It excludes private decisions, trader type, held/abstained decisions, latent-only
events, root seeds and private model configuration. The full session/journal is
explicitly observer research data, not a public snapshot or an agent input.

## Mathematics: signal and accuracy

In tick units, at informed arrival time t:

\[
Y_t=X_t+\varepsilon_t,\qquad \varepsilon_t\sim N(0,\eta^2).
\]

X is current latent value, Y the observed signal, and η its measurement-error
standard deviation. η must be strictly positive. Defaults: η = 2 ticks, so the
root-mean-square measurement error is two ticks (£0.02 with a penny tick).
Errors are independent of latent shocks and arrival draws. Some observations can
be very inaccurate; no assumption makes the informed trader infallible.

## Estimated value: a deliberately simple belief

Each arrival uses a new one-observation Gaussian belief, not a stateful filter.
Before its signal, the agent assumes X has mean m (the same public reference used
by noise traders) and standard deviation τ = 8 ticks. This is a **subjective prior**;
the simulator does not guarantee that its evolving book implies this distribution.

With that assumed normal prior and normal measurement error:

\[
w=\frac{\tau^2}{\tau^2+\eta^2},\qquad
\widehat X=m+w(Y-m),\qquad
u=\frac{\tau\eta}{\sqrt{\tau^2+\eta^2}}.
\]

The estimate is the conditional mean **under these assumptions**; u is posterior
standard deviation. Cleaner signals increase w and reduce u. The agent does not
pretend the raw signal is truth. Positive measurement noise, uncertainty about X,
possible prior misspecification and absence of future data all prevent perfect
information. A Gaussian belief can be unrealistic near a positive price boundary.

This is the one-observation normal-prior/normal-likelihood update discussed in
[Faming Liang's Purdue Bayesian inference notes](https://www.stat.purdue.edu/~fmliang/STAT611/st611ch7Bayes.pdf).
The public reference m uses midpoint rounded to the nearest tick, half up, if both
quotes exist; otherwise it uses the last transaction, then the opening reference.
That rounding is a belief convention, not rounding of submitted order prices.

## Decision rule and costs

Defaults, all per unit and in ticks: execution-cost allowance c = 0.25, minimum
extra edge b = 0.25, uncertainty multiplier z = 0.5. The required gross edge is

\[
H=c+b+zu.
\]

Buy edge is estimated value minus available ask; sell edge is available bid minus
estimated value. Buy one unit at the best ask only if buy edge **strictly exceeds**
H; sell one at the best bid only if sell edge strictly exceeds H. Otherwise hold.
Absent quotes provide no executable opportunity. On an uncrossed book both sides
cannot qualify simultaneously. The instruction is a one-unit limit at the observed
opposing quote, processed atomically; it cannot sweep into a worse price level.

The spread is already included by comparing against the executable quote, not
the midpoint. c is an explicit hypothetical execution-cost allowance, not a fee
ledger or a claim of realised profit. The uncertainty buffer is a conservative
decision heuristic, not an optimal strategy or a confidence guarantee under a
misspecified prior. No decision is tuned using its later markout.

The buffer covers uncertainty in the current value estimate, not all future price,
financing or inventory risk. There is no chosen holding period or exit strategy.

## Markouts and maturity

For each execution at price P, let d = +1 if the resting provider bought and −1 if
the provider sold. For a reference R at horizon h:

\[
M_h=d(R_h-P)=d(R_0-P)+d(R_h-R_0).
\]

M is a per-unit **provider markout**, not realised P&L. Positive is favourable to
the resting provider; negative means the later reference makes that execution
look adverse. The first component is its initial reference edge; the second is
the subsequent signed reference move. When R is the pre-trade public midpoint,
the first component is a spread-capture proxy, not guaranteed revenue.

Use h = 1, 5 and 20 subsequent processed market events, excluding the trade's own
event. R0 is measured immediately before the whole incoming order; Rh is the
post-event reference at the exact maturity event. Same-time events still count
separately. These are event horizons, not seconds or regulatory reporting windows.

Compute **two separately labelled references**: public midpoint and observer-only
latent value. Never substitute latent/last-trade values for missing midpoints.
A missing future midpoint makes that midpoint markout unavailable. A missing R0
prevents decomposition but not M if Rh exists. Unreached horizons remain pending;
no last-observation or end-of-run substitution. An explicit as-of event count
prevents future data from appearing in a markout before it matures.

Event-horizon observer analytics are not emitted in the ordinary public view:
even private abstentions influence the internal event count. A future public
analytics product would need its own public-event or elapsed-time convention.

The decomposition is related to the execution-quality distinction between initial
spread and later price movement discussed in the
[SEC's 2024 execution-information release, note 1228](https://www.sec.gov/files/rules/final/2024/34-99679.pdf).
Our per-unit, provider-signed event markout is not a Rule 605 report; it has no
factor of two, uses this simulated book, and has different horizon conventions.

## First-principles lesson

### 1. A noisy signal is an imperfect measurement

Imagine a thermometer that reads a little high or low. There is a true temperature,
but you see only its reading. Here X is the simulated truth, Y the reading and ε
the measurement error. The agent sees Y and how unreliable the instrument usually
is; it does not get to subtract the actual error.

`N(0, η²)` means a bell-shaped error distribution centred at zero. Zero is its
long-run average error, not the error of every observation. Variance η² averages
squared error; standard deviation η takes its square root to restore price units.
With η = 2 ticks, roughly 68% of errors lie within ±2 ticks and 95% within ±4 ticks.
These are distribution frequencies, not hard limits. A very bad reading is possible.

### 2. Conditional expectation means an average after learning something

An expectation is a probability-weighted average of possibilities. Conditional
expectation recomputes that average after receiving evidence. Before a signal,
the agent centres its possible values at public reference m. After a high signal,
higher values receive more weight; an unreliable instrument shifts the average less.

The expression `E[X | Y]` reads “average possible X given the observed Y.” In this
model its calculated version is m + w(Y − m): start at m and move a fraction w of
the way toward the reading. A **prior** is the belief before the reading; a
**posterior** is the belief after it. Neither word guarantees that the belief is right.

With τ = 8 and η = 2, w = 64 / 68 ≈ 0.941. The model weights the signal about 94.1%
and the public anchor about 5.9%. Remaining uncertainty u ≈ 1.940 ticks. Those
numbers follow from the assumed uncertainties; they were not fitted to this demo.
The model resets this belief at every arrival; it does not combine old readings.

### 3. Expected edge must be measured against a price you can execute

An estimated value of £100.08 does not justify buying if the available seller
requires £100.10. Buying uses the ask, selling uses the bid. Estimated gross buy
edge is estimate − ask. Estimated gross sell edge is bid − estimate.

The default hurdle is 0.25 + 0.25 + 0.5 × 1.940 = 1.470 ticks per unit. The first
quarter-tick allows for assumed execution costs, the second requires extra edge,
and the last term adds caution about estimate uncertainty. Fractional-tick costs
are allowed even though submitted prices must lie on the whole-tick grid.

In the actual demo, the estimate is £99.9825 and a buyer is bidding £100.01.
Estimated sell edge is about £0.0275, greater than the £0.0147 hurdle, so one unit
sells at that bid. Equality would produce a hold; the rule requires strictly more.
Estimated net edge after the cost allowance is edge − c; neither is realised P&L.

### 4. Information quality changes discrimination

Making η larger makes the same numerical reading less persuasive: w falls and
the posterior uncertainty increases. Better information can encourage a trade
when there is a real gap. It can also prevent an unnecessary trade caused by a
bad measurement when price is already fair. There is no universal rule that
cleaner signals must produce more total orders.

Our statistical tests distinguish these situations. They check estimation error
under the assumed prior and, separately, repeated decisions at fair and stale
quotes. Tests use fixed seeds and sampling-error tolerances, not exact stochastic
counts chosen after looking at the results.

### 5. Selection is about which quotes get accepted

A resting seller is a **liquidity provider**: its order waits for someone to take
it. An informed buyer is a **taker** when it accepts that offer. If takers are more
likely to accept offers that are cheap relative to value, the seller's executions
are an unfavourably selected subset of all its potential trades. That is adverse
selection. The matching engine does not need a rule assigning losses to sellers.

For this zero-drift latent walk, future latent increments still have zero mean
even after an informed order. The signal is about today's hidden value, not the
next random shock. The provider can already have traded at a stale price relative
to current hidden value; a later reference makes that visible. A later public
midpoint may also move as actual orders remove or replace quotes. The simulator
does not force it toward latent value after a fill.

### 6. Markouts answer a direction-specific question

For a seller, ask: “Did I sell above or below the later reference?” Selling at
£100.05 with later reference £100.08 gives £100.05 − £100.08 = −£0.03 per unit.
With later reference £100.02 it gives +£0.03. For a buyer, reverse the subtraction:
later reference minus purchase price. The sign convention is always the provider's.

The compact formula d(Rh − P) handles both directions. d is +1 for a resting buyer
and −1 for a resting seller. Positive is favourable, negative adverse, zero equal
to the later reference. There may be no actual exit at that reference price.

A midpoint is halfway between the best bid and ask; it is not itself necessarily
an executable price. Latent value is a model diagnostic, not a public quote.
Longer horizons include more unrelated movement. One bad markout is a reason to
investigate, not proof that the other trader had information.

### 7. Why the statistical tolerances are not exact identities

The mean of n random measurements also varies between samples. Its **standard
error** is the standard deviation of that sample mean: for independent errors of
standard deviation η it is η / √n. More observations make the average more stable.
Normal-sample variance has standard error η²√(2/(n−1)). The tests allow six such
standard errors for moment checks, a deliberately broad regression tolerance.

For paired comparisons, we reuse a standardised shock in both settings and test
their within-pair differences. This accounts for their shared randomness; treating
them as unrelated samples would misdescribe the comparison. Fixed seeds make test
failures reproducible. These checks catch distribution/decision bugs; they do not
validate the market against real observations or promise financial performance.

## Assumptions and failure cases

This keeps Phase 2's independent Gaussian latent walk and simple background flow.
It adds no forced losses or price move after an informed fill. Bad provider
markouts can arise because better-informed takers select stale prices. Individual
informed trades can still be wrong. A negative markout alone does not identify
the cause: market movement, quote depletion and other orders can also contribute.

The prior is not a fitted filter; orders are one unit; costs are assumed; there
is no financing, inventory or risk capital. Midpoints can disappear. Reference
selection and horizon length affect conclusions. Markouts do not establish
strategy profitability, real-market alpha or a causal estimate of information costs.

## Where it appears in QuantLab

The signal service belongs to the market layer; the informed decision function
belongs to the agents layer. Public projection is a separate, sanitised type.
Offline/as-of markout analysis consumes only occurred event records. Replay checks
saved measurements, recomputes estimates/decisions, and resubmits saved orders
without sampling any new random numbers.

## Interview questions

1. Why should an unreliable signal receive less weight than a reliable one?
2. Why can positive apparent spread capture coexist with a negative provider markout?
3. Why is a negative markout evidence to investigate rather than proof of causation?
