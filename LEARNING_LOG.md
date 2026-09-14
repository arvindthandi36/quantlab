# Arvind's learning log

This is a syllabus and evidence log, not a mastery certificate. Authorship and
project ownership do not imply independent implementation or validation of every
component. Answers and reasoning, over time, will establish understanding.

## Phases 0 and 1 — 10 September 2026

### Starting evidence

After the proposed execution convention was explained, Arvind correctly predicted
that A's 3 units would fill before 2 of B's 4 units at the same £100.02 ask,
leaving B with 2. Arvind explicitly said this was new material and asked for it to
be treated as a starting level, with simple first explanations and progressively
harder questions while retaining technical quality. Record this as **correct with
guidance; independent understanding not yet established**. No mastery score awarded.

### What Arvind should now understand

These remain review targets until checked:

- [ ] A bid is an offer to buy; an ask is an offer to sell.
- [ ] A limit specifies an acceptable bound; it does not promise execution.
- [ ] A market order requests immediate available liquidity, not a guaranteed price or size.
- [ ] Better price beats earlier arrival at a worse price.
- [ ] At the same price, earlier orders fill first; partial fills keep their priority.
- [ ] Spread and mid-price are quote summaries, not guaranteed profits or trade prices.
- [ ] A matching engine and a model of why traders submit orders are different components.

### Mathematics introduced

- Price = integer tick count × tick size; exact representations avoid rounding ambiguity.
- Spread = best ask − best bid; mid = (best ask + best bid) / 2.
- Match size = minimum of incoming and resting remaining quantities.
- VWAP = sum(price × executed quantity) / sum(executed quantity).
- Incoming size = executed + resting + cancelled.
- Total accepted order-units = twice traded units + resting units + cancelled units.

See [the lesson](docs/maths/limit_order_book.md). These identities describe order
mechanics, not expected returns or portfolio risk.

### Python/software concepts introduced

- A `src` package layout and isolated dependencies make imports and installation explicit.
- Enums prevent ambiguous side strings; type hints document the contract, while
  runtime validation enforces financial inputs.
- Frozen dataclasses protect instructions and historical observations; only private
  remainders mutate as fills occur.
- A sorted price list answers “best price”; an ordered dictionary answers “oldest
  order here” while allowing direct cancellation; an ID dictionary finds active orders.
- Assertions in tests encode invariants; a separate reference algorithm reduces
  the risk of duplicating a production bug in expected outputs.
- A root seed plus stable named RNG streams avoids accidental coupling between
  future agents; a fixed matching scenario does not need random numbers.

### Design decisions

Positive whole-unit orders; integer ticks; FIFO at each price; resting-price
execution; good-until-cancelled limits; unmet market size cancelled explicitly;
book-lifetime unique IDs; logical submission sequence instead of a wall clock.
These choices were presented before substantial implementation. They are a
baseline, not a claim that Arvind independently selected or validated them.

### Things worth revisiting

Mid-price can lie between allowed order ticks. A positive spread is not a promise
of profit. Available depth can disappear. Market orders can sweep multiple prices.
Preserving quantities does not prove conservation of cash or correct P&L.

### Interview questions

The five checkpoint questions are in [Phase 1 review](docs/learning/phase_01_review.md).
Formal answers remain pending for repetition. Arvind explicitly reviewed Phase 1
as sufficient to continue and authorised Phase 2; this overrides the earlier
progression gate without implying demonstrated mastery of all five questions.

## Phase 2 — 10 September 2026

### What Arvind should now understand

Review targets, not awarded mastery:

- [ ] The clock jumps to events; an event is something that can change state.
- [ ] The queue orders events by time, then scheduling order for exact ties.
- [ ] Trader reasons generate orders; only matching generates transactions.
- [ ] Latent value, quotes and transaction prices are distinct quantities.
- [ ] A market buy cannot execute against other bids; it requires sellers.
- [ ] A seed reproduces random choices; it does not make a model realistic.
- [ ] Replay of recorded instructions differs from generating a fresh seeded run.

Arvind answered **“No”** when asked whether an unobserved latent-value rise must
raise the next transaction price. That is correct. The response demonstrates the
prediction, but its underlying reasoning has not yet been assessed. Repetition
and progressively harder examples should continue from first principles.

### Mathematics introduced

Fair direction coins; uniform discrete sizes/offsets; exponential waiting times;
Poisson arrival counts and intensity; expectation and variance; Gaussian random
increments and square-root-of-time scaling. All variables, units and limitations
are defined in [Phase 2 mathematics](docs/maths/phase_02_market.md).

