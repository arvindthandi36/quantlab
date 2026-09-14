# Phase 6 review — the manual trading desk

> Historical phase record. Current core conventions and release status are in the root README, ASSUMPTIONS and Phase 11 release report. Test counts and runtime labels below describe this phase.


## BUILD REPORT

Phase 6 is implemented. The local browser is a command/display adapter over the
existing OrderBook, event-driven MarketEnvironment, informed/noise/liquidity agents,
FIFO MakerAccount and Phase 4 quote planner. The research engine remains available.
Phase 7 has not begun. No claim of learning mastery is inferred from implementation.

You can personally buy/sell, select market/limit, quantity and price, keep multiple
limits, cancel one/all, inspect FIFO queues, watch partial fills and cumulative
VWAP, hold longs/shorts and observe reconciled P&L. No browser code invents fills or
calculates accounts. The manual and automated maker have separate owned orders
and ledgers. New phases can add scenarios through data and share this exchange.

## TEST REPORT

**599 tests pass: all 486 previous cases plus 113 Phase 6 cases.** The existing
research-version assertion now compares the runtime version instead of hard-coding
0.5.0; its reproducibility test is preserved. Ruff lint and format checks pass,
and the installed dependencies reconcile. Verified Python: 3.14.0 on macOS.

New cases cover hand-calculated buys/sells, marketable/resting limits, partial fills,
FIFO queues, multi-price VWAP, cancellation/re-entry, cash/fees/FIFO P&L, opening
endowments, long/short signs and reserved capacity. Other cases cover deterministic
time controls, public/private boundaries, markout maturity/missingness, manual
quotes, scenarios, tutor hint/retry, both replay methods, tamper detection, generated
mixed operations and actual localhost HTTP requests. Save failures stay visible;
action budgets close sessions without executing an extra order. Matching and account
checks remain enabled, including tests that intentionally corrupt quantities/fees.

The generated mixed-operation test runs 25 Hypothesis examples of up to 30 actions
interleaved with real background events, then checks both replay paths. That is one
collected test case; examples are not inflated into the reported test count.

Browser checks independently exercised the six-unit market buy, FIFO depth expansion,
selected cancellation, a passive sell filling 2 then 3 units, short creation and
covering, end report, actual file upload and verified replay, manual two-sided
quotes, Quant/Beginner switching and Start/Pause. The clock remained 09:30:37.250
while switching views after Pause. No brittle pixel assertions were added.

Measured example, 60-second toxic-flow scenario with an initial manual buy: 451
public actions / 637 evidence records, 0.988 seconds simulation, 2,638,347-byte
journal, 0.091 seconds export, 1.537 seconds verified replay with 465 public frames.
Mean full-state projection over 50 reads was 1.501 ms. These are one-machine
measurements, not performance guarantees. Invariants were not weakened.

## HOW TO LAUNCH THE TRADING SIM

From `<project>`:

```bash
venv/bin/quantlab-trade
```

Equivalent: `venv/bin/python -m quantlab.trading.server`. Open
**http://127.0.0.1:8765**. Use `--port 8766` if needed. No external service or API key.
The launcher binds loopback, bundles all assets and auto-saves ended sessions under
`runs/manual/`. End before closing the server: active sessions are in memory.

## SCREEN / INTERFACE WALKTHROUGH

- **Session setup:** mode, scenario, seed, duration, position limit and optional
  opening long/short for Position management. Each new session is paused.
- **Time bar:** Start/Resume, Pause, one public event, one second, End. Reads do not
  advance the market. End completes ties at the current time and cancels live
  user/automated quotes; it does not advance into the future or liquidate inventory.
- **Account:** position, cash, realised/unrealised/net P&L and remaining FIFO entry.
- **Market:** actual transaction chart, top quotes/spread, P&L or position chart.
- **Book:** aggregated price/quantity/order-count; expand levels for anonymous FIFO.
- **Ticket:** Buy/Sell, Market/Limit, quantity/price; available capacity includes all
  open orders. B/S prepare the side outside input fields and never submit.
- **Orders/executions:** each order's original/filled/remaining/cancelled state,
  cumulative VWAP and every execution/fee. Select an order ID for the breakdown.
- **Risk/markouts:** public reference and fallback, notional exposure, limits,
  drawdown and matured/pending/missing diagnostics with provider/aggressor labels.
- **Review/replay:** full report, all markouts and decisions, journal download and
  read-only verified replay frames. Exported observer data is post-session only.

## ONE COMPLETE MANUAL TRADING SESSION

Normal scenario, seed 42, Free trading, ±20-unit limit, opening cash £10,000.
All the following actions were performed through the browser and independently
reproduced from a saved action sequence. “Complete” means explicitly ended; this
short lesson ends early at 1.980675 seconds, rather than claiming a 60-second run.

