# QuantLab 1.1.0 · Final product release report

Release owner: **Arvind Thandi**. Scope: Phase 15 only. No new financial model, strategy, asset class or research method. Final verification status is recorded below and in the linked evidence.

## 1. FINAL BUILD REPORT

QuantLab now has one shared product identity, navigation and visual system, a Home page, a system overview, a market-environment guide, a limitations page, a product tour and a project-defence entry. Existing trading, derivatives, risk, research and learning workflows remain the calculation authority. Presentation adapters never calculate financial results.

The Home page explains the purpose and offers Start trading, Watch a guided demo, Explore the labs and Learn how QuantLab works. Six recommended journeys open existing Phase 14 demos. The existing `/` trading route remains compatible; the launcher advertises `/home`.

Release preparation includes MIT licensing, a rewritten README, architecture documentation, real screenshots, video/narration plans, reviewer routes and a feature-freeze policy. External publication and video recording are separate actions.

## 2. FINAL TEST REPORT

**1,933 passed in 120.81 seconds. Zero failures and zero skipped cases.** This includes all 1,910 baseline cases plus 23 release cases. The final full-run log is [here](phase_15/final_results.txt). Ruff also passes. The independent fresh-clone suite passed the same 1,933 cases in 148.47 seconds.

The baseline was **1,910 passed**. All original test identifiers and original test files are preserved. The 23 new cases check product routes and isolation, real navigation targets, hidden-scenario separation, asset security, package/licence metadata, the frozen source manifest, eight flagship fingerprints, recording presentation, installation instructions and screenshot/document integrity. Counts reflect pytest cases, including parametrised cases; they are not a marketing measure.

Evidence: [baseline run](phase_15/baseline_results.txt), [collected final cases](phase_15/final_tests.txt), [verification](phase_15/verification.json), [fresh installation](phase_15/clean_install.json). Browser interaction checks supplement these tests; they are not counted as pytest cases. The first final run found a JPEG/PNG extension mismatch in the new capture check (1 failed, 1,932 passed); extensions and references were corrected without changing pixels or weakening the financial tests. [Initial failure](phase_15/initial_asset_failure.txt).

## 3. CORE FINGERPRINT REPORT

The complete pre/post financial workflow output is identical. Its SHA-256 fingerprint is:

```
fa0e7d6462d735408917806704a47204eb1ca8b1ef84285f3e9ca49680b58882
```

All eight flagship engine-result fingerprints match the approved Phase 14 evidence. No financial engine file changed. The only existing source changes are the HTTP presentation adapter, shared navigation and demo entry script. [Full comparison](phase_15/verification.json).

## 4. FINAL VERSION

**QuantLab product/package 1.1.0; financial replay core 1.0.0.** Core 1.0.0 already represented validated financial completion. The product release adds explainability, environments, guided demonstrations and presentation. Keeping the replay identifier avoids invalidating exact historical journals without a financial change. `quantlab --version` prints both; the legacy `python -m quantlab --version` still reports the core identifier. [Version policy](VERSIONING.md).

## 5. HOW TO RUN QUANTLAB