### Python/software concepts introduced

Heap queues with deterministic ties; integer clocks; typed public observations;
independent RNG streams for arrival versus decision draws; immutable event records;
JSON serialisation; replay against a fresh matching engine; statistical tests with
sampling tolerances. Always-on reconciliation uses exceptions, not removable
`assert` statements. A failed book/simulator cannot continue silently.

### Design decisions

An empty initial book; two aggregate non-informational trader sources; separate
public opening reference and hidden latent value; atomic trader events; fixed-time
latent updates; rounded exponential arrival gaps; no Phase 3 features. Arvind also
requested explicit two-sided fill conservation and an aggregate depth display;
both were implemented and tested before continuing Phase 2 verification.

### Things worth revisiting

An expected rate is not a timetable. Changing sigma changes step uncertainty, not
the expected direction. Latent movement cannot reprice existing limits in this
model. FIFO priority persists underneath aggregate depth. Synthetic output does
not establish real-market profitability or meaningful price discovery.

### Interview questions

Three short questions are in [the Phase 2 walkthrough](docs/learning/phase_02_report.md).
Formal answers remain repetition targets. Arvind said Phase 2 was understood well
enough to continue and explicitly authorised Phase 3 only; no mastery score is inferred.

## Phase 3 — 10 September 2026

### Starting level and scope

Arvind understands basic order-book mechanics and asked to learn information
asymmetry, conditional expectation and markouts from first principles. Phase 3 was
explicitly authorised; Phase 4 remains gated on review. An optional pre-build
prediction about trusting noisier signals was offered; no answer is recorded yet.

### Review targets

- [ ] Distinguish latent truth, noisy signal, actual signal error and estimated value.
- [ ] Explain what normal agents, informed agents and the observer can each see.
- [ ] Interpret a conditional mean as a revised probability-weighted average.
- [ ] Compare estimated edge with an executable quote, costs and an uncertainty buffer.
- [ ] Explain why better information can reduce unnecessary trading.
- [ ] Explain adverse selection as which resting quotes get accepted.
- [ ] Calculate a provider markout in either direction and distinguish it from P&L.
- [ ] Explain pending horizons, absent midpoints and why future records cannot enter decisions.

### Mathematics and software introduced

Noisy Gaussian measurements; prior and posterior beliefs; one-signal conditional
mean and remaining uncertainty; executable edge and assumed costs; provider-signed
markouts and spread/reference-move decomposition. Statistical checks use sampling
standard errors and paired comparisons. The [lesson](docs/maths/phase_03_information.md)
defines every quantity and makes its subjective modelling assumptions explicit.

Private signal delivery and pure decision functions are separated from observer
audits. Dedicated public data types strip secrets and private-event timestamps.
Versioned journals verify informed decisions without RNG draws. Markouts use an
explicit occurred-event prefix; absent/pending measurements remain labelled.

### Evidence and things to revisit

The actual seed-42 run has one informed sell at £100.01 and a later negative
latent-reference markout for its resting buyer. It has no mature two-sided midpoint
at the selected horizons, and neutral liquidity fills also have negative latent
marks. Controlled mirrored tests show positive initial spread proxy becoming
negative markout for either provider side. Neither observation proves real-market
profitability or mastery of the concepts.

A current-value signal does not predict the next independent latent shock.
A conditional-mean formula can be correct under assumptions that do not describe
the actual evolving market. A matching invariant is not a monetary ledger.

### Interview questions

The three-question checkpoint is in the [Phase 3 review](docs/learning/phase_03_report.md).
Arvind said Phase 3 was understood well enough to continue and explicitly authorised
Phase 4 only. Formal question answers remain repetition targets; no mastery score is inferred.

## Phase 4 — 10 September 2026

### Starting level and scope

Arvind asked to act as or configure a liquidity provider, while learning inventory,
cash, FIFO realised/unrealised P&L and attribution from first principles. The request
explicitly required honest comparisons and a warning against equating profit with
successful market making. Phase 5 remains gated on review.

### Review targets

- [ ] Explain why buying increases signed inventory and selling decreases it.
- [ ] Explain why positive inventory lowers the quote centre under R−kq.
- [ ] Distinguish a soft quoting restriction from hard resting-order capacity.
- [ ] Separate sale proceeds from profit; reconcile cash plus marked inventory.
- [ ] Calculate a simple FIFO close and remaining unrealised P&L.
- [ ] Explain why markouts do not belong in the cash ledger.
- [ ] Distinguish execution edge from gains due to carrying inventory through price moves.
- [ ] Interpret time-weighted exposure, drawdown, fill-rate denominator and markout coverage.
- [ ] Explain common random numbers without claiming identical counterfactual fills.

