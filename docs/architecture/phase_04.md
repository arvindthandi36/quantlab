# Phase 4 architecture — Market Making Lab

> Historical phase record. Current core conventions and release status are in the root README, ASSUMPTIONS and Phase 11 release report. Test counts and runtime labels below describe this phase.


Owner: **Arvind Thandi**. The [accounting contract](../maths/phase_04_accounting.md)
was defined before implementation. Phase 5 remains unstarted.

## Responsibilities and data flow

```text
MarketMakingLab owns the exchange, account and public decision schedule
    ├── MarketEnvironment: original background clock, agents, signals and random streams
    └── fixed / inventory-aware policy, or manual QuoteRequest
             ↓ public MakerObservation only
         quote plan: exact centre → outward rounding → passive prices → inventory capacity
             ↓ cancel old maker orders, then post replacement orders
         existing OrderBook / FIFO / measured two-sided quantity conservation
             ↓ actual executions against maker-owned orders only
         MakerAccount: execution cash, fees, FIFO lots, current inventory
             ↓ public reference mark + independent reconciliation
         immutable LabRecord / final LabResult (privileged observer evidence)
             ├── public_frames / manual observation (no private state)
             ├── public-event markouts + coverage / inventory and P&L diagnostics
             ├── explicit observer debug
             └── saved journal / full action-and-account replay
```

The previous `MarketSimulation` is now a standalone wrapper over `MarketEnvironment`.
The source driver accepts a caller-owned book; it does not know the maker's strategy
or account. This lets both lab and original simulation use identical background
event logic, without copying agents or matching rules. The original public API,
seeded source ordering, CLI, tests and old journals remain supported.

Strategies live separately from `portfolio/accounting.py` and the lab controller.
`quote_request(observation, config)` is a pure decision function. Maker configuration
contains only the maker's own controls, not hidden market parameters. A manual
request has bid/ask distances and sizes; the programmatic request also supports an
explicit exact centre shift. User input is validated before cancellation begins.

## Time and resting exposure

The maker's decision clock is fixed and public. The controller processes background
events through the next decision time, then pauses. Background events at exactly
that time occur first in their established insertion order. An observer can inspect
background records, but normal manual interaction never pauses on a private arrival.

Decisions run at zero and every refresh interval strictly before the horizon.
Quotes remain live between decisions, including after partial fills. An exhausted
side waits until the next refresh; quotes are not magically replenished mid-order.
At the horizon, process all due background events, cancel remaining maker orders
and retain any inventory at its public mark. There is no forced liquidation fill.

Each replacement cancels all previous maker remainders before posting fresh IDs.
The maker is passive: it cannot cross the external book or its own opposite quote.
Outward adjustments are reported. A registry of all owned IDs plus current quote
IDs detects stale owned orders. Each side independently reserves enough hard-limit
capacity for every remaining unit. Opposite orders are never assumed to fill first.

## Exact accounting and independent checks

Monetary state uses `Fraction` tick-unit amounts. Prices sent to the exchange remain
positive integer ticks; no float or display rounding reaches the ledger. A FIFO
deque holds signed open lots. A fill closes opposite lots first; any remaining
quantity opens a lot on the new side. Fees are immediately expensed.

Every account mutation checks its fill ledger against signed inventory, execution
cash, fees, execution edge, seen trade IDs and maximum inventory. Open lots reconcile
to inventory. Two independent P&L identities reconcile realised/unrealised accounting
and execution-edge/inventory-movement attribution to cash plus marked inventory.
The latter is exact only for the documented reference and event convention.

The controller also reconciles all submitted units, cancellations, resting units
and twice total traded volume across background and maker instructions. It checks
maker capacity after fills and replacements. Errors disable further account/lab
work; no repairs, fabricated exits or balancing entries are inserted. Python `-O`
does not remove the accounting guards.

## Public data and markout clock

`MakerObservation` is a detached immutable object with public quotes, external
reference/source, the maker's own account, current orders and recent fills.
`PublicLabFrame` contains observable actions and own account state, without private
agent labels, source-identifying external IDs, seed, signal or latent values.
Ordinary presentation accepts public-only markout references. Debug is separately
requested and never fed back into an ordinary strategy.

Phase 4 markouts use 1/5/20 subsequent **public exchange events**. This convention
is necessary for interactive public display: Phase 3's internal event count could
disclose private holds. Original Phase 3 analytics retain their previous semantics.
Do not mix the two event clocks in comparisons.

`lab_markouts(..., as_of_records=k)` evaluates an occurred prefix. It registers the
state at each first occurrence of a new public-event index. Private events and
no-action decisions do not advance that index; a no-action final record cannot
retroactively replace a maturity state. Public midpoint and debug latent references
are separate. Unavailable/pending units are excluded from means and their coverage
is reported. No markout feeds the cash account.

## Replay, comparison and teaching

Lab journal schema 1 stores both the saved background events and every maker
request, plan, cancellation, placement, report, account snapshot and fill. Rational
numbers are encoded as exact strings; JSON booleans cannot stand in for numbers.

`ReplayMarketEnvironment` verifies saved background events and informed decisions
against the book as it exists at that moment, without new RNG draws. The lab
interleaves recorded maker requests. Automatic-policy requests are recomputed from
then-current public inputs; manual requests are replayed as explicit instructions.
Every resulting record must match. Source versions are retained as provenance.
Replay proves consistency, not authenticity or the probability of random samples.

The small comparison function runs fixed and inventory-aware policies using the
same exogenous named streams for each seed and checks their complete signatures,
including event kinds. Policies may change public prices and later decisions.
It retains every paired run and reports simple means and markout coverage. There
is no parameter optimiser, research grid, performance leaderboard or Phase 5 engine.

The CLI teaching helper is a small deterministic state machine: a first wrong
prediction gets a hint, a second attempt is recorded, and the explanation is delayed
until after the next market interval. Its scenarios are labelled hypothetical.
Scripted smoke-test answers are not recorded as Arvind's learning evidence.

## Practical limits

Each event retains full immutable book snapshots. Exact account checks scan prior
maker fills; running snapshots therefore cost increasing work as a session grows.
FIFO processing itself is proportional to the lots closed. Queue ordering remains
heap-based, while book complexity is unchanged. This favours short inspectable
sessions and modest comparisons over high-volume execution. Profile before Phase 5.

Python interface boundaries are not a sandbox for hostile code. Full observer
objects, journals and simulation seeds must not be passed to untrusted strategies.