From the downloaded or cloned source directory:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
quantlab --version
quantlab serve
```

Open the `/home` address printed by the launcher. To choose a free alternative port, use `quantlab serve --port 8772`. The browser is not automatically opened. For development tests install `.[dev]` and run `python -m pytest -q`. No remote repository URL is invented.

## 6. HOME PAGE WALKTHROUGH

The opening view states what the laboratory does and identifies simulated execution. Its mechanism diagram explains why the hidden value does not directly set the last transaction. Eight lab cards expose the main capabilities. The recommended order demo comes first, followed by synthetic price formation, hedging, tails, pairs and research selection. An environment table and limitations link make the evidence boundaries visible before a visitor starts.

[Actual Home capture](../assets/readme/home.jpg) · [phone capture](../assets/readme/home-mobile.jpg).

## 7. FINAL NAVIGATION

| Group | Destinations |
|---|---|
| Home | Product overview |
| Trade | Trading Simulator, market making, options, Stat Arb |
| Markets | Environment guide and existing environment chooser |
| Risk | Portfolio, VaR/ES, stress and optimisation panels |
| Research | Research and existing options/risk/Stat Arb experiment panels |
| Learn | Concepts, demos, saved-session teaching, progress, interview and defence |
| About | System overview, assumptions/limitations and product tour |

Existing panels are linked directly rather than duplicated. Shared navigation preserves each lab's actual controls and view selectors. Keyboard users have a skip link, focus outlines and Escape handling for navigation menus. Forty route/width checks covered desktop, laptop, tablet and phone; one demo table overflow was corrected. Sampled core text/button palette contrasts range from 5.60:1 to 12.14:1. This is sampled QA, not certification. [Browser evidence](phase_15/browser_qa.json).

## 8. FINAL TRADING-SIM WALKTHROUGH

In the browser, a paused seed-42 session accepted a manual BUY 6 MARKET. The existing book filled it, producing position 6, VWAP £100.01667, cash £9,399.894 and fees £0.006. No scripted display value was substituted for execution.

The reproducible order showcase uses a separate controlled BUY 10: 3 units at £100.01, 4 at £100.02 and 3 at £100.04. Quantity sums to 10. Total execution cost before fees is £1,000.23; dividing by 10 gives **£100.023 VWAP**. With £0.01 fees, cash moves from £10,000 to £8,999.76. Five units remain at the last ask. The public mark produces −£0.09 marked P&L; a mark is a valuation convention, not a liquidation promise.

The user can buy/sell, set market/limit, size and limit price, cancel a resting order, inspect depth/FIFO evidence and connect fills to accounting. [Order image](../assets/readme/order-vwap.jpg).

## 9. MARKET-ENVIRONMENT WALKTHROUGH

Synthetic markets combine a stochastic latent process, participants with different information/objectives, orders and FIFO matching. Prices come from executions. Ordinary agents do not receive hidden value.

Historical replay reveals recorded observations supplied by the user; the bundled fixture is artificial. User fills and P&L are simulated under documented rules. OHLCV observations do not reveal a real queue, fill probability or the real-world cause of a price move.

Scenarios create a controlled synthetic regime. A hidden regime remains hidden until an explicit ended-session reveal. The release's editorial pages are static: opening Home or limitations cannot reveal or mutate live private state. [Environment table](../architecture/OVERVIEW.md) and in-app Markets guide explain these distinctions.

## 10. GUIDED-DEMOS WALKTHROUGH

Home's first demo enters Quick mode through the existing command interface. The catalogue retains 58 topics and eight flagships. Learn, Quant and Interview remain available. Named capture states deliberately disable mastery credit. Recording mode hides navigation clutter while retaining source badges, evidence labels and limitations in the document. It records no video.

A recommended sequence is order → synthetic price formation → delta hedge → VaR/ES → correlation/residual → winner's curse. [Capture plan](../showcase/CAPTURE_PLAN.md).

## 11. EXPLAINABILITY WALKTHROUGH

Explain from the order result shows the selected demo context, the actual 3/4/3 fills and their VWAP. It connects the definition, reason for change, inputs, dependencies, mathematics, example and use. The presentation layer neither recomputes nor guesses an explanation from hidden state.

Live quiz evidence, replay practice and showcase activity remain separate. The release screenshots use a disposable QA profile with zero graded answers; they do not fabricate Arvind's mastery. [Explain image](../assets/readme/explain-mode.jpg).

## 12. README WALKTHROUGH

The README introduces purpose, capabilities, an actual Home image, all market environments, user order entry and the latent-to-transaction mechanism. It documents microstructure, options, risk, Stat Arb and research discipline, with four verified examples. Architecture, correctness, reproducibility, installation, limitations and reviewer links follow. Video references are explicit future recording plans, not fabricated external links. [README](../../README.md).

## 13. SCREENSHOT / CAPTURE ASSET REPORT

Fifteen JPEGs cover every requested subject plus phone Home. They are native screenshots of the actual local application, using deterministic named states where available. No generated mockups or pixel edits were used. A faulty full-page capture method was discarded; final files use direct viewport captures. The gallery records exact state, dimensions and SHA-256.

[Gallery](../assets/readme/README.md) · [manifest](../assets/readme/captures.json) · [capture plan](../showcase/CAPTURE_PLAN.md). Private signals, user run histories and genuine learner answers are excluded. A viewport image may require the full page to inspect limitations below the fold; recording mode does not remove those sections.

## 14. VIDEO PLAN

Seven plans cover the 60–90 second hero, 3–5 minute technical overview, order execution, hedging, risk, pairs failure and research selection. Each specifies shots, duration, actual states, narration and limitations. No external video has been recorded or published. [Video plan](../showcase/VIDEO_PLAN.md) · [technical narration](../showcase/TECHNICAL_NARRATION.md).

## 15. HERO VIDEO NARRATION

The approximately 170-word draft begins: “QuantLab is an event-driven quantitative finance laboratory. I built it to understand how quantitative models translate into actual trading and risk decisions.” It follows manual orders, hidden value versus transactions, executed hedges, risk, pairs, research and Explain, ending with the model's limits. It is written for Arvind to adapt and speak naturally. [Complete narration](../showcase/HERO_NARRATION.md).

## 16. RECRUITER FAST PATH

Spend 3–5 minutes on README → order → hedge → VaR/ES → winner's curse → architecture → limitations. Each stop identifies the technical property demonstrated, rather than asking the visitor to infer it from a dashboard. [Recruiter walkthrough](../showcase/RECRUITER_WALKTHROUGH.md).

## 17. TECHNICAL REVIEWER FAST PATH

The reviewer guide points directly to matching, accounting, agents/simulation, derivatives, portfolio risk, research, Stat Arb and invariant tests. It recommends tracing one fill into cash and position before reading broader abstractions. [Technical walkthrough](../showcase/TECHNICAL_WALKTHROUGH.md) · [architecture](../architecture/OVERVIEW.md).

## 18. PROJECT-DEFENCE GUIDE

The guide gives short technical points and deeper references for ticks, event ordering, private information, adverse selection, common random numbers, evaluation discipline, hedging risk, tail risk, pairs assumptions and historical execution. It distinguishes what the implementation demonstrates from what Arvind still needs to practise explaining. It is not a set of memorised claims. [Project defence](../showcase/PROJECT_DEFENCE.md).

## 19. CLEAN-INSTALL REPORT

**Passed on macOS / Python 3.14.0.** The fresh clone passed all **1,933 tests in 148.47 seconds**, Ruff and dependency checks. The installed product reports 1.1.0, Arvind Thandi and MIT; imports resolve to the new environment’s site-packages. All 16 major page/asset probes returned HTTP 200. Final code, tests, verification scripts, package configuration and licence match the tested clone; later changes only complete documentation/evidence.

The workspace currently has no tracked files or configured remote. Validation therefore exports the intended release source into a temporary Git repository and performs a genuine fresh local clone. It leaves the real workspace index untouched. A new virtual environment installs the package non-editably with the documented `pip install .`; development dependencies are added only for tests. Downloaded dependency wheels are reused in an offline wheelhouse, not inherited from the development environment.

The checks verify installed package origin, MIT metadata/file, console version, dependency consistency, full tests, lint, core output and all major HTTP routes from outside the checkout. The evidence does not claim a public GitHub clone, Windows/Linux installation or a Python-version matrix. [Machine-readable report](phase_15/clean_install.json).

## 20. REPOSITORY HYGIENE REPORT

A controlled release export contains source, documentation, fixtures and reproducible evidence. `.gitignore` excludes user runs, environments, caches, logs, generated packages and local release artifacts. Useful earlier audit reports remain. Existing personal run history is left untouched and excluded from the release. Broken older architecture links were corrected without deleting their substantive content. [Asset policy](ASSET_POLICY.md).

The existing editable development installation was refreshed so its console launcher also reports 1.1.0. No remote repository setting, commit, tag or publication was performed in the working project. Temporary validation commits are confined to the disposable clone source.

## 21. SECURITY / SECRET SCAN

**No credential-pattern or unnecessary absolute-user-path findings; no broken relative document file links.** User-generated runs are excluded by the release export policy.

The scan checks release text for common API/token patterns, private-key blocks, credentials embedded in URLs and unnecessary absolute user paths, and checks relative document file links. It reports locations rather than candidate secret values. This is a heuristic source scan, not proof that all possible secrets or vulnerabilities are absent. Existing loopback/Host/input protections remain tested. [Scan evidence](phase_15/source_audit.json) · [local security scope](../../SECURITY.md).

## 22. LIMITATIONS PAGE SUMMARY

The in-app page and documentation cover market simulation, historical replay, options, risk, Stat Arb, research, execution and security/deployment. Each explains what is simplified, why, where the model can fail and how a production system differs. Examples include uncalibrated agents, close-based historical execution, Black–Scholes assumptions, uncertain tail estimates, relationship breaks and local single-user deployment. [Limitations](../LIMITATIONS.md).

## 23. CHANGELOG SUMMARY

The user-facing changelog distinguishes the financial core 1.0 milestone from the 1.1 product release: explainability, environment distinctions, guided demos and final product presentation. Detailed previous phase audits remain available separately. [Changelog](../../CHANGELOG.md).

## 24. FILES CHANGED

| Area | Files and purpose |
|---|---|
| New product module | `src/quantlab/product/{__init__,cli,content,pages}.py`: identity, launcher, static shared content and pages |
| Existing presentation adapters | `src/quantlab/trading/navigation.py`, `server.py`, `static/demos.js`: shell, editorial routes/assets, demo deep links |
| New visual assets | `static/product.css`, `static/product.js`: common presentation, keyboard menus, text-only currency sign consistency and chart alternatives |
| Package/repository | `pyproject.toml`, `.gitignore`, `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, `FEATURE_FREEZE.md` |
| Main documentation | `README.md`, `CHANGELOG.md`, `ROADMAP.md`, `ASSUMPTIONS.md`, `LEARNING_LOG.md` |
| Architecture/limits | `docs/architecture/OVERVIEW.md`, `docs/LIMITATIONS.md`; link corrections in the earlier assumptions archive |
| Showcase | Capture/video/narration/recruiter/reviewer/defence/GitHub metadata guides in `docs/showcase/` |
| Genuine captures | Fifteen JPEGs, gallery and capture manifest in `docs/assets/readme/` |
| Release evidence | This report, version/asset policies and `docs/release/phase_15/` evidence |
| Verification | `tests/product/test_release.py`, `scripts/release_source.py`, `phase15_verify.py`, `phase15_captures.py`, `phase15_install.py` |

