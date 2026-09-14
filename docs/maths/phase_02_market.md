# Phase 2: a market that runs by itself

## Intuition

The order book is a matching rule. It does not explain why anyone trades. Phase 2
adds a small population model: random limit instructions from noise traders and
market instructions from traders with external execution needs. Orders meet in
the existing book; transaction prices come from those matches.

Alongside the market is a hidden value that changes randomly. No current trader
receives that value. Therefore a value update cannot itself move a quote or cause
a trade. This intentionally leaves the link between value and price discovery
for a later, explicitly reviewed model.

An **event** is an occurrence that the simulator needs to process. Instead of
checking every instant, a queue lists future occurrences. The simulated clock
jumps to the earliest one. Events with exactly equal timestamps use the order in
which they were scheduled. This is a software convention, not a statement about
real exchange latency.

## Mathematics

### Random direction, size and limit placement

Each arrival independently chooses buy or sell with probability 1/2: a fair coin.
A **uniform discrete draw** means each allowed integer is equally likely. Default
noise sizes are 1–4 units, liquidity sizes 1–3 units, and noise price offsets are
−2, −1, 0, +1 or +2 ticks, each with probability 1/5.

The noise reference is the current two-sided midpoint, rounded to the nearest
tick with half ticks rounded upward. With only one side or neither side, use the
last transaction, if any; otherwise use the configured opening reference.

\[
p_{limit,ticks}=p_{public\ reference,ticks}+J.
\]

J is the sampled signed tick offset. This rule is non-informational and independent
of the buy/sell coin: a limit can cross the spread. It does not set two-sided quotes
or manage inventory and is not a market-making strategy. A nonpositive sampled
limit is skipped with an explanation, not rounded or clamped to a valid price.

### Arrival intensity and exponential waiting times

An **intensity** λ is an expected number of arrivals per unit of time, here seconds.
λ = 1/s means one arrival per second on average, not exactly one every second.

We independently sample the time W until the next arrival from an exponential
distribution. Its mean and cumulative probability are:

\[
E[W]=1/\lambda,\qquad P(W\le t)=1-e^{-\lambda t}.
\]

E means expectation: the long-run average over repeated samples. P means probability,
t is elapsed seconds, and e is the base of the exponential function. A larger λ
makes short waiting times more likely. For noise λ = 1/s, the probability of at
least one arrival in the next second is about 63.2%. Default liquidity λ = 0.6/s
gives a mean waiting time of about 1.667 seconds. These are mathematical model
properties, not measured real-market parameters. See [NIST's exponential model](https://www.itl.nist.gov/div898/handbook/apr/section1/apr161.htm).

With independent exponential gaps at constant rate, the number N(T) of arrivals
in T seconds has a **Poisson distribution**:

\[
E[N(T)]=\lambda T,\qquad \operatorname{Var}[N(T)]=\lambda T.
\]

Variance measures squared dispersion around the mean; standard deviation is its
square root, in the original units. Five seconds at 1/s gives an expected five
noise arrivals, with standard deviation √5, about 2.24 arrivals. A run with four
arrivals is ordinary variation, not evidence of a broken rate. The connection
between independent exponential gaps and Poisson counts is documented by
[NIST's homogeneous Poisson-process model](https://itl.nist.gov/div898/handbook/apr/section1/apr171.htm).

**An arrival is not a fill.** An order still needs eligible opposite liquidity.
A market buy can arrive and receive no execution at all.

The engine stores elapsed time as integer microseconds. Each continuous gap is
rounded up to at least one microsecond. This adds at most one microsecond per
gap, so implemented arrivals approximate a continuous Poisson process. At default
rates the discretisation is tiny; at extremely high rates it is not. A zero rate
disables that arrival source rather than manufacturing an infinite timestamp.

### The latent-value random walk

The hidden value takes a Gaussian, zero-drift arithmetic step at each scheduled
value update:

\[
X_{t+\Delta t}=X_t+\sigma\sqrt{\Delta t}\,Z,
\qquad Z\sim N(0,1).
\]

- X is hidden value measured in ticks, allowed to have fractional ticks.
- Δt is the interval in **seconds**, converted from the integer clock.
- σ is step uncertainty measured in ticks per square-root second.
- Z is a fresh standard normal draw: mean zero, variance one. Normal means a
  symmetric bell-shaped distribution with small moves more common than large ones.
  See [NIST on normal distribution parameters](https://www.itl.nist.gov/div898/handbook/pmc/section5/pmc51.htm).

Zero drift means no expected upward or downward step. It does not mean every
sample path stays flat. The increment has:

\[
E[\Delta X]=0,\qquad \operatorname{Var}(\Delta X)=\sigma^2\Delta t.
\]

Independent step variances add. Therefore variance grows proportionally with time
and standard deviation grows with its square root. Doubling elapsed time multiplies
standard deviation by √2; quadrupling time doubles it. Using Δt instead of √Δt
in the shock term would give the wrong variance scaling.

Defaults are σ = 2 ticks/√second, Δt = 1 second, and a £0.01 tick: a one-second
increment has standard deviation two ticks, or £0.02. The value is held constant
between scheduled updates. A final incomplete interval receives no invented update.

Arithmetic Gaussian increments can eventually produce nonpositive values. The
implementation aborts if that happens, or if a result is nonfinite. It does not
silently change the model through clipping, reflection or substituted values.

### Reproducibility and statistical verification

A seed chooses the starting state of a pseudorandom generator. Named streams
separate latent shocks, noise arrivals, noise decisions, liquidity arrivals and
liquidity decisions. Extra decision draws cannot move future arrival times.
Reproduction requires the configuration, implementation and appropriate runtime;
it is not evidence that the financial assumptions are true.

Statistical tests compare sample averages and variances with model expectations,
allowing sampling uncertainty. A **standard error** describes how much an estimator
such as a sample average varies between repeated samples. The tests use broad
six-standard-error bands, not an exact required random sample. The count test
also allows for microsecond rounding. See the documented tests in
`tests/statistical/test_market_processes.py`; passing them establishes these basic
generator properties within tolerances, not calibration to financial markets.

## Where it appears in QuantLab

`market/events.py` owns the clock/heap; `market/processes.py` contains both stochastic
equations; `agents/basic.py` turns observable information and random draws into
explained orders; `market/simulation.py` connects them to `OrderBook.submit`.
`market/records.py` derives the tape from actual executions. The public observation
contains no latent fields. Explicit observer debug mode reveals values to Arvind
for inspection, without changing trader behaviour.

## Assumptions

Independent constant-rate arrivals, fair directions, uniform sizes/offsets,
independent Gaussian latent increments, one instrument, an empty initial book,
serial immediate matching, no account constraints, and no economic response to
hidden value. Existing limits persist until filled or manually cancelled; the
autonomous agents have no cancellation policy. See [ASSUMPTIONS.md](../../ASSUMPTIONS.md).

## Failure cases

Liquidity may vanish; external execution needs are abandoned when unfilled. Old
limits can accumulate. Constant independent arrivals miss clustering and activity
patterns. Gaussian constant-σ moves miss jumps and changing volatility. A latent
value that nobody observes cannot anchor transaction prices. Full snapshot logging
uses substantial memory for long sessions. Replay validates mechanical consequences,
not the authenticity of a log or the plausibility of a random sample.

## Interview questions

1. Why does an arrival rate of 2/s not imply an arrival exactly every half second?
2. Why does doubling σ multiply increment variance by four?
3. Why can transaction price stay above a falling hidden value in this model?

