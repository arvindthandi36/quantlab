# Technical reviewer fast path

Start with [the system overview](../architecture/OVERVIEW.md) and [units/invariants](../conventions.md).
Then follow one instruction into an execution, its ledger and its verifier.

| Inspect | Source | What to challenge |
|---|---|---|
| Matching | [book](../../src/quantlab/orderbook/book.py), [conservation](../../src/quantlab/orderbook/conservation.py) | Price/time priority, partial fills, no silent repair |
| Accounting | [accounting](../../src/quantlab/portfolio/accounting.py), [manual session](../../src/quantlab/trading/session.py) | Reservations, exact flows, long/short lots, independent identities |
| Stochastic market | [simulation](../../src/quantlab/market/simulation.py), [public projection](../../src/quantlab/market/public.py), [signals](../../src/quantlab/market/signals.py) | Event ordering, RNG separation, observation access |
| Derivatives | [pricing](../../src/quantlab/options/pricing.py), [IV](../../src/quantlab/options/iv.py), [options session](../../src/quantlab/options/session.py) | Bounds, Greeks, solver fallback, multipliers, executed hedges |
| Risk | [covariance](../../src/quantlab/risk/covariance.py), [metrics](../../src/quantlab/risk/metrics.py), [session](../../src/quantlab/risk/session.py) | PSD checks, tail convention, full repricing, ledger integration |
| Research | [engine](../../src/quantlab/research/engine.py), [statistics](../../src/quantlab/research/statistics.py) | Registration, pooling, pairing, failure retention, evaluation reuse |
| Stat Arb | [statistics](../../src/quantlab/statarb/statistics.py), [session](../../src/quantlab/statarb/session.py) | Past-only data, model vintages, leg risk, costs |
| Replay | [stock verifier](../../src/quantlab/trading/replay.py), [environment layer](../../src/quantlab/environments), [demo replay](../../src/quantlab/demos/replays.py) | Version gates, corruption checks, action/frame alignment, source retention |
| Teaching | [Explain](../../src/quantlab/explainability), [tutor](../../src/quantlab/tutor), [demos](../../src/quantlab/demos) | Public-state projection, future leakage, mastery isolation |
| Tests | [conservation](../../tests/unit/test_conservation.py), [core workflows](../../tests/core_workflows.py), [demos](../../tests/demos), [product](../../tests/product) | Generated sequences, cross-lab behaviour, mutation canaries, local HTTP |

Run the [installation/test commands](../../README.md#installation). Inspect the frozen source and
before/after fingerprints in [release evidence](../release/phase_15/verification.json).
A passing statistical test does not calibrate a model. Browser polish does not alter a numerical
claim. Review [limitations](../LIMITATIONS.md) and [versioning](../release/VERSIONING.md) together.
