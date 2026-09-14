# Phase 12 — explain the actual QuantLab state

12 September 2026. Core 1.0.0 remains approved and unchanged. Phase 12 is ready for
review; Phase 13 has not begun. All financial examples below come from the existing
Python engines. [Recorded responses](evidence/demo.json) and the
[reproduction script](../../scripts/explanation_demo.py) retain the detailed evidence.

## BUILD REPORT

Added one explanation layer over the approved engine: actual-value panels, four
learning depths, before/after input comparisons, five isolated what-ifs, a 70-concept
registry, local search, six small relationship maps, fourteen independent examples,
three clickable architecture branches, replay-point explanations and public-context
tutor questions. No external AI service or frontend dependency is required.

The financial core stays at 1.0.0. Explanation responses use the separate schema
`quantlab-explanation-v1`. Matching, accounting, pricing, Greeks, IV, risk, regression,
optimisation and random processes have not been reimplemented. No core bug was found.

## TEST REPORT

Final full suite: **1,507 passed in 83.43 seconds**, comprising **all 1,346 original tests unchanged**
and **161 new tests**. No failures or skips. Ruff lint and formatting checks pass. An isolated wheel build also passed; all six explanation modules and three browser assets match the source in the built package.
See [test evidence](evidence/test_report.json) for the final runtime, collection
comparison, per-file new-test counts and frozen-source check.

New checks cover registry integrity and prerequisites; all four depths; actual fills,
P&L components, Greek units, VaR methods, z-score windows and signed pending legs;
public/observer boundaries; future-data mutations; replay in four financial labs;
hypothetical state/RNG isolation; local HTTP/token validation; unchanged learning
evidence; tutor integration; formula metadata; search; and safe observation failures.

Browser acceptance checked actual VWAP, portfolio delta, VaR, z-score and their Python
agreement; changed holdings; volatility, correlation and threshold what-ifs; a quiz
without answering it; search; replay rewind; and desktop/390-pixel layouts. No browser
console errors were observed. These interactive checks are additional acceptance
evidence, not counted as automated tests. They used a disposable learning profile.

## CORE-REGRESSION FINGERPRINT REPORT

The representative Phase 11 workflows produced identical complete outputs before
and after Phase 12. These SHA-256 hashes use sorted-key JSON with standard separators:

| Workflow | Before = after fingerprint |
|---|---|
| A + D: real stock/options/hedge/accounting, risk, stress and replay | `dd664478c90ad6a76a51ceba52bfffe3e7ff034f8c7efea7b1941e501c79756b` |
| B: registered research, full/light agreement and tutor context | `ba51bd97bd9cb4346134fc1b8212562a5932fa9cbaf780f79654422e5b051fa7` |
| C: incomplete Stat Arb execution, attribution, risk and replay | `f375bb45462068e377616ac1cbd7cdc5a8c49df6e9c2c4235e5ce4cb53667b5c` |

[Before](evidence/core_workflows_before.json) and
[after](evidence/core_workflows_after.json) retain the outputs. The baseline manifest
also verifies unchanged original tests and financial Python sources. Only server and
navigation adapters changed among pre-existing Python modules. Fingerprint equality
proves these workflows are unchanged, not that every conceivable workflow is correct.

## HOW TO USE EXPLAIN MODE

