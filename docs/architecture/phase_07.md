# Phase 7 teaching contract

> Historical phase record. Current core conventions and release status are in the root README, ASSUMPTIONS and Phase 11 release report. Test counts and runtime labels below describe this phase.


Defined before implementation. This is a local, structured tutor, not a chatbot.
The Phase 1–6 exchange, account, replay and research calculations remain authoritative.
No Phase 8 options implementation is authorised.

## Separation and evidence

The tutor receives detached public event contexts, not an engine, random generator,
full observer journal or callable trading interface. Tutor HTTP commands have their
own route, lock, revision and local progress file; they never enter a market command
log. Teaching while a market is running does not freeze wall time; Pause remains
the trader's choice. Given the same market actions and explicit ticks, adding tutor
interactions must leave the entire market evidence and RNG paths identical.

Contexts identify an actual session/public event/order/trade or verified research
result. Live contexts include only available public facts. They are frozen when a
question is asked, so subsequent price changes cannot silently change the answer.
The tutor teaches retrospective events and optional pre-trade predictions against
the observed book. A prediction is not a promise about a later live order book.

Post-session review separates what was known at each order from later public
outcomes. Observer information requires an ended session and an explicit reveal
request; it has a separate response/render path and never enters questions,
mastery, notes or progress exports. Decision reasoning and financial outcome are
separate dimensions. No profitable trade creates mastery or generic praise.

## Local evidence, hints and scheduling

Each concept starts not assessed. Viewing explanations or passage of time gives
no score. Valid graded answers record attempts, wrong answers, first-attempt success
and success after help. A transparent practice index uses a neutral pseudocount:
100 × (1 + sum of credits)/(2 + number of credited answers), over at most the most
recent 10 answers; credit = 1 for unassisted first success, 0.5 after help/retry,
0 for wrong. Round for display; report categories and evidence counts, not spurious
scientific precision. Categories require breadth of answer evidence. Repeating an
already credited question/context on the same UTC day is practice, not new score.

Misconceptions are linked to explicitly chosen distractors. One wrong question is
a one-off error; two distinct question instances on the same misconception are
repeated evidence. Never infer a misconception from an arbitrary free-text phrase.
Wrong answers receive a conceptual hint, then a stronger hint, then explanation
on the configured final attempt (default 3). Asking Explain early earns no success
credit; later answers to that revealed question are practice only.

Reviews use UTC learning time, independent of simulation time. A wrong/revealed
answer is due after one day; assisted success after two; successive unassisted
success after 3, 7, 14 and 30 days. Overdue, repeated-error and foundational concepts
receive priority. Time changes priority, never mastery. Automatic questions are
limited by a configurable public-event gap and no repeated source event. Explicit
Quiz me / review remains available; disabling tutoring does not block trading.

Difficulty advances one level at a time from demonstrated unassisted success and
assessed prerequisites. Levels are intuition, calculation, quant reasoning and
interview/research. Go deeper may show a harder explanation without granting score
or silently raising the assessed level. Unimplemented domains are visible as
prepared/not assessed, with no artificial calculus/options quizzes.

## Questions and modes

Structured questions declare concept, level, triggers, prerequisites, answer type,
validator, targeted hints and four teaching layers: intuition, maths with defined
variables, the actual QuantLab context, and an interview transfer question.
Numerical validation uses exact decimal/fraction inputs and declared tolerances.
Conceptual validation uses explicit choices/sets of reasons. Open notes are ungraded;
local rules do not pretend to understand unrestricted prose.

Interview and project-defence modes use implemented topics, fewer hints and delayed
debrief rather than immediate explanations. Rubric-based reason selection tests
concepts, not speaking fluency. An optional future language interface has no network
implementation, keys or automatic data transmission.

Progress persists independently of sessions using an atomic, versioned local JSON
store, with readable Markdown/JSON exports and an explicit reset. Corrupt progress
must fail visibly rather than silently assigning fresh mastery. Demo/test progress
uses separate temporary stores and is never attributed to Arvind.

## Implemented components

- `catalog.py`: eleven domains, implemented/prepared flags, prerequisite edges.
- `context.py`: immutable, explicit schemas for public book, executions, position,
  own quotes, matured marks and completed research summaries.
- `curriculum.py` / `questions.py`: concept-specific definitions, worked arithmetic,
  structured reason sets and deterministic option ordering. No unrestricted prose grading.
- `progress.py`: schema validation, reconciled answer counters, recent credits,
  misconception evidence, review dates and atomic local writes.
