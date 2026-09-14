# Phase 13 review report

12 September 2026 · QuantLab core 1.0.0 · environment schema `quantlab-environment-v1`

## BUILD REPORT

Phase 13 is implemented in the existing local application. Open [the review preview](http://127.0.0.1:8770/)
or launch the checkout with `quantlab serve`. Trading offers Synthetic Market, Historical Replay
and Scenario Market, with persistent source badges, manual controls, shared Explain/Tutor and
verified journals. Historical accounting, risk and causal regression reuse approved calculations.
Scenarios use existing stock, paired and option engines. There is no real-order or paid-feed integration.

**No real historical dataset is bundled.** The working local import supports recorded user data;
the demonstrations below use explicitly artificial test bars. This is the user's permitted
fallback, not a claim to have obtained or redistributed real market history.

Phase 14 has not begun. Safe public replay hooks and a factual summary are foundations only;
no annotated guided-replay product or Phase 15 README redesign was added.

## TEST REPORT

**1,732 passed in 101.04 seconds.** Exactly 1,507 original cases remain, plus 222 new environment
cases and three new registry-driven cases. No original case is missing. All 61 pre-existing test
files are byte-identical. Ruff passes; the changed Python modules pass formatting checks.

Coverage includes strict schema/offsets/DST/adjustments, progressive state, next-close orders,
partial limits/market remainder, shared volume, exact ledgers, generated mixed sequences,
corruption failure, causal pair/risk, future mutation, detached what-if, hidden/reveal/replay,
real parameter changes, rejected-request isolation, research metadata and local HTTP boundaries.

Hands-on browser checks covered selection/import fixture/manual execution, actual VWAP Explain,
current-holding risk what-if, public Tutor, option trade/hedge, hidden selection/reveal, read-only browser replay import, portfolio-delta agreement and mobile
layout. At width 390, document width is 390: no page overflow. No browser warnings/errors were
reported in the final historical interaction. Browser observations supplement, rather than inflate,
the automated count. Learner answers were not submitted during browser checks.

Evidence: [full test output](evidence/test-results.txt), [preservation audit](evidence/verification.json).

## CORE SYNTHETIC FINGERPRINT REPORT

The pre/post `tests.core_workflows` outputs are identical across workflow groups A/D, B and C:
shared stock/options/account/risk workflows and causal Stat Arb. Their complete saved-output SHA-256 is:

`85db8c8d9ed780bdaa20a893ac888639f3eeaf131263616e0f5e31740cccf88f`

[Before](evidence/core_workflows_before.json) · [After](evidence/core_workflows_after.json).
The frozen source manifest verifies that every existing financial implementation remains unchanged.
Only five pre-existing files changed: server/navigation adapters and Phase 12 registry/service/panel.
The environment facade also tests the original direct stock workflow against the original engine.

## HOW TO CHOOSE A MARKET ENVIRONMENT

Open Trading and expand **Choose your market environment**. The cards explain what is real,
what is simulated, what the model knows and how execution works.

| Choice | Meaning | First action |
|---|---|---|
| Synthetic Market | Controlled agents, hidden value process, actual simulated FIFO matching | Use synthetic market; retain the approved desk/lab controls |
| Historical Replay | Recorded imported observations plus explicitly assumed paper fills | Import CSV/provenance, select instrument(s), set execution assumptions |
| Scenario Market | A deliberately configured synthetic mechanism | Select a known entry/seed, or choose Hidden scenario |

End a session with actions before switching. Export before shutting down the process. Imports and
active sessions are held in memory; journals need their original data files to reproduce historical runs.

## SYNTHETIC MARKET WALKTHROUGH

Select Synthetic. The opening book is still £99.99 bid / £100.01 ask. Buy six market units:
the first two execute at £100.01, then four at £100.02 under the original FIFO matching.
VWAP is £100.016666… because the four-unit fill receives more weight. The latent value is
neither an executable quote nor copied into the transaction tape. Step time to admit actual
agent orders. Existing options, risk, market making and Stat Arb workflows remain available.

## HISTORICAL REPLAY WALKTHROUGH

Choose Historical → provide a CSV and provenance → select one or two instruments → start.
The first complete bar is revealed. Submit market/limit instructions while paused; they wait.
Step observation reveals the next bar and evaluates eligible orders. Play/Pause/Speed do the
same in sequence; Step time can reveal nothing across a gap. The chart only knows the prefix.
Account, execution tape, risk and pair signals update from that same public information.

Historical options are unavailable: an underlying OHLCV file provides no option chain.
Two exactly aligned series enable the existing causal regression and separate ended research.
The browser shows current closes for both; its price chart shows the first selected instrument.

## HISTORICAL DATA / PROVENANCE WALKTHROUGH

[Schema](HISTORICAL_DATA_SCHEMA.md) documents exact CSV columns, metadata, offsets and adjustment
contracts. Timestamps mean **bar end/availability**, not bar start. Source/licence/transformations
are declared explicitly. Prices are positive finite tick values; volume is whole units; duplicate,
out-of-order and incomplete records fail. No malformed values are silently repaired.

Raw sessions must declare no corporate actions; adjusted sessions must declare every OHLC field
consistently adjusted. These declarations cannot certify a provider's data. Mixed declarations
and impossible OHLC ranges fail, but consistent-looking numeric data could still be mislabelled.

The bundled [five-bar sample](sample/artificial_fixture.csv) and [its metadata](sample/artificial_fixture.metadata.json)
are invented test data. The browser fixture button instead generates 100 paired artificial bars.
Neither is official exchange data. Use your own appropriately licensed recorded export for a real
historical path. Full-file hashes and end dates are absent from live public snapshots.

## HISTORICAL EXECUTION-MODEL EXPLANATION

At t you know the current bar. Your instruction first becomes eligible at a later observed close.
The candidate buy price is close plus adverse ticks; sell is close minus adverse ticks. A market
instruction tries once and cancels any remainder. A limit instruction fills only at a qualifying
candidate close and can otherwise wait. High/low alone never fills it.

Each instrument has a shared `floor(volume × participation)` unit budget for all instructions
and both sides. Floor means round down: 25 × 10% gives two whole units. Submission order assigns
this paper budget; it is not historical queue priority. Default fees are £0.001 per filled unit.
No quoted spread, queue position or reconstructed trade is invented. See [execution contract](HISTORICAL_EXECUTION.md).

## ONE HISTORICAL MANUAL TRADING SESSION

**Artificial five-bar mechanics demonstration; not real market history.** Starting cash £10,000,
one-penny ticks, 10% participation, volume 20 each bar, one-tick adverse slippage.

| Time | Instruction / revealed evidence | Result | Net marked P&L |
|---|---|---|---|
| 09:30 | Close £100.00; submit market buy 3 | Accepted, zero fills now | £0 |
| 09:31 | Close £100.05; budget floor(20 × 0.10) = 2 | Buy 2 at £100.06; remaining 1 cancels; fee £0.002 | −£0.022 |
| 09:31 | Submit sell 1, limit £100.04 | Wait for a later observation | −£0.022 |
| 09:32 | Close £100.02; candidate sell £100.01 | Below limit; no fill despite high £100.20 | −£0.082 |
| 09:33 | Close £100.08; candidate sell £100.07 | Sell 1; fee £0.001; one long unit remains | +£0.027 |
| 09:34 | Final close £100.03 | End with the remaining unit marked, not liquidated | −£0.023 |

Final cash £9,899.947; realised gross £0.01; unrealised −£0.03; fees £0.003.
Therefore £0.01 − £0.03 − £0.003 = **−£0.023**. Exact execution ledgers reconcile; the existing
portfolio presentation uses floating-point values, so raw JSON may show tiny display residuals.
Ending does not promise an exit at the last close. [Full timeline](evidence/demo.json).

## FUTURE-LEAKAGE ADVERSARIAL TEST

At observation 40, mutate every later OHLC value, volume and timestamp in both artificial
series. Re-run the same decisions to observation 40. Entire current public states match:

`a27c995070493850101528630d10be19e88c02d60fb822c5a57eec7dfb8981c8`

The matching hash includes revealed chart data, account/order state, current regression/residual/z,
and past-return risk. The dedicated tests additionally compare Explain, Tutor, order/action digests
and isolated hypotheses at four cutoffs, one/two instruments and three mutation variants.
Full dataset identities differ, as they should. Public equality is conditional on identical metadata,
valid files, history and decisions through t; it does not claim to hide a CSV from its owner.

## HISTORICAL EXPLAINABILITY DEMO

Explain current price reports the recorded closes and their change. With recorded data it says:
“The replay records the movement but does not establish why the real market moved.”
With a fixture it explicitly says the observations are artificial. It does not invent latent value.

Explain VWAP selects a real paper order and its recorded fills. In the five-bar demonstration,
the sell's executed VWAP is **£100.07**, labelled SIMULATED HISTORICAL EXECUTION.
VaR is labelled MODEL CALCULATION and uses revealed returns only. Unknown historical depth,
quotes, option Greeks or unimplemented risk measures stay unavailable. A position-risk what-if
revalues detached current holdings; it neither predicts an unseen fill nor changes the account.

## HISTORICAL TUTOR DEMO

The public question asks whether a recorded price path alone establishes why the market moved.
It does not: a price is evidence of movement, not a proof of the cause. The fixture question
explicitly says it is artificial. “Quiz me on this” for an executed historical VWAP uses those
actual paper fill prices/quantities and the existing numerical validator. No answer is exposed
in the question DTO; changed-context answers are rejected. Reading awards no mastery.

## SCENARIO MARKET WALKTHROUGH

The [12-entry library](SCENARIOS.md) spans baseline/high-volatility/thin/informed stock markets,
opening-position reduction, residual trend/mean reversion/shocks, liquidity/correlation/relationship
breakdowns and option quote-volatility shock. Each changes genuine existing engine inputs.
The same wrapper supplies controls, source labels, public projections and reproducible journals.
Paired manual trading retains the causal warmup: 32 observations with default 20/12 windows.
A short paired demonstration can show a mechanism before trading is available; default duration 60 allows both.

## KNOWN SCENARIO DEMO

Normal, seed 42, 20 seconds: buy one market unit, immediately sell it, then finish. The original
engine charges spreads and fees. Net P&L is **−£0.022**, maximum drawdown **£0.022**. This is
a real simulated round trip, not a preset loss. The same fixed policy is separately evaluated
across regimes below. All 12 scenario kinds are tested for real inputs and deterministic replay.

## HIDDEN SCENARIO DEMO

The deterministic test demonstration privately uses the liquidity-shock configuration, seed 42,
40 observations. The live public name remains **Scenario Session**. Initially, each venue's
best-level external depth is 40. At observation 20, it is two. The user can observe lower displayed
quantity but is not told the hidden scenario, seed or future shock schedule. In the browser,
hidden selection uses a fresh server-owned random seed/key rather than this fixed demo selection.

## POST-SESSION HIDDEN-TRUTH REVEAL

After observation 40/end and an explicit reveal, the configuration identifies the liquidity-shock
scenario and the midpoint call to the original venue liquidity control. Compare that mechanism
with the displayed depth change. It explains the controlled experiment, not a real-market cause.
A verified hidden replay starts with hidden public frames; reveal requires its ended frame.
The complete scenario parameters and version are retained in its ended journal and verified.

## SCENARIO CHALLENGE DEMO

The known normal-market round trip **loses £0.022 and succeeds** at finishing within £1 maximum
drawdown. Profitability and objective success are separate. The tests also exercise a positive
terminal P&L with an earlier breached drawdown, which fails the objective. Option delta-band
checks include the moment an option trade is executed, even if a hedge immediately follows.
The liquidity acknowledgement objective is explicitly self-reported, not automatic proof of skill.

## SCENARIO COMPARISON RESEARCH DEMO

Same fixed maker configuration, three independently seeded ten-second runs per regime; nine
runs total. Registered through the existing Phase 5 engine. Different exogenous configurations
use separate derived streams and **unpaired** comparisons. Nothing is pooled with historical data.

| Scenario | Mean P&L £ | Mean max drawdown £ | Mean absolute inventory units | Mean 5-event markout £/unit | Mean buy fills | Mean sell fills |
|---|---:|---:|---:|---:|---:|---:|
| normal | 0.0997 | 0.3143 | 2.8971 | 0.0158 | 4.0000 | 5.6667 |
| high_volatility | -0.0103 | 0.2660 | 2.0669 | 0.0029 | 4.6667 | 5.3333 |
| toxic_flow | 0.3733 | 0.3640 | 1.7479 | 0.0167 | 7.3333 | 9.3333 |

The toxic sample happens to have the highest mean here. **Three short runs cannot rank robustness**;
all three Student-t mean intervals include zero. These are deliberately small demonstrative data,
not evidence that informed flow helps a maker or that any policy has real-market alpha.
Markouts, missing coverage and complete distributions are retained, not forced to tell a story.
[Registration](evidence/scenarios_research/registration.json) · [all outcomes](evidence/scenarios_research/runs.jsonl)
· [full experiment](evidence/scenarios_research/experiment.json).

A separate [historical-style pair study](evidence/historical_research/experiment.json) compares
entry z thresholds 2.0/2.5 with training end 30 and evaluation end 80. Fixed, rolling and walk-forward
modes are tested. One artificial recorded-style path per threshold is not independent Monte Carlo data.
Its evidence is labelled HISTORICAL with dataset fingerprints and its fixture provenance; it is
an ended research result and never fed backwards into live decisions.

## REPLAY / DATASET-FINGERPRINT DEMO

Original five-bar dataset identity:

`e3cfecbde6eab755be5b0a55ef4462b446f2edf08040050f20cbb756e2a42632`

Every historical action and final public state reproduces. Changing a price in the original CSV
causes explicit fingerprint rejection. Source/provenance/range edits also fail. Hidden scenario
replay similarly verifies seed/configuration, execution schema, version and each public state.
[Historical journal](evidence/historical_journal.json) · [hidden journal](evidence/hidden_journal.json).

A fingerprint is a content identity check, not proof that a dataset is authentic or a model is
correct. A seed chooses a repeatable sequence of random draws; repeating it supplies no additional
independent market evidence. A fresh account at the start cannot erase what the person remembers.

## PERFORMANCE REPORT

Measured on this local Python 3.14/macOS environment, single uninstrumented sample; timings are
indicative, not portable latency guarantees. Financial/RNG behavior was not changed to optimise them.

| Operation | Time |
|---|---:|
| Validate/load 5,000 bars | 119.208 ms |
| 100 progressive one-observation steps | 107.021 ms total |
| Average progressive step, including public fingerprint | 1.070 ms |
| Verify historical replay, 102 captured frames | 278.822 ms |
| 20 public snapshot projections | 34.475 ms |
| 40 environment switches | 18.812 ms |

At observation 100 of the 5,000-bar source, the public JSON is **25,490 bytes**;
the full dataset is not sent. Charts retain at most 300 revealed bars. The mobile click-to-updated-chart
check took 261 ms including browser-control round trip, not an isolated JavaScript render benchmark.
Its visible range changed only from the newly revealed £99.63 close; page width stayed 390 px.
The desktop and mobile controls were inspected. No optimisation was necessary after measurement.

## FILES CHANGED

Pre-existing changes are confined to:

- `src/quantlab/trading/server.py`: environment API/routes, dispatch, clock and account separation.
- `src/quantlab/trading/navigation.py`: shared selector assets.
- `src/quantlab/explainability/service.py`: environment-aware Explain/quiz/what-if/replay dispatch.
- `src/quantlab/explainability/registry.py`: three environment concepts.
- `src/quantlab/trading/static/explain.js`: source labels, shared panel events and supported what-if controls.

New `src/quantlab/environments/`: protocol/facade, strict loader, historical execution, scenarios,
coordinator, public explanations, Tutor, research adapters and artificial fixtures. New frontend:
`markets.html`, `markets.js`, `markets.css`. New tests are entirely in `tests/markets/`.
`scripts/phase13_evidence.py` produces the deterministic example, replay and performance evidence.
Seven requested market guides, this report, sample and verification/research records are in
`docs/markets/`. README, ROADMAP, ASSUMPTIONS, LEARNING_LOG and CHANGELOG were updated.
Financial kernels, existing tests, approved pricing/matching/accounting/risk/stat-arb formulas,
old desk scripts and release version were not changed.

## RED TEAM

Fixed during this build: future-sensitive file hashes in live projections; correct source dispatch;
unsupported historical measures returning unavailable; rejection without an unjournalled state change;
scenario comparison falsely claiming paired identical paths; single-path research borrowing a
multi-run Tutor summary; hidden opening labels; quote/ledger display gaps; same-bar peak exposure;
replay metadata forgery; aggregate portfolio-delta selector agreement; and mobile grid overflow. Tests lock down the financial/information cases.

Remaining limitations:

- Bars cannot prove queue fills, attainable closes, price impact or actual historical execution.
  The volume budget and fixed slippage are assumptions. Quotes/trades/depth adapters are future work.
- No real historical dataset is included. User provenance, adjustment claims, bar availability and
  volume units need care. Corporate-action and multi-currency processing are deliberately absent.
- Historical shorting has no borrow/financing/margin realism. Marks are not liquidation prices.
  Gaps mix return intervals; tiny tail samples produce fragile risk estimates.
- Paired historical research uses fixed units; legs can fill unevenly. There is no claim of
  beta neutrality, convergence, robust stationarity inference or future alpha.
- Hidden mode protects application inputs, not a local owner reading files/memory. A public engine
  with only one scenario candidate can narrow inference. Prior knowledge survives restart/reveal.
- Scenario shocks are stylised and not calibrated forecasts. Holding zero inventory can pass a
  drawdown objective. A liquidity acknowledgement alone does not establish understanding.
- Scenario comparison is limited to three stock presets; other presets remain manual/replay labs.
  Three demonstration runs are too few for robustness claims. Historical evidence is one path.
- Imports and active sessions are in memory; export before shutdown and retain source files.
  These adapters are local teaching software, not broker accounting or exchange certification.

## 3-QUESTION ARVIND CHECK

1. A bar's high exceeds your sell limit, but its close minus slippage is below it. Does your order fill under this replay rule, and why?
2. A hidden session's displayed depth drops sharply. What can you conclude from that observation, and what remains uncertain?
3. Your replay matches exactly and a strategy earns money on one imported path. What has been verified, and what has not been established?

No answers or mastery have been inferred. Phase 14 awaits a separate review and instruction.
