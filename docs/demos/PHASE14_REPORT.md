# QuantLab Phase 14 · review report

13 September 2026

## BUILD REPORT

Phase 14 is implemented and ready for Arvind's review. It adds 58 guided topics, eight flagships,
four depths, prediction checkpoints, saved-session teaching, annotated replay, explicit hindsight,
process/outcome reflections, concept journeys, recording presentation, named captures and Markdown
outlines. **Phase 15 has not begun.** No major financial model or approved financial calculation changed.

Demos use bounded, genuine engine runs held separately from personal sessions. Playback pauses
before revealing an execution event; the prepared run remains on the server. It is a guided replay,
not a live order ticket. Selecting a different hedge branch runs genuine core instructions.

## TEST REPORT

**1,910 passed; 0 failures.** All **1,732 prior test IDs** remain, with
**178 additional tests**. No existing test source changed. Final suite: **86.62 seconds**.
Ruff passed across `src`, `tests` and `scripts`.

Coverage includes every catalogue entry; deterministic resets; exact fills/accounting; real hedge
branches; information-boundary canaries; signal/markout evidence; historical source labels;
showcase/replay mastery isolation; hints/retries; prior-practice restart protection; verified journal
imports; Options command/frame alignment; corruption rejection; positive/negative moment selection;
10,000-transition selection; genuine long-journal replay; local HTTP controls; responsive styling.

[Complete test output](evidence/test-results.txt) · [ID/source audit](evidence/verification.json).
Browser QA used a separate temporary learning profile, not Arvind's personal mastery record.

## CORE FINGERPRINT REPORT

The approved financial source files are byte-identical. The only pre-existing source edits are
`trading/server.py`, `trading/navigation.py`, and `trading/static/explain.js`.

| Approved Phase 13 replay | Before and after SHA-256 | Result |
|---|---|---|
| Historical | `7e9cff366b6953b31f7adf460935202ac78f5320bd3a4e1845d18d303f9b6e3a` | Identical |
| Hidden | `6f7e28be55bf98713a62bf1c053fa8c8526427bd3cf2e17f826959c5c459e47c` | Identical |

The representative core workflow report is identical before/after. Its combined digest is
`fa0e7d6462d735408917806704a47204eb1ca8b1ef84285f3e9ca49680b58882`.

[Frozen pre-Phase-14 manifest](evidence/phase13_manifest.json) ·
[Core before](evidence/core_before.json) · [Core after](evidence/core_after.json) ·
[Phase 13 comparisons](evidence/phase13_fingerprints.json).
Fingerprints establish reproducibility, not real-world model validity.

## HOW TO OPEN DEMOS