### Implementation and observed evidence

The lab implements the [predeclared contract](docs/maths/phase_04_accounting.md)
and a [first-principles lesson](docs/maths/phase_04_market_making.md). The seed-42
inventory-aware demo ends flat with £0.036 net P&L, while available one-event
midpoint markouts average negative. The 20-pair comparison lowers average inventory
under inventory-aware quoting but worsens mean P&L and drawdown. These mixed results
were retained without tuning; they are teaching evidence, not real-market alpha.

Manual mode uses OBSERVE → PREDICT → DECIDE → RESULT → EXPLAIN. A wrong first
answer receives a hint and retry. Scripted test answers exercised this flow; they
are explicitly not Arvind's answers and do not establish understanding.

### Things worth revisiting

Fewer inventory units need not imply smaller P&L drawdown. A public marking
reference may be influenced by the maker's own transactions. Realised P&L and
markouts can have opposite signs because they answer different questions.
Quote replacement loses queue priority. End marks do not guarantee liquidation.

### Interview questions

The three-question checkpoint is in the [Phase 4 review](docs/learning/phase_04_report.md).
Formal answers remain repetition targets. On 11 September 2026, Arvind said:
“I understand Phase 4 well enough to continue. Proceed to Phase 5 only.”
This authorises Phase 5 without claiming mastery of unanswered checkpoints.

## Phase 5 — 11 September 2026

Arvind requests a rigorous, reusable Monte Carlo research environment, with market
making as its first experiment rather than its permanent scope. Personal directional
market/limit trading belongs to Phase 6; options and other strategies remain later
labs on the same market infrastructure. Phase 6 is not authorised yet.

The learning sequence is hypothesis → experiment design → repeated sessions →
distributions → statistics → interpretation → limitations. The research contract
records the baseline hypothesis (less inventory, uncertain P&L advantage), sample
sizes and unchanged strategy parameters before results. The sensitivity sweep is
exploratory; its winner is not declared optimal.

New concepts: random variables/distributions/expected values, sample means,
variance/SD/SE, quantiles/tails, confidence intervals, bootstrap, paired differences,
covariance/correlation, law of large numbers, central limit intuition, null and
alternative hypotheses, p-values, practical effects, selection bias, multiple
testing and evaluation discipline. The [first-principles lesson](docs/maths/phase_05_research.md)
uses INTUITION, MATHEMATICS, QUANTLAB EXAMPLE, ASSUMPTIONS, COMMON MISTAKES and
INTERVIEW QUESTIONS around actual recorded experiments.

Before showing sample-size results, an optional prediction asked what should happen
to SE when independent sessions increase from 100 to 400. No user answer is recorded
at this point. Automated CLI tests use scripted answers; they are not Arvind's
answers or evidence of mastery. The teaching mode gives a hint and retry before
showing its explanation after the observations.

The 1,600-pair development study shows lower mean absolute inventory but lower P&L
for the inventory-aware rule. The Gaussian equal-skill control selects a development
winner with mean 0.369 and observes mean 0.031 on untouched evaluation: selection
can create apparent skill despite known zero true expectation. Neither the control
nor synthetic market profitability establishes real-world alpha.

Review [Phase 5 results](docs/learning/phase_05_report.md), its confidence intervals,
downside distributions, exact extreme replay and red-team limitations. Phase 5's
three questions and repetition remain pending; Phase 6 awaits explicit review.


## Phase 5 review and Phase 6 — 11 September 2026

Arvind explicitly says Phase 5 is understood well enough to continue and authorises
Phase 6 only: a personal trading app with real buys/sells through the existing
engine. This is sufficient permission to build Phase 6, not evidence of mastery of
unanswered research questions. Phase 7 remains unauthorised.

Built the manual browser desk and wrote a first-principles lesson connecting bid,
ask, spread, liquidity, market/limit, FIFO, partial fills, VWAP, long/short, cash,
realised/unrealised P&L and directional risk directly to its controls. Beginner and
Quant are explanation views over the same market. The optional checkpoint asks a
prediction, permits hint/retry and explains an actual trade without future answers.

