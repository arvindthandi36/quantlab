# Release asset policy

| Category | Release treatment |
|---|---|
| Source | `src/`, scripts and package configuration; retain readable implementations |
| Documentation | README, guides, assumptions and substantive historical audit reports |
| Test fixtures | Artificial examples and explicit provenance; never describe them as real history |
| Reproducible evidence | Fixed-seed journals, numerical reports, fingerprint manifests and reviewed UI captures |
| User-generated runs | `runs/` is ignored; never included by the release source-export script |
| Local tools/builds | Environments, caches, egg-info, build, dist and release-artifacts are ignored |

Only genuine reviewed screenshots belong under `docs/assets/readme/`. Final videos are not yet
recorded. Place future `hero-demo.gif` there only when it exists; README must not embed broken placeholders.
Original imported datasets and their redistribution rights remain the user's responsibility.

This checkout initially had zero tracked files and no configured remote. The release preparation
uses a controlled source export and a temporary Git repository to verify a fresh clone without
inventing a public URL or changing the user's Git history. Audit documentation is retained.
