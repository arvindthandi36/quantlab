# Phase 3 review — informed flow and markouts

> Historical phase record. Current core conventions and release status are in the root README, ASSUMPTIONS and Phase 11 release report. Test counts and runtime labels below describe this phase.


Owner: **Arvind Thandi**. Verified: 10 September 2026. QuantLab 0.3.0.
Phase 3 is implemented; **Phase 4 remains unstarted, pending review and authorisation**.

## BUILD REPORT

Added a simple informed trader, an independent noisy-signal source, an executable
edge rule with an explicit cost allowance and uncertainty buffer, and provider
markouts at 1/5/20 subsequent processed events. Every transaction still comes from
the existing FIFO matching engine. No losses, profits or post-fill price moves
are assigned by an informed-trader rule.

The [six-part information contract](../maths/phase_03_information.md) was documented
before implementation. Normal agents retain public observations only. An informed
agent receives current public quotes and a fresh noisy measurement, its timestamp
and stated accuracy. Latent truth, actual signal error and future records remain
outside agent inputs. Observer debug shows those diagnostics for learning.

Public output now uses separate sanitised types and anonymous order IDs. It omits
trader identity/type, private holds, seed, model parameters and hidden values.
Private events cannot advance a public snapshot timestamp. The observer journal
contains privileged research state and is explicitly labelled as such.

JSON schema 2 stores informed audits. Replay recomputes decisions from saved
signals and then-current public quotes, then verifies actual matching. Old Phase 2
schema-1 journals remain readable. Informed flow is opt-in: `--informed` enables
one arrival per second in expectation; the original default Phase 2 run remains.

No market-making strategy, account, inventory management, P&L, options or machine
learning was added. There are no new runtime dependencies.

## TEST REPORT

**248 passed; 0 failed, 0 skipped.** The 184 existing cases remain, with 64 new cases:

| New test file | Cases | Main evidence |
| --- | ---: | --- |
| `tests/unit/test_informed.py` | 33 | Known signal draws, valid noise, belief arithmetic, costs, strict threshold, buy/sell/hold, missing quotes, stale/future rejection |
| `tests/unit/test_markouts.py` | 12 | Both provider signs, spread-to-adverse examples, pending/missing references, exact maturity, prefix-only access and multi-fill orders |
| `tests/integration/test_informed_market.py` | 14 | Reproduction, replay without RNG, conservation, old journals, unchanged past under longer horizons, stream separation, public data/timing boundaries, corrupt audits |
| `tests/statistical/test_information.py` | 5 | Signal error moments, posterior calibration, clean/strong signal behaviour and selection without assigned losses |

The full suite contains 10 statistical cases. The existing generated-operation
test runs 200 Hypothesis examples; these examples are not counted as 200 separate
pytest cases. Existing single/partial/multi-level/multi-order fills, market
remainders, cancellations and generated mixed sequences still reconcile measured
buyer quantity = seller quantity = recorded trade quantity. Always-on failure
guards remain active under Python optimisation.

Statistical evidence is deliberately scoped. Error-moment tests use 12,000 draws
per noise level; belief calibration uses 8,000 trials under the stated Gaussian
prior. Behaviour comparisons use 8,000 paired measurements. A separate 7,000-trial
selection test draws truth, noisy information and later shocks, executes informed
orders through the real book, and compares provider reference valuations with
random-direction flow. It requires some informed trades to be wrong. This is a
controlled data-generating process, not a calibrated whole-market experiment.

Sampling comparisons use documented six-standard-error tolerances. Cleaner
signals improve estimation under the assumed prior, encourage buying a real
positive value gap and discourage unnecessary trading at fair quotes. Stronger
positive value gaps encourage buying. Better information need not raise total flow.

Ruff lint and format checks, dependency consistency and installed command-line
entry points pass. The saved short demo matches a fresh seeded run and its replay
exactly, including its rendered debug timeline and derived markouts. Verified
environment: Python 3.14.0 on macOS; pytest 9.1.1, Hypothesis 6.168.0, Ruff 0.16.6.
Other supported Python versions have not been exercised here.

## ONE SHORT DETERMINISTIC DEMO

Run from the repository root:

```bash
venv/bin/quantlab-market-demo --informed --seed 42 --duration 5 --debug
venv/bin/quantlab-market-demo --debug --replay docs/learning/phase_03_session.json
venv/bin/quantlab-market-demo --informed
```

The first command shows observer diagnostics. The second checks saved evidence;
do not add `--informed` to replay, which uses saved configuration. The third is
the normal public view. `--limit` bounds the displayed timeline, not the run;
`--expand-orders` adds FIFO detail to final aggregated depth.

Actual result: **15 events, 3 trades, 3 executed units**, from unchanged seed 42.
The times below all start at the illustrative 09:30 origin. Prices are rounded
for explanation; the [captured trace](phase_03_demo.txt) and
[observer JSON](phase_03_session.json) retain the underlying evidence.

