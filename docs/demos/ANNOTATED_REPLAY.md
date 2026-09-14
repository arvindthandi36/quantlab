# Teach Me This Session and annotated replay

Open **Demos → Teach Me This Session**, then select a completed compatible session or load its
saved JSON journal. Supported native formats are Trading, Options, Risk, Stat Arb, and Phase 13
Synthetic/Historical/Scenario wrappers. This does not need the original live in-memory session.
Historical imports need the exact original CSV and metadata imported through Markets first;
the built-in 100-row fixtures are also recognized by exact fingerprint, never by name alone.

## Verification comes first

The original replay API enforces its original schema, runtime/version, accounting, execution,
source and final-state checks. A failed verification leaves the current demo and personal session
unchanged. An arbitrary list of frames is not accepted as a verified journal.

Trading and Options record intermediate visual frames inside some commands. The teacher retains
initial state plus the final frame of each completed command revision. This prevents an Options
market-step frame from being attributed to the following hedge. Frame count must reconcile to
recorded action count plus one; otherwise teaching fails loudly.

## Selection, not a transcript of everything

A bounded candidate heap ranks executions, multiple fills/levels, partial fills (including an
IOC remainder), cancellations, inventory/P&L movements, markout updates, hedge actions, leg
risk, risk estimates, drawdown and rejected instructions. It prefers concept variety and then
presents selected moments chronologically. Magnitudes can identify large movements; a positive
P&L sign never awards “good process”. Both gains and losses remain eligible.

Selection cost is linear in transitions plus the displayed evidence inspected at those transitions,
with a bounded candidate heap. Verifying and retaining frames remains the original replay's cost.
The benchmark separately measures 10,000 public transitions and a genuine 252-action saved journal.

## The teaching sequence

Each selected moment presents **BEFORE → YOUR ACTION → PREDICT → RESULT → EXPLAIN**. Before
reveal, the title is neutral, the question comes from the public state and the recorded instruction,
and outcome-derived tags/concepts are withheld. After reveal, Explain uses that exact next
command-boundary state and its predecessor. Maths, dependencies and professional uses come from
Phase 12. Hindsight requires finishing the walkthrough and explicitly opting in.

The end summary gives what happened, selected decisions/concepts, the highest-ranked learning
moment, a clearly labelled selected exposure/P&L-move risk proxy, one misleading interpretation,
three review questions and one interview question. It is not a complete risk audit.

## Process and outcome

A user may select one of four quadrants and write a reason. This remains **their reflection**.
QuantLab reports process quality as unknown without a declared objective, rule or forecast.
A profitable path alone is insufficient evidence of a sound decision. Reflections do not change
mastery, risk settings or financial state.

Replay answers are ungraded practice because the user may already remember the completed path.
Loading, watching and completing a session cannot manufacture mastery.
