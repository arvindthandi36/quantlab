# Phase 5 — learning research through QuantLab experiments

QuantLab is a synthetic quantitative research environment. Synthetic performance
is not evidence of real-world alpha. Read the [actual experiment report](../learning/phase_05_report.md)
alongside this lesson; amounts below are explanations, not promises of returns.

## 1. Random variables, distributions and expected value

### INTUITION

Before a session runs, its eventual P&L is unknown. Call that uncertain result X.
X is a **random variable**: a rule that turns a possible random market history
into a number. Its **probability distribution** describes which values can occur
and how likely they are. **Expected value** is the probability-weighted average
over all possible histories, not a result any one session must achieve.

### MATHEMATICS

For discrete possible outcomes, E[X] = sum of x times P(X=x). A sample of n sessions
provides an estimate: x-bar = (x1 + ... + xn)/n. This is the **sample mean**.
The true expectation under the model generally cannot be enumerated exactly.

### QUANTLAB EXAMPLE

The baseline repeats a complete 30-second market, each with its own seed. The
1,000 evaluation outcomes form an **empirical distribution**: the distribution
of what this finite sample actually produced. A histogram groups those values
into bins. Its shape changes somewhat with bin choices, so both strategies share
bin boundaries. The empirical CDF at x is the fraction of outcomes at or below x.
At zero it includes exactly-zero sessions; probability of losing uses strictly X<0.

### ASSUMPTIONS

Independent pseudorandom sessions use identical model settings within a variant.
The empirical distribution approximates the synthetic population, not a real asset.

### COMMON MISTAKES

A profitable example is not an estimate precise enough to establish skill. The
mean is not the most likely individual outcome. A histogram with no large crash
does not establish that crashes are impossible.

### INTERVIEW QUESTIONS

What is the difference between an expected value and a sample mean? How would
an empirical CDF show the fraction of simulations losing more than £0.50?

## 2. Variance, standard deviation and standard error

### INTUITION

**Standard deviation (SD)** describes how much individual session outcomes vary.
**Standard error (SE)** describes uncertainty in the estimated average. Collecting
more independent sessions helps estimate the average without making each session
less risky. Before opening the precision result, predict what happens from 100
to 400 sessions.

### MATHEMATICS

Sample variance s² = sum((xi−x-bar)²)/(n−1). Squaring prevents positive and negative
deviations cancelling. The n−1 denominator accounts for estimating the mean from
the same sample. Variance of pound outcomes has units pounds squared. Taking its
square root gives s in pounds. Estimated SE(x-bar) = s/sqrt(n).

Going from 100 to 400 multiplies n by four: sqrt(n) doubles, so SE roughly halves
if the estimated SD stays similar. Going to 1,600 should approximately halve it
again. Actual sample SD changes, so ratios need not be exactly 1/2.

### QUANTLAB EXAMPLE

The precision report uses the first 100, 400 and 1,600 development sessions for
each policy. It shows both SD and SE and plots the running mean. The prefixes
overlap; they are not three independent experiments. It also groups sessions into
disjoint blocks and reports variation between block means. There are only four
blocks of 400 in 1,600 observations, so that particular estimate is noisy.

### ASSUMPTIONS

Finite variance and independence between sessions. Trades within one session
are dependent: do not inflate n by counting each fill as another simulation.

### COMMON MISTAKES

Using SD as uncertainty of the average, or using SE to describe downside risk of
one session. Claiming that more simulations make a strategy's individual outcomes
safer. Treating repeated identical seeds as new independent data.

### INTERVIEW QUESTIONS

What happens to SE when n quadruples? Can SD remain large while SE becomes small?

## 3. Quantiles and tail risk

### INTUITION

Sort the outcomes from worst to best. Quantiles locate points in that ordering.
The fifth percentile describes the lower end of P&L; the 95th percentile of
drawdown describes a bad drawdown region. Two strategies with similar averages
can have very different lower tails.

### MATHEMATICS

For sorted x0,...,x(n−1), calculate a=(n−1)p. Interpolate between entries floor(a)
and ceil(a). This is the documented linear quantile convention. With values
10,20,30,40, the 25th percentile is 17.5. Other conventions are legitimate but
produce different small-sample results; record which one is used.

### QUANTLAB EXAMPLE

Every metric reports mean, median, SD, SE, minimum, maximum and 5/25/75/95th
percentiles. P&L additionally reports strict breaches of £0, −£0.25, −£0.50 and
−£1.00. The lower-tail mean averages the worst ceil(0.05n) observations; it is
labelled with this convention rather than implying an exact population risk measure.
An extreme run keeps its seed/configuration and can be replayed event by event.

### ASSUMPTIONS

The sample needs enough independent sessions to populate its tail. Rare risks
absent from the market model cannot appear just because more seeds are run.

### COMMON MISTAKES

Calling a positive mean safe; deleting outliers without investigating them;
interchanging a mean confidence interval with a future-outcome percentile range.