| Time from open | Action / actual result | Position | Net P&L |
|---|---|---:|---:|
| 0 | Market buy 6: 2@100.01, 4@100.02 | +6 | −£0.076 |
| 0 | Buy limit 5@99.98 rests behind opening 5 units | +6 | −£0.076 |
| 0 | Cancel that buy: all 5 waiting units removed | +6 | −£0.076 |
| 0 | Sell limit 8@100.02 joins behind 1 earlier ask unit | +6 | −£0.076 |
| 0.089780 s | Next public buy consumes the earlier ask; no own fill | +6 | −£0.046 |
| 0.688953 s | Next public buy fills 2 of the resting sell; 6 remain | +4 | −£0.028 |
| 0.980675 s | Next public buy fills 3 more; 3 remain | +1 | −£0.001 |
| 0.980675 s | Cancel remaining 3 sell units | +1 | −£0.001 |
| 0.980675 s | Market sell 3@99.99: close 1 long, open 2 short | −2 | −£0.064 |
| 1.980675 s | Step one second; public reference falls | −2 | −£0.034 |
| 1.980675 s | Market buy 2@100.01 closes the short | 0 | −£0.066 |
| 1.980675 s | End; reconcile and save | 0 | −£0.066 |

Final cash £9,999.934, gross realised loss £0.05, fees £0.016, net realised loss
£0.066, unrealised zero. Six executions traded 16 units with £1,600.19 turnover.
Maximum drawdown £0.076; maximum long +6 and short −2. Time-average absolute
position 3.685918 units. Limit fill rate 5/13 = 38.4615%: the cancelled five-unit
buy and eight-unit sell both count in submitted limit quantity. Two orders had
cancelled quantity. “Ever partially filled” includes intermediate fills within
an atomic incoming order, even if later matches complete it.

## ORDER-BY-ORDER EXPLANATION

1. **user-1:** market buy six consumes the best asks first. It pays the resting
   prices, not midpoint. Four of its six units execute at the second level.
2. **user-2:** £99.98 is below the best ask, so five units wait. Existing same-price
   orders stay ahead. Cancel removes the waiting quantity without reversing trades.
3. **user-3:** sell eight at £100.02 waits behind the earlier remaining ask. The
   first public buy fills that earlier order. Two later buys fill two and three of
   yours. Five are executed, three wait, then cancellation removes only those three.
4. **user-4:** selling three when long one closes the oldest remaining long unit,
   then establishes a two-unit short at £99.99. Cash increases; net P&L still loses.
5. **user-5:** buying two closes the short at the available £100.01 ask, paying the
   spread relative to the public mark and a new fee. The final account is flat.

The saved review stores bid, ask, reference and position before each manual order,
alongside the execution and subsequent public timeline. It does not grade these
decisions by their later profit or infer Arvind's reasoning from automated tests.

## VWAP EXAMPLE

`(2 × £100.01 + 4 × £100.02) / 6 = £100.016666…`, displayed **£100.01667**.
The exact internal result is 30005/3 ticks. An order's VWAP is different from the
book mid, the account's remaining FIFO entry and its public valuation reference.

## P&L EXPLANATION

Eight total bought units cost £800.12; eight sold units receive £800.07. Gross
loss £0.05 plus fees £0.016 gives net **−£0.066**. At flat, net equals realised.
While positions were open, unrealised valued their remaining FIFO lots at the
public reference. The short gained £0.03 in marked value when the reference fell
£0.015, but buying back incurred the available ask price rather than that mark.
Neither markouts nor spread-capture attribution are added a second time to P&L.

## SCENARIO DEMO

Five configurations change actual parameters or opening depth/positions: Normal,
High volatility (latent sigma 8 rather than 2 ticks/√second), Toxic flow (4 informed
arrivals/second and cleaner signals), Thin liquidity (one unit per opening level,
lower noise flow, no automated maker), Position management (default +8, or chosen
negative opening units). Private values remain hidden; a higher latent volatility
does not force every transaction/reference to move more.

Two additional saved, three-second challenges were run without changing the outcome:

- **Thin:** market buy six executes only three at £100.02 VWAP and cancels three.
  Ends long three with net −£0.093; the target of five was **not met**.
- **Position management:** starts short eight endowed at £100.00, buys eight at
  £100.01875 VWAP and ends flat. Net −£0.158 including fees; the zero-position
  target **was met**. Achieving the objective is distinct from earning a profit.

Both complete their three-second horizons and remain inside the £1 drawdown budget.
These are uncalibrated learning scenarios, not replicas of real markets.

## REPLAY DEMO

Load `docs/learning/phase_06/manual-session.json` in the app. Browser verification
rebuilds the background records and every user action through the engine, checks
all exchange/account evidence and reaches −£0.066 with position zero. Playback
only displays rebuilt public frames; buttons cannot trade into that replay.

The saved manual, thin and position journals also verify programmatically. For
the manual journal, both RNG-free recorded-event replay and regeneration using
seed 42 plus its saved actions reproduce the evidence. Seed regeneration requires
the recorded QuantLab/Python versions. Checksums detect damage, not adversarial
forgery; the engine checks consistency independently of the checksum.

