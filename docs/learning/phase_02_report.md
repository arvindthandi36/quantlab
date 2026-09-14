# Phase 2 build, verification and walkthrough

> Historical phase record. Current core conventions and release status are in the root README, ASSUMPTIONS and Phase 11 release report. Test counts and runtime labels below describe this phase.


Project owner: **Arvind Thandi**. 10 September 2026. Version 0.2.0.
Phase 2 review is pending; Phase 3 has not started.

## What changed

The existing matcher now checks actual buyer/seller reductions against every
recorded trade and reconciles totals across each submission. A failed check raises
and disables subsequent trading on that instance. Depth displays aggregate
**Price | Total Quantity | Order Count**, with optional FIFO expansion.

A new small market starts empty and runs automatically: a microsecond event
clock/queue, latent-value updates, noise limits, liquidity market orders, a real
transaction tape, isolated seeded RNG streams and versioned JSON replay.

## Exact verification results

**184 tests passed**, with no skipped or expected-failure tests, on Python 3.14.0
and macOS. Ruff lint and formatting pass. No new runtime dependencies were added.

| Stage | Exact collected test cases |
| --- | ---: |
| Original Phase 0/1 baseline rerun | 83 |
| After requested conservation/depth additions | 105 |
| Final suite, including Phase 2 | 184 |

The final suite includes five statistical cases: arrival counts at two rates and
Gaussian increment moments at three time intervals. These use justified sampling
tolerances. The existing Hypothesis case generates 200 mixed-operation sequences;
that is one collected pytest case, not 200 separate test cases.

Verification covers chronological/tied events, horizon semantics, model units,
invalid inputs, absence of latent information in trader APIs, absence of latent
effects on order/trade paths, independent arrival versus decision streams, exact
seed reproduction, empty markets, true tape provenance, conservation, bounded
display, saved/replayed output, corrupted journals and failure to resume after an
aborted event. Two injected accounting bugs prove the book's conservation guards
raise rather than silently accepting wrong trade or cumulative volume.

## Run and inspect

From the repository root:

```bash
venv/bin/quantlab-market-demo --debug
venv/bin/quantlab-market-demo --debug --save session.json
venv/bin/quantlab-market-demo --debug --replay session.json
venv/bin/quantlab-market-demo --expand-orders
venv/bin/quantlab-demo --expand-orders
```

Default market view hides latent values; `--debug` explicitly reveals observer
values. `--limit` controls displayed event count; it does not truncate the journal.
The default run uses seed 42, five seconds, one-second latent updates, σ = 2 ticks
per √second, noise intensity 1/s, liquidity intensity 0.6/s, and a £0.01 tick.

The [captured timeline](phase_02_demo.txt) and [saved observer journal](phase_02_session.json)
come from an actual run. Saved instructions were replayed against a fresh book;
every execution report and snapshot agreed. No random draws were made during replay.

## The actual demo, event by event

Time below is elapsed seconds after the illustrative 09:30 origin. Latent currency
values are rounded to four decimals for display; full floating-point values remain
in the journal. There is no initial standing liquidity.

| Time | Event and explanation |
| --- | --- |
| 0.269340 | Noise buys 1 with limit £100.01. Its random offset is +1 tick from the public £100 opening reference. There are no asks, so this becomes the first resting bid. |
| 1.000000 | The scheduled latent update moves hidden value from £100 to about £99.9934. No order is submitted; the bid remains at £100.01. |
| 2.000000 | The next latent update moves hidden value to £99.9857. There is still no trade. |
| 2.066857 | Noise buys 2 with limit £100.01, again opening reference +1 tick. There is no two-sided midpoint or last trade yet. This joins behind the earlier bid: 3 units across 2 orders. |
| 2.451686 | Liquidity flow requests a market buy of 3 for an external execution need. Buyers cannot execute against other buyers; with no asks, all 3 units are unfilled and cancelled. |
| 3.000000 | Hidden value moves to £99.9830. Both bids remain unchanged because no trader observes this value. |
| 3.438500 | Liquidity flow needs to sell 1. It matches the oldest bid, executing 1 at that resting order's £100.01. This is tape trade #1. |
| 3.656763 | Liquidity flow needs to sell 2. The next bid supplies both units at £100.01: tape trade #2. Both bids are now exhausted. |
| 4.000000 | Hidden value rises slightly to £99.9843. The book remains empty and no trade occurs. |
| 4.209911 | Noise sells 4 at £99.99: last transaction £100.01 minus a random 2-tick offset. No bids remain, so all 4 units rest as an ask. |
| 4.471500 | Noise sells 3 at £100.01: last transaction plus a zero offset. This creates another ask level; no buyer appears to execute it. |
| 5.000000 | The final scheduled latent update moves value to £99.9721. The run ends with 7 ask units across 2 levels, no bids, and 2 trades totalling 3 units. |

