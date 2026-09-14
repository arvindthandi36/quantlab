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

At the Phase 15 installation gate, this checkout had zero tracked files and no configured remote.
That gate used a controlled source export and a temporary Git repository to verify a fresh local
clone without changing the working project's Git history. The source is now published at
[arvindthandi36/quantlab](https://github.com/arvindthandi36/quantlab). The original audit evidence
is retained as a record of that local-clone validation.