- `service.py`: relevance, question lifecycle, hints, modes, reviews and adaptation.
- `bridge.py`: local app integration and independent learning-error state.
- `adapters.py`: actual Phase 4 public observations and verified Phase 5 run rows.
- `terminal.py`: optional Phase 4 manual interface to the same tutor.
- `tutor.js`: rendering and input collection. Financial calculations and answer
  validation remain in Python. `OptionalLanguageLayer` is only a protocol; nothing
  calls a language service or sends data externally.

The Phase 6 server feeds the tutor a detached public snapshot after an action/tick.
The new `/api/tutor` command route never calls `TradingSession.command`.
Existing Phase 6 `learn`/`predict` commands remain for old replay compatibility;
the new browser panel does not use them. The exchange and account modules are unchanged.

## Exact mastery rule and limits

For the last at most ten **eligible graded attempts**, let c be 1 for a correct
unassisted first attempt, 0.5 for a correct attempt after a hint/retry, and 0 for an
incorrect attempt. The practice index is:

`score = 100 × (1 + Σc) / (2 + n)`.

Here n is the number of eligible attempts in that window. The added 1 and 2
provide one neutral success and failure as a stabiliser; they are not actual
answers. Before any eligible evidence the score is absent, not 50 or zero.
Displayed scores round to a multiple of five using Python's nearest rounding.

Categories use the unrounded index and evidence count:
Beginning after any eligible evidence; Developing at n≥3 and score≥40;
Comfortable at n≥6 and score≥70; Strong at n≥10 and score≥85.
These thresholds and half credit are explicit design choices, not empirically
calibrated estimates of human competence. At ten eligible answers the neutral
stabiliser keeps the index away from 0 and 100.

Every valid graded attempt contributes to reconciling counters:
`attempts = correct_first + correct_after_hint + incorrect`.
Invalid types, unknown options, empty/nonsensical numbers and duplicate reason
selections are validation errors, not graded misconceptions. Numerical exponents
are bounded before fraction parsing. Matching/accounting still use their own exact
financial validation.

Credit is suppressed for a completed or revealed concept/context/difficulty on
the same UTC day, retaining the last 200 completion keys per concept. Counts still
record practice. A genuinely harder calculation has a different difficulty key.
A revealed harder explanation is also blocked from earning immediate copy credit.
Wrong retries can each provide zero-valued evidence. These rules discourage easy
repetition; they are not tamper-resistant examination controls.

The dashboard shows per-concept evidence; domain rows aggregate assessed counts
and attempts, not pretend domain-wide mastery probabilities. Prepared concepts
have no questions and cannot be graded.

## Misconceptions and review timing

A misconception key distinguishes concept and selected incorrect option.
Evidence stores the explicit selected claim, question ID, time and mode; a
numerical error is labelled calculation evidence rather than an inferred belief.
A structured reason-set error is labelled reasoning evidence. One question can
have several retries without being labelled recurrent; another incorrect question
instance with the same key makes it repeated. This is not a diagnosis of a stable
mental model. Identical-context question instances can be deliberate later reviews.

Due date after wrong/revealed practice is one learning day; after helped success,
two. Consecutive eligible first successes use 3, 7, 14, 30 days, capped at 30.
An explicit explanation with no previous due date creates a one-day reminder;
it does not increase score or attempt count. A duplicate success earns no further
score and returns to a two-day practice interval.

Due priority is `4 × repeated misconception count + min(overdue days,30) +
number of dependent concepts`. UTC calendar time drives review only, not market
time, random draws or score decay. Weakness also increases contextual relevance
by up to nine points. A due question may return at the normal automatic cadence;
Review now and Quiz me are voluntary alternatives.

Default automatic spacing is eight **public exchange actions**, adjustable 1–100.
Unchanged snapshots do not rewrite progress or generate duplicate prompts. No
automatic prompt replaces an unanswered question or a prediction awaiting a
decision. A completed prediction's result remains visible through the next gap.
Explicit study/review may replace a question without grading it.

## Difficulty and teaching lifecycle

Three eligible, unassisted first successes at the current assessed level, plus
at least one assessed attempt on each prerequisite, permit the next level.
Two consecutive wrong answers reduce the target by one, never below intuition.
Prerequisites need assessment, not assumed mastery or forced completion of the
entire graph. They constrain questions only; no market control is gated.

The four labels are intuition, calculation, quantitative reasoning and
interview/research criticism. Calculations use real fills, book quotes, signed
positions or research sample size/SD. Hypothetical moves/count changes are
explicitly labelled as hypothetical. A qualitative concept without a sensible
arithmetic question moves to structured reasoning after its intuition evidence;
we do not fabricate arithmetic to fill the label. Explicit interview mode can
offer the next available supported challenge once prerequisites are assessed.
A newcomer with no usable foundation remains at intuition. Go deeper reveals a
higher explanation without awarding evidence.

