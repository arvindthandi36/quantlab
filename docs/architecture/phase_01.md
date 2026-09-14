# Phase 0/1 architecture

> Historical phase record. Current core conventions and release status are in the root README, ASSUMPTIONS and Phase 11 release report. Test counts and runtime labels below describe this phase.


## Responsibilities

```text
src/quantlab/
    domain.py              validated instructions and price units
    randomness.py          deterministic named RNG factory
    orderbook/
        models.py          immutable observations
        _side.py           private sorted prices and FIFO levels
        book.py            matching, cancellation and integrity checks
    demo.py                deterministic demonstration and CLI presentation
tests/
    unit/                  individual economic/engineering rules
    integration/           full demo and generated mixed sequences
    reference_book.py      deliberately different, flat-list test oracle
docs/
    architecture/          software decisions
    maths/                 equations connected to implementation
    learning/              review prompts and verification notes
```

There are no empty agent, risk, derivatives, UI or statistical-test modules. Add
them only when a phase has a real responsibility for them.

## How an order moves

1. Construct a `LimitOrder` or `MarketOrder`. Reject invalid IDs, sides, prices
   and sizes before an instruction can reach the book.
2. `OrderBook.submit` rejects reused IDs and assigns the next arrival sequence.
3. `_match` takes the best opposing price and its first remaining order.
4. Check the incoming limit, if present. If the best price is ineligible, worse
   prices cannot qualify either. Stop.
5. Execute the smaller remaining quantity at the maker's limit. Emit a `Trade`,
   reduce both remainders, and remove the maker only when fully filled.
6. Repeat until the incoming size is exhausted or no eligible maker remains.
7. Rest the remaining limit quantity or cancel the unmet market quantity. Return
   an `ExecutionReport` accounting for every unit of the instruction.

“Maker” means the order already resting. “Taker” means the incoming order consuming
it. A single limit order can act as taker now and maker later if its remainder rests.

## The two views of an order

`LimitOrder` is the immutable original instruction. `RestingOrder` is private
storage holding that instruction, its remaining size and original arrival
sequence. `OrderView` is a frozen copy for consumers. Historical reports and
snapshots never change when later orders execute.

This separation lets a future UI or portfolio module inspect results without
accidentally changing quantities or observing a supposedly historical snapshot mutate.

## Data structures and costs

Each side has ascending `prices` and a dictionary mapping price to an
`OrderedDict[order_id, RestingOrder]`. Lowest ask is `prices[0]`; highest bid is
`prices[-1]`. Ordered dictionaries preserve FIFO and support deleting any ID
without walking or rebuilding a deque. A separate book-wide dictionary indexes
active orders. A used-ID set prevents lifetime ID reuse.

Let N be active orders, L active levels, K matched resting orders, and D levels
removed while matching. Expected dictionary costs assume ordinary hash behaviour.

| Operation | Cost and reason |
| --- | --- |
| Best quote | O(1), access one list endpoint |
| Add to existing level | Expected O(1), append to its ordered dictionary |
| Add a new level | O(L), binary search locates insertion but list elements shift |
| Match K orders | O(K + D·L) worst-case bound; level removal can shift prices |
| Find/cancel an active order | Expected O(1); O(L) if its price level becomes empty |
| Snapshot/depth | O(N + L), copy actual orders and aggregate sizes on access |
| Integrity diagnostic | O(N + L log L), including comparing sorted price indices |

The engine is not marketed as a high-frequency exchange. These costs are explicit
and easy to profile later; a balanced price tree would add dependency/implementation
complexity before the project has a demonstrated performance bottleneck.

## Reproducibility and randomness

Matching has no RNG: the same accepted instruction sequence yields the same
reports and state. IDs and arrival sequences come from deterministic processing,
not UUIDs or wall-clock time.

For Phase 2 preparation, `RandomStreams(seed).create(name)` hashes a versioned
JSON encoding of the root seed and stream name with SHA-256, then seeds a local
`random.Random`. No use of Python's salted `hash()` or the global RNG occurs.
Keep the returned generator to advance a stream; calling `create` again restarts
it. Tests verify stream separation and reproduction across process hash salts.

Named streams help prevent extra noise-trader draws from shifting latent-process
draws. They do not themselves solve counterfactual market-path changes, and the
matching demo does not consume them. Future experiment metadata must retain model
configuration, seed, stream names, simulator and Python versions.

## Failure and observation policy

Invalid instructions raise `TypeError` or `ValueError`. Unknown cancellation
returns `None` and does not change state. Missing quotes/VWAP also return `None`
with an explicit interpretation. The demo prints a reason for unavailable quotes.
No calculation is replaced with a fabricated number.

`check_invariants()` performs an explicit diagnostic scan even under Python's
optimised mode; it is called after each operation in generated tests and the demo.
Normal submissions do not pay for that full scan. A separate test ledger checks
per-order/global conservation; structural checks alone cannot prove it.

No thread safety, event clock, general replay or account ledger is implied.

## Phase 2 preparation: requested strengthening

The engine now runs `verify_conservation` after each fill using measured remainder
changes and again for the full submission. Reports expose measured buyer/seller
totals. Corruption raises `AssertionError`; later submissions and cancellations
raise `RuntimeError` on that failed book. Diagnostic snapshots remain available,
but the instance must be discarded; there is no silent repair.

`orderbook/display.py` formats aggregated depth from immutable snapshots.
`PriceLevel.order_count` counts actual active instructions. Run
`quantlab-demo --expand-orders` for queue detail.

After these additions the then-current suite passed **105 tests** (the original
83 plus 22 conservation/display cases). Phase 2 simulation tests are recorded
separately in its completion report.
