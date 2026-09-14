# Information boundaries

| Surface | Permitted evidence | Excluded evidence |
|---|---|---|
| Built-in before checkpoint | Selected public state, declared demo setup, instruction, prospective question | Later fills/P&L, unobserved signal, latent truth, expected answer |
| Built-in result | That checkpoint's actual next result and its before state | Other future results and private observer state |
| Saved replay before | Verified public predecessor, user instruction | Next-state tags, outcome-based topic/title, final summary, source digest/configuration |
| Saved replay result | Verified next command-boundary state | Unreached horizons, later outcomes, hidden model truth |
| Explicit ended hindsight | Completed model/configuration evidence when the source provides it | New grading eligibility or claims the user knew it earlier |
| Explain | Exactly the selected public point and permitted predecessor | Personal live account fallback, later frames, private demo payload |

Built-in deterministic seeds are declared configurations; this is a cooperative educational
boundary, not a cryptographic challenge. A user controlling the local code can regenerate a
built-in path. Hidden scenario configuration is withheld from its normal presentation. Saved
journals can contain private seeds/evidence; importing one does not authorize displaying that
private content before the explicit hindsight gate.

The server may have already prepared later built-in evidence. The browser receives only the
selected point. Tests replace future results/private payloads with canaries and require the
entire before response and Explain response to remain unchanged. Result fingerprints and
full scripts are withheld until recap or explicit showcase capture entry.

## Evidence types

Use the Phase 12 source distinctions: **CALCULATION**, **SYNTHETIC MODEL FACT**,
**HISTORICAL OBSERVATION**, **SIMULATED EXECUTION**, **MODEL ASSUMPTION**, and
**REAL-FINANCE CONTEXT**. Phase 13's more specific artificial-fixture and public-synthetic labels
remain valid. “Historical” describes the replay adapter, not a claim that the fixture is real data.
Every historical demo adds **SIMULATED HISTORICAL EXECUTION** to its visible source badge.

Historical prices establish recorded movement, not hidden cause. No order-book depth, queue,
informed flow, option chain or historical execution certainty is inferred from OHLCV.

## Mastery boundaries

The existing Question validator and Progress.grade own conceptual grading. Only eligible Learn
answers are sent to that grader. Hint/retry rules, explicit answer reveal, disabled tutor and
known-answer tracking apply. Showcase, Quick, Quant, Interview, saved replay and previously
revealed answers remain practice. Demo activity lives in a separate `*-demos.json` file beside
an explicitly configured learning profile. No market RNG is consumed by questions or grading.

## Failures

Corrupt/version-incompatible journals and mismatched source data fail before replacing current
presentation state. Engine rejections are not repaired. Invalid answers do not count as attempts.
A progress-file write failure is reported without concealing or changing a financial result.