| Time | Event and explanation |
| --- | --- |
| 00.009521 | Informed signal ≈ £100.0339; estimate ≈ £100.0319. The book is empty, so it holds. Information cannot create a counterparty. |
| 00.269340 | Noise trader randomly buys 1 with a £100.01 limit, opening reference plus one tick. No ask exists, so its bid rests. |
| 01.000000 | Latent value moves from £100 to ≈ £99.9934. Existing bids do not change. |
| 01.066817 | Informed signal ≈ £99.9814, error ≈ −£0.0120; estimated value ≈ £99.9825. The £100.01 bid offers ≈ 2.750 ticks of sell edge against a 1.470-tick hurdle. It submits a one-unit sell limit at that bid. Trade #1 executes at the resting buyer's £100.01. |
| 02.000000 | Latent value becomes ≈ £99.9857. Trade #1's 1-event latent markout matures: the resting buyer paid £100.01, now ≈ 2.426 ticks above the reference. |
| 02.066857 | Noise trader randomly bids for 2 at £100.02: last transaction plus one tick. With no seller, both units rest. |
| 02.451686 | Liquidity trader needs to buy 3 immediately. There are no asks; all 3 remain unfilled and are cancelled. |
| 03.000000 | Latent value falls to ≈ £99.9830. This event creates no transaction. |
| 03.438500 | A one-unit liquidity sell matches the £100.02 bid: trade #2. One bid unit remains. Trade #1 also reaches its 5-event horizon, with latent markout ≈ −2.698 ticks. |
| 03.656763 | Another liquidity trader sells 2. Trade #3 fills the remaining 1 at £100.02; unmet size 1 is cancelled. |
| 04.000000 | Latent value rises slightly to ≈ £99.9843; the depleted book stays empty. |
| 04.209911 | A random four-unit noise sell rests at £100.00, last transaction minus two ticks. |
| 04.471500 | A random three-unit noise sell rests at £100.02, last transaction plus zero ticks. |
| 04.485043 | Informed signal ≈ £99.9836; error ≈ −£0.0006; estimate ≈ £99.9858. Buying at £100 has negative estimated edge, and no bid exists to sell to. It holds. |
| 05.000000 | Latent value ends ≈ £99.9721. Last actual transaction remains £100.02. The horizon ends without invented fills. |

Final aggregated asks: 3 units / 1 order at £100.02 and 4 units / 1 order at
£100.00. No bids. Submission accounting is **17 order-units = 2 × 3 traded units
+ 7 resting units + 4 cancelled units**. Every actual fill has one measured unit
on each side and one recorded unit.

All matured midpoint markouts in this tiny run are unavailable because their
horizon books lack one side. The 20-event horizons remain pending. The program
does not substitute latent values into the missing midpoint column. Trades #2
and #3 also have negative latent markouts despite being liquidity-driven, which
is a useful reminder that a negative markout alone does not identify informed flow.

## DUMMY EXPLANATION

One trader now has an imperfect thermometer for hidden value. The other traders
only see the market. The informed trader compares its best estimate with prices
someone is actually offering, leaves room for assumed costs and mistakes, and
either sends an ordinary order or waits.

In the demo, a buyer's old £100.01 bid looks generous to an informed seller whose
estimate is about £99.9825. The seller accepts it. The engine sees an ordinary
crossing limit, matches one unit and uses the resting bid as the transaction price.
Later analysis judges that purchase against a later reference. No component writes
“make this buyer lose” into the market.

## MATHS LESSON

The complete [first-principles lesson](../maths/phase_03_information.md) defines
every symbol, units, probabilities, sampling tolerances and assumptions. Its core:

- **Noisy signal:** Y = X + ε. X is current hidden value, Y the reading; error ε
  averages zero but can be large. Its standard deviation η measures usual uncertainty.
- **Conditional expectation:** a probability-weighted average after receiving
  evidence. Under the assumed Gaussian belief, estimate = m + w(Y − m), where
  w = τ²/(τ² + η²). A less reliable reading receives less weight.
- **Expected edge:** estimated value minus executable ask for buying, executable
  bid minus estimate for selling. Compare with H = c + b + zu. The agent's
  uncertainty u = τη/√(τ² + η²), not knowledge of its actual measurement error.
- **Information quality:** η = 2 and prior uncertainty τ = 8 give w ≈ 0.941 and
  u ≈ 1.940 ticks. With c = 0.25, b = 0.25 and z = 0.5, H ≈ 1.470 ticks.
- **Adverse selection:** an informed taker preferentially accepts stale quotes
  favourable to itself. The provider's filled orders are therefore a selected
  subset, not a random sample of the prices it was willing to offer.

The belief is subjective, reset per signal and uncalibrated. Its conditional mean
is exact under its assumed prior, not a claim of perfect filtering in this market.
Signals measure current value. Future latent shocks still have zero expected
increment; information does not predict or cause the next random shock.

## MARKOUT EXPLANATION

For the resting provider, d = +1 for a buyer and −1 for a seller:

**Markout = d × (future reference − execution price)**

Positive means favourable to that provider, negative adverse. It is a gross,
per-unit reference valuation, not an actual exit, fee-adjusted result or P&L ledger.

For trade #1 the provider bought at £100.01. One event later latent reference is
approximately £99.985735, so its markout is approximately **−£0.024265 per unit**.
The informed seller's decision did not receive this future value or markout.

