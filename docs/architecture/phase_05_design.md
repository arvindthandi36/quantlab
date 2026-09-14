# Phase 5 research contract — recorded before experiments

> Historical phase record. Current core conventions and release status are in the root README, ASSUMPTIONS and Phase 11 release report. Test counts and runtime labels below describe this phase.


11 September 2026. Synthetic quantitative research, not evidence of real-world alpha.

## Hypotheses and frozen design

The Phase 4 maker parameters remain unchanged. No parameter is tuned to win.
Baseline hypothesis: inventory-aware quoting reduces average absolute inventory;
the sign of its mean net P&L advantage is uncertain. Primary outcome is paired
net P&L difference, inventory-aware minus fixed, per complete 30-second session.
The two-sided null is zero mean difference. A £0.05/session difference is the
declared illustrative practical threshold, not a real investment hurdle.

Root seed 20260911. Development and evaluation seeds occupy separate deterministic
namespaces. Development: 1,600 pairs; inspect prefixes 100, 400, 1,600 for sampling
precision and prefix 1,000 for the larger Phase 4 comparison. Final evaluation:
1,000 fresh pairs, run only after the unchanged baseline configuration is frozen.
These counts and hypotheses are fixed before results. No stopping on significance.

Sweep: inventory sensitivity k = 0, 1/4, 1/2, 1, 2 ticks/unit; 100 development
sessions/value, same exogenous weather. Predict lower average absolute inventory
as sensitivity increases; P&L and markout changes are uncertain. This is exploratory,
not selection of an optimum. No sweep result changes the final baseline.

Selection-bias lesson: 50 deliberately equal-mean Gaussian payoff variants,
40 development observations each, then 400 untouched evaluation observations of
the selected winner. This is a labelled statistical control, not fabricated market
execution P&L. True expected payoff is zero for every variant; variant-specific
noise makes selection optimism observable. Keep all development variants and
evaluate the winner selected solely on development data. No seed searching.

## Reusable boundary and evidence

The engine knows experiment designs, named variants, seed plans, scalar metrics,
missing values, coverage, fingerprints and a simulator-adapter protocol. It does
not import a matching engine, maker, asset class or portfolio. Market-making and
Gaussian controls implement adapters. Later directional/options/portfolio adapters
can supply the same contract without building Phase 6 now.

Write an immutable registration JSON before execution. Store every requested run,
including failures; any failure marks the experiment incomplete and disables
inferential summaries rather than selecting survivors. Record all seeds, exact
configuration, versions, timestamps, durations, metrics and replay fingerprints.
Timing/timestamps are provenance and excluded from deterministic outcome digests.
Interpretation is separate from the immutable prediction. No parallel workers yet.

Evaluation access is logged before running, including failed attempts; repeated
overlapping evaluation seeds warn explicitly. A local registry is a guardrail,
not a security boundary or a proof against overfitting.

## Randomness, observational unit and inference

One whole session is one observation; a pair is one unit for differences/bootstrap.
Trade events within a session are not independent Monte Carlo observations.
Preserve named independent streams for latent shocks, each arrival process, trader
decisions and signals. For identical market configurations, verify exogenous
arrival/shock/signal fingerprints match across variants. Endogenous orders, prices
and fills may differ. Market-parameter sweeps reuse base seeds but cannot claim
identical realised exogenous paths when intensities/volatility/noise change.

Report n/available/missing for each metric; sample variance uses n−1; standard
error is s/sqrt(n). Quantiles use linear interpolation at (n−1)p. Mean confidence
intervals use Student t, exact for independent normal outcomes and approximate
for nonnormal outcomes at sufficiently large n. Also report percentile bootstrap
mean intervals with 2,000 resamples and independently derived reproducible seeds.
Bootstrap complete session outcomes or paired differences, never individual fills
and never unpaired sides. Degenerate/insufficient data are explicit, not NaN JSON.

Report paired t statistic, two-sided p-value, difference in pounds and standardised
paired effect; no p-value establishes that a strategy works. Coverage is empirical
Monte Carlo uncertainty conditional on this synthetic model, not model uncertainty.
Correlations are exploratory; constants/missing data have explicit coverage.
No simultaneous-coverage claim for many sweep metrics/intervals.

P&L lower-tail thresholds: below £0, −£0.25, −£0.50 and −£1.00. Include all runs,
worst outcomes and drawdown upper tail. Histograms share bins; ECDF includes ties.
Markouts retain Phase 4 public-event horizons and available/missing/pending units.

## Batch mode and forensics

Profile first. Retain all accounting/conservation checks. Lightweight mode streams
lab records into scalar accumulators and pending markouts; no full event/book
history is retained. Full mode retains the existing replay journal. Both consume
identical random draws and produce identical metrics and event fingerprints.
Save seed/configuration for every run and identify extrema deterministically.
Re-running an extreme in full mode must match its saved metrics/fingerprint before
writing the existing replay journal; then replay that journal with no random draws.
Historical simulator versions must match; no silent cross-version reproduction claim.

Phase 6 remains unimplemented and gated on Arvind's review of Phase 5.