The demonstrated seed-42 manual session buys six, cancels a resting buy, receives
five passive sell units in two fills, cancels the remaining three, opens a short,
then covers to flat. Six executions / 16 units produce net −£0.066 including £0.016
fees. The thin-book challenge misses its five-unit acquisition target; the opening
short-position challenge reaches flat but loses £0.158. Objectives and profitability
are distinct; no favourable outcome is engineered or inferred as trading skill.

Automated and browser tests are our verification evidence, not Arvind's answers.
The three Phase 6 questions in the [review report](docs/learning/phase_06_report.md)
remain unanswered. Repetition is still appropriate for earlier concepts. Wait for
Arvind's Phase 6 review before starting Phase 7.


## Phase 6 approval and Phase 7 — 11 September 2026

Arvind explicitly said “Phase 6 is approved. Proceed to Phase 7 only.”
All 599 previous tests were required to remain passing. Permission to build is not
evidence that earlier review questions have been answered or mastered.

Phase 7 introduces answer-based local learning history. Every concept starts Not
assessed. The earlier conversation and automated test answers are not silently
converted into scores. The normal learner profile starts empty.

The demonstration learner (separate temporary storage) bought six actual units,
chose midpoint incorrectly, received a quantity hint and corrected the answer.
The worked VWAP is (2×£100.01 + 4×£100.02)/6 = £100.01667. Its two answers survive
a Tutor restart. Three learning-calendar days later, the old event returns for
review; another midpoint error is repeated evidence. After a liquidity assessment,
the same fills support a Level 2 interview calculation with delayed explanation.

At one simulated second the actual session ends with marked P&L +£0.044, £0.006
fees and maximum drawdown £0.076. None of those values creates answer credit or
proves that buying was a good decision. The Phase 5 study supplies actual mean,
SD, SE and paired-difference values; synthetic results do not establish real alpha.

Review targets: weighted versus unweighted prices; SD versus SE; execution versus
markout versus account P&L; conditioning a decision on what was known then; the
difference between learning evidence and a calibrated skill estimate.

These are demonstrated software behaviours, not Arvind's answers. Phase 7 awaits
review. Phase 8 remains unstarted and unauthorised.

## Phase 7 approval and Phase 8 — 11 September 2026

Arvind explicitly approved Phase 7 and authorised Phase 8 only, requiring all
747 previous tests to remain passing. Earlier unanswered checks remain repetition
targets; approval to build is not evidence of mathematical mastery.

The Options Lab teaches from actual contracts, quotes, premium cash flows,
positions, stock hedges, solver diagnostics and research results. The browser
demonstration uses an isolated temporary profile. Buying a call prompts the
asset-versus-cash lesson; a hint followed by a correct structured answer is assisted
success. Phase 5 derivatives results supply actual mean, SD and SE to the same tutor.
No demonstration answer is written into Arvind's learning record.

The seed-42 call costs £230.2151 plus fee. Selling 51 stock units nearly hedges it;
the next move changes delta, motivating a sale of two more. Leaving that hedge
unchanged until day 30, settling the option and buying back 53 shares gives
−£194.8211 net P&L. This is an actual result, not a programmed penalty or a
judgement about the learner. Daily hedge research is a different policy.

Repetition targets: rights versus obligations; cash versus profit; multipliers;
slope versus curvature; annual/daily/percentage-point units; theoretical versus
executable value; IV versus process volatility versus RV; Newton's vega divisor;
why a bracket helps; temporary delta neutrality; limits of model-conditional research.

Phase 8 awaits review. Phase 9 remains unstarted and requires explicit authorisation.


## Phase 8 approval and Phase 9 — 12 September 2026

Arvind approved Phase 8 and requested Phase 9 only. Approval is permission to
continue, not evidence of mastery. No new answer or score has been attributed to
Arvind. Browser QA uses an isolated temporary learning profile.

New repetition targets: cash versus value versus P&L; covariance versus correlation;
why cross terms matter; covariance PSD; VaR is a threshold, not maximum loss;
exact empirical tail mass; ES severity; sample versus model uncertainty; local
delta versus gamma/vega/theta; full repricing versus realised outcomes; solver
feasibility; actual hedging trades and explicit order limits.

The one-call demo's actual 51-share sale leaves delta 0.143575 but vega 1143.26204.
Full one-day MC VaR falls from £89.698948 to £3.823316. A separate +20-vol-point
stress gains £228.527168 while actual P&L remains -£2.11105. This illustrates
remaining exposure, not a guaranteed trading rule.

Phase 9 is implemented and awaits review. Phase 10 remains unstarted.


