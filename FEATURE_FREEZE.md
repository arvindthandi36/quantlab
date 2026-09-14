# QuantLab feature freeze

**Product version: 1.1.0. Financial replay core: 1.0.0.**

QuantLab's planned product feature set is frozen. The final release quality gate passed on 13 September 2026: 1,933 tests in the working environment and 1,933 in a fresh local clone, unchanged financial fingerprints and verified installation/routes.
No further implementation phase is started by this release preparation.

Future changes default to:

- Bug fixes with relevant regression evidence.
- Documentation corrections.
- Compatibility updates that preserve or explicitly version replay behavior.
- Meaningful test improvements.
- Clearly justified, separately reviewed future versions.

Do not add unrelated financial features to this release. Preserve accounting and information
boundaries, document changed assumptions, and investigate any changed financial fingerprint.
Publication, tags and external videos remain separate actions.

## Optional future research — not release commitments

Hawkes arrivals, stochastic volatility, execution impact, richer market data, live paper feeds and
advanced factor models could be studied in future versions. Their presence here is not approval
to implement them, a timetable or a claim about present capabilities.

[Release report](docs/release/PHASE15_REPORT.md) · [Version policy](docs/release/VERSIONING.md).
