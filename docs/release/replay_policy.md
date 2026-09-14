# Version and replay compatibility policy

Core release candidate: **QuantLab 1.0.0**. Schema versions are independent of package versions. Never edit a journal's version to force it through a loader. Checksums detect accidental changes, not an adversary who can recompute them.

| Journal | Recorded metadata | Compatibility contract |
|---|---|---|
| Market | schema 1/2, simulator/Python versions, configuration including seed, all event/order/execution/private evidence | Recorded-event verification replays saved instructions and compares every transition without RNG. Legacy schema 1 cannot contain informed flow. Acceptance means these specific recorded events reconciled, not that a new seeded run matches another runtime. |
| Market making | lab schema 1, simulator/Python versions, market/maker configuration, actions and account/exchange evidence | Recorded-event/action verification compares full records and the strategy's public decision. Older records are evidence verification only; not silently claimed seed regeneration. |
| Manual stock | schema 1, QuantLab/Python versions, scenario/seed, actions, evidence, final public state | Default verifies recorded events. Optional seed regeneration requires exact recorded package/Python versions. Every reconstructed action, account and final state must agree. |
| Options | `quantlab-options-v1`, package/Python versions, contract/model config, seed, commands, stock and option evidence | Exact versions required; regenerate and compare full journal. A 0.9.0 journal is not regenerated under 1.0.0. |
| Risk | `quantlab-risk-v1`, package/Python/NumPy/SciPy versions, account baselines, settings, actions, final/evidence digests | Exact runtime metadata required; reconstruct original baselines and guarded actions. |
| Stat Arb | `quantlab-statarb-v1`, package/Python/NumPy/SciPy versions, process/rules/seed, actions/fingerprints, observed history and evidence | Exact metadata; causal generation and every command/fingerprint plus final journal must match. |
| Research | registration/experiment schema, versions, root/pool/indices/child seeds, variants, all run rows, fingerprints and digests | Verify saved record integrity for reading. `reproduce_run` requires matching package/Python and then exact outcome/fingerprint comparisons; NumPy/SciPy changes can therefore fail verification even when preliminary version gate passes. Use the recorded environment. |

A changed schema needs an explicit migration with invariant tests. A changed financial rule requires a new package/model version; no silent reinterpretation. Older archived results retain their original versions and outcomes. No migration from older option/risk/Stat Arb versions is claimed here.

Live public state never includes the root market seed, private shocks, latent value, informed measurements or future observations. Complete journals are privileged observer records and are exported only after ending, including from the ended replay frame. A user who uploads a complete journal already possesses that private information; visual replay still shows only each historical public frame. Explicit observer reveal is separated from tutoring.

Uploads use finite JSON with duplicate object keys rejected, maximum 25 MB input, and maximum nesting of 64. Journal-specific schemas and financial checks follow parsing. No pickle, `eval`, arbitrary file URL or executable migration is used. Visual replay retains at most 64 MB of serialized frames; the non-capturing Python verifier remains available for larger valid sessions. There is no guarantee against hostile local denial of service.
