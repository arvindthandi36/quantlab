# Phase 7 review — adaptive Quant Tutor

> Historical phase record. Current core conventions and release status are in the root README, ASSUMPTIONS and Phase 11 release report. Test counts and runtime labels below describe this phase.


11 September 2026 · QuantLab 0.7.0 · Phase 7 implemented, awaiting Arvind's review.
**Phase 8 has not started.** The overall roadmap is unchanged.

The demonstration answers in this report belong to a separate demonstration
learner. They are not Arvind's answers and do not populate his personal progress.

## BUILD REPORT

The local tutor now connects actual Phase 6 orders, fills, account observations
and matured public markouts to structured teaching. The same teaching engine
accepts public Phase 4 market-maker observations and verified Phase 5 experiments.
Matching, account calculations and research statistics remain authoritative.

Implemented:

- An optional trading-desk panel with prediction, answer, staged hints, Explain,
  Go deeper, Why does this matter?, Quiz me, collapse and disable controls.
- A separate learning dashboard, interview and project-defence modes, local
  answer history, misconception evidence, spaced review, JSON/Markdown export
  and an explicit learning-only reset.
- Eleven learning domains and 72 concepts: 52 supported through Phase 6, with
  20 later concepts prepared and unassessed. No artificial options/calculus quiz.
- Four teaching layers and four difficulty labels. Real arithmetic uses actual
  event quantities. Qualitative topics progress to reasoning where arithmetic
  would be artificial. No trading function is gated by learning scores.
- Public post-session reviews, with separately requested ended-session observer
  forensics. The tutor never consumes hidden observer records.
- Frozen question contexts, strict local validators, configurable question
  spacing, persistence validation and a separate learning-error state.

There is no external language-model dependency, key or data transmission. A
protocol leaves room for a future optional language layer; it has no network
implementation. See the [teaching-system contract](../architecture/phase_07.md)
for the exact lifecycle, scoring, boundaries and limitations.

## TEST REPORT

**747 passed: all 599 original tests plus 148 new tests. No failures or skips.**
The [full test output](phase_07/test-report.txt) records the final run.

The original matching, conservation, queue, accounting, market, research, manual
trading and replay tests remain in the suite. New tests cover answer evidence,
hint/reveal behaviour, repetition, misconceptions, scheduling, prerequisites,
difficulty, every supported concept, numeric tolerances and invalid inputs,
real event triggers, persistence/reset/export, disabled tutoring, both interview
modes, information boundaries, replay rewinds and market independence.

Integration tests use actual Phase 6 sessions, actual Phase 4 observations and
complete Phase 5 experiments. Both adverse-buying and adverse-selling examples
use real resting orders and subsequent public prices; conservation still passes.

Additional checks passed: Ruff lint, formatting across 150 Python files,
syntax checks for both browser scripts, and installed-package dependency checks.
The editable package is version 0.7.0. HTTP tests require temporary loopback
listeners; the restricted execution environment initially denied those listeners,
then the full suite passed with local-server permission. No test was removed or
weakened to bypass that restriction.

Browser verification exercised a real six-unit trade, wrong answer, hint,
correction, actual-fill explanation, saved history, interview calculation,
project-defence debrief, learning map, recorded research and ended-session review.
The reviewed browser reported no console errors. This was desktop verification;
it does not claim a full mobile/accessibility audit.

## HOW TO USE THE TUTOR

Start the local app from the project folder:

```bash
venv/bin/python -m quantlab.trading.server --port 8766 --learning-path runs/learning/progress.json
```

