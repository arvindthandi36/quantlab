# Phase 3 architecture

> Historical phase record. Current core conventions and release status are in the root README, ASSUMPTIONS and Phase 11 release report. Test counts and runtime labels below describe this phase.


Owner: **Arvind Thandi**. The [information contract](../maths/phase_03_information.md)
was defined before implementation. Phase 4 is not started.

## Data flow and authority

```text
observer-owned clock / queue / current latent value
        │
        ├── latent event → change current value; no order, no repricing
        │
        └── informed arrival
              ├── signal service: current value + independent measurement error
              │       ↓ PrivateSignal(time, measurement, stated noise)
              └── PublicObservation(bid, ask, last trade, opening reference)
                      ↓
                 InformedTrader.decide
                 estimate → executable edge → hurdle → one-unit limit or hold
                      ↓ only an order crosses into the matching engine
                 OrderBook.submit → measured conservation → actual executions
                      ↓
                 privileged immutable EventRecord + optional InformedAudit
                      ↓
                SessionResult / observer JSON
                 ├── project_public → separate sanitised public types
                 ├── observer debug → truth, error, estimate, action, execution
                 ├── analyse_markouts(as_of_events=...) → matured diagnostics
                 └── replay → re-evaluate saved signals and verify matching
```

Normal traders retain their Phase 2 interfaces. Noise traders receive four public
fields; liquidity traders receive only a random execution need. Neither is given
the simulator, configuration, RNG seed, private signal, latent value or journal.
The informed decision function receives a public observation and a measurement,
never latent truth or the actual measurement error. Agent inputs contain no queue
or later record. The simulation samples latent updates only when they occur.

The simulator and complete session are trusted observer APIs. These boundaries
prevent accidental information use by these implementations; they are not process
isolation or a security sandbox for arbitrary hostile Python code. A future agent
plugin must not be handed the simulator or access to its memory/files.

## Timing and randomness

Informed arrivals are independent exponential gaps, using the same integer-clock
convention as Phase 2. Initial scheduling order is latent, noise, liquidity,
informed; exact ties follow insertion order. At most four sources are pending.
An informed signal describes current state after earlier processed events at that
time. The decision and one-unit limit submission are atomic. Freshness requires
the signal timestamp to equal the decision timestamp; stale/future signals fail.

Two named streams are added: `market.informed.arrivals` and
`market.informed.signals`. They do not consume latent or background-flow draws.
Changing signal noise therefore preserves arrival times and latent shocks,
although different informed orders can change the book and later public decisions.
Extending the horizon preserves the original run's entire event prefix.

The default informed rate is zero to preserve the established Phase 2 examples.
`--informed` enables one arrival per second in expectation. Rate and signal/cost
parameters are available through `SimulationConfig`. There are no new runtime
dependencies. Version 0.3.0 records Python and simulator versions in journals.

## Public projection

`PublicSession`, `PublicEvent` and `PublicSnapshot` contain public facts without a
back-reference to private state. Order IDs become `order-N`, with N the accepted
order sequence, not the private event sequence. Trade references and FIFO depth
use the same aliases. Public output contains no trader labels, private reasons,
seed, model parameters, latent updates or informed abstentions.

`public_snapshot()` advances its timestamp on a submitted order, or to the declared
session horizon once processing completes. Private events leave the public
snapshot unchanged, including its timestamp. Observer `now_us` and `step()` remain
privileged interfaces. A public client must consume projected events/snapshots,
not forward every observer callback as an observable notification.

Markouts use the internal event count, including private events. Even midpoint
markouts are therefore observer analytics in this phase. A public analytics feed
would first need a public-event or elapsed-time horizon convention.

## Markout records

Each actual execution generates two reference families, midpoint and latent, at
configured increasing event horizons (defaults 1, 5, 20). The sign is the resting
provider's side, derived from the opposite of the execution's aggressor side.
Each result retains trade quantity, price, reference values, initial reference
edge, subsequent signed reference move, maturity and availability status.

For a trade in processed event n, horizon h uses state immediately after event
n+h. Event numbers are one-based processed positions, not scheduling IDs. Multiple
fills from one incoming order share its pre-order reference and event horizon.
The trade's own event does not count as one of its future events.

`as_of_events=k` reads only the first k records. Pending records have no future
reference, future timestamp or markout. A missing midpoint at maturity stays
missing even if it reappears later. References never substitute for one another.
Markouts are per unit in ticks; multiply by tick size for currency per unit, and
by quantity if a total gross reference valuation is explicitly needed. No total
P&L or fee-accounting claim is made.

## Replay and failure policy

JSON schema 2 adds private audits and informed configuration. Schema 1 Phase 2
journals still load, with informed flow disabled. Loading checks clock order,
latent continuity, signal freshness/noise/error reconciliation, the decision
recomputed from the saved signal and then-current public quotes, every execution
report and every book snapshot. No new random draws occur. Markouts are derived
again from the verified records; there is no independent mutable markout ledger.

Replay checks consistency, not authenticity or whether random draws are probable.
A forged, internally consistent signal could pass; regeneration from the recorded
seed/runtime is a separate check. Unexpected numeric states raise. The existing
failed-book/failed-simulator rules remain in force. There is no silent repair.

The estimate is O(1). Markout analysis is O(E + TH) for E events, T executions and
H horizons (two reference families). Complete book snapshots still dominate
storage for long runs. Public projection copies visible snapshots to enforce the
boundary; the implementation favours inspection over high-volume performance.

## Verification map

- `test_informed.py`: signal construction, exact belief examples, threshold/cost
  decisions, both directions, missing quotes, freshness and invalid parameters.
- `test_informed_market.py`: full simulation/replay/conservation, horizon-prefix
  causality, independent streams, secret-free projections and private-timing guards.
- `test_markouts.py`: both signs, spread decomposition, missing/pending references,
  exact maturity, prefix-only access and multiple executions in one event.
- `test_information.py`: signal moments, belief calibration under its assumed prior,
  information quality, and selection in independent controlled stochastic trials.
- All existing matching, cancellation, generated-sequence and market tests remain.
