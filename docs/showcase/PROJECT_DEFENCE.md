# Project defence — questions to understand, not memorise

Use one actual example and one limitation for each answer. Say when you do not yet know.

| Question | Technical points to explain | Go deeper |
|---|---|---|
| Why integer ticks? | Exact comparisons on a declared price grid; monetary accounting retains exact fractions | [Units](../conventions.md) |
| Why event-driven? | Process events in timestamp/sequence order; explicit causality and reproducible clocks | [Market design](../architecture/phase_02.md) |
| Why latent value differs from price? | Value influences information and orders; resting offers and matching determine executions | [System](../architecture/OVERVIEW.md) |
| Why can a maker lose with a positive spread? | Fees, inventory moves, asymmetric information; distinguish realised P&L and diagnostic markout | [Maker maths](../maths/phase_04_market_making.md) |
| Why common random numbers? | Comparable exogenous paths can reduce variance of a paired difference; pairing must be valid | [Research](../maths/phase_05_research.md) |
| Why doesn't a profitable backtest prove alpha? | Sampling noise, selection, costs, model misspecification and evaluation reuse | [Winner demo](../demos/scripts/winner.md) |
| Why isn't delta-neutral risk-free? | Local first-order offset; gamma, vega, jumps, costs and model error remain | [Options](../maths/phase_08_options.md) |
| Why ES alongside VaR? | Threshold versus average tail severity; finite-sample tail convention and sparse data | [Risk](../maths/phase_09_portfolio_risk.md) |
| Correlation vs cointegration? | Co-movement is not a stationary linear combination; fitted residuals need defensible diagnostics | [Stat Arb](../maths/phase_10_statistical_arbitrage.md) |
| Why historical simulated execution? | Bars omit queue/depth truth; timing, participation and slippage are model assumptions | [Historical fills](../markets/HISTORICAL_EXECUTION.md) |
| What does replay establish? | Specific transitions reconcile under declared compatibility; it does not establish real-world validity | [Replay policy](../release/replay_policy.md) |
| Why distinguish process from outcome? | A realised gain cannot supply a missing objective or decision rule | [Annotated replay](../demos/ANNOTATED_REPLAY.md) |
| Biggest unrealistic assumptions? | Choose relevant agent, execution, derivative, covariance and data limitations; explain consequences | [Limitations](../LIMITATIONS.md) |
| Why two version numbers? | Product 1.1.0 adds presentation around unchanged core 1.0.0; keep strict old replay gates intact | [Version decision](../release/VERSIONING.md) |

A useful answer: define the mechanism, point to the implementation/test, show an observed result,
then discuss an assumption that could invalidate the interpretation. This is preparation for later
learning, not authorisation to begin another implementation phase.
