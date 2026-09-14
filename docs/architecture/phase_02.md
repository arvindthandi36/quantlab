# Phase 2 architecture

> Historical phase record. Current core conventions and release status are in the root README, ASSUMPTIONS and Phase 11 release report. Test counts and runtime labels below describe this phase.


## Data flow

```text
validated SimulationConfig + five named RNG streams
                ↓
EventQueue: time_us, scheduling sequence, kind
                ↓
MarketSimulation.step()
    ├── latent update → hidden value only
    └── trader arrival → Decision(order, reason)
                             ↓
                       OrderBook.submit
                             ↓
             verified fills + remaining book + report
                ↓
immutable EventRecord → SessionResult → transaction tape
                ↓
human timeline / JSON journal / verified replay
```

The existing order book retains economic matching rules. The simulator decides
when to call it. Presentation modules only read results. No graphical interface,
wall-clock sleeps, live prices or external service are required.

## Clock and event ordering

The queue is a Python `heapq`: schedule/pop cost O(log E) for E queued events.
The market normally has at most three pending events, one per active source.
Scheduled events are ordered by integer elapsed microseconds and then their
scheduling sequence. An event ID identifies its insertion, so its number need
not increase down the chronological timeline. It is not the book's order-arrival
sequence, which counts accepted instructions only.

Initially schedule the first latent update, then noise and liquidity arrivals.
After each event, schedule that source's next occurrence. At equal times, earlier
schedule calls win, including events subsequently inserted for the current time.
Events exactly at the configured horizon execute; the final clock then reaches
the horizon without processing future events. No wall clock is consulted.

A trader arrival includes decision, immediate submission and matching atomically.
All resulting tape entries share that timestamp. We deliberately do not add a
second event for zero-latency submission; doing so would introduce an extra tie
convention before we have a latency model to justify it.

## Information boundaries and price formation

`PublicObservation` contains best bid, best ask, last transaction price and the
configured opening reference. Noise traders receive this record; liquidity traders
need only their random execution need. Neither receives latent value or the queue.

The price anchor uses midpoint only with both sides, then last trade, then opening
reference. Initial latent value and public reference are configured independently.
A test changes the latent path while holding public setup fixed and requires
identical orders and transactions. There is no informed trader in Phase 2.

The simulation begins with an empty book. Noise limits build real depth; liquidity
market orders consume it when available. Noise limits can also cross existing
orders. Latent updates do not generate trades or reprice outstanding instructions.

## Reproducibility versus replay

Regeneration starts a fresh simulator using the same configuration and named RNG
streams. The journal records simulator and Python versions because distribution
sampling implementations may change between runtimes. Streams are named
`market.latent`, `market.noise.arrivals`, `market.noise.decisions`,
`market.liquidity.arrivals`, and `market.liquidity.decisions`.

Replay starts an empty matching engine and submits the **saved instructions**,
without invoking a trader or RNG. Every resulting execution report and complete
book snapshot must match the journal. Clock ordering, value continuity, scheduled
latent updates, horizon completion and quantity conservation are also checked.
Invalid JSON numeric types, nonfinite numbers and unsupported schema versions fail.

The journal includes full configuration, model/runtime versions, microsecond event
times and insertion IDs, before/after latent values, decision reasons, orders,
execution reports and book snapshots. The tape is derived from these reports so
there is no second independent source of transaction truth.

This is mechanical replay, not an exact counterfactual experiment or cryptographic
proof of authenticity. A rewritten but internally consistent history need not
be detectable without regenerating it from its claimed seed and version.

## Failure policy and scope

Bad configuration fails before execution. Nonpositive/nonfinite latent results
abort. Event-budget exhaustion raises instead of returning a truncated successful
run. A simulator that fails mid-event refuses to resume, because its clock or book
may already have changed. Conservation failures similarly poison the affected book.

All events retain complete immutable snapshots. This makes inspection transparent
but costs O(sum of active order counts across events) memory/work. The timeline
caps displayed events and explicitly reports omissions; it does not truncate the
stored journal. This implementation is intended for short teaching/debug sessions.

No informed flow, market-making strategy, adverse-selection analysis, accounts,
P&L, options, machine learning, regimes or additional agents were implemented.

