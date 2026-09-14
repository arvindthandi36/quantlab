# Phase 8 review — Options & Derivatives Lab

> Historical phase record. Current core conventions and release status are in the root README, ASSUMPTIONS and Phase 11 release report. Test counts and runtime labels below describe this phase.


11 September 2026 · QuantLab 0.8.0 · Phase 8 only. Phase 9 has not begun.
Implementation evidence is separate from Arvind's learning assessment.

## BUILD REPORT

European calls and puts now trade inside an integrated local lab. Contracts have
explicit strike, expiry, underlying, multiplier and units. Stable analytical
pricing, parity, five Greeks, finite differences, a diagnosed IV solver and
risk-neutral Monte Carlo support the same selected instruments shown in the chain.

Options execute against finite synthetic dealer bid/ask quotes. Stock hedges
pass through the existing Phase 6 order/risk/accounting interface and Phase 1
FIFO matching engine. Exact option FIFO lots, fees, cash funding, stock accounts
and settlement reconcile marked equity after every operation. There are no
invented hedge fills or hard-coded option losses.

The interface includes Beginner/Quant views, manual option and stock tickets,
automatic benchmark hedging, Greek shocks, seven useful chart views, reports,
registered research and verified public replay. Tutor questions use actual current
contract, execution, position, numerical-solver or completed-research facts.

## TEST REPORT

**898 tests passed in 27.50 seconds: all original 747 plus 151 new cases.**
Collection comparison confirms **zero original test identifiers removed**.

| Added test file | Cases |
|---|---:|
| Unit option pricing | 56 |
| Integration options session | 37 |
| Integration options tutor | 42 |
| Integration options HTTP | 10 |
| Integration options research | 6 |
| Total new | 151 |

Coverage includes six published numerical benchmarks, parity/bounds/monotonicity
properties, all five Greeks versus finite differences, IV convergence/fallback/
invalid/boundary cases, near expiry, four buy/sell call/put combinations, FIFO
accounting, multipliers, partial liquidity, real hedges, fixed expiry references,
cash funding, stochastic MC validation, common random paths and deterministic replay.
Generated mixed option operations check equity conservation. Tutor tests cover
current facts, units, graded levels, disabled/error isolation, RNG separation,
same-revision rewind privacy and completed numerical diagnostics.

The final HTTP regression preserves original journal JSON text through browser
upload: parsing and reserialising in JavaScript can change 100.0 into 100 and break
a numeric checksum. Browser import, final-frame matching and backward stepping
were subsequently verified successfully.

Ruff checks and formatting pass across 175 Python files. JavaScript syntax checks,
dependency consistency and both new installed command-line entry points pass.
Browser acceptance covers buy, manual hedge/re-hedge, expiry, stock close, reports,
IV fallback, MC, finite differences, research-to-tutor and replay. Narrow-width
testing at 390 pixels verified stacking and no page-wide horizontal overflow;
wide tables scroll inside their own containers.

## HOW TO OPEN THE OPTIONS LAB