Observe: selected public facts identify a real event.
Predict: optional, bounded question about the *observed* book.
Decide: the trader freely uses the existing controls.
Result: actual execution, including no fill/remainder where applicable.
Explain: intuition, defined mathematical quantities, exact event context and transfer.
Test: structured answer with evidence, or a subsequent voluntary quiz.
Revisit: due/review-now practice on a saved, clearly identified context.

Interview and project defence defer the explanation until Show debrief, permit
at most one hint, and record the mode with the answer. They evaluate selected
reasoning, not unrestricted speaking ability. Timer scoring is deliberately
omitted: timing was optional and is not a measure of understanding.

## Three information compartments

1. **Live learning:** public quotes, anonymous market facts, own order/fill/account
   state and already matured public marks. No latent value, signal, counterparty
   type, private next-event clock or future reference.
2. **Public post-session review:** pre-match observed quotes/position are separated
   from subsequent executions and public references. The pre-match section does
   not re-label an execution's VWAP as information known before the order.
3. **Observer-only:** an explicit POST with `reveal: true`, accepted only for an
   ended current session or ended replay frame. It returns a separate labelled,
   capped view of hidden records. It is not passed to Tutor or Progress. Starting
   a new live session or moving to an earlier replay frame clears this panel.

Rewinding replay also invalidates questions and cached contexts from later frames
of that source, even if tutoring is disabled during the rewind. Re-enabling cannot
restore future-frame information into the current live teaching context.

A negative provider mark is a signed reference diagnostic; it does not prove
informed identity and is never added to P&L. A profitable result does not grade
decision quality. Reviews may cite an actually cancelled order releasing capacity
or an actually correct first answer; they do not infer motivation, skill or an
optimal trade from outcomes.

These are program boundaries, not a sandbox against a malicious local Python
operator. Saved seeds/code and ended observer journals can reveal the model.
Checksums detect accidental alteration; they do not authenticate research authors.

## Phase 4 and Phase 5 integration

Phase 4's optional `--manual --adaptive` reads the same `MakerObservation` type as
the existing quoting policies and uses the shared question/grade engine. Its own
local progress file is `runs/learning/maker-progress.json`, avoiding simultaneous
writers with the browser. It can be supplied programmatically with an existing
Tutor to share one managed learner. Learning failure is reported separately and
does not change manual quote decisions. Browser manual-maker mode also exposes
real own quotes and inventory through the Phase 4 quote planner.

The research adapter invokes Phase 5's verified experiment loader, then recomputes
mean, SD, SE, intervals, extremes and paired differences from complete run rows
using the existing statistics module. It refuses incomplete/survivor-only samples,
missing outcomes and n<2. Units come from each variant's metric metadata.
Paired rows are aligned by run address, not sorted outcome. No simulation is run
or random stream drawn when opening results. The browser exposes a small registry
of saved development/evaluation/sensitivity studies, not arbitrary local paths.
New completed studies can be passed to `research_contexts(path)` programmatically.

Reopening old evaluation results does not create untouched evidence. Pairing is
explained through covariance, not as a guaranteed reduction in error. Observed
minimum is a sample extreme, not drawdown or a worst-possible-loss bound.
Nothing treats synthetic gains or a small p-value as evidence of real alpha.

## Storage, failure handling and reproducibility

The browser defaults to `runs/learning/progress.json`; `--learning-path` selects
another profile. Writes use a flushed/fsynced temporary file followed by atomic
replacement. Use one writer process per profile; this is not a distributed or
multi-user store. Multiple browser tabs share the same profile, session and active
question; stale question IDs are rejected. Recent answer history is capped at 200
and per-concept recent attempts at ten; aggregate counters persist.

Unknown schemas/fields and unreconciled counts fail visibly. A corrupt profile
disables learning while the exchange still works. Explicit reset preserves an
unreadable original as `.json.unreadable`; it will not overwrite an existing backup.
The reset clears learning, never trades/journals. Exports contain categories,
strong/weak lists, mistakes, recent answers and review recommendations, with no
raw observer state.

Market independence means identical financial evidence for identical ordered
market actions/ticks and seed/version, with or without tutor interactions. Wall
clock reading/thinking and local I/O can delay a person or server; a running market
does not promise identical execution for orders submitted at different times.
Pause for deliberate comparison. Learner dates, session IDs, scores and hints
are outside the market journal and random streams. Restarting restores learning;
live trading state still requires its existing saved replay.

Questions are reconstructed from saved public context and the installed bank.
Cross-version question-bank migration is future engineering work, not a claim
that an unanswered prompt can safely survive arbitrary curriculum changes.
