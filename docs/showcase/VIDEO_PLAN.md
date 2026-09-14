# External video plan

No external video or GIF is recorded by this release preparation. Use the actual 1.1.0 UI,
Phase 14 named states and [capture plan](CAPTURE_PLAN.md). Keep all source labels and limitations.
Record with a temporary learning profile, avoid personal journals, and never count rehearsal as mastery.

| Video | Duration | Shot sequence | Narration focus | Key state / honest limit |
|---|---|---|---|---|
| 1 · Hero | 60–90 s | Home → order fill → option hedge → VaR/ES → pair residual → winner distribution → Explain | What QuantLab is; one observable decision in each lab | [Hero narration](HERO_NARRATION.md); synthetic evidence, no alpha claim |
| 2 · Technical overview | 3–5 min | How it works → FIFO → ledger → private/public boundary → Greeks/risk → causal pairs → registration/replay | Why event-driven, exact matching, separated information and research discipline | [Technical outline](TECHNICAL_NARRATION.md); production limitations at the end |
| 3 · An order becomes a trade | 2–3 min | `order-before-submit` → prediction → `order-after-multifill` → Explain VWAP | Cheapest asks then FIFO; finite depth changes average cost | Actual fills 3/4/3, VWAP £100.023, fee £0.01; public mark is not liquidation |
| 4 · Options / delta hedging | 3–4 min | Buy call → `delta-before-hedge` → full/partial choice → `delta-after-hedge` → market move → volatility shock | Multiplier, signed delta, gamma, residual vega | Full sells 51; partial sells 26. BSM, whole units and costs remain assumptions |
| 5 · Risk / VaR / ES / stress | 2–3 min | `var-vs-es-tail` → tail chart → Risk stress tab → full repricing | Quantile versus average tail; stress is hypothetical | VaR 10 for both, ES 12/48. No regulatory compliance claim |
| 6 · Stat Arb / model failure | 3–4 min | `correlation-vs-residual` → regression → past-only z → relationship breakdown | Correlation does not establish mean reversion; execution creates leg risk | Controlled synthetic processes; no claim of real-world cointegration |
| 7 · Research / winner's curse | 2–3 min | All 50 development means → `winner-before-test` → `winner-after-test` → assumptions | Lock before untouched evaluation; publish selection procedure | variant-32 mean 0.277506 → 0.047892. It deteriorates but stays positive |

## Recording procedure

1. Start the release server in a disposable run directory with a separate `--learning-path`.
2. Open the selected demo and retain its declared fixed seed. Do not search for better outcomes.
3. Use Quick or explicit showcase capture; enter Recording mode and optional larger text.
4. Rehearse before recording. A named state includes the selected genuine branch, not just a picture.
5. Show the disclosure when observer information is intentionally revealed after the session ends.
6. Compare the visible numbers to the exported Markdown script. Record the product/core versions.
7. Place reviewed assets in `docs/assets/readme/`; update README only once real files exist.

Historical shots must retain **SIMULATED HISTORICAL EXECUTION** and **ARTIFICIAL FIXTURE** for the
bundled data. Do not imply reconstructed fills actually occurred. Video editing must not remove
these labels or splice different branches into one continuous account.
