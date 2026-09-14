# ruff: noqa: E501 -- HTML and editorial strings retain readable sentence boundaries.
"""Shared presentation copy. No financial calculations or private state."""

ENVIRONMENTS = (
    (
        "Synthetic",
        "No real market observations",
        "Value process, participants, orders and fills",
        "Configured mechanisms; private value is hidden from ordinary agents",
        "Actual fills from the simulated FIFO order book",
    ),
    (
        "Historical replay",
        "Imported recorded OHLCV; bundled fixture is artificial",
        "Your orders, fills and P&L",
        "Revealed observations and supplied provenance; no hidden cause",
        "Paper execution at later closes, under participation, slippage and fee assumptions",
    ),
    (
        "Scenario",
        "No real market observations",
        "A controlled synthetic regime and executions",
        "Configured mechanism; hidden scenarios require an explicit ended-session reveal",
        "Existing simulated execution model for the scenario's lab",
    ),
)

LIMITATIONS = (
    (
        "Market simulation",
        "Agents and latent dynamics are deliberately simple and uncalibrated.",
        "Controlled mechanisms make causal teaching and repetition possible.",
        "Trading patterns or apparent advantages may disappear under other agents or regimes.",
        "Production work needs calibration, richer behaviour and independent live-data validation.",
    ),
    (
        "Historical replay",
        "OHLCV provides neither queue priority nor observed depth. User fills are simulated.",
        "The input schema makes bar availability and provenance explicit without inventing a book.",
        "Bar-close execution can materially misstate fill probability, timing, costs and P&L.",
        "Venue data, timestamps, corporate actions and an independently validated execution model are needed.",
    ),
    (
        "Options",
        "European cash-settled options use Black–Scholes assumptions and finite synthetic quotes.",
        "One transparent model links values, Greeks, IV inversion and stock hedging.",
        "Jumps, changing volatility, illiquidity and hedging costs leave risks after a delta hedge.",
        "Desks use market surfaces, contract-specific conventions, model validation and operational controls.",
    ),
    (
        "Risk",
        "Covariance, distribution, horizon and cross-lab alignment are explicit model inputs.",
        "Controlled VaR, ES and stress comparisons expose the assumptions behind each estimate.",
        "Unstable correlations, sparse tails and unmodelled scenarios can understate losses.",
        "Independent validation, backtesting, data governance and regulatory processes are separate work.",
    ),
    (
        "Stat Arb",
        "Linear regression, rolling residual statistics and simple causal rules.",
        "Known synthetic relationships allow inspection of fitting, execution and deliberate breakdown.",
        "Correlation need not imply cointegration; a fitted spread need not converge. Legs may fill unevenly.",
        "Real research needs robust diagnostics, costs, borrow constraints and structural-break monitoring.",
    ),
    (
        "Research",
        "Experiments are conditional on their simulator, sampling design and finite sample.",
        "Seeds, registrations and retained failed/losing runs make the procedure inspectable.",
        "Selection, repeated evaluation, dependent observations or model error can invalidate inference.",
        "An untouched evaluation is useful evidence, not proof of a deployable trading advantage.",
    ),
    (
        "Execution",
        "Integer quantities, price-time priority and simplified costs; no network latency model.",
        "The real simulated matcher makes partial fills and accounting consequences observable.",
        "A simulated fill does not establish venue access, historical fill probability or liquidation value.",
        "Real venues require routing, feed recovery, latency budgets and operational reconciliation.",
    ),
    (
        "Security / deployment",
        "One local user, loopback server, no internet-facing authentication service.",
        "A local application avoids brokers, account credentials and external learning services.",
        "Untrusted files can consume resources; a hostile local process remains outside the trust boundary.",
        "Network deployment would require authentication, isolation, monitoring and a separate security review.",
    ),
)

LAB_CARDS = (
    (
        "01",
        "Trade manually",
        "Submit buys, sells, market and limit orders. Inspect queues, fills, cash and positions.",
        "/",
    ),
    (
        "02",
        "Make markets",
        "Quote both sides. Follow spread, inventory and adverse selection.",
        "/#maker",
    ),
    (
        "03",
        "Price & hedge options",
        "Connect option values, Greeks and implied volatility to executed stock hedges.",
        "/options",
    ),
    (
        "04",
        "Inspect portfolio risk",
        "Compare VaR and ES, stress positions and explore constrained allocations.",
        "/risk",
    ),
    (
        "05",
        "Study statistical arbitrage",
        "Trace regression, residuals, z-scores, leg risk and relationship failure.",
        "/statarb",
    ),
    (
        "06",
        "Run reproducible research",
        "Use Monte Carlo, comparisons and untouched evaluation with honest uncertainty.",
        "/research",
    ),
    (
        "07",
        "Learn from the evidence",
        "Ask why a value changed, predict a result and revisit a verified session.",
        "/demos",
    ),
    (
        "08",
        "Choose the environment",
        "Distinguish synthetic mechanisms, historical observations and controlled scenarios.",
        "/environments",
    ),
)

FEATURED = (
    ("order", "How a trade actually happens", "Start here · orders, depth, fills and VWAP"),
    (
        "synthetic-prices",
        "How synthetic prices emerge",
        "Value → information → orders → transactions",
    ),
    ("delta-hedge", "Delta hedging", "A hedge changes exposure; risk remains"),
    ("tails", "VaR vs Expected Shortfall", "The threshold and the severity beyond it"),
    (
        "pairs",
        "Correlation vs cointegration",
        "Similar price paths, different residual behaviour",
    ),
    (
        "winner",
        "How backtests can fool you",
        "Fifty equal-skill variants and one selected winner",
    ),
)
