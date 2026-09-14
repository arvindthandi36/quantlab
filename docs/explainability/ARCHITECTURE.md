# Phase 12 architecture

The QuantLab 1.0 financial engine remains the source of truth. The explanation schema
is separately versioned (`quantlab-explanation-v1`); reading does not change replay
versions, user actions, learning evidence or market RNG.

The adapter accepts only server-owned public snapshots. It projects fields required
by a concept into detached evidence, attaches registry text and dependency links,
and compares two observed states. Changed inputs are observations, not percentages
of causal attribution. No financial formulas are implemented in browser JavaScript.

The server retains bounded explanatory observations outside financial sessions.
Replay explanations read the selected public frame and its predecessor, never the
final session object. A separate explicitly requested, ended-session observer route
may reuse the established tutor observer boundary. Observer facts never enter quiz
inputs. Hypotheticals reconstruct detached inputs and call the approved matching,
pricing, portfolio risk, quoting and causal signal APIs.

The registry, evidence, examples, search, graph and annotated public replay hooks
are reusable by later demonstrations. No historical ingestion or polished Phase 14
demo catalogue is introduced.

## Flow and ownership

```text
Approved Python engine → public lab snapshot → allowlisted evidence projection
                                               ↓
Registry + assumptions → explanation response ← previous projected observation
                                               ↓
                                 panel / map / tutor question

Public snapshot → detached hypothetical inputs → existing core API → amber result
```

`registry.py` owns definitions and relationships. `evidence.py` reads public results;
its only arithmetic beyond presentation differences is delegated to approved APIs
(for example exact execution VWAP). `service.py` owns mode gates, source selection,
bounded observations and the tutor bridge. `sandbox.py` owns detached calls to existing
matching, pricing/Greeks, risk, quote-policy and causal-decision functions. `examples.py`
owns small independent demonstrations. None has permission to book hypothetical results.

The shared server/navigation adapters add HTTP routes and static assets. Existing
financial response dictionaries, replay versions and execution paths retain their
original contract. Failure to retain a new explanation observation is logged without
turning an already executed financial action into a failed response.

## API, version and preparation

- `GET /api/explanations`: registry, labs, four depths, assumption groups and six maps.
- `GET /api/explanations/search?q=...`: bounded keyword/alias search.
- `POST /api/explanations`: `explain`, `what_if`, `quiz`, `example` or `replay_hook`.
- `explain` takes concept, lab, depth, mode, optional selected order/risk method,
  optional explicit observer reveal and source metadata.
- `what_if` takes a named hypothesis and a small input object. It returns a source
  point, assumptions, controlled inputs and detached outputs.
- `replay_hook` returns frame index, public transition type, relevant concept IDs,
  and compact pre/post calculation/execution evidence. Raw private command journals
  are excluded. Legacy frames need not contain the original manual quote request.

POST uses the existing local token, JSON and same-origin protections. Clients cannot
submit a replacement snapshot or research filesystem path. The current source is
`synthetic`; a request claiming `historical` is rejected until such an environment
actually exists. This prevents a future-ready field from relabelling present data.
Schema `quantlab-explanation-v1` is separate from financial core version 1.0.0.

## Budgets and history

At most two detached observations are retained per financial lab. Each is limited
to 2 MB; an oversized observation is discarded rather than truncated or repaired.
Selected-order comparisons retain the latest twenty orders. A new financial session
clears comparability. Manual quote request evidence retains only the current session.
This is a recent-observation comparison cache, not a new persistent financial journal.

Replay compares the selected verified public frame with its immediate predecessor.
All hypothesis inputs are detached. They have no live account, random-stream or
research-store capability. Limits include 10,000 frozen-book orders/units, 2,001
published threshold observations, bounded volatility/correlation and inventory rules.
Risk what-ifs use the fast existing delta-normal API, not new Monte Carlo experiments.

See [information boundaries](INFORMATION_BOUNDARIES.md),
[hypothetical assumptions](WHAT_IF_MODE.md) and the unchanged
[core architecture](../release/architecture.md).
