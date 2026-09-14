"""Concept-specific teaching; separate concepts never borrow unrelated answer credit."""


def lesson(prompt, right, wrong, other, intuition, maths, interview, mistake):
    return (
        prompt,
        "rule",
        (("rule", right), ("wrong", wrong), ("other", other)),
        intuition,
        maths,
        interview,
        mistake,
    )


ADDITIONAL = {
    "bid": lesson(
        "Which visible quote is an offer to buy?",
        "Bid",
        "Ask",
        "Midpoint",
        "A bid is a buyer's offer.",
        "Best bid = highest resting buy price.",
        "Why does an immediate seller approach the bid?",
        "bid_confused_with_ask",
    ),
    "ask": lesson(
        "Which visible quote first serves an immediate small buy?",
        "Best ask",
        "Best bid",
        "Midpoint",
        "An ask is a seller's offer.",
        "Best ask = lowest resting sell price.",
        "Why can a larger buy execute above the best ask?",
        "bid_confused_with_ask",
    ),
    "spread": lesson(
        "What is the displayed spread?",
        "Best ask minus best bid",
        "Ask plus bid",
        "Guaranteed maker profit",
        "The spread is the gap between the nearest buyer and seller.",
        "S = A − B; A is best ask, B best bid.",
        "Why is a wide spread not automatically attractive to a maker?",
        "spread_guarantees_profit",
    ),
    "midpoint": lesson(
        "What is the midpoint?",
        "Halfway between best bid and ask",
        "The last execution",
        "A guaranteed execution price",
        "The mid is a reference, not an order offering quantity.",
        "M = (A+B)/2; A is best ask, B best bid.",
        "How can midpoint move with no transaction?",
        "midpoint_is_execution",
    ),
    "market_orders": lesson(
        "What does a market order request?",
        "Immediate matching against eligible opposite liquidity",
        "Guaranteed full execution",
        "A resting order at the midpoint",
        "A market order accepts available prices; this engine cancels any unfilled remainder.",
        "Q = F + C; Q requested, F filled, C cancelled for a completed market order.",
        "Why are order size and displayed depth both relevant?",
        "market_order_guarantees_liquidity",
    ),
    "depth": lesson(
        "What does aggregated depth count?",
        "Resting quantity and order count at each price",
        "Only the last trade",
        "Private latent value",
        "A depth level summarises individual FIFO orders without replacing them.",
        "D(p)=Σqᵢ at price p; qᵢ is each resting quantity.",
        "Why preserve individual orders underneath a depth view?",
        "aggregation_removes_fifo",
    ),
    "order_flow": lesson(
        "What is order flow here?",
        "The sequence of submitted orders and executions",
        "The hidden value process",
        "Only profitable trades",
        "Orders arrive over time; some rest, some trade, some cancel.",
        (
            "Signed executed flow = buy-aggressor units − sell-aggressor units over a "
            "stated window."
        ),
        "Why does signed flow alone not identify private information?",
        "flow_reveals_private_information",
    ),
    "informed_trading": lesson(
        "What makes the model trader informed?",
        "A noisy private signal that may give estimated edge",
        "Perfect knowledge of future prices",
        "Every profitable trade",
        "Information can improve an estimate without removing uncertainty.",
        (
            "Estimated buy edge = estimated value − ask − costs; the model also "
            "requires an uncertainty buffer."
        ),
        "Which signal assumptions make this synthetic trader unrealistic?",
        "informed_means_perfect",
    ),
    "toxic_flow": lesson(
        "What does toxic flow describe from a provider's perspective?",
        "Flow associated with adverse subsequent reference moves",
        "Every large trade",
        "A known illegal counterparty",
        "The phrase describes unfavourable selection, not a proven identity or intention.",
        (
            "Average provider markout = Σqᵢmᵢ/Σqᵢ at a declared horizon; mᵢ signed "
            "per-unit markout, qᵢ fill units."
        ),
        "Why do coverage and the chosen horizon matter?",
        "toxic_flow_identifies_counterparty",
    ),
    "random_variables": lesson(
        "Before a run, what is a random variable?",
        "A quantity whose realised value depends on the random draw",
        "A guaranteed average",
        "A programming error",
        "Before rolling, a die result is uncertain; a session outcome is similar.",
        "X denotes an uncertain outcome; x is one realised value.",
        "Which quantities are random before a seed is fixed?",
        "random_variable_is_guarantee",
    ),
    "expectation": lesson(
        "What is an expected value?",
        "A probability-weighted average, not a guaranteed result",
        "The outcome every run must equal",
        "The best possible result",
        "An average across possible outcomes can differ from every realised outcome.",
        "E[X]=Σpᵢxᵢ; pᵢ is probability of outcome xᵢ, with Σpᵢ=1.",
        "Why can a positive-expectation decision still lose?",
        "expectation_is_guaranteed",
    ),
    "variance": lesson(
        "What does variance measure?",
        "Average squared distance from the mean",
        "Uncertainty about the mean only",
        "The average outcome itself",
        "Squaring stops positive and negative deviations cancelling.",
        "Var(X)=E[(X−μ)²]; μ=E[X]. Sample variance s²=Σ(xᵢ−x̄)²/(n−1).",
        "Why do independent variances add but standard deviations do not?",
        "variance_is_mean",
    ),
    "conditional_probability": lesson(
        "What does conditioning do?",
        "Updates probabilities using specified information",
        "Reveals a certain future",
        "Changes already recorded trades",
        "Learning something changes the set of plausible outcomes.",
        "P(A|B)=P(A and B)/P(B), for P(B)>0; A,B are events.",
        "Why must the conditioning information exist at decision time?",
        "conditioning_is_foresight",
    ),
    "distributions": lesson(
        "What does the distribution of session outcomes show?",
        "The range and relative frequency of outcomes",
        "Only the mean",
        "Guaranteed future frequencies",
        "The whole spread of outcomes matters, including extremes.",
        "An empirical distribution assigns weight 1/n to each of n observed sessions.",
        "Why can two strategies with the same mean have different risks?",
        "distribution_is_just_mean",
    ),
    "poisson_arrivals": lesson(
        "What does this model's constant-rate random arrival assumption imply?",
        "Random waiting times with a fixed average rate",
        "Exactly equal gaps",
        "Real market arrivals must follow it",
        "An average arrival rate does not schedule each arrival at equal intervals.",
        (
            "P(N(t)=k)=exp(−λt)(λt)^k/k!; λ events/second, t seconds, k count under "
            "independent Poisson arrivals."
        ),
        "How would clustering challenge constant-rate arrivals?",
        "poisson_means_equal_gaps",
    ),
    "normal_distributions": lesson(
        "What is a limitation of Gaussian noise in the signal model?",
        "It is a symmetric light-tail modelling choice, not guaranteed reality",
        "It removes all signal error",
        "It produces only positive errors",
        "Normal noise is centred and symmetric, but actual information errors may not be.",
        "ε ~ N(0,σ²); ε is signal error, zero its mean, σ its standard deviation.",
        "What changes if errors are biased or heavy-tailed?",
        "gaussian_means_no_error",
    ),
    "law_of_large_numbers": lesson(
        "What can more independent, comparable sessions improve?",
        "Stability of the average under suitable finite-mean assumptions",
        "Guarantee each individual session profit",
        "Remove model misspecification",
        "Averages tend to stabilise as independent evidence accumulates.",
        (
            "For iid finite-mean Xᵢ, sample mean x̄ₙ approaches E[X] as n grows; not "
            "monotonically in every sample."
        ),
        "Why is convergence of an average not a promise about the next run?",
        "more_runs_guarantee_profit",
    ),
    "standard_deviation": lesson(
        "What does session standard deviation describe?",
        "Dispersion among individual session outcomes",
        "Only uncertainty of their mean",
        "The mean itself",
        "SD uses the original units to describe spread among outcomes.",
        "s=√[Σ(xᵢ−x̄)²/(n−1)]; xᵢ outcomes, x̄ average, n sample size.",
        "Why can SD stay large while SE becomes small?",
        "sd_confused_with_se",
    ),
    "confidence_intervals": lesson(
        "How should a 95% frequentist confidence procedure be interpreted?",
        (
            "Across repeated samples, its intervals cover the fixed parameter about 95% "
            "of the time under assumptions"
        ),
        "95% of individual outcomes lie inside it",
        "The next run is guaranteed inside it",
        (
            "An interval expresses estimation uncertainty, not a guaranteed range of "
            "next-run profit."
        ),
        (
            "Mean interval = x̄ ± t* s/√n; t* is the selected Student-t critical value, "
            "x̄ sample mean, s SD, n count."
        ),
        "Why is a confidence interval different from a prediction interval?",
        "mean_interval_predicts_next_run",
    ),
    "bootstrap": lesson(
        "What does this research bootstrap resample?",
        "Complete independent sessions with replacement",
        "Dependent individual fills as independent runs",
        "Only profitable sessions",
        "Resampling whole sessions preserves dependence inside a session.",
        "A bootstrap draw samples n session indices with replacement from n original sessions.",
        "What assumption fails if the sessions themselves are dependent?",
        "fills_are_independent_sessions",
    ),
    "multiple_testing": lesson(
        "Why be cautious after checking many variants?",
        "More opportunities to select a lucky-looking result",
        "Each extra check guarantees accuracy",
        "A single favourable interval proves all hypotheses",
        "Repeated searching creates more chances to mistake noise for an effect.",
        (
            "For m independent null tests at level α, chance of ≥1 false rejection = "
            "1−(1−α)^m; dependence changes this expression."
        ),
        "How do pre-registration and untouched evaluation address different risks?",
        "multiple_tests_have_no_cost",
    ),
    "monte_carlo": lesson(
        "What does a Monte Carlo estimate use?",
        "Repeated simulated outcomes to estimate a model quantity",
        "One chosen profitable run",
        "A proof of real-market profit",
        "Repeated draws help estimate an average within the specified model.",
        "μ̂=(1/n)ΣXᵢ; Xᵢ is one simulated outcome, n the number of independent runs.",
        "Why report sampling uncertainty and model limitations separately?",
        "simulation_proves_real_profit",
    ),
    "data_structures": lesson(
        "Why keep FIFO orders within each price level?",
        "The queue preserves arrival priority after price selection",
        "Aggregation makes arrival order unnecessary",
        "Larger orders should skip ahead",
        "The depth summary and the matching queue answer different questions.",
        "Price selects a level; increasing arrival sequence selects its FIFO head.",
        "How would you test that a depth display never changes matching?",
        "aggregation_removes_fifo",
    ),
    "testing": lesson(
        "What should a conservation discrepancy do?",
        "Fail loudly so the accounting bug is visible",
        "Repair the balances silently",
        "Be ignored if P&L is positive",
        "Tests and runtime invariants catch broken accounting; they do not prove realism.",
        (
            "Σ buyer filled = Σ seller filled = Σ recorded trade quantity for each "
            "match operation."
        ),
        "Why combine generated operation sequences with hand-worked cases?",
        "accounting_may_be_repaired",
    ),
    "randomness": lesson(
        "What does a fixed random seed provide?",
        "Repeatable model draws with compatible code and settings",
        "A representative profitable outcome",
        "The same trades under every strategy",
        "A seed identifies a reproducible draw sequence, not a good result.",
        (
            "Seed + version + stream addressing determines pseudo-random draws; "
            "decisions still determine execution."
        ),
        "Why keep learning interactions outside market random streams?",
        "seed_guarantees_unchanged_outcomes",
    ),
    "algorithms": lesson(
        "What orders the matching process?",
        "Eligible price first, then arrival order at that price",
        "Latent value then trader wealth",
        "Highest profit for the user",
        "The exchange follows explicit priority rules, independent of trader identity.",
        (
            "Buy limit accepts asks p≤L in ascending p; sell accepts bids p≥L in "
            "descending p; equal p uses FIFO."
        ),
        "How would you audit multi-level matching with partial remainders?",
        "matching_optimises_user_profit",
    ),
    "numerical_correctness": lesson(
        "Why use exact quantities and rational accounting?",
        "So rounding cannot hide conservation discrepancies",
        "So economic assumptions become true",
        "So every financial quantity is necessarily an integer",
        "Exact arithmetic makes reconciliation inspectable; display rounding is separate.",
        "VWAP=Σpᵢqᵢ/Σqᵢ can be fractional even when prices are integer ticks.",
        "Where should rounding be allowed, and where should it fail tests?",
        "rounding_can_hide_accounting",
    ),
    "pnl_attribution": lesson(
        "Does cash from selling prove a profit?",
        "No; realised costs, remaining marked inventory and fees matter",
        "Yes; proceeds are all profit",
        "Only unrealised P&L matters",
        (
            "Realised P&L comes from closed units; unrealised P&L marks remaining units "
            "to a reference."
        ),
        (
            "Net P&L = realised P&L after fees + unrealised P&L; do not add sale "
            "proceeds or markouts again."
        ),
        "How can a maker gain execution edge but lose overall?",
        "realised_confused_with_unrealised",
    ),
    "quote_skew": lesson(
        "For a long maker, why might shifting both quotes down help reduce inventory?",
        "It can make the ask more competitive and the bid less competitive",
        "It guarantees inventory falls without cost",
        "It reveals hidden future prices",
        (
            "A quote shift changes incentives to trade; it offers no guarantee or "
            "universal optimum."
        ),
        (
            "Centre c=R−kq; R public reference, q signed inventory, k chosen skew "
            "strength; bid=c−h, ask=c+h, h half-spread before tick/risk constraints."
        ),
        "What execution and opportunity costs can inventory reduction introduce?",
        "lower_inventory_is_always_safer",
    ),
    "tail_outcomes": lesson(
        "What can the worst observed run tell you?",
        "An observed extreme, not the worst possible future loss",
        "A proven bound on all future loss",
        "Nothing if the mean is positive",
        "Averages can hide painful individual runs. A finite sample can miss rarer outcomes.",
        (
            "Observed minimum=min(x₁,…,xₙ); it is sample-dependent and not a population "
            "lower bound."
        ),
        (
            "Why does a larger sample sometimes reveal worse extremes while improving "
            "mean precision?"
        ),
        "observed_minimum_bounds_risk",
    ),
}