## Phase 9 approval and Phase 10 — 12 September 2026

Arvind approved Phase 9 and explicitly requested Phase 10 only. Existing basic book
understanding is assumed; most statistical-arbitrage concepts are introduced from
first principles. Repetition remains appropriate. Approval does not imply recalled
mastery, and no quiz answer has been fabricated or credited.

New learning targets: correlation versus cointegration; fitting a line and interpreting
its residual; beta units versus dollar/factor neutrality; causal rolling z-scores;
mean-reversion expectations versus guarantees; delayed/partial pair execution; actual
cost/P&L reconciliation; fixed versus walk-forward fitting; regime failure; parameter
search records; winner's curse and an untouched holdout. The 18-topic maths document
uses intuition, mathematics, QuantLab example, assumptions, common mistakes and
interview questions for every topic.

Desktop acceptance exercises and automated tutor checks use temporary learning
profiles, not Arvind's answer history. Three short check questions are supplied for
review. Phase 11 remains unstarted.


## Core approval and Phase 12 — 12 September 2026

Arvind approved QuantLab 1.0.0 core and requested Phase 12 only. Earlier “unstarted”
statements above are historical phase checkpoints. Approval does not establish
recalled mastery. No answer has been submitted on Arvind’s behalf.

New learning targets: trace a displayed number to actual evidence; distinguish
accounting from model assumptions; interpret before/after inputs without invented
causal percentages; separate a controlled hypothetical from executed P&L; distinguish
per-unit, contract and portfolio Greeks; read VaR and ES as conditional distributions;
understand residual normalisation and why its window excludes the current point.

Four explanation depths support repetition. Opening lessons does not earn mastery.
Quiz prompts reuse the existing tutor and current public facts; explicit answers are
required for assessed evidence. Browser checks use a disposable learning profile.

Phase 12 is implemented and awaits review. Phase 13 has not begun.


## Phase 13 — sources of market evidence, 12 September 2026

Arvind approved Phase 12 and authorised Phase 13 only. This is permission to build the next
phase, not proof of mastery. No Phase 13 check answer has been submitted or graded for Arvind.
Browser checks used a separate temporary profile; reading/exploration did not earn mastery.

New review targets, explained from first principles in the market documentation:

- A synthetic model specifies a mechanism; a historical path records what happened without
  identifying its hidden cause. A scenario is an intentionally configured synthetic model.
- A complete bar becomes available at its timestamp. Submitting now does not entitle an order
  to use a later high/low. Next-close execution is a declared paper rule, not a historical fact.
- A volume participation budget is a cap, not evidence of historical queue priority.
- Changing the future must leave today's chart, model fit, orders, risk and lesson unchanged.
- Seed/configuration and dataset/provenance fingerprints answer different reproducibility questions.
- One historical path is not many independent experiments; objective success is separate from P&L.

Questions for review: why high/low does not imply a fill; what public evidence can show about a
hidden regime; why a profitable result or a matching replay cannot establish future alpha.
Phase 13 was subsequently approved for Phase 14; this entry records the earlier build gate.

## Phase 14 — following evidence through a guided replay, 13 September 2026

Arvind approved Phase 13 and authorised Phase 14 only. This is permission to build, not a claim
of mastery. Browser QA used a separate temporary learning profile, not Arvind's personal record.

The new sequence is observe → predict → result → explain → maths → system connections → use
and limitations. It reuses previous phase concepts and adds no major financial model. Demos are
short, restartable and source-labelled. A saved session can be verified and taught without its
original live session. Before a reveal, the teacher cannot use the next result to title the event,
describe the user's process, or disclose a private signal.

Important repetitions: a fill is not necessarily good news; a delta hedge does not remove vega;
equal VaR can conceal unequal tail severity; similar price correlations do not establish a stable
tradable residual; the best of many noisy development results can mostly reflect selection luck.
A good outcome does not prove a good process, and a bad outcome does not by itself disprove one.

Watching and completing demos are recorded separately from mastery. The three Phase 14 review
questions are in the report; no Arvind answer has been inferred or graded. Phase 14 awaits review.
Phase 15 has not begun.


## Phase 15 · product release preparation

Arvind approved Phase 14 and requested the final presentation/release phase. MIT licensing was
explicitly selected: Arvind Thandi, 2026. Approval is not inferred mastery. Showcase captures use a
separate temporary learning profile. The defence guide identifies concepts to revisit, not memorised
answers or automatic evidence of understanding. No subsequent implementation phase is started.