### INTERVIEW QUESTIONS

Why might a strategy with a higher mean be less desirable? What is missing from
a tail-risk estimate when the simulated market excludes crashes or funding risk?

## 4. Paired comparisons, covariance and correlation

### INTUITION

Common random numbers mean **testing two strategies under the same weather**.
Each pair receives the same latent shocks, arrival times and signal errors.
Those are exogenous: they originate outside the strategies. The quotes, fills,
subsequent prices and book states are endogenous consequences and may differ.

Rather than compare two noisy means separately, calculate the difference inside
each pair. D = inventory-aware P&L − fixed P&L. Shared favourable or unfavourable
weather can partly cancel, making the policy difference easier to estimate.

### MATHEMATICS

Cov(X,Y) = E[(X−E[X])(Y−E[Y])]. Positive covariance means values tend to move in
the same direction around their means. Correlation divides covariance by SD(X)SD(Y)
and ranges from −1 to +1. It is undefined if either quantity is constant.

Var(B−A) = Var(B) + Var(A) − 2Cov(A,B). Positive shared-weather covariance can
reduce difference variance. Common random numbers do not guarantee a reduction:
the covariance may be small or negative. SE of mean D is SD(D)/sqrt(number of pairs).

### QUANTLAB EXAMPLE

The engine aligns pairs by run address and simulation seed and verifies their
exogenous fingerprints. It reports the entire D distribution, its mean and median,
SD, SE, intervals, and positive/negative/tied proportions. Exploratory session-level
relationships include inventory versus P&L and maximum inventory versus drawdown.
Missing markouts are excluded pairwise with the number available reported.

### ASSUMPTIONS

Pairs are independent of other pairs. Dependence inside a pair is intentional.
Exact path pairing requires identical exogenous market configurations. A volatility
or arrival-intensity sweep reuses seeds but changes realised paths, so it does not
claim identical weather or automatically receive the paired analysis.

### COMMON MISTAKES

Sorting each strategy's P&Ls separately before subtracting destroys pairing.
Resampling sides independently destroys shared-weather dependence. Correlation
does not show that exposure caused a loss: price moves may affect both quantities.

### INTERVIEW QUESTIONS

When can common random numbers reduce uncertainty? Why do identical seeds not
require identical fills? What would zero correlation fail to rule out?

## 5. Confidence intervals and bootstrap

### INTUITION

A large positive sample mean is different from a **precisely estimated** positive
mean. A confidence interval measures uncertainty of the mean under specified
assumptions. It does not bound most individual future outcomes.

**Correct frequentist interpretation:** if we repeatedly generated samples and
built intervals by this procedure, about 95% would contain the fixed true mean
when the procedure's assumptions are adequate. For a particular realised interval,
the fixed mean is either covered or not.

Do not say: **“There is a 95% probability that the true mean lies inside this
particular realised interval.”** That is not this frequentist interpretation.

### MATHEMATICS

Student mean interval: x-bar ± t(0.975,n−1) × s/sqrt(n). Student t accommodates
estimated variance. The procedure is exact for independent normal observations;
its large-sample use for nonnormal P&L relies on an adequate approximation.
See the [NIST definition and interpretation](https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm).

For a percentile bootstrap, sample n observations **with replacement** from the
observed n values. Some original sessions appear repeatedly and others disappear.
Calculate the mean; repeat 2,000 times. The 2.5th and 97.5th percentiles of those
means form the interval. The resampling generator has its own recorded seed.
For paired comparisons resample whole differences, preserving the matched unit.
[SciPy documents percentile and paired resampling](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html).

### QUANTLAB EXAMPLE

Both individual mean P&L and mean paired differences receive Student and bootstrap
intervals. Statistics operate on session-level floating-point summaries; the
underlying execution ledger remains exact rational arithmetic. Fewer than two
observations cannot estimate SE. Constant samples give a zero-width plug-in interval
but do not prove the underlying population has no variability.

### ASSUMPTIONS

Representative independent sessions, finite variance and enough observations.
The simple percentile bootstrap has imperfect coverage, especially in small,
skewed or heavy-tailed samples. It cannot invent unseen market regimes, repair a
biased simulator or remove parameter-selection bias. Neither interval captures
uncertainty about whether this synthetic market resembles a real one.

### COMMON MISTAKES

Bootstrapping individual fills, counting resamples as new market evidence, or
claiming nominal 95% coverage is guaranteed for every nonnormal P&L sample.

### INTERVIEW QUESTIONS

What does “with replacement” mean? Why must the bootstrap unit be a full session
or a matched session pair? Why are 2,000 bootstrap means not 2,000 new markets?

## 6. Law of large numbers and central limit intuition

### INTUITION

The law of large numbers says sample averages tend to approach expected value
as independent observations accumulate under suitable conditions. It does not
say the path moves closer after every new observation. It does not make individual
outcomes less volatile.

