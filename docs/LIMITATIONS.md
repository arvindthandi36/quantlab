# QuantLab limitations

A correct implementation can still describe an unrealistic market. The in-app page at `/limitations` uses the same release copy.

## Market simulation

**What is simplified?** Agents and latent dynamics are deliberately simple and uncalibrated.

**Why?** Controlled mechanisms make causal teaching and repetition possible.

**What could fail?** Trading patterns or apparent advantages may disappear under other agents or regimes.

**How production differs** Production work needs calibration, richer behaviour and independent live-data validation.

## Historical replay

**What is simplified?** OHLCV provides neither queue priority nor observed depth. User fills are simulated.

**Why?** The input schema makes bar availability and provenance explicit without inventing a book.

**What could fail?** Bar-close execution can materially misstate fill probability, timing, costs and P&L.

**How production differs** Venue data, timestamps, corporate actions and an independently validated execution model are needed.

## Options

**What is simplified?** European cash-settled options use Black–Scholes assumptions and finite synthetic quotes.

**Why?** One transparent model links values, Greeks, IV inversion and stock hedging.

**What could fail?** Jumps, changing volatility, illiquidity and hedging costs leave risks after a delta hedge.

**How production differs** Desks use market surfaces, contract-specific conventions, model validation and operational controls.

## Risk

**What is simplified?** Covariance, distribution, horizon and cross-lab alignment are explicit model inputs.

**Why?** Controlled VaR, ES and stress comparisons expose the assumptions behind each estimate.

**What could fail?** Unstable correlations, sparse tails and unmodelled scenarios can understate losses.

**How production differs** Independent validation, backtesting, data governance and regulatory processes are separate work.

## Stat Arb

**What is simplified?** Linear regression, rolling residual statistics and simple causal rules.

**Why?** Known synthetic relationships allow inspection of fitting, execution and deliberate breakdown.

**What could fail?** Correlation need not imply cointegration; a fitted spread need not converge. Legs may fill unevenly.

**How production differs** Real research needs robust diagnostics, costs, borrow constraints and structural-break monitoring.

## Research

**What is simplified?** Experiments are conditional on their simulator, sampling design and finite sample.

**Why?** Seeds, registrations and retained failed/losing runs make the procedure inspectable.

**What could fail?** Selection, repeated evaluation, dependent observations or model error can invalidate inference.

**How production differs** An untouched evaluation is useful evidence, not proof of a deployable trading advantage.

## Execution

**What is simplified?** Integer quantities, price-time priority and simplified costs; no network latency model.

**Why?** The real simulated matcher makes partial fills and accounting consequences observable.

**What could fail?** A simulated fill does not establish venue access, historical fill probability or liquidation value.

**How production differs** Real venues require routing, feed recovery, latency budgets and operational reconciliation.

## Security / deployment

**What is simplified?** One local user, loopback server, no internet-facing authentication service.

**Why?** A local application avoids brokers, account credentials and external learning services.

**What could fail?** Untrusted files can consume resources; a hostile local process remains outside the trust boundary.

**How production differs** Network deployment would require authentication, isolation, monitoring and a separate security review.

Canonical [assumptions](../ASSUMPTIONS.md) and [units](conventions.md) govern the calculations. Educational software; not investment advice.