All pre-existing financial modules and all old test files remain byte-for-byte equal to the Phase 15 baseline. [Frozen-file comparison](phase_15/verification.json).

## 25. FINAL RED TEAM

- Passing tests and identical fingerprints protect known behaviour; they do not establish market realism, profitable strategies or complete correctness.
- The release is a local single-user laboratory. It has no production exchange infrastructure, multi-user deployment hardening or operational service guarantee.
- The synthetic mechanisms are deliberately simplified and uncalibrated. Historical bars cannot establish actual historical fills or hidden causes.
- The dependency ranges remain supported policy; one clean macOS/Python 3.14 installation is evidence for that environment only. Strict floating-point replay still depends on the numerical stack.
- Product and financial-core versions intentionally differ; reviewers must use the documented version meanings.
- Browser QA samples major workflows at four sizes. It is not formal WCAG certification, exhaustive assistive-technology testing or a full browser/platform matrix. The product has a light theme; no dark-theme support is claimed.
- Dense technical tables use contained scrolling on small screens. Full analytical work is easier on a larger display.
- Secret scanning is heuristic. Public publication, external videos and review of a real remote repository remain separate tasks.
- A showcase completion or approved implementation phase is not evidence of learner mastery. Arvind's later explanation and practice remain essential.

## 26. FEATURE FREEZE CONFIRMATION

**QuantLab 1.1.0 is feature frozen as of 13 September 2026.** All final gates have passed.

Future changes default to bug fixes, documentation, compatibility and meaningful tests. Optional research directions are explicitly not release commitments. No Phase 16 or other implementation phase has begun. [Feature freeze](../../FEATURE_FREEZE.md).

## 27. 3-QUESTION ARVIND CHECK

1. Why can hidden latent value, the best ask and the last transaction all be different at the same moment?
2. What does an identical replay fingerprint establish, and what does it fail to establish about a strategy?
3. If an order fills during historical replay, why can we not say that it would have filled in the real historical market?