The isolated review server is running at **[Open Demos](http://127.0.0.1:8771/demos)**.
The approved Phase 13 server on 8770 was left alone.

On another run, launch QuantLab normally and choose **Demos** in navigation, or append `/demos`
to that server's address. No broker, API key, plugin or recording program is required.

## DEMO CATALOGUE WALKTHROUGH

1. Filter a domain or search a concept such as “delta” or “historical”.
2. Pick Quick for a concise demonstration, Learn for eligible questions, Quant for maths and
   assumptions, or Interview for project-defence prompts.
3. Read the public before state and instruction. Predict, use a hint, retry, or reveal the result.
4. Follow the engine evidence, Explain, concept journey, professional use and limitations.
5. Finish with a recap; restart if you want to inspect another branch.

| Domain | Topics |
|---|---:|
| Trading | 6 |
| Market Making | 6 |
| Research | 6 |
| Options | 11 |
| Risk | 10 |
| Stat Arb | 10 |
| Markets | 4 |
| Engineering | 5 |

The smaller topics reuse relevant genuine episodes with their own central-concept focus; they
are not 58 separate financial models. Suggested durations are 3–6 minutes, depending on reading pace.

## FLAGSHIP ORDER-EXECUTION DEMO

At the first screen you see asks of 3 at £100.01, 4 at £100.02 and 8 at £100.04. Predict what a
BUY 10 MARKET instruction does. The actual engine records **3, 4 and 3 units** at those prices.
Cheaper sell offers execute before more expensive ones; the last price level retains 5 units.

VWAP is the average you actually paid, weighting each fill by units:
`(3×100.01 + 4×100.02 + 3×100.04) / 10 = £100.023`.
Actual fees are **£0.01**, cash becomes **£8,999.76**, and position is **+10**. At the new public
mark £100.015, marked P&L is **−£0.09**; that mark is not a promised liquidation price.

Order size → available depth → multiple fills → VWAP → execution cost. This connects to
institutional execution and transaction-cost analysis. [Actual outline](scripts/order.md).

## FLAGSHIP ADVERSE-SELECTION DEMO

A seller rests 3 units at **£100.05**. Before the fill, only the public book, own order and
inventory are visible. A fill alone does not establish whether the counterparty was informed.
The first real provider fill occurs at **0.014236 simulated seconds**.

After finishing and explicitly entering hindsight, the first signal audit shows latent value
**£100.20**, noisy signal **£100.19717**, estimate **£100.18851**, estimated buy edge
**13.85114 ticks**, and hurdle **1.47014 ticks**. The informed rule actually buys because the
estimated edge clears costs, minimum edge and uncertainty allowance. It does not receive perfect
latent truth or future values.

Five subsequent engine events later, latent reference is **£100.20610**: the seller's latent
markout is **−£0.15610 per unit**. The same trade's public-midpoint markout is **£0.00** at that
horizon. Both are shown honestly. Negative markout can also arise without informed trading;
this controlled model provides additional observer evidence, not a general diagnostic proof.
[Actual outline](scripts/picked-off.md).

## FLAGSHIP DELTA-HEDGE DEMO

1. Buy a genuine at-the-money call contract, multiplier 100. Aggregate option delta is **51.14358**.
2. Predict the signed stock hedge. The full branch sells **51 stock units** through the FIFO book,
   leaving delta **0.14358**. Partial sells **26**; no-hedge sells **0**.
3. Advance the seeded market one model day. Stock becomes **£99.73** and full-branch delta
   becomes **−1.78995**. Gamma describes sensitivity of delta to spot; time and IV inputs also matter.
4. Re-hedge by buying **2 stock units**, leaving delta **0.21005**.
5. Raise the IV input to **30%**. Delta changes to **1.41004** and vega remains positive.

Delta is a local sensitivity, not a guarantee about tomorrow. A near-neutral stock hedge does
not remove volatility exposure, costs or model risk. Every branch has genuine fills and a
replayable native Options journal. [Actual outline](scripts/delta-hedge.md).

## FLAGSHIP VaR-VS-ES DEMO

The two controlled samples have equal **95% VaR = 10**, but **ES = 12 versus 48**.
Before revealing the tails, predict whether equal VaR implies similar tail severity. The charts
mark the VaR threshold and show the worst observations that determine ES.

VaR asks where the bad tail begins under the selected convention. ES asks how severe losses
are on average within that tail. Neither is a maximum possible loss. The existing empirical
calculation uses the exact worst 5% mass; only five effective tail observations are available.
These are deliberate teaching distributions, not evidence that a live portfolio is safe.
[Actual outline](scripts/tails.md).

## FLAGSHIP CORRELATION-VS-COINTEGRATION DEMO

The two existing completed teaching samples have price correlations **0.980805** and **0.982840**.
They look similarly correlated, but the known synthetic residual processes differ. Inspect actual
prices, training regression, residuals and causal z-scores. The fit uses the first 160 rows;
later z-scores use only prior residual windows.

Correlation measures co-movement. A stable residual relationship is a different property; high
price correlation alone does not establish it. The following existing decoupling scenario
breaks a previously stable relationship and shows why historical fit is not a permanent law.
No empirical cointegration-test claim is invented. [Actual outline](scripts/pairs.md).

## FLAGSHIP WINNER’S-CURSE DEMO

All **50** variants have known true expected payoff **zero**. The existing Phase 5 experiment
selects the highest development mean from 40 runs per variant and writes its selection lock
before untouched evaluation is executed. Root **140042** was fixed in advance.

The winner is **variant-32**. Its development mean is **0.277506**; the 400-run untouched evaluation
mean is **0.047892**. Observed deterioration is **0.229614**. The evaluation remains slightly
positive; it was not replaced with a forced loss for a more dramatic story.

Selecting the maximum of noisy estimates favours luck. Publishing only the winner conceals the
search that produced it. These are Gaussian statistical-control payoffs, **not trade P&L** or
50 genuine production strategies. [Actual outline](scripts/winner.md).

## FLAGSHIP SYNTHETIC-PRICE-FORMATION DEMO

Follow public orders and executions first. The ordinary view shows bid, ask, last transaction,
book and tape; it does not expose the hidden model value or private signals.

After completion, explicit observer review separates **latent value → agent information →
orders → book → matching → transaction price**. Its actual event table compares latent value,
best bid, best ask and last transaction. A latent-process update is not itself a trade. Noise
agents use public information; informed decisions use a noisy measurement. The resting order
sets each execution price through matching.

The short walkthrough samples six public checkpoints, with full public timelines retained at
those points. Intervening events are not claimed to be absent. [Actual outline](scripts/synthetic-prices.md).

## FLAGSHIP HISTORICAL-EVIDENCE DEMO

The source is a clearly labelled **artificial historical-style fixture**. At the opening £100
observation, submit a paper BUY 3. No immediate fill is fabricated. At the next revealed bar,
fixture close is **£99.63** and the documented adverse-tick rule fills at **£99.64**, charging
**£0.003** fees. Paper position is +3.

Recorded observation, user instruction, simulated execution and simulated P&L are separate kinds
of evidence. OHLCV does not contain queue priority or depth. This cannot establish that you
would actually have filled on a historical exchange, nor why a real price moved.
[Actual outline](scripts/historical.md).

## TEACH-ME-THIS-SESSION WALKTHROUGH

From a completed compatible lab, use **Teach Me This Session**, or load its original saved JSON
in Demos. Native Trading, Options, Risk, Stat Arb and Phase 13 environment journals are supported.
Historical sources still require exact original CSV/metadata fingerprints. Version or evidence
mismatches fail before replacing the current presentation.

The browser successfully loaded the exported order journal without its original live session.
It began at the original public book with no fills and asked what the chosen BUY would do to
position. The result appeared only after reveal. Replay practice did not earn mastery.
[Replay contract](ANNOTATED_REPLAY.md).

## ANNOTATED REPLAY DEMO

The selected order moment is **public point 0 → BUY 10 MARKET → verified next command boundary**.
Before reveal: no next-fill tags, selected outcome concepts, final summary or private configuration.
After reveal: actual three fills, updated book/account and the relevant central explanation.
A later ending action is a separate moment.

Longer sessions rank a bounded number of useful executions, partial fills, cancellations, inventory
or P&L moves, hedge/leg events, markouts and risk warnings. The teacher prioritises varied topics
and includes both gains and losses. It does not narrate every event or claim to provide a full audit.

## DECISION-VS-OUTCOME DEMO

After a revealed event, choose one of the four process/outcome quadrants and write your reason.
The selector starts with **Choose your own assessment**, not an automatically favourable label.
The saved result is marked **YOUR REFLECTION — not an automatic process grade**.

QuantLab says process quality is unknown without adequate decision-rule or objective evidence.
The order demo's −£0.09 marked outcome is neither proof of bad process nor an invitation to call
it a good trade. Profit alone would not establish sound process either.

## CONCEPT-JOURNEY DEMO

The order journey links Market order → Market depth → VWAP → Execution cost. The option journey
links Option price → Delta → Gamma → Delta hedge → Vega. Click a concept to open Phase 12
at the selected demo point. Registry graph edges retain their original dependency descriptions;
lesson order is not presented as proof of real-world causation.

## RECORDING-MODE WALKTHROUGH

Toggle Recording mode, optionally Larger text, and use the remaining clear checkpoint controls.
Unrelated navigation disappears, but source badges, artificial-data labels, limitations and
production differences remain. This was checked at **390 × 844** without document overflow.
The viewport was restored afterwards. No video, GIF, external screen recorder or final marketing
asset was created. [Recording guide](RECORDING_MODE.md).

## DEMO-SCRIPT EXPORT EXAMPLE

Complete a flagship or explicitly enter showcase capture, then choose **Export Markdown script**.
The [order script](scripts/order.md) contains setup, instruction, actual fills/accounts, central
explanation, maths, professional use, capture names, limitations and result digest. Each of the
eight flagships has an equivalent outline. Browser export uses the same Python exporter; it is
withheld before recap/showcase so the script cannot leak future answers into an active prediction.

## CAPTURE-STATE DEMO

Choose `order-before-submit` and then `order-after-multifill` from named captures. The first is
the original book; the second contains the exact 3/4/3 fills and £100.023 VWAP. The hedge equivalents
are `delta-before-hedge` and `delta-after-hedge`; the selection equivalents are `winner-before-test`
and `winner-after-test`. Entering capture mode explicitly disables learning credit and records
known question exposure. It does not grant observer/hindsight permission.

## TUTOR INTEGRATION

The Phase 7 Question validators and Progress.grade are reused. Learn alone can submit eligible
conceptual evidence. Hints, attempts, retry, reveal and disabled-tutor behavior are respected.
Quick/Quant/Interview, showcase and saved replay remain practice.

Demo viewed/completed/checkpoint-attempt counts live separately from mastery. Prior answer practice
and explicit result exposure survive restart, preventing a showcase answer from later becoming
fresh first-attempt credit. The normal live tutor's active question and market RNG are untouched.

## EXPLAIN INTEGRATION

The demo checkpoint, result, equation and journey open the existing Phase 12 panel in an explicit
demo context. It uses the selected public point and permitted predecessor, not the personal live
account or later frames. The browser check returned the actual **£100.023** VWAP and **3/4/3** fills.
Portfolio option delta uses the aggregate selector, including its multiplier and stock hedge.
Central definitions, maths, assumptions and professional-use text are reused rather than copied.

## PERFORMANCE REPORT

Measured on this local machine; these are observations, not service-level promises.

| Operation | Measured time |
|---|---:|
| First build of winner's control | 406.1 ms |
| Cached winner restart | 0.17 ms |
| Mean before-view construction, 20 reads | 0.17 ms |
| Verify and teach genuine 252-action journal, 469,908 bytes | 73.2 ms |
| Select six moments from 10,000 transitions | 44.5 ms |

Other flagship builds in this run were under 100 ms. Research is cached; normal playback does not
rerun it. Journal verification still has the original action/version/64 MB frame constraints and
an added 25 MB import ceiling. Selection is bounded; it does not remove those source limits.

The browser-control file-picker call had a long automation delay despite a short requested timeout.
It ultimately loaded successfully; that tool delay is not reported as application replay latency.
[Reproducible timing evidence](evidence/demo-report.json).

## FILES CHANGED

Existing source edits are limited to:

- `src/quantlab/trading/server.py`: lazy demo hub, local demo endpoints and new assets.
- `src/quantlab/trading/navigation.py`: Demos link and new assets; Demos owns its source labels.
- `src/quantlab/trading/static/explain.js`: explicit selected-demo context for the existing panel.

New files include `src/quantlab/demos/` (small builders, public projections, replay/teaching,
progress, predictions, export and observer presentation), `trading/static/demos.html/.css/.js`,
four test files in `tests/demos/`, and `scripts/phase14_evidence.py`.

Documentation adds the six requested guides, this report, eight outlines and frozen/generated
evidence. README, ROADMAP, ASSUMPTIONS, LEARNING_LOG and CHANGELOG now record Phase 14.
The final recruiter README overhaul and Phase 15 release/media work remain out of scope.

## RED TEAM

Issues actively tested and corrected:

- **Outcome leakage:** before responses ignore modified future/private payloads; saved replay also
  withholds outcome-derived tags and concepts.
- **Wrong action attribution:** Options intermediate frames are filtered to verified command boundaries;
  frame/action counts must reconcile.
- **Fake mastery:** watching, replay and showcase cannot grade concepts; prior answer practice cannot
  become first-attempt credit after restart. Hint/retry grading remains with the existing tutor.
- **Source confusion:** historical fixture views retain explicit simulated-execution badges, including
  recording mode. The separate personal-environment banner is not mounted over Demos.
- **Account interference:** real demo execution uses detached sessions; HTTP and RNG-isolation tests
  preserve personal engine state. The Explain panel cannot fall back to that account in demo context.
- **Profit-based praise:** process stays unknown; quadrant classification requires the user's reason.
- **Cherry-picked outcomes:** fixed seeds, all 50 development means, actual still-positive evaluation,
  unchanged engines and genuine adverse-selection references are retained.

Remaining limitations:

- Built-in runs are prepared server-side; the guarantee is controlled disclosure, not an absence of
  future data from local memory. Anyone controlling the local source can inspect it.
- Heuristic moment ranking can miss the user's intent. It is a teaching sample, not an audit or a
  defensible automatic process/risk score. Known replay outcomes remain ungraded practice.
- Gaussian controls are deliberately simpler than trading research. Synthetic known-process examples
  do not validate real-market cointegration, causation, execution quality or alpha.
- The adverse example is clearly adverse against latent reference; its public-midpoint markout is
  not equally negative. This distinction is preserved rather than edited into a cleaner story.
- Historical imports depend on user-supplied provenance and exact source retention. No real data is
  bundled, no OHLC queue truth is inferred, and no actual historical fill is promised.
- One local server owns one demo presentation state. Large journals can hit original visual replay
  limits. Exported paths are audits, not a new general-purpose replacement journal format.
- No production venue latency/operational infrastructure, external recording or final marketing assets
  are supplied by this phase.

## 3-QUESTION ARVIND CHECK

1. You buy 10 units across several ask levels. Why can the last traded price differ from your VWAP?
2. A seller's latent-reference markout is negative while its public-midpoint markout is zero.
   Can both calculations be correct, and what would explain the difference?
3. A development winner makes money on untouched evaluation. Why does that fact alone still fail
   to establish a sound research process or a real trading advantage?

No answer has been inferred or graded. **Phase 14 awaits your review; Phase 15 has not begun.**