Launch the application normally. Click **?** beside a key metric or **Explain a value**
above a lab. Select an order for VWAP, a risk method for VaR/ES, or the relevant concept.
The [Explain page](http://127.0.0.1:8769/explain) offers search, maps and small examples.
That address is the separate Phase 12 local preview used for this review.

For a fresh VWAP example, buy six market units in Trading and open Explain VWAP.
For a changed value, inspect a metric, take an actual action, then reopen its panel.
Use the amber sandbox to explore a hypothesis. See the [user guide](USER_GUIDE.md).

## EXPLANATION PANEL WALKTHROUGH

The panel starts with a plain definition and **Your current value**. **Why is it this
value?** displays the recorded inputs. Beginner presents the main trace first; a
separate expandable section retains complete calculation inputs. **Why did this
change?** compares two actual observations. Further sections cover meaning, drivers,
downstream effects, mathematics, dependencies, assumptions, professional context and
related concepts.

Beginner gives intuition. Maths opens the equation and symbol definitions. Quant
opens assumptions and detailed inputs. Interview adds a reasoning challenge. Switching
depth never changes the underlying number. Missing evidence stays unavailable; it is
not replaced by a textbook example disguised as your session.

## CONCEPT REGISTRY SUMMARY

There are **70 concepts in 12 domains**, from order-book mechanics through probability,
derivatives, research methods and reproducibility. Coverage is Trading 20, Market
Making 14, Options 14, Risk 13, Stat Arb 13, Research 12 and Learning 12. Counts overlap
because a shared concept appears in more than one lab.

Each entry has its definition, relevance, drivers, prerequisites, relationships,
formula/variables where applicable, locations, uses, assumptions and limitations.
One registry supplies the interface, API and maps. The
[coverage index](CONCEPT_REGISTRY.md) identifies every concept. A mechanism may have
a structured trace rather than a standalone number.

## CONCEPT MAP WALKTHROUGH

Choose **Execution → P&L**. Start at order size: a larger order may need more available
depth, consume worse prices, change VWAP and change execution cost. Click VWAP to see
your actual fills. Choose the volatility, correlation, inventory, Stat Arb or research
chain to follow a different relationship.

An arrow means a dependency or conceptual relationship. It does not establish a
real-world causal effect. Prerequisite links are separately checked for cycles.

## ONE VWAP EXPLANATION

The demo buys six units. The actual matching engine records:

| Fill | Units | Price | Price × units |
|---|---:|---:|---:|
| 1 | 2 | £100.01 | £200.02 |
| 2 | 4 | £100.02 | £400.08 |
| Total | 6 | | £600.10 |

**VWAP = £600.10 / 6 = £100.01667**, rounded for display. The exact engine result is
6001/60 GBP. Four of the six units traded at £100.02, so that price has twice the
weight of the first fill. An ordinary average of the two prices would give the
wrong execution average.

The equation is `VWAP = Σ(PᵢQᵢ) / ΣQᵢ`: `Pᵢ` is fill i's price, `Qᵢ` its executed
quantity, and `Σ` means add across fills. Fees are separate. A different sequence of
available prices or fill quantities changes VWAP. It connects execution to cost and
P&L. A market order can receive several prices; a limit order may remain unfilled.
[Investor.gov's order explanation](https://www.investor.gov/introduction-investing/investing-basics/how-stock-markets-work/types-orders)
provides the corresponding real-market distinction.

## ONE P&L “WHY DID THIS CHANGE?” EXPLANATION

Before buying, marked P&L is £0. After the six-unit purchase it is **−£0.076**:

| Recorded component | Before | After |
|---|---:|---:|
| Position | 0 | 6 |
| Cash | £10,000.000 | £9,399.894 |
| Public reference | £100.000 | £100.005 |
| Stock-desk realised P&L, including fees | £0 | −£0.006 |
| Unrealised P&L | £0 | −£0.070 |
| Total marked P&L | £0 | **−£0.076** |

The £600.10 purchase exchanged cash for stock; it was not all a loss. The stock is
currently marked at £600.03, creating a £0.07 open-position loss. Fees add £0.006.
The desk already includes those fees in its realised figure; subtracting them again
would double-count them. The consolidated risk account instead reports gross realised
P&L and separate fees. The explanation states which convention applies.

This is an exact accounting decomposition from the core. It is stronger evidence
than an invented claim that one market factor “caused 42%” of a P&L change.

## ONE OPTION / GREEKS EXPLANATION

Initially the selected £100-strike call has 30 days remaining, stock £100, volatility
20% and rate/dividends zero. Its per-unit **delta is 0.5114357531**. Delta describes
the local slope: for a small stock-price move, the option's value changes by about
delta times that move, holding the other model inputs fixed.

One contract represents 100 units, so one long contract has **51.14357531 stock-equivalent
delta units**. The interface distinguishes per-unit, contract and whole-portfolio
Greeks. Portfolio delta also includes actual stock positions.

After one real simulated day, delta is **0.5260707383**. The recorded changed inputs
are stock **£100 → £100.21**, time **30 → 29 days**, and volatility
**0.20 → 0.2000631540**. The panel reports these observations without allocating
unsupported percentages to them. Gamma describes how delta itself changes with
stock price; that is why an old hedge can become stale.

`Δ = ∂V/∂S`: `V` is per-unit option value, `S` the stock price, and `∂` means a local
change while holding other inputs fixed. Professional Greek exposure also scales
with position size and contract units.
[OIC's Greek exposure explanation](https://www.optionseducation.org/news/may-office-hours-faqs)
provides that context.

## ONE VaR EXPLANATION

In the recorded script, the portfolio contains the call after one simulated day and
six QL-DESK stock units. With 1,000 already-generated scenarios, **95% one-day Monte
Carlo VaR is £94.45946811**. A real purchase of five QL-STOCK units increases it to
**£103.56857621**. The changed-input trace identifies the additional underlying holding.
The confidence, horizon and scenario settings are unchanged.

VaR is a threshold in a modelled loss distribution. A 95% VaR leaves a worst 5% tail;
it is not the maximum loss. The dependency trace follows holdings → instrument
repricing → scenario losses → ordered loss threshold. Expected Shortfall describes
the average loss in that tail, including the engine's fractional boundary convention.

The browser acceptance case is deliberately separate: 5,000 scenarios, day zero and
five added QL-DESK units gave **£89.69894770 → £91.98888068**. These are different
portfolios/settings, not inconsistent explanations of one case. Professional market
risk frameworks also distinguish tail measures and model requirements; this teaching
implementation is not a regulatory system.
[BIS market-risk framework summary](https://www.bis.org/bcbs/publ/d457_inbrief.pdf).

## ONE STAT-ARB Z-SCORE EXPLANATION

At public observation 80, the core has fitted `Y ≈ α + βX` using earlier data:
α = **5.9970915867**, β = **0.9377952472**. Current prices are X = £97.38 and
Y = £97.64. The residual—the gap between Y and that fitted line—is **0.3204072428**.

The earlier residual window has mean **−0.0220777650** and standard deviation
**0.1543125136**. Standard deviation measures the window's typical spread around
its mean. The core reports:

`z = (current residual − earlier mean) / earlier standard deviation = 2.219424723`.

The residual is about 2.22 of those historical standard-deviation units above its
earlier mean. That is not a 2.22% probability or proof that it will converge.
At observation 81 the residual becomes 0.5683993815, the earlier mean −0.0134773719
and standard deviation 0.1635359828, producing **z = 3.5580961661**. The panel shows
all three changes and the shifted normalisation window. The current observation
is excluded from its own normalisation; changing later rows cannot change this score.

## ONE ENGINEERING EXPLANATION

**Why integer ticks?** Matching must decide whether a price crosses another price
without a floating-point rounding dispute. QuantLab matches whole grid increments;
the demo's £100.01 and £100.02 fills remain exact. The average of fills can be a
fraction even though every executed price lies on the grid.

The seed lesson explains reproducible pseudorandom streams; the replay lesson adds
that seed alone is insufficient without matching versions, configuration and actions.
The event-clock lesson explains deterministic event ordering. None presents these
engineering choices as a source of financial profit.

## WHAT-IF VOLATILITY DEMO

Before advancing the option session, increase annual volatility from **20% to 30%**
in the isolated model. Hold spot, strike, time, rate and dividends fixed:

| Per-unit measure | 20% | 30% |
|---|---:|---:|
| Model value | £2.28715063 | £3.43013864 |
| Delta | 0.51143575 | 0.51715069 |
| Gamma | 0.06954844 | 0.04634182 |
| Vega per 1.00 volatility | 11.43262040 | 11.42674899 |

Volatility is the model's uncertainty scale. Vega measures local sensitivity to
that scale; its units matter. A one-percentage-point volatility move is 0.01, so
per-point vega is the displayed per-1.00 quantity divided by 100. A ten-point change
requires full repricing for the exact model difference; multiplying one starting
vega by 0.10 is an approximation. These concepts support option risk analysis.
[OIC's Greeks and volatility material](https://www.optionseducation.org/videolibrary/greeks-and-volatility).

When Risk is already attached, this what-if can additionally reprice a detached
portfolio and run the existing delta-normal risk API. This is model-based analysis,
not an executed option sale, live account mark or new Monte Carlo result.

## WHAT-IF CORRELATION DEMO

For the script portfolio after the real five-unit QL-STOCK purchase, raise the common
factor correlation **0.25 → 0.90** while holding configured daily volatilities and
positions fixed:

| Same delta-normal approximation on both sides | 0.25 | 0.90 |
|---|---:|---:|
| One-day loss standard deviation | £71.01179 | £74.71972 |
| 95% VaR | £116.80400 | £122.90300 |
| 95% Expected Shortfall | £146.47693 | £154.12532 |

Correlation describes co-movement. The covariance between the first two factors
rises from **0.000030 to 0.000108** in daily return-squared units. Covariance combines
co-movement with each factor's own volatility. In this portfolio, higher positive
co-movement reduces diversification. That direction is not universal: opposite
exposures can behave differently.

The live Monte Carlo VaR of £103.57 is not used as the baseline for this comparison.
Both hypothetical columns use the same fast approximation. A configured custom
covariance matrix is replaced in this detached hypothesis, and that is disclosed.

## WHAT-IF ORDER-SIZE / VWAP DEMO

After the real six-unit purchase, freeze the remaining visible book and try a
hypothetical market buy of **20**. The existing matcher fills **one at £100.02 and
eight at £100.03**: nine filled, eleven unfilled, **VWAP £100.02888889**. Unfilled
market-order remainder cancels. Your actual position remains six.

This is **HYPOTHETICAL SNAPSHOT ANALYSIS**. It includes displayed own orders and
omits live self-trade controls, account limits, fees and subsequent market reactions.
It explains available depth, not what certainly would have happened in a live market.

The other two sandboxes use the same isolation rule. Inventory 0 → +20 invokes
the existing inventory-sensitive quote policy, including its nonlinear soft-limit
term and hard-limit clipping; it does not claim the manual desk automatically uses
that policy. Entry threshold 2.0 → 2.5 changes observation 80 from short to wait,
while observation 81 still qualifies. That scan is not an executed backtest.

## LIVE VS HINDSIGHT PRIVACY DEMO

The script requests hidden observer evidence while the stock session is live:
**rejected**. It then ends the session and explicitly requests observer mode:
permitted and separately labelled, with **quiz disabled**. Normal explanations never
receive latent value, informed signals, unpublished regimes or future market prices.

Public post-session markouts remain distinct. In this short session, the first
public observation horizon has matured: the first buy fill's markout is £0.00 and
the second's −£0.01 per unit. Longer horizons remain pending, not zero. Own-side
markout is `s(Rₕ − P)`, where s is +1 for buying or −1 for selling, P is the fill
price and Rₕ the later public reference. A negative markout does not prove the
counterparty was informed. See [information boundaries](INFORMATION_BOUNDARIES.md).

## REPLAY EXPLANATION DEMO

The verified stock replay at frame zero has no order and **no VWAP**. At the actual
trade frame it has the two recorded fills and **VWAP £100.01667**. Looking at the
end first does not make those fills available at frame zero.

In the browser, the initial Stat Arb replay frame likewise showed no z-score; the
next recorded frame showed **2.21942472**. “Selected replay point — public information”
was visible throughout. Annotation hooks provide public pre/post evidence and concept
IDs; they do not redesign the journal or expose raw hidden commands. Later public
evidence requires selecting a later frame; observer truth requires its separate gate.

## TUTOR / QUIZ INTEGRATION DEMO

After Explain VWAP, **Quiz me on this** asks: “Which average describes this order's
execution price?” Its context contains the actual two and four units at the two fill
prices. The existing tutor handles submitted answers; none was submitted on Arvind's
behalf. Reading and what-ifs leave learning evidence unchanged. A quiz request can
record an encounter, which is distinct from assessed mastery.

Research explanations also read verified results. The small four-run study has mean
P&L **−£0.0095**, sample standard deviation **£0.02595509**, standard error
**£0.01297754**, and interval **[−£0.05080034, £0.03180034]**. Standard error measures
uncertainty in the estimated average, not variability of an individual trade. For
independent observations, `SE = s/√n`: s is sample standard deviation, n the number
of independent runs. The interval crossing zero does not establish profitable alpha.
An independent constructed example holds s fixed and quadruples n, halving SE.

## ARCHITECTURE VIEW WALKTHROUGH

On Explain, inspect three branches: market/accounting, options/hedging and Stat
Arb/research. Follow market events → orders → FIFO fills → accounting → positions →
risk and explanation. The options branch connects model values to contract positions,
Greeks and hedging. The Stat Arb branch connects observed data, regression, residuals,
z-scores, decisions, execution and evidence.

Every branch links to concept explanations. The browser renders Python values; it
does not manufacture a fill or calculate a competing VaR. The implementation and API
contract are in [ARCHITECTURE.md](ARCHITECTURE.md).

## MODEL-RISK CONNECTION DEMO

Open VaR → **Assumptions — what if they are wrong?** The panel links its interpretation
to the Phase 11 model-risk categories: positions and valuation, volatility/covariance,
scenario dynamics, option model and finite-sample uncertainty. If tail behaviour or
correlations differ from the model, the result can understate losses even if every
line of arithmetic is correct. More Monte Carlo paths reduce simulation noise;
they do not repair a wrong model.

Seven curated assumption groups connect the registry to the
[approved model-risk map](../release/model_risk.md) and
[assumptions register](../../ASSUMPTIONS.md). Explanations distinguish recorded
calculations, model assumptions, controlled synthetic facts and real-finance context.
They do not assign a precise numerical penalty to an assumption being wrong.

## PERFORMANCE REPORT

Warm Python response construction, thirty reads per concept, on this local machine:

| Explanation | Median | Empirical p95 |
|---|---:|---:|
| Actual VWAP | 0.89 ms | 0.99 ms |
| Stock P&L | 0.96 ms | 1.14 ms |
| Selected delta | 9.23 ms | 9.82 ms |
| Existing VaR report | 6.93 ms | 7.40 ms |
| Current z-score | 1.79 ms | 1.98 ms |

Ten repetitions of each sandbox gave medians: order size **0.38 ms**, inventory
**0.48 ms**, threshold **3.30 ms**, correlation **5.93 ms**, volatility **9.32 ms**.
The risk report's 1,000 paths were already computed. Clicking Explain did not launch
a fresh experiment. These measurements exclude browser rendering and are not universal
latency guarantees. [Raw performance evidence](evidence/performance.json).

The example cache retained **442,909 serialised bytes**. Twenty repeated risk reads
retained about **23 KB** of traced Python allocations, with a **385 KB** traced peak;
this is not whole-process memory. Retention is capped at two observations per lab,
2 MB per observation. Oversized observations are dropped, never silently truncated.

## FILES CHANGED

| Files | Purpose |
|---|---|
| `src/quantlab/explainability/{registry,evidence,service,sandbox,examples,__init__}.py` | New authoritative metadata, public projections, modes/history/tutor bridge, detached core calls and examples |
| `src/quantlab/trading/server.py` | Local explanation routes and protected observation hooks |
| `src/quantlab/trading/navigation.py` | Shared Explain navigation/assets |
| `src/quantlab/trading/static/explain.{html,css,js}` | Explorer, four-depth panels, actual/hypothetical distinction and visuals |
| `tests/unit/test_explanation_registry.py` | Metadata, graph, search, symbols and coverage checks |
| `tests/integration/test_explanation_{state,sandbox,http}.py` | Actual engine sessions, replay, privacy, isolation and HTTP integration |
| `scripts/explanation_demo.py` | Reproducible worked evidence and bounded performance measurements |
| `docs/explainability/` | Architecture, registry, boundaries, what-if contract, style, user guide, this report and evidence |
| `README.md`, `ROADMAP.md`, `ASSUMPTIONS.md`, `LEARNING_LOG.md`, `CHANGELOG.md` | Phase 12 usage, approval boundary, assumptions and learning record |

All original tests remain byte-for-byte unchanged. The earlier portable Phase 11
bundle remains a core-only historical artefact; use this checkout for Phase 12.

## RED TEAM

- Recent-observation comparison is not complete causal attribution. Unobserved
  intermediate states and interactions can matter; no additive causal shares are claimed.
- Legacy public frames lack some manual quote-request details, decision-time slippage
  benchmarks and separate spread-capture attribution. The panel explicitly reports
  missing evidence instead of fabricating those quantities.
- Some concepts explain a mechanism, assumption or unavailable estimate rather than
  a scalar. Coverage counts do not mean seventy independently observed financial metrics.
- Detached book analysis omits live protections and market response. Correlation and
  volatility portfolio what-ifs use an approximation with fixed assumptions. Threshold
  scans ignore evolving position state and are not backtests.
- Exact accounting, future-data tests and matching fingerprints demonstrate internal
  consistency, not profitable trading, model realism or production readiness.
- Keyword matching is limited. It does not understand arbitrary natural-language
  questions. Scored quizzes use existing tutor topics; unsupported topics provide
  interview prompts or request relevant public evidence.
- Explicit observer review is currently the ended stock simulation only. It is not
  a new general historical data source. Public replay remains bounded by the selected frame.
- The interface is locally served and escapes displayed evidence, but cannot protect
  hidden information from someone controlling the Python process or local filesystem.
- Performance was measured on bounded warm workloads. Long sessions can lose recent
  comparison retention at the configured cap; their financial state is not modified.
- No historical ingestion, polished Phase 14 demo catalogue or recruiter README
  overhaul was started. Phase 13 requires Arvind's review and authorisation.

## 3-QUESTION ARVIND CHECK

1. Why does the four-unit fill affect your VWAP more than the two-unit fill?
2. If hypothetical volatility raises the option's model value, has your real account
   made that profit?
3. If VaR rises after your holdings change, what evidence should Explain show before
   you accept its explanation?
