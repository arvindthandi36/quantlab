# Phase 14 architecture

Phase 14 adds teaching presentation to approved engines. It does not add a financial model.
Core 1.0.0, Phase 12 explanations and Phase 13 environment calculations remain unchanged.

## Narrative and result are different things

A **narrative** specifies an instruction, a question, a concept reference and a reason to inspect
an event. An **engine result** contains actual prices, fills, accounts or statistical calculations.
Narrative text never supplies a replacement price, P&L, option value, VaR or z-score.

Built-in demonstrations prepare a bounded genuine engine run, keep its later evidence on the
server and reveal it checkpoint by checkpoint. “Reveal engine result” advances the presentation
through that run; it is not a live personal-account order ticket. This permits reproducible
capture states and fast playback. The full/partial/no-hedge choice rebuilds a genuine Options
session using that selected policy; it is not a browser interpolation between pictures.

## Components

- `registry.py`: 58 data-driven catalogue records, all eight requested domains and eight flagships.
- `models.py`: `Spec`, `Moment`, `Evidence`, central-concept-backed `Question` construction.
- `build_trading.py`: `TradingSession`, actual FIFO/accounting, noisy informed flow and mature markouts.
- `build_options.py`: actual `OptionsSession`, stock hedge book, pricing curves and safeguarded IV.
- `build_calculations.py`: approved risk examples, shocks, Phase 10 residual/causal models and leg execution.
- `build_research.py`: bounded equal-skill control, Phase 5 selection experiment, summaries and paired analysis.
- `build_environments.py`: original HistoricalSession and ScenarioSession; no alternate execution rule.
- `replays.py`: original journal verification, followed by command-boundary public frames.
- `annotations.py` / `replay_questions.py`: bounded event ranking and prospective public-context questions.
- `projections.py`: Phase 12 explanations and graph; receives only the selected public point.
- `observer.py`: clearly separate ended-demo private review. Never an ordinary checkpoint input.
- `application.py`: generic presentation state machine and isolated demo path.
- `progress.py`: activity counters and previously revealed questions, separate from tutor mastery.
- `exports.py`: deterministic Markdown outlines from actual evidence and the central registry.

The browser renders Python results. Its only numerical work formats values and positions SVG
coordinates. It performs no pricing, risk, VWAP, signal, hedge-sizing or grading calculation.

## Integration and isolation

Only three pre-existing source files change: the HTTP adapter, shared navigation, and the
Phase 12 browser panel. `/api/demos` has the same loopback, origin, token, JSON and response
security contract as the existing labs. `/api/demos/availability` is a small read-only endpoint
for completed-session links. No demo command is sent to the user's live trading engine.

The Explain panel receives an explicit demo context; it cannot silently read the personal
account. Its separate live tutor and what-if controls are suppressed in that context. Ordinary
Explain continues to use its original endpoints and behavior.

## Reproducibility and limits

Root seed **140042** was fixed before examining results. Existing Phase 10 examples retain
101001/101002/101003; look-ahead uses 201042; historical fixtures retain Phase 13's source seed.
No seed search or outcome substitution occurs. Restart rebuilds starting accounts, books and
inputs; it does not erase the user's memory or award fresh mastery for known answers.

Research controls cache their deterministic evidence in process memory. Other demos take small,
bounded core runs. Saved journals are limited to 25 MB at import and retain the original version,
action and 64 MB visual-frame checks. Annotation selects at most eight moments, six by default.
This is a single local presentation state per server; use one server per independent workspace.

Run `venv/bin/python scripts/phase14_evidence.py` to rebuild the eight scripts and measurement
report. See [recorded evidence](evidence/demo-report.json) and [the full build report](PHASE14_REPORT.md).