To separate apparent spread from later movement, write:

**Markout = initial signed reference edge + subsequent signed reference movement.**

The mirrored controlled tests illustrate the user's requested stale-seller and
stale-buyer situations. These are analytic fixtures using real matching, not
additional claimed random demo runs:

| Provider | Execution | Pre-trade midpoint | Later midpoint | Initial edge | Reference move | Markout |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Resting seller, informed buyer | £100.05 | £100.025 | £100.075 | +£0.025 | −£0.050 | −£0.025 |
| Resting buyer, informed seller | £99.95 | £99.975 | £99.925 | +£0.025 | −£0.050 | −£0.025 |

Later quotes are separate exogenous instructions in these fixtures; the informed
agent never receives them. Both directions can also produce favourable provider
markouts in separate tests. There is no forced one-way outcome.

An event horizon counts subsequent processed market events, including latent and
private holds. A trade in event 4 reaches h=1 after event 5, and h=5 after event 9.
Scheduling IDs such as `[e5]` are insertion IDs, not this processed-event count.
`analyse_markouts(session, as_of_events=k)` excludes later records even when the
caller holds a complete session. Unreached horizons stay pending; absent future
midpoints stay missing. These analytics are observer-only in Phase 3.

## FILES CHANGED

Paths below are relative to the project root; links open the main implementations.

| Files | Change |
| --- | --- |
| [agents/informed.py](../../src/quantlab/agents/informed.py) | New measurement/decision types and Gaussian belief/edge rule |
| [market/signals.py](../../src/quantlab/market/signals.py) | New signal sampler and privileged audit |
| [market/public.py](../../src/quantlab/market/public.py) | New public-only types, aliases and projections |
| [analytics/markouts.py](../../src/quantlab/analytics/markouts.py), `analytics/__init__.py` | New markout records, signs, references and maturity calculations |
| `market/config.py`, `market/events.py`, `market/records.py`, [market/simulation.py](../../src/quantlab/market/simulation.py) | Added informed parameters/events/audits, signal delivery and safe public snapshots |
| [market/replay.py](../../src/quantlab/market/replay.py), `market/journal.py` | Decision audit verification, schema 2 and Phase 2 compatibility |
| `market/timeline.py`, `market_demo.py` | Explicit public/debug views, private diagnostics, markouts and opt-in CLI |
| `src/quantlab/__init__.py`, `pyproject.toml` | Version 0.3.0 |
| Four new test files listed above | 64 added cases |
| [Model/lesson](../maths/phase_03_information.md), [architecture](../architecture/phase_03.md), this report, `phase_03_demo.txt`, `phase_03_session.json` | Design contract, teaching, actual captured evidence |
| `README.md`, `ROADMAP.md`, `ASSUMPTIONS.md`, `LEARNING_LOG.md`, `CHANGELOG.md` | Current scope, usage, limitations and review gate |

The matching-engine implementation remains the established component; all its
tests run again with Phase 3. FIFO depth and always-on conservation are preserved.

## RED TEAM

1. **Beliefs are not calibrated.** The public anchor plus fixed Gaussian prior is
   a transparent approximation, not the true conditional distribution of latent
   value given this evolving book. Accuracy tests under that prior cannot certify
   calibration of the full simulation. Repeated signals are not accumulated.
2. **Execution is unusually easy.** One-unit aggressive limits see and reach a
   quote atomically. There is no latency race, hidden liquidity, inventory, credit
   constraint or competing informed population. The uncertainty buffer covers
   estimate uncertainty, not every risk faced by a real trader.
3. **Markouts are diagnostics.** Negative marks can result from unrelated shocks
   or changing quotes. Midpoints may move mechanically after depletion, may be
   non-executable, or may not exist. Latent references are model truth, not traded
   exit prices. Neither source alone proves causal adverse selection or profitability.
4. **The first demo is sparse.** It has one informed fill and no usable midpoint
   at the selected maturities. It cannot establish a stable effect. Controlled
   mirrored and stochastic tests establish the declared mechanisms, not real-market alpha.
5. **No economic ledger yet.** Decision costs are assumed allowances; cash, fees
   and P&L are not booked. Quantity conservation protects units, not monetary accounting.
6. **Privacy is an interface boundary.** Public types and normal agent inputs are
   tested for leaks, including private event timing. The full Python simulator,
   seed and saved journal are privileged; this is not a sandbox for hostile code.
7. **Horizon and storage limits matter.** Event horizons depend on the mix of
   private/public events, so they are unsuitable for a public feed as currently
   defined. Full immutable book histories favour short explanations over long-run
   efficiency. Replay proves consistency, not authenticity or cross-version RNG identity.

## 3-QUESTION ARVIND CHECK

1. The numerical signal stays the same but its noise increases. Should its weight
   in the estimate rise or fall?
2. Estimated value is £100.08, ask £100.06, hurdle £0.03 per unit. Buy or hold, and why?
3. A resting seller sells at £100.05; later reference is £100.08. What is its
   per-unit markout, and is it favourable or adverse?

These are learning checks, not a mastery score. Phase 4 waits for Arvind's review.