# Two correct claims and two explicit misconceptions for level-3 reasoning.
REASONING = {
    "vwap": (
        "Why can a larger buy have worse VWAP than the initial best ask?",
        "Quantity at the best ask can run out",
        "Remaining units may trade at higher eligible asks",
        "Every unit executes at the midpoint",
        "Fees are automatically embedded in the VWAP",
    ),
    "standard_error": (
        "Why does the mean's SE scale with 1/√n for iid observations?",
        "Independent variances add, giving variance of the average σ²/n",
        "Taking the square root converts that variance to SE σ/√n",
        "Individual session SD must shrink as n grows",
        "Correlated sessions obey the same formula without adjustment",
    ),
    "correlation": (
        "Why can common random numbers improve comparison precision?",
        "Positive covariance removes shared variation in B−A",
        "Negative covariance can instead increase variance of B−A",
        "Pairing guarantees smaller SE",
        "Shared seeds force identical strategy trades",
    ),
    "adverse_selection": (
        "Which mechanisms besides private information can produce negative provider marks?",
        "Other public orders or cancellations move the midpoint",
        "Unrelated random price movement follows the fill",
        "The sign alone identifies an informed counterparty",
        "Adding the mark to P&L explains the cause",
    ),
    "markouts": (
        "Which statements correctly interpret a matured markout?",
        "Its sign is relative to the recorded side and horizon",
        "It is a reference-price diagnostic, not extra account profit",
        "It was known at execution time",
        "Negative means the trader was certainly informed",
    ),
    "spread_capture": (
        "Why can positive execution edge coexist with net losses?",
        "Inventory can lose value between executions",
        "Fees can outweigh remaining gross gains",
        "Positive quoted spread guarantees realised profit",
        "Markouts should be added as extra losses",
    ),
    "quote_skew": (
        "Why is lowering quotes for long inventory a trade-off?",
        "A more competitive ask may increase the chance of selling",
        "Less competitive bids can give up otherwise favourable fills",
        "Lower inventory proves lower total risk at any cost",
        "This rule is universally optimal",
    ),
    "decision_quality": (
        "What evidence supports decision assessment without hindsight?",
        "Contemporaneous public information and recorded reasoning",
        "Explicit assumptions and risk constraints known when deciding",
        "Profit alone proves a good decision",
        "Later hidden value was information the trader should have used",
    ),
    "selection_bias": (
        "Why can the best development variant disappoint in evaluation?",
        "Selecting among noisy means also selects favourable estimation error",
        "Repeated evaluation peeking can make evaluation part of selection",
        "The winning development mean is unbiased after selection",
        "More variants automatically solve overfitting",
    ),
}