Open [the trading desk](http://127.0.0.1:8766/) and its
[learning dashboard](http://127.0.0.1:8766/learning). Port 8766 keeps the previously
running Phase 6 session on 8765 available. The server must remain running.

1. The desk opens paused. Submit a manual order with the existing controls.
2. Expand Quant Tutor. A relevant real event creates a question, subject to the
   configured event gap and the question already on screen.
3. Answer before requesting Explain. An error gives a conceptual hint; another
   gives a stronger hint; the default third error reveals the worked explanation.
4. Read the four layers: intuition, maths, the identified QuantLab event, interview.
   Go deeper is voluntary and awards no credit simply for reading.
5. Open Learning dashboard to inspect evidence, revisit a concept, study saved
   experiments, or select Interview / Project defence and Quiz me.
6. End a session and choose Review this session. Observer-only information has a
   separate explicit reveal control and is unavailable during live trading.

The optional Predict action asks about the currently observed book. Make your
own trading decision afterwards; the result comes from the actual engine. If
the market moves between observation and submission, a prediction is not a
promise about the changed book. Pause is available for unhurried practice.

Default automatic spacing is eight public exchange actions. Change it, the hint
attempt limit, or the enabled setting from the learning view. Collapse affects
visibility; disable stops tutoring. Neither blocks trading. Questions left
unanswered are not repeatedly replaced as market events arrive.

Progress survives app restarts in `runs/learning/progress.json`. Export buttons
produce JSON and readable revision notes. Reset requires the exact phrase
`RESET LEARNING` and affects learning only. Use one server writer per profile.

The Phase 4 terminal integration is optional:

```bash
venv/bin/python -m quantlab.maker_demo --manual --adaptive
```

It uses `runs/learning/maker-progress.json` to avoid two writers sharing the browser
profile. A managed programmatic caller can share one Tutor instance. The browser
research selector opens the saved development, evaluation and sensitivity studies;
new complete studies can be supplied through the local research adapter.

## ONE LIVE-TRADING TEACHING DEMO

Reproduce the isolated demonstration with:

```bash
venv/bin/python -m quantlab.tutor_demo --output runs/learning/demo
```

The saved evidence is [demo.json](phase_07/demo.json), with a
[short transcript](phase_07/demo.txt) and [revision export](phase_07/revision.md).
Its market seed is 42. Its separate learning calendar begins at noon UTC on
11 September 2026; calendar changes never advance the market.

| Step | What actually happens | What the tutor does |
|---|---|---|
| Observe | Public bid £99.99, ask £100.01; position zero | Uses public quotes only |
| Decide | Submit a six-unit market buy while paused | Does not submit or modify the order |
| Result | Two units fill at £100.01, four at £100.02 | Identifies a multi-level execution |
| Test | Demo learner selects the displayed midpoint | Records one error and gives a quantity hint |
| Explain | Demo learner then selects quantity weighting | Shows the actual fills in a worked formula |
| Persist | Recreate Tutor from its progress file | Restores both VWAP attempts |
| Revisit | Move only the demo learning calendar forward three days | Offers the old, labelled trade for review |
| Interview | Assess liquidity, then request VWAP interview | Uses the same fills for a Level 2 calculation |

The hint is: “Treat each executed unit as one observation; price levels can
contain unequal quantities.” It does not immediately supply the answer.

The worked answer is:

`VWAP = Σ(pᵢ × qᵢ) / Σqᵢ = (100.01 × 2 + 100.02 × 4) / 6 = £100.01667`.

Here `pᵢ` is each execution price, `qᵢ` its quantity, and `Σ` means add the terms.
Four units receive twice the weight of two units. VWAP measures execution price;
fees are separate. The midpoint does not promise a price at which six units can
trade. The first two units use the best ask; later units consume the next level.

## ONE POST-SESSION REVIEW DEMO

After advancing this actual session one simulated second and ending it:

| Recorded result | Value |
|---|---:|
| Executions | 2, filling 6 units |
| Fees | £0.006 |
| Final marked net P&L | +£0.044 |
| Maximum marked drawdown | £0.076 |

The position remains long six; ending cancels orders but does not invent a
liquidation. The account marks that inventory using its public reference.

**What was known then:** immediately before submission, bid £99.99, ask £100.01,
position zero and reference £100.00. The fill VWAP is not put into this section.

**What happened afterwards:** the post-order public reference is £100.005. At
0.089780 seconds it is £100.010, then at 0.688953 seconds £100.025. The marked
position benefits from that later rise. These are observed outcomes, not advice
that the trader should have known the future.

**What the learner did well:** the review cites the specific first-answer liquidity
and later numeric VWAP responses. **What to improve:** it cites the two recorded
midpoint answers and the architecture answer. It does not infer the trader's
motivation or praise a profitable position.

The three session questions concern VWAP, slippage and available liquidity. The
interview question asks which contemporaneous evidence could justify a decision.
The review explicitly presents all four possibilities:

- Good decision, good outcome.
- Good decision, bad outcome.
- Bad decision, good outcome.
- Bad decision, bad outcome.

P&L alone cannot identify the applicable decision-quality category. Observer-only
forensics can be requested separately after the end; it is absent from the
learning demo export and never becomes live teaching input.

## ONE RESEARCH-TUTOR DEMO

The tutor loads the existing complete Phase 5 development study, verifies it and
recomputes statistics from its 1,600 paired session outcomes. These are saved
simulation results, not new runs selected for this lesson.

| Strategy variant | Mean net P&L | Session SD | Mean SE | Observed minimum / maximum |
|---|---:|---:|---:|---:|
| Fixed quotes | £0.182372 | £0.255528 | £0.006388 | −£0.923 / £0.950 |
| Inventory-aware | −£0.135929 | £0.402600 | £0.010065 | −£2.973 / £0.746 |

SD describes how dispersed individual session outcomes are. SE describes the
sampling uncertainty of an estimated mean, under the stated sampling assumptions.
For independent sessions, `SE = s / √n`, where `s` is sample SD and `n` the number
of sessions. Here `√1600 = 40`, so fixed-quote SE is £0.255528 / 40 ≈ £0.006388.
Four times as many independent sessions would halve SE if SD stayed the same;
it would not make individual outcomes half as variable.

The initial question asks which quantity measures uncertainty in the mean. The
demo selects SD, receives a distinction-focused hint, and then selects SE.

The paired mean difference, inventory minus fixed, is **−£0.318301**. Its SE is
**£0.009755**, versus an independent-sample benchmark of **£0.011921**.
Pairing compares both strategies in corresponding simulated circumstances.
`Var(X−Y) = Var(X) + Var(Y) − 2Cov(X,Y)`: `X` and `Y` are the paired strategy
outcomes; covariance measures how they move together. Positive covariance can
reduce difference uncertainty here. Pairing is not guaranteed to help every model.

The follow-ups cover costs, tail outcomes, model assumptions and selection bias.
Neither a positive mean nor a small uncertainty estimate establishes real alpha.
Reopening evaluation seeds does not make them untouched evidence again. Observed
extremes are sample outcomes, not hard bounds on possible loss.

## MASTERY SYSTEM EXPLANATION

Every concept begins **Not assessed**, with no score. Time, pages viewed,
explanations and financial profit earn no mastery credit.

For the last at most ten eligible graded attempts:

`practice score = 100 × (1 + sum of credits) / (2 + number of attempts)`.

An unassisted first success earns 1, success after a hint/retry earns 0.5, and an
incorrect answer earns 0. The added 1 and 2 stabilise a very small sample; they
are not invented learner answers. Display rounds to steps of five.

In the demo, the first wrong answer gives `100×1/3 = 33⅓`, displayed as 35.
The helped correction gives `100×1.5/4 = 37.5`, displayed as 40. Both remain
Beginning. The interface shows evidence and categories, not a claim that 40 is a
scientifically measured level of intelligence or trading ability.

Beginning requires some eligible evidence; Developing requires at least three
recent eligible attempts and score ≥40; Comfortable requires six and ≥70;
Strong requires ten and ≥85. These thresholds are documented design choices.

Counters reconcile exactly:
`attempts = correct first + correct after hint + incorrect`.
Unknown options and malformed numbers are rejected, rather than graded as beliefs.
Repeating a completed/revealed concept, source context and difficulty on the same
UTC day adds practice history but no further score. Explanations cannot be copied
straight back for new credit. Recent completion keys are bounded, so this is a
learning aid rather than a tamper-resistant examination system.

Three eligible unassisted successes at the current level, with prerequisites
assessed, allow progression. Two consecutive errors lower the target one level.
Advanced questions require foundational assessment; trading remains unrestricted.

## MISTAKE-LOG DEMO

The first incorrect choice, “Use the displayed midpoint,” is recorded against
VWAP question `q-1` as a **One-off error**. Repeating that choice on a later
question instance `q-2` changes it to **Repeated misconception**.

The evidence includes the selected claim, question identifier, source context,
mode and learning time. Multiple retries of one question do not masquerade as
several independent encounters. A wrong numeric answer is calculation evidence;
the tutor does not invent a psychological explanation for it. The architecture
error is separately tagged with `mode: defence` for later project-defence review.

## SPACED-REVIEW DEMO

The helped VWAP correction is due after two calendar days. At three days the
demo finds it due and revisits the saved actual fill. The market clock has not
advanced as a result of changing the learning calendar. The repeated error then
sets a one-day review interval.

Scheduling is explicit: wrong/revealed material returns after one day; helped
success after two; consecutive eligible first successes after 3, 7, 14 and then
30 days. Priority is four times the count of repeated misconceptions, plus overdue
days capped at 30, plus the number of concepts that depend on this foundation.
Calendar time changes review priority, not the score. Review now is voluntary;
automatic review obeys the configured event gap.

## INTERVIEW-MODE DEMO

After assessing liquidity, the demo selects Interview and VWAP. The same actual
six-unit execution becomes a Level 2 question requiring **100.01667**. A declared
tolerance accepts the rounded decimal. Submission moves to a debrief stage with
no immediate explanation; Show debrief reveals the worked answer and update.

Interview mode permits at most one hint, preserves the question's actual source
and supports deeper reasoning follow-ups. It evaluates structured reasoning or
numbers. It does not claim to evaluate fluent oral defence or unrestricted prose.
Timing was optional and has not been used to score the learner.

## PROJECT-DEFENCE DEMO

The demo asks why the UI and matching engine are separate. Selecting “So the UI
can invent convenient fills” records an explicit architecture error in defence
mode. The delayed debrief explains that the engine supplies authoritative fills,
while interfaces submit intentions and display results. The earlier valid VWAP
does not excuse an architecture misconception.

Go deeper can reveal structured reasoning and criticism without granting score.
Supported defence material includes price-time priority, reproducibility, common
random numbers, synthetic-market limitations, testing and research integrity.
Options and later-phase techniques are excluded. The mistake log retains which
defence questions caused difficulty.

## LEARNING-DASHBOARD WALKTHROUGH

- **Practice & interview:** choose the teaching mode, an encountered concept,
  answer and ask for hints or deeper explanations.
- **Research:** open a verified saved study and compare its actual values. The
  page does not launch or change simulations.
- **Your learning map:** expand one of eleven domains to inspect concept status,
  attempts, recent answer evidence, prerequisites and due dates. Prepared topics
  stay clearly unassessed. Domain rows show assessed counts rather than invented
  aggregate competence probabilities.
- **Revisit & repair:** find weak concepts, due reviews, explicit misconception
  evidence and recent responses. Open a clearly identified saved context.
- **Your local notebook:** change frequency/hints, export progress or reset it.

The final personal profile starts without these demonstration scores. Correct
test answers and the user's approval to build are not imported as mastery.

## PRIVACY / INFORMATION-BOUNDARY TEST

Live input uses immutable allowlisted schemas for book, own executions, account,
own quotes, matured public markouts and complete research summaries. It contains
no engine, RNG, signal, latent value, future event queue or private identity.

Tests inject unknown hidden fields both at top level and inside fill records;
they are ignored by projection or rejected by strict context validation. Pending
or future-dated markouts cannot become lessons. Ordinary question and progress
exports are checked for observer fields. Corrupt/unknown stored fields fail
visibly instead of being repaired into apparently valid learning evidence.

After an ended session, explicit observer reveal uses a separate route and UI
section. Requests during live trading or an earlier replay frame are rejected.
The observer records never enter Tutor or Progress. The public review's
“known then” section uses the pre-match observation, not the execution result.

Red-team testing found and fixed two subtle hindsight routes: an execution VWAP
appearing in a pre-trade description, and a later-frame question remaining after
rewinding replay. Rewinds now invalidate later questions and cached contexts,
including when tutoring was disabled before the rewind and re-enabled afterwards.
The UI clears separate observer content when the public session/frame changes.

These are application boundaries for normal use, not security against someone
who edits Python, reads saved seeds or opens the full ended observer journal.

## RNG-INDEPENDENCE TEST

Across seeds **0, 42 and 91**, tests apply identical market actions and explicit
ticks with tutoring enabled and disabled, adding teaching interactions only to
the enabled branch. Market evidence and complete replay journals remain equal.
The short demonstration also compares byte-identical journals and validates replay.

Tutor commands have their own route and storage. Learning calendar time, question
IDs, option ordering and mastery never draw from market random streams. Option
ordering uses a hash of the public question and option ID; it does not encode
correctness or consume any RNG.

This guarantee holds for the same ordered actions/ticks. In a running interactive
session, time spent reading, file I/O and differently timed human orders may alter
which public state an order encounters. Pause provides a controlled teaching
moment. We do not claim two differently timed human sessions must match.

## FILES CHANGED

Paths below are relative to the project root.

| Area | New or modified files and purpose |
|---|---|
| Tutor curriculum | New `src/quantlab/tutor/catalog.py`, `curriculum.py`, `questions.py`: concepts, prerequisite graph, four-layer lessons and validators |
| Public boundaries | New `src/quantlab/tutor/context.py`, `adapters.py`: detached public schemas and Phase 4/5 integration |
| Learning state | New `src/quantlab/tutor/progress.py`, `service.py`, `bridge.py`: evidence, persistence, scheduling, modes and application integration |
| Phase 4 interface | New `src/quantlab/tutor/terminal.py`; modified `src/quantlab/maker_demo.py` for optional adaptive manual teaching |
| Trading server | Modified `src/quantlab/trading/server.py` for separate tutor/dashboard/export/review routes and profile configuration |
| Browser interface | Modified `src/quantlab/trading/static/index.html`, `app.js`; new `learning.html`, `tutor.js`, `tutor.css` |
| Reproducible demo | New `src/quantlab/tutor_demo.py`, `docs/learning/phase_07/demo.json`, `demo.txt`, `revision.md` |
| Tests | New `tests/unit/test_tutor_progress.py`, `test_tutor_questions.py`, `tests/integration/test_quant_tutor.py`, `test_tutor_http.py` |
| Package / local data | Modified `pyproject.toml`, `src/quantlab/__init__.py` to 0.7.0 and demo entry point; `.gitignore` excludes personal learning records |
| Documentation | Updated `README.md`, `ROADMAP.md`, `ASSUMPTIONS.md`, `LEARNING_LOG.md`, `CHANGELOG.md`; new `docs/architecture/phase_07.md`, this report and the saved test report |

The existing individual FIFO order queues, matching conservation checks, account
and financial calculations remain unchanged. Tutor code receives their outputs.

## RED TEAM

**Defects found and fixed during implementation:** pre-match hindsight in review
text; stale future questions after replay rewind, including disabled/re-enabled
tutoring; nested research-unit metadata; qualitative Go deeper returning the same
level; scoring/copy-credit edge cases; duplicate prompts and unchanged observation
writes; and correct-choice position shortcuts. Regression tests cover these cases.

**Remaining weaknesses and unrealistic assumptions:**

1. The mastery index, half credit, categories and scheduling intervals are
   transparent heuristics, not psychometric calibration. Ten recent answers and
   multiple-choice recognition cannot establish professional competence.
2. Misconceptions reflect chosen options, not a diagnosis of thought. Repeated
   guesses can still game scores; local files are editable. Interview/defence
   choices cannot assess fluent explanation, creativity or nuanced prose.
3. One local profile has one writer and one active question shared across tabs.
   Atomic replacement protects partial writes, not concurrent processes or all
   disk failures. Curriculum migration/version compatibility remains limited.
4. Public references can be endogenous, stale or influenced by the learner's
   actions. Negative markouts are diagnostics, not extra account losses, causal
   proof of informed trading or a verdict on decision quality.
5. The synthetic market remains uncalibrated, with simplified information,
   arrivals, price response, inventory and costs. Teaching from its outputs does
   not validate the model or demonstrate transferable alpha.
6. Research uncertainty depends on complete, appropriately independent sampling
   and the chosen statistic. Pairing need not help; observed extremes are not
   worst-case bounds; repeatedly viewing evaluation results weakens research
   separation. No lesson reverses that contamination.
7. Tutor work and human thinking have wall-clock costs. Exact path independence
   is conditional on identical market actions and ticks, not identical wall time.
8. Observer separation is intended for honest local use. It cannot erase what a
   learner already saw after ending a session or prevent reading local model code.
9. The browser research list is deliberately small; arbitrary new studies need
   the local adapter. Phase 4 terminal and browser profiles default to separate
   files. Mobile, assistive-technology and broad browser testing are incomplete.
10. No external conversational layer, timed scoring, voice defence, options,
    advanced risk engine or Phase 8 work is included. Prepared domains remain
    visible and unassessed.

## 3-QUESTION ARVIND CHECK

These are optional review questions, not a gate on using the platform.

1. Your order fills two units at £100.01 and four at £100.02. Why is the simple
   average of those two prices the wrong average execution price?
2. Independent simulation count quadruples while session SD stays unchanged.
   What happens to the standard error of the sample mean?
3. A resting seller receives a negative provider markout. Does that prove an
   informed buyer or a bad decision? What additional evidence would you need?

Phase 7 awaits Arvind's review. Phase 8 remains unstarted.
