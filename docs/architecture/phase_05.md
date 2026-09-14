# Phase 5 architecture — reusable synthetic research

> Historical phase record. Current core conventions and release status are in the root README, ASSUMPTIONS and Phase 11 release report. Test counts and runtime labels below describe this phase.


The [pre-experiment contract](phase_05_design.md) fixes the hypotheses, seed pools,
sample sizes and baseline parameters. The [maths lesson](../maths/phase_05_research.md)
explains the estimands and assumptions. No Phase 6 manual trading application has
been added. Directional trading, options and later portfolio labs can implement
the same research adapter protocol while using the existing market infrastructure.

## Boundaries

| Component | Responsibility |
| --- | --- |
| `research/models.py` | Generic validated experiment design, named JSON configurations, adapter protocol, scalar outcomes and provenance fingerprints |
| `research/seeds.py` | Stable seed addresses from root, pool and index; disjoint development/evaluation namespaces |
| `research/engine.py` | Register before execution, run every requested session, retain failures, analyse complete experiments, save evidence |
| `research/registry.py` | Locked append-only evaluation-access audit; warn on previously exposed seeds |
| `research/statistics.py` | Quantiles, sample moments, t intervals/tests, generic percentile bootstrap, paired differences, covariance/correlation and tails |
| `research/analysis.py` | Per-session distributions, caller-selected relationships, primary outcome inference and deterministic extreme selection |
| `research/sweeps.py` | Change exactly one nested configuration field across variants; preserve the base config |
| `research/adapters/maker.py` | Convert the existing maker lab into public scalar outcomes; stream diagnostics and markout maturities |
| `research/adapters/control.py` | Known equal-skill Gaussian control proving that the engine does not require an order book or market maker |
| `research/replay.py` | Verify saved seed/config metrics and event fingerprint against full regeneration, then existing journal replay |
| `research/reporting.py` | Markdown distributions, shared-bin histograms, empirical CDFs and explicit missing coverage |
| `research/lessons.py` | Prediction/hint/retry, sample-size prefixes, selection control and significance examples |
| `research/performance.py` | cProfile and traced-memory measurements with full/batch equivalence assertions |
| `research/cli.py` | Discoverable comparison, sweep, inspection, extreme replay and teaching commands |

The generic engine imports no maker, exchange, instrument, position or strategy
class. The adapter protocol requires `validate`, `environment_key`, `run` and
`metric_units`. A run returns named finite scalar metrics (or explicit missing),
coverage, an exogenous fingerprint and a trajectory fingerprint. Optional full
evidence belongs to the adapter, not the generic experiment record. Named
correlations and the primary metric belong to the experiment specification.

## Seed architecture and pairing

SHA-256 over a versioned root/name/index tuple derives a session integer. Development
seeds are even and evaluation seeds odd, guaranteeing pool disjointness even in
the event of a hash collision. Within-pool duplicates are checked before execution.
The same root/pool/start/count regenerates the same ordered addresses. Extending
the count preserves its prefix. Strategy names do not enter session seed derivation:
variants intentionally share a seed at each address. Bootstrap namespaces are
separate and use NumPy PCG64 with the precise library version recorded.

Within a market, existing named `RandomStreams` separately control latent shocks,
each trader's arrivals, noise/liquidity decisions and informed signal errors. No
global RNG is used. The streaming observer performs no draws. Adding an unrelated
draw to signals cannot alter arrival or latent streams; it can legitimately change
informed decisions and later endogenous public prices.

For an identical market configuration, the adapter hashes arrival time, scheduling
sequence/kind, latent before/after and current noisy signal. All paired variants
must match these hashes. Trade and book differences are expected. Market-parameter
sweeps can change exogenous paths; they keep reproducible seeds but disable the
strict paired-CRN inference flag. This avoids pretending that changed volatility
or arrival intensity produced identical realised weather.

## Lifecycle, failure and evidence

1. Validate the design/configurations and allocate all distinct seeds.
2. Exclusively create an experiment directory and `registration.json` containing
   question, prior hypothesis, exact config, parameters, root/seeds, count,
   simulator/library/platform versions, timestamp and design digest.
3. For evaluation, claim all planned seeds in the exposure registry **before**
   access. Attempts consume exposure even when a run fails. Overlap warns; it is
   recorded in the result. The registry uses a file lock on the supported POSIX host.
4. Execute each address/variant sequentially. Flush one row to `runs.jsonl` after
   each success or failure. Conservation/accounting exceptions are retained as
   failures; no clamping, resampling replacement seeds or deleting losing runs.
5. If every requested run completed, calculate distributions and inference.
   Otherwise mark the experiment incomplete and disable survivor-only inference.
   A stopped process leaves its registration and partial rows; it does not claim
   completion. Automated resume is deliberately not implemented yet.
6. Save `experiment.json` and `summary.md`; plot all observed outcomes. The record
   contains automatic descriptive interpretation and limitations. Further human
   interpretation can be a separate review document referencing the outcome digest.
   The original hypothesis is never overwritten.

`record_digest` detects accidental alteration of the entire record. `outcome_digest`
excludes timestamps and runtime so reproduced outcomes compare exactly. Loading
checks the complete ordered run address set, seed derivation and content digests.
These checks are not digital signatures: a deliberate editor can recompute a hash.
Python/NumPy/SciPy versions are recorded; cross-version RNG/float identity is not
promised. Full regeneration verifies the actual trajectory rather than assuming
seed equality is sufficient.

## Full replay versus lightweight batches

The market environment counts events separately from its retained records so
turning retention off cannot disable the event budget. The maker lab accepts a
record sink and optionally retains records. A lightweight lab cannot return a
fake empty replay result: attempts to access its full history raise explicitly.

The accumulator consumes each transient immutable record. It retains time areas
for inventory/quote spread, counts, turnover, peak/drawdown, the final exact account,
incremental digests, and not-yet-mature markouts indexed by target public event.
At maturity it adds exact weighted sums and coverage counts, then discards that
pending entry. It does not retain book/event histories or access future marks.
Only public events affect public markout maturities and public diagnostics.

Matching, account and conservation checks remain active. The underlying book and
account still retain the state needed for their own correctness checks, including
fills, so batch memory is not constant in session duration. Runtime is dominated
by inspectable repeated accounting reconciliation; no unsafe shortcut was taken.
There is no parallel executor or worker-seed allocator in this phase.

Every completed row has its replay address, complete config through the registered
variant and both fingerprints. Extreme selection sorts by requested metric with
lowest run address breaking ties. Full regeneration must match metrics, coverage
and both fingerprints before the existing lab journal is saved. That full journal
is then replayed through the established matching and accounting checks without RNG.

## Metric conventions and limits

Maker monetary summaries are in GBP using the configured tick size. Exact ledger
fractions remain in the full replay journal; statistics use finite floats.
Distributions are across whole sessions, equally weighted by session. Markout
means within a session are weighted by available execution quantity. The sample
distribution of session markout means therefore differs from a pooled unit-weighted
markout. Per-horizon available/missing/pending units and exact weighted sums remain
in every row; no missing value becomes zero. All requested sessions, including
no-fill sessions, remain in P&L and risk distributions.

The predeclared loss thresholds, practical-effect threshold, sample sizes and
bootstrap count are in the research contract. Confidence intervals do not include
model uncertainty or selection adjustments; exploratory correlation is not causal.
Normal public agent/manual inputs remain unchanged; experiment configs and replay
journals are privileged offline research evidence, not inputs for live decisions.
