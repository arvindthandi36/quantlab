# Provenance and source honesty

**No real historical market dataset is bundled in Phase 13.** No redistribution licence
was assumed. The permitted fallback is used: local import plus an unmistakably artificial
fixture for demonstrating the mechanics.

`sample/artificial_fixture.csv` is five invented bars produced by
`scripts/phase13_evidence.py`. Its JSON metadata states `artificial_fixture`; it is original
project test material, with no third-party observations. The browser fixture button generates
a separate 100-bar paired example using the existing seeded synthetic factor process.
Neither is official exchange data, real market history, or evidence of a trading strategy's alpha.

For your own data, obtain it with appropriate local-use rights, check the provider's units,
availability timestamps and adjustment basis, then supply the documented CSV and metadata.
Keep the exact original export and provenance alongside any saved journal. Importing a file
neither certifies its origin nor grants redistribution rights. Dataset source/rights strings
are user claims, not verified licence determinations.

A SHA-256 fingerprint covers **exact CSV text and all metadata**, including source, licence,
timezone, basis, actions and transformations. A whitespace-only file change therefore changes
identity even if parsed prices agree. This conservative choice avoids silent provenance edits.
Replay verifies the original identity, embedded metadata/range, execution version, QuantLab
version and every public state digest; changed source files fail explicitly.

Live provenance shows source, instrument, timezone, frequency, adjustment basis, available
fields and revealed date range. The full range/hash become available only after completion.
Public synthetic/scenario evidence is labelled as such, never a historical observation.
Historical explanations separate recorded prices, paper executions and model calculations.
Artificial observations have their own evidence label.

Imports are local process memory, with no cloud upload, paid-data dependency or live brokerage.
Export before stopping the server. Store licensed user data outside the public repository.
