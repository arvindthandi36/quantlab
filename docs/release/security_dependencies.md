# Dependency, security and privacy audit

This is a local single-user application, not an internet-facing service. The supported launcher binds to `127.0.0.1`, validates loopback Host, checks Origin and a per-process token on mutations, serves only fixed assets, and sets a restrictive self-only content policy. There is no broker, market-data API, analytics telemetry, remote tutor or external transmission in the application's default code path. The explicitly requested installation/advisory audit uses package indexes; it does not send learning answers or trading journals.

Learning progress and automatic journals remain in ignored `runs/` directories. Exported complete replay contains private *synthetic* market evidence and should be treated as observer material. Live/replayed public snapshots omit private sources; early-frame export is blocked. Public save/job locations use basenames rather than the user's directory path. Some local development exceptions can contain filesystem details in the terminal; `--debug` is opt-in and tracebacks are not normal browser output.

Inputs are finite, duplicate-key-rejecting JSON with a size/depth cap, followed by schema and domain validation. Assets and routes cannot be selected as arbitrary filesystem paths. Rendered user text uses escaping or text content; UI code does not insert arbitrary uploaded HTML. No pickle or evaluated replay code. Session mutation/read locks protect coherent portfolios, but there is no multi-user authorisation, durable event service, encrypted local store, server-process file lock, TLS or guarantee against a hostile local process/denial of service. Do not expose the port through a proxy or tunnel as a public service.

## Dependencies

| Dependency | Purpose / necessity | Constraints and licence review |
|---|---|---|
| NumPy | Scenario arrays, stable linear algebra and sample calculations; replacing it with handwritten loops reduces clarity/performance. | Runtime >=2,<3. BSD family and bundled permissive notices; installed wheel expression recorded. |
| SciPy | Normal tails, t intervals and constrained optimisation; independent mature numerical implementations. | Runtime >=1.15,<2. BSD-3-Clause plus bundled-library notices. |
| Matplotlib | Exportable research plots and reports. | Runtime >=3.10,<4. Matplotlib licence, recorded from package metadata. |
| pytest | Test discovery and fixtures. | Dev >=8,<10, MIT. |
| Hypothesis | Mixed operations and meaningful generated invariants. | Dev >=6,<7, MPL-2.0. Test tooling; preserve its licence notices if redistributing it. |
| Ruff | Static analysis and formatting. | Dev >=0.12,<1, MIT. |
| setuptools | Isolated package build backend. | Build >=68; only needed when building. Not an application runtime import. |
| pip | Installation tooling, not financial code. | Documented upgrade >=26.2.1,<27 after advisory findings. MIT. |

Transitive numerical/report packages: contourpy (contouring), cycler (plot cycles), fonttools (font handling), kiwisolver (layout), Pillow (image output), python-dateutil/six (date compatibility), pyparsing (plot parsing), packaging (version metadata). Transitive testing packages: iniconfig (test configuration), pluggy (pytest hooks), Pygments (test display), sortedcontainers (Hypothesis support). They are not reimplemented in the standard library; ranges are resolved by their owning dependencies and exact tested versions are recorded in the constraint snapshots and [metadata inventory](phase_11/dependencies.json). The inventory preserves licence expressions; this audit is not a legal compliance certification. No owner-selected open-source licence is invented for QuantLab itself.

The first advisory scan reported 12 advisory rows for pip 25.2, representing six distinct advisory IDs (some aliases duplicated). The installer was upgraded to 26.2.1. The final scan found **no known vulnerabilities** in the queried environment. This is a time-specific database result, not proof of absence or a future guarantee. Raw initial and final audit results are retained. The temporary auditor's dependencies are not installed as QuantLab runtime dependencies.

The procedure follows the [Python Packaging Guide](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) for virtual environments and uses [pip-audit](https://pypi.org/project/pip-audit/), whose advisory source and limitations are documented by its maintainers.

## Repository hygiene

The original worktree had no Git commits. No user index/history was reset or fabricated. A filtered source snapshot is committed in a temporary validation repository, then genuinely cloned for installation. A portable Git bundle can convey that same release source without a remote service. `runs/`, environments, caches, generated wheels/bundles and credential-file patterns are ignored; `.gitignore` is not a secret scanner.

Source, tests, scripts and documentation were scanned for high-confidence private-key/API-token patterns without printing values. No matches were found. Historical local-path text in four reports/profiles was replaced with portable placeholders; financial JSON evidence and its digests were not relabelled. Old tests/counts are explicitly marked as historical, and the root documents describe the current core. The archived phase evidence is deliberately retained (~60 MB before compression), because a complete clone also supports documented reproductions and the legacy replay fixture.
