# Phase 0/1 build and verification report

> Historical phase record. Current core conventions and release status are in the root README, ASSUMPTIONS and Phase 11 release report. Test counts and runtime labels below describe this phase.


10 September 2026. Project owner: **Arvind Thandi**. Phase 2 has not started.

Historical report of the initial Phase 1 delivery. Arvind subsequently authorised
Phase 2. The matching/display additions passed 105 tests before Phase 2 test
completion. The captured Phase 1 demo has been refreshed to the aggregate display;
its fills and quantity totals are unchanged. Current results are in
[the Phase 2 report](phase_02_report.md).

## Build report

Created an installable, typed Python package with exact price units, validated
limit/market instructions, deterministic named RNG streams, a price-time matching
engine, cancellation, partial fills, immutable observations and a runnable demo.
Depth, quotes and executed volume derive entirely from orders and fills.

Added pytest, Hypothesis and Ruff configuration, a pinned development-dependency
snapshot, architecture/maths documentation, a roadmap, assumptions, changelog and
learning log. No empty future-feature modules or UI infrastructure were added.

## Test report

Verified on **Python 3.14.0, macOS**, using pytest 9.1.1, Hypothesis 6.168.0 and
Ruff 0.16.6. The engine uses only the Python standard library.

| Check | Result / scope |
| --- | --- |
| `venv/bin/python -m pytest` | 83 passed; no skipped or expected-failure tests |
| Matching unit tests | Both sides; price then FIFO; resting-price execution; equal-price crossing; limit bounds; partial fills; cancellation at each queue position; market shortages; IDs; quotes; immutable observations |
| Input and numerical tests | Invalid types, bools, zero/negative sizes/prices, NaN/infinity, off-grid values, exact decimal conversion, low Decimal precision, half-tick midpoints |
| RNG unit tests | Same seed/name reproduces; distinct streams; no global-state mutation; independence from Python process hash salt; invalid seed/name rejection |
| Generated integration test | 200 generated sequences, each up to 100 mixed actions; compare trades/state to separate flat-list matcher; check structural and per-order/global conservation invariants after every action |
| Demo integration tests | Exact programmatic reproduction, real CLI output, JSON agreement between module and installed console entry points, execution from outside the repository |
| `venv/bin/ruff check .` | Passed |
| `venv/bin/ruff format --check .` | Passed |
| `venv/bin/python -m pip check` | No broken requirements |
| `venv/bin/quantlab-demo` | Priority, book structure and session quantity checks passed |

The generated-sequence test is one collected pytest test, not 200 separate pytest
tests. It is property-based verification of deterministic mechanics, **not** a
statistical confidence claim. It shares input records with the engine but no
production matching/storage/eligibility helper. The ledger additionally verifies
each order's original size against its executions, cancellations and active remainder.

The first test invocation could not collect tests because Python skipped an
editable-install `.pth` file marked hidden under `.venv/`. A transient flag change
allowed the unit tests to run but subprocess imports still failed when the flag
reappeared. Recreating the environment as `venv/` resolved both imports and subprocess
entry points. These failures were fixed without skipping tests or adding import
path injection. Initial style findings were formatted/fixed and checked again.

## Demonstration evidence

The [captured CLI output](phase_01_demo.txt) comes from the executable demo.
The first buy fills A for 3 and B for 2 at £100.02. The completed scenario yields:

\[
42 = 2\times18+2+4.
\]

42 counts all accepted buy and sell order-units. Executing 18 units consumes 36
order-units. Two remain bid; four were cancelled (two explicitly, two unmet).
No P&L, returns or strategy performance statistics have been generated.

## Architecture lesson

The immutable instruction states what was requested. The private remainder tracks
what is still available. Sorted prices identify the best offer; FIFO dictionaries
choose who gets filled first at that price. Reports and snapshots copy results
out, allowing future user interfaces and accounting modules to consume them safely.
See [the architecture walkthrough](../architecture/phase_01.md).

## Quant lesson

Limit orders supply conditional liquidity; aggressive instructions consume it.
A limit is a price bound, while the resting quote determines this engine's execution
price. The spread measures the distance between the best available buying and
selling quotes. Depth determines how far an aggressive order must travel through
prices and whether it fills at all. See [the maths lesson](../maths/limit_order_book.md).

## Code lesson

Enums plus runtime validation prevent ambiguous instructions. Frozen dataclasses
separate historical facts from changing remainders. Integer ticks and rational
statistics avoid silent rounding. Combining dictionaries and sorted lists makes
the priority algorithm explicit, with documented performance costs. Tests compare
behaviour and accounting identities rather than merely repeating each implementation step.

## Red team

1. Submitted flow has no agents or value process; the engine establishes matching
   mechanics, not realistic price formation or profitable strategies.
2. No trader identity, cash, inventory, fees or P&L ledger exists; unit conservation
   is not a substitute for economic accounting.
3. Sorted-list level updates and retained used IDs limit scale; serial execution
   excludes concurrency and realistic latency.

## Arvind check

The [five review questions](phase_01_review.md) move from limits and fills through
VWAP, accounting, data structures and model criticism. Arvind's guided starting
prediction is recorded in [LEARNING_LOG.md](../../LEARNING_LOG.md), without awarding
mastery. Answers to this checkpoint and the Phase 1 review are pending.
