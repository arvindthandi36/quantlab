# Contributing to QuantLab

The planned 1.1.0 feature set is frozen. Useful changes fix a demonstrated bug, correct documentation,
improve compatibility or strengthen a meaningful test. Discuss larger model changes before building.

Create a Python environment, install `.[dev]`, then run `python -m pytest -q` and
`ruff check src tests scripts`. Describe the triggering case, resulting behaviour, tests and
assumption changes. Do not change expected financial values just to make a test pass.

Keep financial calculations in Python. Preserve exact accounting, causal information boundaries,
strict journal verification and public/source labels. Avoid new dependencies without a concrete need.
Do not commit personal runs, credentials, imported licensed datasets or local environments.

The [MIT licence](LICENSE) applies. [Feature freeze](FEATURE_FREEZE.md) and
[asset policy](docs/release/ASSET_POLICY.md) describe the release scope.