The final last transaction is **£100.01**, hidden value is approximately **£99.9721**,
and the best ask is **£99.99**. These are different concepts. With no bid, current
spread and midpoint are unavailable. No realised/unrealised P&L is calculated.

The seven order submissions total 16 units. Three traded units consume three
buyer units and three seller units. Seven units remain as asks and three unmet
market-buy units were cancelled: **16 = 2 × 3 + 7 + 3**.

## First-principles maths

The new concepts are fair direction coins, uniform integer sizes/offsets, expected
arrival rates, exponential gaps, Poisson counts, Gaussian random steps, variance
and square-root-time scaling. They are defined with variables, units, examples,
tests and weaknesses in [the maths lesson](../maths/phase_02_market.md).

## Files changed relative to the Phase 1 delivery

Existing files updated:

- `src/quantlab/orderbook/book.py`: per-fill/whole-submission reconciliation and failed-book guard.
- `src/quantlab/orderbook/models.py`: measured buyer/seller report totals and level order count.
- `src/quantlab/demo.py`: aggregate depth and `--expand-orders`; Phase 1 JSON schema moves to 2.
- `src/quantlab/__init__.py`, `pyproject.toml`: version 0.2.0 and new console entry point.
- `tests/integration/test_generated_sequences.py`: independent two-sided reductions and side checks.
- `README.md`, `ROADMAP.md`, `ASSUMPTIONS.md`, `CHANGELOG.md`, `LEARNING_LOG.md`:
  current capabilities, review gates, assumptions and learning evidence.
- Phase 1 architecture, maths, report/review notes and demo capture: conservation/display
  additions and truthful historical status.

New source files:

- `orderbook/conservation.py`, `orderbook/display.py`: invariant and aggregate-depth presentation.
- `agents/__init__.py`, `agents/basic.py`: public observations and two explained trader rules.
- `market/__init__.py`, `market/config.py`: market package and validated parameters/units.
- `market/events.py`, `market/processes.py`: integer clock/heap and stochastic equations.
- `market/records.py`, `market/simulation.py`: event evidence, tape, step/run orchestration.
- `market/replay.py`, `market/journal.py`, `market/timeline.py`: verification, serialisation and output.
- `src/quantlab/market_demo.py`: run/save/replay CLI. Other source paths above are inside `src/quantlab/`.

New tests: `unit/test_conservation.py`, `unit/test_depth_display.py`,
`unit/test_events.py`, `unit/test_market_models.py`, `unit/test_basic_agents.py`,
`integration/test_simulation.py`, `integration/test_replay.py`, and
`statistical/test_market_processes.py`, all under `tests/`.

New documentation/artifacts: this report, the maths lesson, the architecture
walkthrough, the captured Phase 2 timeline and its JSON observer journal.

## RED TEAM

1. **No price discovery toward latent value.** Neither agent sees it, so prices
   may wander away indefinitely. This is deliberate isolation of mechanics, not
   a calibrated equilibrium model.
2. **Artificial order flow.** Constant independent arrival rates, fair directions,
   uniform sizes, no account constraints, abandoned unmet needs and no autonomous
   cancellations omit real behaviour and can produce stale/unbalanced books.
3. **Simple value process and costly debugging.** Gaussian constant-volatility
   steps miss jumps/regimes and may leave the positive domain. Full snapshots cost
   memory, microsecond rounding approximates arrival times, and atomic events omit
   latency. Replay is a consistency check, not proof of financial realism or authenticity.

## Three-question check

1. Why did the market buy at 2.451686 seconds fail despite 3 bid units being visible?
2. At an average noise rate of 1/s, how many arrivals do you expect over 5 seconds—and must exactly that many occur?
3. Why could trades execute at £100.01 while latent value was below £100?

Phase 3 requires Arvind's review and explicit authorisation.