The central limit theorem concerns the **sampling distribution of the average**.
Imagine many independent groups of n sessions and compute one mean per group.
For large enough n and suitable conditions, those means can look approximately
normal even when individual P&Ls do not. This motivates approximate mean inference.

### MATHEMATICS

For independent identically distributed finite-variance observations, the variance
of a mean is sigma²/n. The standardised mean sqrt(n)(x-bar−mu)/sigma approaches a
standard normal distribution. No proof is needed to use the key distinction:
distribution of individual X versus distribution of the estimated mean.

### QUANTLAB EXAMPLE

Look at the running mean and block-mean results in the precision experiment.
Then compare SD and SE columns. A visibly stable average can coexist with large
individual losses. There is no claim that the first 1,600 runs reveal the exact
expectation or prove normality of the individual outcomes.

### ASSUMPTIONS

Independence and adequate moments matter. Extreme heavy tails, changing regimes
and dependence can undermine the approximations. Four large blocks provide only
four observed group means, so their apparent shape says very little about normality.

### COMMON MISTAKES

“After enough runs all outcomes approach the mean”; “the CLT makes P&L normally
distributed”; “more precise synthetic estimates eliminate model risk.”

### INTERVIEW QUESTIONS

Which distribution is approximately normal in the CLT? Why is the running mean
allowed to move away from its eventual limit for a while?

## 7. Hypothesis tests, p-values and practical significance

### INTUITION

The null hypothesis here says the true mean paired difference is zero. The
alternative says it differs from zero. Ask how surprising the observed difference
would be if the null and the statistical model were correct.

### MATHEMATICS

t = mean(D)/SE(mean(D)). This compares the observed effect with its uncertainty.
The two-sided p-value is the null-model probability of a test statistic at least
as extreme in either direction. It is not the probability that the null is true,
and it is not the probability the strategy works. We report the actual effect in
pounds and a standardised paired effect mean(D)/SD(D).

### QUANTLAB EXAMPLE

The baseline freezes one primary paired comparison. The significance control
generates independent Gaussian effects with a tiny true mean 0.001 across 200,000
observations, and a meaningful true mean 0.10 across only 20 noisy observations.
Both are labelled synthetic statistical controls, not exchange executions. Compare
their p-values, interval widths and effects against the declared illustrative
0.05 practical threshold. More data can make a tiny effect statistically detectable;
a useful effect can remain uncertain in a small sample.

### ASSUMPTIONS

The paired t-test assumes independent differences; exact small-sample theory is
normal. Large-sample approximation is conditional on suitable finite-variance
behaviour. The practical threshold is a teaching choice, not a funded-trading hurdle.

### COMMON MISTAKES

“p<0.05 means strategy works”; “p>0.05 proves zero effect”; choosing the test,
direction or stopping point after inspecting results. A zero-variance difference
has an explicitly undefined t-test rather than a fabricated p-value.

### INTERVIEW QUESTIONS

Can a tiny effect be statistically significant? Can a meaningful effect have a
wide confidence interval? What claim does a p-value actually condition on?

## 8. Selection bias, multiple testing and train/test discipline

### INTUITION

Explore many noisy variants and some will look excellent by luck. **Multiple
testing** creates many chances to find a flattering result. **Data snooping** uses
the observed data to choose hypotheses or parameters. **Selection bias** arises
when selected results cease to represent the full attempted set. The **winner's
curse** is optimism in the selected winner's measured performance.

### MATHEMATICS

Even if every variant has true expectation zero, the maximum of many noisy sample
means usually exceeds zero. Selection conditions on being unusually high.
For independent 5%-level tests under all true nulls, the probability of at least
one false positive is 1−0.95^m; correlations change that calculation. The engine
does not apply that independence formula blindly to correlated strategy variants.

### QUANTLAB EXAMPLE

The flagship control gives 50 variants exactly the same true expected payoff.
Each gets 40 development sessions. Select the highest sample mean, record that
choice, then generate 400 untouched evaluation observations for the winner.
All development results remain stored; no seed is searched to force deterioration.
The observed change is displayed even if a particular sample does not deteriorate.

The real market sensitivity sweep is exploratory. It never calls the best sample
mean optimal. Baseline evaluation runs unchanged Phase 4 parameters on a disjoint
pool after development work. Evaluation access is logged before sessions run,
including failed attempts; repeated overlapping seeds produce explicit warnings.

### ASSUMPTIONS

The local registry is a guardrail, not a security system. Creating another registry
or bypassing the engine defeats it. Honest governance and model validation remain
necessary. Independent test seeds do not address model misspecification.

### COMMON MISTAKES

Repeatedly checking evaluation performance while tuning gradually turns the test
set into another development set. Reusing the same seeds is useful for pairing
but cannot create fresh evidence. Hiding losing variants or failed sessions is
survivor bias; incomplete experiments cannot receive survivor-only inference.

### INTERVIEW QUESTIONS

Why distrust the measured winner among 50 variants? When is a test set no longer
untouched? Why doesn't a perfect train/test split establish real-world alpha?