Open [the local Options Lab](http://127.0.0.1:8766/options).
The stock desk and learning dashboard are links in its header.

To start it again from the project directory:

    venv/bin/python -m quantlab.trading.server --port 8766

Use one server per learning profile. The app shares learning between stock,
options and dashboard pages. All browser/demo answers during development used
temporary separate profiles; they were not added to Arvind's progress.

## OPTIONS SCREEN WALKTHROUGH

1. **Trade & hedge:** choose expiry and click a call/put quote at a strike.
   The selected ticket shows strike, time remaining, multiplier, moneyness,
   theoretical value and six-decimal executable bid/ask. The chain rounds prices
   to four decimals and labels that rounding.
2. Choose buy/sell and whole contracts. Premium is per underlying unit; actual
   filled quantity, premium cash flow and fee appear after execution. Unfilled
   quote quantity cancels; stale revisions reject.
3. The **Delta Hedging Lab** shows option delta, actual stock holding and combined
   delta. Submit a manual market/limit stock order, or use the explicit benchmark.
   The stock book displays real aggregated depth and order counts.
4. Step the model clock. Check changing delta, positions and P&L charts.
5. **Pricing & Greeks:** inspect scales, finite-difference validation/parity, exact
   shock repricing versus local approximation, IV diagnostics, MC confidence
   intervals, and payoff/value/delta/gamma/synthetic-smile curves.
6. **Research:** register fresh paired sessions using the selected contract's
   original configuration. A completed study can be sent to the shared tutor.
7. **Session report & replay:** see additive P&L, Greek/exposure/hedging/volatility
   measures, download an ended journal and navigate verified public replay frames.

The default call expires on model day 30; the session allows 60 daily steps.
An expired option has no live quote or time value. Ending early marks positions;
stock closes only through real orders. A research horizon can extend past option
expiry, so distinguish full-session RV from the option's life.

## ONE MANUAL OPTION TRADE

Seed 42, stock £100, ATM call, strike £100, 30 ACT/365 days, multiplier 100,
zero rate/dividends, 20% base quote volatility.

| Opening item | Value |
|---|---:|
| Theoretical call value per unit | £2.287150628 |
| Synthetic bid | £2.272150 |
| Synthetic ask | £2.302151 |
| Midpoint mark | £2.2871505 |
| Buy one contract: premium cash flow | −£230.2151 |
| Explicit option fee | £0.05 |
| Option asset marked value | £228.71505 |
| Immediate net P&L | −£1.55005 |

Cash paid is not all an immediate loss: it acquires an option asset. The initial
marked loss is the ask-to-midpoint concession plus fee. Selling instead credits
cash and opens a liability; it does not create immediate realised premium profit.

## BLACK-SCHOLES EXAMPLE

A separate standard one-year benchmark makes the formula easy to reproduce:
stock=strike=£100, volatility 20%, rate 5%, dividend yield zero.
Call **£10.45058357**, put **£5.57352602** per underlying unit.
This differs from the manual ticket because time and rate differ.
The [first-principles lesson](../maths/phase_08_options.md) derives the variables,
assumptions and risk-neutral interpretation. Numerical reference cases are checked
against the primary [QuantLib test suite](https://github.com/lballabio/QuantLib/blob/master/test-suite/europeanoption.cpp).

## PUT-CALL PARITY EXAMPLE

Call minus put is £4.87705755, equal to discounted stock minus discounted strike:
100 − 100 exp(−.05). The model parity residual is zero to displayed precision.
An apparent executable-price discrepancy must still account for contract terms,
dividends, funding, fees, shorting and available size; it is not automatically free arbitrage.

## GREEKS WALKTHROUGH

For the one-year benchmark, per underlying unit:

| Greek | Analytic | Finite difference | Meaning |
|---|---:|---:|---|
| Delta | .636830651 | .636830643 | Local option-price slope versus stock |
| Gamma | .0187620173 | .0187620171 | Change in delta versus stock |
| Vega | 37.52403469 | 37.52403469 | GBP per 1.00 absolute annual volatility |
| Theta | −6.414027546 | −6.414027547 | GBP per model year elapsed |
| Rho | 53.23248155 | 53.23248154 | GBP per 1.00 absolute annual rate |

One volatility percentage point means .01: per-unit vega contribution about
£.37524035. Daily theta is about −£.01757268 per unit. Multiply by 100 for one
contract, then by signed contract count for a position. A negative quantity reverses
the exposure. Delta is a sensitivity, not literal real-world ITM probability.

In the shock lab a £.10 stock move gives exact change £.063776789 versus local
delta-plus-gamma £.063776875. For a £30 move the approximation overstates the exact
change by £2.55814. A £1 stock rise plus one elapsed day gives exact £.6283783
versus local £.6286390. Small-change accuracy does not justify large-shock certainty.

## IMPLIED-VOL SOLVER DEMO

Feed the one-year call's £10.45058357 premium back to the solver, starting at .30.
It recovers **.20 annual decimal volatility** in four evaluated iterations,
using three Newton updates and zero bisections. Residual is about −7.11e−15.
The solver reports status, method, bracket, iterations and residual.

## NEWTON-RAPHSON FAILURE / FALLBACK DEMO

Stock £100, strike £120 call, .25 years, rate .05, true model volatility .30:
target premium £1.0491632166. At starting volatility **.001**, numerical vega is zero.
Newton would divide by that slope, so the solver takes a safe bracket step instead.
Four subsequent Newton updates converge in six evaluations to
**.3000000000000035**, with residual about 3.73e−14.

The actual browser also recovered the selected OTM call's synthetic midpoint IV
after a .1% starting guess, reporting Newton + bisection and one bracket step.
At impossible prices, expiry or unidentified bounds the API rejects or returns
no reliable IV; an iteration limit is never silently labelled success.

## MONTE CARLO VS ANALYTIC PRICING DEMO

One-year benchmark call, independent pricing seed 42, analytical £10.45058357:

| IID terminal paths | Estimate | Standard error | Approximate 95% mean interval |
|---|---:|---:|---|
| 100,000 | £10.47364338 | £.04670079 | £10.38211042–£10.56517635 |
| 1,000,000 | £10.45130580 | £.01473418 | £10.42242730–£10.48018430 |

Risk-neutral drift is rate minus dividend yield; the physical trading-process
drift is not inserted into pricing. SE measures uncertainty in the average,
not the dispersion of individual payoffs. Ten times the paths reduces typical
SE by roughly √10, not ten. Analytical pricing remains faster for this contract.

## ONE MANUAL DELTA-HEDGING SESSION

These events were performed in the browser and reproduce in the saved demo.

| Event | Stock | Stock held after action | Combined delta | Net marked P&L |
|---|---:|---:|---:|---:|
| Buy one ATM call | £100.00 | 0 | +51.1436 | −£1.55005 |
| Manually sell 51 stock at £99.99 | £100.00 | −51 | +.1436 | −£2.11105 |
| Observe day 1 | £100.21 | −51 | +1.6071 | −£5.70135 |
| Manually sell two more at £100.20 | £100.21 | −53 | −.3929 | −£5.72335 |
| Leave hedge unchanged to expiry, day 30 | £100.77 | −53 | −53 | −£194.23810 |
| Manually buy back 53 at £100.78 | £100.77 | 0 | 0 | −£194.82110 |

The first two hedges only offset sensitivity at those observations. This deliberately
sparse policy leaves a changing exposure for the next 29 days. At expiry the option
disappears, leaving the stock short until the user closes it.
All three stock orders created actual Phase 1 executions; there was no direct
assignment of a mathematical hedge target to inventory.

## DISCRETE-HEDGE FREQUENCY EXPERIMENT

Registered root 88042, development pool, 1,000 matched paths; **4,000 complete sessions**.
Each buys one ATM 20-day call, multiplier 100, flat 20% quote volatility, zero
rate/drift, stock process volatility 20%. Every variant sees the same stock path.
Hedged variants start with a hedge and perform a final hedge at expiry.

| Hedge schedule | Mean net P&L | P&L SD | Mean explicit fees | Mean stock turnover | Mean interval RMS delta |
|---|---:|---:|---:|---:|---:|
| Every step | −£3.8935 | £36.6346 | £.28746 | 237.458 | .2687 |
| Every 5 steps | −£5.8293 | £78.1644 | £.19991 | 149.914 | 13.7285 |
| Every 20 steps | −£4.6548 | £145.1890 | £.15200 | 102.000 | 27.8265 |
| No hedge | −£12.2956 | £285.8320 | £.05000 | 0 | 53.3353 |

Daily hedging reduced dispersion and sampled residual exposure, while increasing
turnover/fees. **The mean-P&L comparison does not prove daily superiority.**
Every-five minus daily mean difference was −£1.9358, 95% paired mean interval
[−£6.2015, +£2.3298]; every-twenty minus daily was −£.7613,
interval [−£9.4299, +£7.9072]. Both include zero.

Fees here are explicit fees. Stock bid/ask concessions also enter actual P&L:
in this one-contract, ample-depth experiment the hedge pays £.01 per traded stock
unit, so its mean spread cost rises with turnover. Option entry concession is
also included. Those costs must not be subtracted again from net P&L.
Small grid-based RMS delta does not eliminate unobserved within-step/gamma risk.

## REALIZED VS IMPLIED VOLATILITY EXPERIMENT

Registered before execution, 1,000 common-shock paths; **3,000 complete sessions**.
Same 20-day long call and initial 20% quote volatility, daily hedging:

| Stock process volatility | Mean observed RV | Mean net P&L | P&L SD |
|---|---:|---:|---:|
| 15% | 14.8978% | −£50.9796 | £31.8492 |
| 20% | 19.8642% | −£3.8935 | £36.6346 |
| 30% | 29.7973% | +£90.9188 | £69.2332 |

The model's average direction is sensible for a long-gamma, delta-hedged position.
The 20%-minus-15% paired mean difference is £47.0862, interval
[£45.9695, £48.2028]; 30%-minus-15% is £141.8985, interval
[£137.9092, £145.8877]. These are conditional development results, not a trading rule.
Future RV is unknown in live trading; costs, gamma weighting, discrete rebalancing,
path dependence and model error remain relevant.

## OPTION EXPIRY DEMO

At day 30, observed stock £100.77 gives call payoff £.77 per unit, or £77 for
one 100-unit contract. The option closes exactly once; realised gross option
P&L becomes £77 − £230.2151 = **−£153.2151**. Time value is zero.
That expiry reference and payoff remain fixed if the stock moves on later days.
The short stock hedge is a separate position and is not silently settled with the option.

## P&L / GREEKS SESSION REPORT

Final closed demo positions: zero option contracts and zero stock.

| Additive component | GBP |
|---|---:|
| Option realised gross | −153.2151 |
| Option unrealised | 0 |
| Stock realised gross | −41.4500 |
| Stock unrealised | 0 |
| Financing | 0 |
| Less all explicit fees | −.1560 |
| **Net P&L = final cash/equity** | **−194.8211** |

After the first option fill: delta 51.1436, gamma 6.95484, vega 1143.26204 per
1.00 volatility, theta −1390.96882 per year, rho 401.55965 per 1.00 rate.
Ending Greeks are zero. Maximum absolute delta 53; gamma 13.22319;
vega 1143.26204. There were three executed hedge occasions and 106 stock units
of turnover. Observed RV was 19.7793%; starting quote input 20%; ending IV is
undefined for the expired contract. Maximum recorded portfolio drawdown £194.8211.

Premium, marked option value, spread diagnostics and cash balance are not
additional terms to add to the P&L table.

## PHASE 5 RESEARCH INTEGRATION DEMO

OptionsAdapter runs the same session/exchange through the existing generic engine.
Registration, addressed seeds, complete-run records, distributions, uncertainty,
bootstrap, paired analysis and version metadata are reused. The worst session
from each large study was regenerated with full evidence: metrics and both
fingerprints matched, then the resulting options journal replayed exactly.
Original registered outcomes remain unchanged after display-only refinements.

Saved evidence:

- [Frequency registration and complete results](phase_08/experiments/frequency/experiment.json)
- [Frequency summary](phase_08/experiments/frequency/phase8-summary.json)
- [Volatility summary](phase_08/experiments/volatility/phase8-summary.json)
- [Frequency extreme-session replay](phase_08/experiments/frequency/verified-worst-session.json)
- [Volatility extreme-session replay](phase_08/experiments/volatility/verified-worst-session.json)

## PHASE 7 TUTOR INTEGRATION DEMO

After the actual call purchase, the tutor asks whether paying premium is immediately
a realised loss. Its worked facts show one contract × 100, actual premium, cash
flow and fee. The demonstration requested a hint, then selected that cash falls
alongside an option asset; the recorded result was assisted success.
Numerical questions calculate signed option exposure and additional stock needed
from actual quantities/multipliers/Greeks. Solver lessons use actual diagnostic output.

A separate browser study ran 32 paired paths for the selected OTM call. Choosing
“Ask the tutor about these results” produced a standard-error lesson from its actual
daily-hedged sample: mean −£2.35226, SD £8.39487, SE £1.48402.
No sample answer or P&L result was credited to Arvind. Unanswered concepts remain
unassessed. Rewind/new-session logic removes future active derivative contexts.

## PERFORMANCE REPORT

Measured locally on macOS arm64, Python 3.14.0, NumPy 2.5.3, SciPy 1.18.1.
Individual timings are medians of five warmed calls and depend on machine load.

| Task | Measured time |
|---|---:|
| One analytical price | .000917 ms |
| 100k MC paths, full estimate/SE/interval | 6.958 ms |
| 1m MC paths, full estimate/SE/interval | 71.284 ms |
| 100k scalar payoffs, pre-generated normals | 11.127 ms |
| Same vectorised payoff calculation | .471 ms |
| One 20-day daily-hedge session, reduced capture | 23.147 ms |
| Same session with full evidence | 43.772 ms |
| 4,000 frequency sessions, engine execution/analysis | 48.247 seconds |
| 3,000 volatility sessions, engine execution/analysis | 65.036 seconds |

Vectorisation improved the measured payoff calculation about 23.6×, with
numerical-equivalence checks. Batch capture avoids repeated bulky evidence but
keeps accounting/conservation checks. Full/reduced metrics and fingerprints agree.
Profiling identifies exact-accounting/invariant work as a large execution cost;
those checks were retained. See [timings](phase_08/demo/performance.json) and
[cumulative profile](phase_08/demo/hedging-profile.txt). Batch times are not directly
comparable to isolated medians because workloads and capture differ.

## FILES CHANGED

New Python modules under src/quantlab/options:

- models.py: contract and pricing units/validation.
- pricing.py, iv.py, monte_carlo.py: analytical prices/Greeks, diagnosed roots and MC.
- quotes.py: finite synthetic dealer quotes and transparent smile.
- portfolio.py: exact FIFO option cash, positions, realised/unrealised reconciliation.
- underlying.py: actual Phase 6/Phase 1 stock venue integration.
- session.py: causal stock steps, commands, hedges, funding, expiry, reports/replay.
- analytics.py: server-produced curves, shocks and realised volatility.
- research.py: reusable Phase 5 derivatives adapter.
- application.py and package initializer: local app boundary and API.

New options_demo.py and options_experiments.py create reproducible evidence.
The server adds options routes; options.html/css/js add the interface.
Existing stock/learning pages link to it; tutor.js supports the derivatives panel.
Tutor catalog/context/questions/service/progress/bridge integrate the new public
facts, prerequisites and lessons, with new tutor/derivatives.py.
Five new test files contain 151 cases. pyproject.toml and package version are
0.8.0 with two entry points; .gitignore excludes private options sessions.
README, ROADMAP, ASSUMPTIONS, LEARNING_LOG, CHANGELOG, architecture, maths lesson
and this review/evidence directory are updated.

## RED TEAM

**Fixed during review:** independent premium/multiplier ledger checks; buy-versus-sell
cash lessons; stale quote rejection; zero/low-vega diagnostics; exact expiry
reference persistence; original-text browser replay; same-revision rewind privacy;
mutable snapshot isolation; saving errors separated from financial outcomes; end
still permitted at the command budget; midpoint input precision; explicit
six-decimal tickets and small-screen overflow.

**Remaining limitations:**

- The option dealer has synthetic finite quotes, not a full exchange or risk-managed
  counterparty. Liquidity refreshes mechanically. No option price discovery, margin,
  assignment, jump risk, stochastic volatility or impact calibration is claimed.
- The smile is transparent but not guaranteed free of cross-strike/calendar arbitrage.
  Fixed-volatility Greeks differ from total sensitivities of a moving smile.
- Continuous frictionless Black–Scholes assumptions differ from discrete, costly
  stock execution. Borrowing is unlimited inside position limits; zero live dividends
  avoid silently omitting dividend cash flows.
- Marking at midpoint is not executable liquidation. Explicit fees exclude spread
  already embedded in fills. Gross hedging error and RMS delta measure different things.
- RV and confidence intervals are finite-sample/model-conditional. Daily grid
  neutrality does not remove gamma or overnight/gap exposure. No future RV rule is
  used to pick profitable paths.
- IV near bounds can be economically unstable even with a tiny numerical residual.
  Midpoint spreads can materially change IV for deep OTM contracts.
- Replay checksums detect disagreement, not malicious forgery. A person who knows
  the seed or ending can reconstruct a path; public-view isolation is pedagogical.
- Live sessions are memory-resident. Large histories/evidence incur cost; the local
  app serves a shared session and one writer per learning profile. Cross-version
  exact replay is explicitly unsupported.
- Structured tutor answers test particular claims/calculations, not a calibrated
  measure of broad expertise. Automated demo answers never establish user mastery.

## 3-QUESTION ARVIND CHECK

1. You pay £230.2151 for the call. Why is that not immediately a £230.2151 loss?
2. Selling 51 shares nearly hedged the call. Why did the hedge need changing after
   the stock moved, even though no new option was bought?
3. Newton's IV update divides by vega. What can go wrong when vega is nearly zero,
   and what does keeping a bracket protect?

Phase 8 awaits Arvind's review. **Do not begin Phase 9.**