Browser uploads now send the original file text, preserving `10000.0` versus
`10000` and other JSON number representations needed by the checksum. A regression
test exercises this exact HTTP path. Reserialising parsed JSON in JavaScript was
caught during browser verification and fixed rather than weakening verification.

## BEGINNER MODE EXPLANATION

Short definitions explain bid, ask, spread, mid, market/limit, position, P&L, VWAP
and partial fills. An optional observed-book question gives a hint and retry, then
asks for a trade and explains the actual result. It neither interrupts every order
nor reveals future prices. Switching the explanation view changes no engine state.
See the [first-principles lesson](../maths/phase_06_trading.md) for worked mathematics.

## QUANT MODE EXPLANATION

Shows correctly defined top-five depth imbalance, last trade log return,
√sum(squared log returns) over at most 20 returns, recent aggressor buy/sell volume,
flow imbalance and existing exposure/markouts. Counts and missing values are
explicit. Volatility is trade-window, unannualised and not a forecast. Flow does
not reveal informed identities. Exact financial computations remain in Python.

## FILES CHANGED

- New `src/quantlab/trading/`: `session.py` commands/ownership/risk/time/account routing;
  `scenarios.py` reusable configurations; `analytics.py` public metrics/formatting;
  `replay.py` verified actions/journals; `server.py` locked local HTTP/timer/save;
  `static/index.html`, `style.css`, `app.js` interface; package `__init__.py`.
- `portfolio/accounting.py`: optional explicitly valued opening inventory, retaining
  the same FIFO accounting and all zero-opening defaults.
- `market/simulation.py`, `market/replay.py`: publish external real executions to
  background observations; permit a verified early-ended replay horizon.
- `pyproject.toml`, `quantlab/__init__.py`: version 0.6.0, launcher and bundled assets.
  `.gitignore` excludes generated manual sessions.
- `tests/trading_helpers.py`, `unit/test_manual_trading.py`,
  `integration/test_manual_sessions.py`, `integration/test_trading_http.py`:
  113 new collected cases. Existing `integration/test_research_engine.py` keeps
  its version/reproducibility assertion current.
- README, ROADMAP, ASSUMPTIONS, LEARNING_LOG, CHANGELOG; Phase 6 architecture,
  maths lesson, this report and three loadable demo journals.

## RED TEAM

**Checked/fixed:** engine-derived fills; FIFO user priority; exact cumulative VWAP;
passive fills updating accounts; actual cancellation; global conservation and
per-account reconciliation; all outstanding orders reserving capacity; no own
self-trades; public allowlist and anonymised IDs; no future marks/private timestamps;
pause/reads not advancing; unchanged RNG streams from user commands; replay after
partial fills; browser number-preservation on upload; equal-time ending; stale
response revision protection; clean bounded sessions and visible save failure.

**Material limits remain:**

- Synthetic, single-asset market; one local shared session, no authentication between
  tabs. Loopback/Origin/token checks are not a hostile-code sandbox or production
  exchange service. A locally informed user can inspect code/seeds or exported files.
- No latency, borrowing, margin, capital check, interest or forced liquidation.
  Position capacity is conservative and can reject a market order that would have
  partially filled safely. Self-cross prevention is conservative across eligible
  own opposite orders. Background non-maker agents have no capital/inventory limits.
- The external public midpoint/last-trade fallback can be stale or influenced by
  endogenous quote feedback. Phase 5's public-versus-latent divergence limitation
  persists. A public marked gain is not guaranteed executable profit.
- Midpoint markouts are affected by later own/public quote changes and cancellation,
  including end-of-session cancellations. They are descriptive, not a causal proof
  of informed flow, and trade-window diagnostics are not calendar-time statistics.
- Reads return all session trade/history data for simple charts; very large manual
  sessions use more memory. Live setup is limited to 300 seconds/5,000 commands.
  UI import is capped at 20 MB (HTTP envelope 25 MB); larger programmatic journals
  can be verified through Python within the replay evidence limits. This is a
  bounded teaching application, not a high-throughput exchange benchmark.
- Active sessions are in memory until ending. Automatic saving/download protect
  ended sessions, not an unexpected process crash mid-session. Checksums are not
  signatures; consistent forged evidence is not authenticated history.
- Browser testing is on the provided local browser; no claim of exhaustive device,
  assistive-technology, cross-browser or cross-Python coverage. The layout adapts
  to narrower screens and uses semantic controls without relying on colour alone.

## 3-QUESTION ARVIND CHECK

1. Why is the six-unit example's VWAP closer to £100.02 than £100.01?
2. Your five-unit limit has filled two. What does cancelling it remove?
3. You are short two units and the public reference rises £0.03. What happens to
   marked P&L, assuming no trades or fees in that interval?

Answers and Phase 6 review remain pending. Do not begin Phase 7 before Arvind's review.
