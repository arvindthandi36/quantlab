"""Authoritative explanation text and relationships; no financial implementations."""

# ruff: noqa: E501 -- authored metadata rows remain one record per line.

import re
from dataclasses import asdict, dataclass

DEPTHS = ("beginner", "maths", "quant", "interview")
LAB_PATHS = {
    "trading": "/",
    "maker": "/#maker",
    "research": "/research",
    "options": "/options",
    "risk": "/risk",
    "statarb": "/statarb",
    "learning": "/learning",
}

# id | name | domain | intuition | economic relevance | direct drivers | limitation
_ROWS = """
bid|Bid|Market mechanics|The highest displayed price someone is currently willing to pay.|It is the first available selling price, subject to displayed quantity.|Resting buy orders, cancellations and executions.|A displayed quote may disappear before another order reaches it.
ask|Ask|Market mechanics|The lowest displayed price someone is currently willing to accept.|It is the first available buying price, subject to displayed quantity.|Resting sell orders, cancellations and executions.|A quote is available for a limited quantity, not for every order size.
spread|Spread|Market mechanics|The gap between the best ask and the best bid.|Crossing the gap creates an immediate execution cost relative to the midpoint.|Changes to the best bid or ask.|The spread is not a liquidity provider's guaranteed profit.
midpoint|Midpoint|Market mechanics|The price halfway between the best bid and best ask.|It is a useful public valuation reference for inventory and markouts.|The two best displayed quotes.|There need not be an executable order at the midpoint.
depth|Market depth|Market mechanics|The quantity waiting at each displayed price level.|An order larger than the best level can reach worse prices.|New limit orders, fills and cancellations.|Only visible resting liquidity is represented; no hidden liquidity or latency.
queue_priority|FIFO priority|Market mechanics|Earlier orders at the same price execute before later ones.|Joining a queue does not guarantee that an incoming order reaches you.|Price priority, arrival sequence and cancellations.|The simulator models price/time priority at one exchange.
limit_orders|Limit order|Trading / execution|An instruction to buy no higher, or sell no lower, than a chosen price.|It controls the worst acceptable execution price but can leave you waiting.|Limit price, opposite quotes, size and earlier orders.|A limit price is not a promised transaction price or fill.
market_orders|Market order|Trading / execution|An instruction to take available opposite orders now.|It prioritises immediacy over a chosen price; large sizes may sweep levels.|Order size and visible opposite liquidity.|In QuantLab any unfilled market remainder cancels.
partial_fills|Partial fill|Trading / execution|Only part of the submitted quantity has executed.|An incomplete position may leave exposure or a hedge unfinished.|Available quantity, price limit and queue position.|A resting remainder and a cancelled remainder are different outcomes.
order_size|Order size|Trading / execution|The number of units requested in an order.|Larger orders can consume deeper and more expensive liquidity.|The submitted quantity.|A size prediction against a frozen book does not predict subsequent reactions.
vwap|VWAP|Trading / execution|An average execution price that gives larger fills more weight.|It tells you what price you actually paid across several fills.|Each recorded execution price and quantity.|QuantLab shows your order's VWAP, not a whole-market daily benchmark; fees are separate.
slippage|Slippage|Trading / execution|The difference between an execution price and a specified comparison price.|It measures execution quality only when the benchmark and side are stated.|Fill prices, weights, order side and the chosen benchmark.|Changing the benchmark can change the interpretation. No benchmark means no measured slippage.
execution_cost|Execution cost|Trading / execution|The cost of trading relative to a stated reference, plus separately disclosed fees.|Repeated small costs can overwhelm a small estimated advantage.|Execution prices, side, quantity, fees and benchmark.|An execution-cost estimate is not a complete future P&L forecast.
position|Position|Trading / execution|The net units you hold: positive is long and negative is short.|Its sign and size determine how price movements affect your account.|Buys, sells and settlement.|Cash received from a short sale is offset by the obligation represented by the short position.
realised_pnl|Realised P&L|Trading / execution|Profit or loss recognised when open inventory is closed.|It separates completed trading outcomes from the value of positions still open.|Closing fills, FIFO entry lots and the lab's fee convention.|The stock desk expenses fees in realised P&L; consolidated reports show gross realised P&L and separate fees.
unrealised_pnl|Unrealised P&L|Trading / execution|The gain or loss on positions still open at the current mark.|It shows how open inventory has changed in value before liquidation.|Current reference mark, remaining lots and quantities.|A valuation mark is not a guaranteed liquidation price.
pnl_attribution|P&L and its changes|Trading / execution|Profit and loss is the change in account equity from its starting value.|Cash movements alone can confuse trade proceeds with profit.|Realised P&L, unrealised P&L, fees and financing.|Component changes reconcile accounting; they do not by themselves identify a trader's skill.
fees|Fees|Trading / execution|Charges paid for executed trades.|Fees reduce net outcomes even when gross trading gains are positive.|Filled quantity and the configured fee schedule.|Fees are synthetic and exclude many real brokerage, clearing and funding costs.
markouts|Markout|Market microstructure|A signed comparison between an execution price and a later public reference.|It helps assess whether the price subsequently moved against the side that traded.|Execution side and price, selected horizon and observed later reference.|A negative markout does not prove the counterparty was informed. Pending horizons have no value yet.
inventory|Inventory|Market microstructure|The units a liquidity provider currently holds.|An accumulation of units creates directional exposure and constrains new quotes.|Executed buys and sells.|An inventory limit controls size; it does not cap every possible loss.
quote_skew|Inventory quote skew|Market microstructure|A quoting rule can shift both quotes to encourage reducing inventory.|Under the inventory rule, long inventory lowers the quote centre.|Public reference, inventory, sensitivity, spread, grid rounding and safety limits.|Manual quotes use the user's chosen shift; they do not secretly apply the automatic inventory rule.
spread_capture|Spread capture|Market microstructure|The apparent advantage from trading on a favourable side of a reference price.|It is one component to compare with inventory changes, fees and later price movement.|Fill prices and the contemporaneous public reference.|Later adverse movements can outweigh apparent spread capture.
adverse_selection|Adverse selection|Market microstructure|Trading can be more likely when your quote is disadvantageous to you.|A stale attractive quote can be selected by better-informed flow.|Information quality, quote freshness and decision thresholds.|Public markouts estimate outcomes; they cannot identify hidden information from one trade.
order_flow|Order flow|Market microstructure|The sequence of submitted buy and sell instructions.|It consumes and replenishes the book and changes inventory.|Agent arrivals, decisions and user orders.|A buy-heavy tape is observed activity, not proof of future price rises.
expectation|Expected value|Probability|A probability-weighted average of possible outcomes.|It describes a model's average outcome, not the next realised outcome.|Possible outcomes and their probabilities.|A positive average can coexist with large losses or model error.
variance|Variance|Probability|The average squared distance of observations from their mean.|It measures dispersion and feeds volatility and risk calculations.|Distances from the mean and the observation convention.|Squaring emphasises extremes; variance alone does not describe tail shape.
sample_mean|Sample mean|Statistics|The average of the observations actually collected.|It estimates an average outcome but varies between samples.|All included observations and their count.|A selected or dependent sample can give a misleading estimate.
standard_deviation|Standard deviation|Statistics|The square root of variance, expressed in the original measurement units.|It gives a scale for typical dispersion and for standardised scores.|Observation variability and the sample convention.|It is not the same as uncertainty in an estimated mean.
standard_error|Standard error|Statistics|The estimated sampling variability of an estimator, such as the mean.|It helps distinguish a noisy estimated advantage from a precisely estimated one.|Independent sample count and outcome variability.|Treating correlated fills as independent sessions understates uncertainty.
confidence_intervals|Confidence interval|Statistics|An interval produced by a method designed for repeated-sample coverage.|It makes uncertainty around a mean visible.|Standard error, sample size, confidence level and interval method.|A realised frequentist interval does not assign a probability to a fixed unknown mean.
correlation|Correlation|Portfolio theory|A scale-free measure of linear co-movement.|It affects diversification and is useful for diagnosing relationships.|Paired observations, covariance and both standard deviations.|High price correlation does not establish a stable residual or profitable convergence.
covariance|Covariance|Portfolio theory|A measure of whether two returns tend to deviate from their averages together.|It retains the scale needed to combine risks across assets.|Synchronous returns, means and measurement units.|Price covariance and return covariance are not interchangeable.
covariance_matrices|Covariance matrix|Portfolio theory|A table of individual variances and pairwise covariances.|It connects position exposures to total portfolio variance.|Volatility, correlations or a selected return sample.|A valid matrix must be symmetric and positive semidefinite; an estimated matrix may be unstable.
portfolio_variance|Portfolio variance|Portfolio theory|The dispersion of a combined portfolio, including cross-asset terms.|Position signs and co-movement determine whether risks reinforce or offset.|Exposures and the covariance matrix.|Linear variance omits nonlinear option responses and changes in volatility.
diversification|Diversification|Portfolio theory|Combining exposures can reduce risk when movements offset imperfectly.|More holdings help only if their risks do not all reinforce one another.|Position weights, volatility and correlation.|Rising correlation can weaken diversification; long/short portfolios can respond differently.
portfolio_optimisation|Portfolio optimisation|Portfolio theory|A model chooses weights to improve a stated objective under constraints.|It makes the objective and trade-offs explicit.|Estimated means, covariance, allowed weights and constraints.|Optimisation can amplify estimation errors; proposed weights are not executed trades.
option_pricing|Option model value|Derivatives|A model estimates the value of a payoff that depends on a future underlying price.|It supports quotes, Greeks and risk revaluation.|Spot, strike, time, volatility, rate, dividends and payoff type.|QuantLab uses European Black–Scholes assumptions, not a production volatility surface.
black_scholes|Black–Scholes model|Derivatives|A model prices a European option under a specified constant-volatility process.|It provides one consistent relationship between price and sensitivities.|Spot, strike, remaining time, volatility, rate and dividend yield.|Continuous frictionless hedging and lognormal dynamics are idealisations.
delta|Delta|Derivatives|For a small stock move, delta approximates the option value change per unit of stock movement.|It sets the first-order stock hedge and contributes to portfolio risk.|Spot, strike, time, volatility, rate, dividends and option type.|Delta changes as inputs change; delta-neutral does not mean risk-free.
gamma|Gamma|Derivatives|Gamma measures how quickly delta changes as the stock price moves.|It explains why yesterday's delta hedge can become stale.|Spot, strike, time and volatility.|A local curvature estimate does not describe every large jump.
vega|Vega|Derivatives|Vega measures the option value's sensitivity to the volatility input.|A stock hedge does not remove this exposure.|Option inputs and the size of the volatility change.|Raw vega is per 1.0 volatility change; one percentage point is 0.01.
theta|Theta|Derivatives|Theta measures how option value changes as calendar time passes, holding other inputs fixed.|It separates time sensitivity from movements in spot or volatility.|Remaining time and other option inputs.|Annual theta and daily theta differ; actual P&L also reflects other changing inputs.
rho|Rho|Derivatives|Rho measures sensitivity to the interest-rate input.|Rates can affect option values even if spot does not move.|Rate, remaining time and other option inputs.|Raw rho is per 1.0 rate change, not per percentage point.
implied_volatility|Implied volatility|Numerical methods|The volatility input that makes a chosen option model match a quoted price.|It allows prices to be compared using a model's volatility scale.|Market price and the other fixed pricing inputs.|It is model-dependent and can be unavailable for impossible prices or unstable low-vega quotes.
volatility|Volatility|Derivatives|A scale for price-return variability under a stated model and time unit.|It changes option values and scenario risks.|The selected model input or the chosen return observations.|An option's annual volatility input differs from a daily return volatility estimate.
delta_hedging|Delta hedge|Derivatives|A stock position is used to offset an option portfolio's current first-order stock sensitivity.|It can reduce small-move directional exposure.|Current option quantities, multipliers, deltas and stock position.|Discrete rebalancing, rounding, transaction costs, gamma and vega leave risk.
contract_multiplier|Contract multiplier|Derivatives|The number of underlying units represented by one option contract.|It converts per-unit prices and Greeks into contract or position amounts.|The instrument contract specification.|Confusing one contract with one unit can scale exposure by 100 in this lab.
var|Value at Risk (VaR)|Risk|A loss threshold at a chosen confidence level and horizon.|It summarises a model's loss distribution while allowing worse outcomes.|Holdings, prices, horizon, return model, covariance, confidence and scenario count.|VaR is not the maximum possible loss and does not describe severity beyond its threshold.
expected_shortfall|Expected Shortfall|Risk|The average loss in the worst selected fraction of outcomes.|It describes tail severity beyond the VaR threshold.|The complete loss tail, confidence level and scenario assumptions.|A few tail observations give a fragile estimate; rare unmodelled events remain possible.
stress_testing|Stress P&L|Risk|The portfolio is repriced under a specified hypothetical shock.|It asks about vulnerabilities that an ordinary risk model may miss.|Selected shocks and current holdings.|A stress is a conditional scenario, not a probability forecast or an actual trade.
drawdown|Drawdown|Risk|The fall from the account's previous peak marked value.|It records the loss experienced along a path, not just the final outcome.|The sequence of marked account values.|A past maximum drawdown is not a future loss limit.
exposure|Exposure|Risk|A description of how positions respond to prices or other risk factors.|It helps identify what can move portfolio value.|Positions, marks, multipliers and sensitivities.|Gross, net, delta and notional exposure answer different questions.
regression|Regression fit|Statistical arbitrage|A fitted line summarises how one observed series relates to another.|It supplies a hedge-ratio estimate and residual for a stated training window.|Training observations, intercept convention and model specification.|A fitted relationship is not evidence of a real-world causal link.
regression_beta|Regression beta|Statistical arbitrage|The slope of the fitted relationship between Y and X.|It determines the model's units of X per unit of Y.|The past training window and ordinary least squares fit.|A statistically fitted ratio is not guaranteed to be stable or executable at exact sizes.
residual|Residual / spread|Statistical arbitrage|The difference between Y and the fitted value predicted from X.|It separates the fitted relationship from its current deviation.|Current X and Y, fitted intercept and fitted slope.|A residual can drift or break; a large value need not revert.
z_score|Z-score|Statistical arbitrage|The residual's distance from its recent mean in units of recent standard deviation.|It expresses a deviation relative to its own recent scale.|Current residual, earlier residual mean and earlier residual standard deviation.|A z-score is not a probability or a trade recommendation; tiny variance can make it unstable.
stat_arb_signal|Stat-arb decision|Statistical arbitrage|A prespecified rule maps an observed residual score and position state to an action.|It makes entry, exit and risk conditions explicit and testable.|Z-score, entry/exit/stop thresholds, holdings and risk limits.|Qualifying for entry does not guarantee a fill, convergence or profitable exit.
leg_risk|Incomplete pair risk|Statistical arbitrage|One leg can execute while the other remains unfilled.|The temporary position can carry directional exposure the intended pair would reduce.|Execution order, each book's depth and actual filled sizes.|An intended hedge is not an executed hedge.
lookahead_bias|Look-ahead bias|Research methods|A decision uses information that would only be available later.|It can create a backtest advantage that cannot be traded in sequence.|Training boundaries, normalisation windows and data availability.|A clean split is necessary but does not establish that a strategy will generalise.
selection_bias|Winner's curse|Research methods|Selecting the best noisy result tends to select some favourable noise.|Best-of-many backtests can disappoint on untouched data.|Number of candidates, noise and selection protocol.|An impressive selected result is not independent evidence after selection.
monte_carlo|Monte Carlo|Numerical methods|Repeated model-generated scenarios approximate an average or distribution.|It supports pricing, risk and comparisons when many possible outcomes matter.|Model assumptions, independent paths, seed and estimator.|More paths reduce sampling noise, not model error.
root_finding|Root finding|Numerical methods|A numerical search finds an input that makes a specified discrepancy zero.|The IV solver uses it to match an option model price to a quote.|Target, bracket, tolerance and derivative behaviour.|A failed solve must remain unavailable rather than return a plausible-looking number.
randomness|Deterministic seeds|Engineering / reproducibility|A seed identifies a reproducible sequence of pseudorandom draws.|It lets another run reproduce a result or a bug.|Root seed, named child streams, model version and actions.|The same seed is not enough if the model, draw order or actions change.
reproducibility|Verified replay|Engineering / reproducibility|The same supported model and recorded actions recreate checked results.|It makes execution and accounting auditable.|Versions, configuration, seed and ordered actions.|Replay agreement proves consistency of an implementation, not realism of its assumptions.
integer_ticks|Integer ticks|Engineering / reproducibility|Matching prices are whole increments on a price grid.|Exact tick comparisons avoid floating-point ambiguity in price priority.|The instrument tick size and valid integer prices.|Fractional analytical values may still exist; execution must obey the grid.
event_driven|Event-driven clock|Engineering / reproducibility|The simulated clock advances between explicit actions and arrivals.|It gives every matching decision a defined ordering.|Event times and deterministic tie-breaking sequence.|It models ordering, not production exchange latency or network timing.
architecture|UI / engine separation|Engineering / reproducibility|The browser displays Python results; the engine decides trades and accounts.|A presentation change must not invent a fill or alter a risk calculation.|Public API responses and the validated financial modules.|A readable explanation does not replace reconciliation and regression checks.
common_random_numbers|Common random numbers|Research methods|Compared strategies can share exogenous draws within a paired seed.|It can reduce noise in the difference between their outcomes.|Named streams, pairing and strategy-dependent decisions.|Shared randomness does not force equal fills or make dependent observations independent.
model_risk|Model risk|Research methods|An answer can be internally correct while its assumptions misrepresent the world.|It connects numerical results to the conditions under which they can mislead.|Dynamics, data, execution rules, estimation and implementation choices.|Passing tests does not prove that a synthetic market resembles a live venue.
mastery|Learning evidence|Engineering / reproducibility|Mastery records assessed reasoning rather than pages opened.|It separates exposure to an explanation from demonstrated understanding.|Submitted quiz answers, evidence and review history.|Reading or running a hypothetical must not increase mastery.
current_price|Current observed price|Trading / execution|The latest price observation revealed in this environment.|It marks holdings and provides context for the next decision.|The next revealed observation or simulated transaction.|A recorded move does not establish its real-market cause; a bar close is not an executable quote.
historical_replay|Historical replay|Engineering / reproducibility|Recorded observations are revealed progressively while paper orders follow an explicit execution rule.|It separates real data from simulated fills and prevents decisions using unseen bars.|Observation clock, source data and execution convention.|Paper fills do not reconstruct exchange executions, queue position or market impact.
market_environments|Market environments|Engineering / reproducibility|The environment defines where observations come from and what the simulator knows.|It distinguishes synthetic model evidence from historical observation and controlled scenarios.|Chosen source, capabilities, provenance and visibility mode.|Evidence from different environments must not be silently pooled or given the same causal interpretation.
""".strip()

LAB_CONCEPTS = {
    "trading": "bid ask spread midpoint depth queue_priority market_orders limit_orders partial_fills vwap position realised_pnl unrealised_pnl pnl_attribution fees markouts drawdown order_size slippage execution_cost",
    "maker": "inventory quote_skew spread_capture adverse_selection order_flow depth spread markouts position pnl_attribution fees exposure queue_priority limit_orders",
    "options": "option_pricing black_scholes delta gamma vega theta rho implied_volatility volatility delta_hedging contract_multiplier pnl_attribution root_finding monte_carlo",
    "risk": "var expected_shortfall covariance correlation covariance_matrices portfolio_variance diversification exposure stress_testing portfolio_optimisation drawdown pnl_attribution model_risk",
    "statarb": "regression regression_beta residual z_score stat_arb_signal correlation leg_risk lookahead_bias position pnl_attribution execution_cost selection_bias standard_deviation",
    "research": "sample_mean standard_deviation standard_error confidence_intervals expectation variance monte_carlo common_random_numbers selection_bias lookahead_bias reproducibility model_risk",
    "learning": "mastery architecture integer_ticks event_driven randomness reproducibility common_random_numbers model_risk expectation standard_error confidence_intervals lookahead_bias",
}
LAB_CONCEPTS = {k: tuple(v.split()) for k, v in LAB_CONCEPTS.items()}

PREREQUISITES = {
    "spread": ("bid", "ask"),
    "midpoint": ("bid", "ask"),
    "vwap": ("partial_fills",),
    "slippage": ("vwap",),
    "execution_cost": ("slippage", "fees"),
    "unrealised_pnl": ("position",),
    "realised_pnl": ("position",),
    "pnl_attribution": ("realised_pnl", "unrealised_pnl"),
    "markouts": ("midpoint",),
    "quote_skew": ("inventory", "spread"),
    "adverse_selection": ("markouts",),
    "standard_deviation": ("variance",),
    "standard_error": ("standard_deviation", "sample_mean"),
    "confidence_intervals": ("standard_error",),
    "correlation": ("covariance",),
    "covariance_matrices": ("covariance",),
    "portfolio_variance": ("covariance_matrices",),
    "diversification": ("portfolio_variance", "correlation"),
    "portfolio_optimisation": ("portfolio_variance",),
    "gamma": ("delta",),
    "vega": ("volatility",),
    "theta": ("option_pricing",),
    "delta": ("option_pricing",),
    "delta_hedging": ("delta", "contract_multiplier"),
    "implied_volatility": ("option_pricing", "root_finding"),
    "expected_shortfall": ("var",),
    "regression_beta": ("regression",),
    "residual": ("regression_beta",),
    "z_score": ("residual", "standard_deviation"),
    "stat_arb_signal": ("z_score",),
    "reproducibility": ("randomness",),
    "common_random_numbers": ("randomness",),
}

# Relationship edges are typed. Only prerequisite edges are asserted to be acyclic.
CHAINS = (
    ("order_size", "depth", "slippage", "vwap", "execution_cost", "pnl_attribution"),
    ("volatility", "option_pricing", "vega", "exposure", "var", "stress_testing"),
    (
        "correlation",
        "covariance_matrices",
        "portfolio_variance",
        "var",
        "portfolio_optimisation",
    ),
    ("inventory", "quote_skew", "order_flow", "exposure", "pnl_attribution"),
    ("regression", "residual", "z_score", "stat_arb_signal", "position", "pnl_attribution"),
    (
        "event_driven",
        "market_orders",
        "queue_priority",
        "partial_fills",
        "pnl_attribution",
        "architecture",
    ),
)

ASSUMPTIONS = {
    "execution": {
        "name": "Visible single-venue execution",
        "description": "Displayed FIFO liquidity, no hidden orders, latency or exchange competition.",
        "failure": "Real fills and execution costs can differ when liquidity reacts or moves.",
        "url": "/explain#model_risk",
    },
    "valuation": {
        "name": "Public reference marks",
        "description": "Open positions use the specified public mark and documented fee convention.",
        "failure": "Marked equity can differ from proceeds available on liquidation.",
        "url": "/explain#model_risk",
    },
    "bsm": {
        "name": "European Black–Scholes model",
        "description": "Constant volatility and rates, lognormal underlying and European payoff.",
        "failure": "Jumps, changing IV, smile and exercise features can invalidate local sensitivities.",
        "url": "/explain#black_scholes",
    },
    "risk": {
        "name": "Conditional return scenarios",
        "description": "Selected IID return law, covariance, finite paths and fixed-IV option revaluation.",
        "failure": "Dependence, tail events and volatility shocks outside that model can be missed.",
        "url": "/explain#var",
    },
    "regression": {
        "name": "Past-window linear relationship",
        "description": "OLS training and z-score normalisation use only earlier published observations.",
        "failure": "Breaks, drift and serial dependence can make a fitted spread unreliable.",
        "url": "/explain#regression",
    },
    "inference": {
        "name": "Independent research units",
        "description": "Uncertainty is measured across the defined complete independent runs.",
        "failure": "Dependent or selected samples make ordinary intervals overconfident.",
        "url": "/explain#standard_error",
    },
    "replay": {
        "name": "Versioned deterministic implementation",
        "description": "Same supported versions, seeds, configuration and actions.",
        "failure": "A changed implementation need not reproduce an old stream or result.",
        "url": "/explain#reproducibility",
    },
}

FORMULAS = {
    "spread": (
        "s = a − b",
        {"s": "spread in GBP", "a": "best ask in GBP", "b": "best bid in GBP"},
    ),
    "midpoint": ("m = (b + a) / 2", {"m": "midpoint in GBP", "b": "best bid", "a": "best ask"}),
    "vwap": (
        "VWAP = Σᵢ(Pᵢ Qᵢ) / ΣᵢQᵢ",
        {
            "Pᵢ": "recorded price of fill i in GBP",
            "Qᵢ": "executed units in fill i",
            "i": "fill index",
            "Σ": "sum across recorded fills",
            "VWAP": "quantity-weighted execution price in GBP",
        },
    ),
    "position": (
        "q_new = q_old + signed fill",
        {
            "q_new": "new position in units",
            "q_old": "previous position in units",
            "signed fill": "positive bought units or negative sold units",
        },
    ),
    "pnl_attribution": (
        "P&L = realised gross + unrealised + financing − fees",
        {
            "P&L": "total net marked gain in GBP",
            "realised gross": "closed-lot gain before fees",
            "unrealised": "open-lot gain at the public mark",
            "financing": "accrued funding in GBP",
            "fees": "executed trade charges; stock desk realised already includes these",
        },
    ),
    "markouts": (
        "M = s (R_h − P)",
        {
            "M": "own-side markout, GBP per unit",
            "s": "+1 for buyer, −1 for seller",
            "R_h": "public reference observed at horizon h",
            "P": "execution price",
            "h": "selected future public-event horizon",
        },
    ),
    "quote_skew": (
        "c = r − kq(1 + excess); excess = max(0, |q|−soft)/(hard−soft)",
        {
            "c": "inventory-rule quote centre in ticks",
            "r": "public reference in ticks",
            "k": "inventory sensitivity in ticks per unit",
            "q": "inventory in units",
            "excess": "fraction beyond the soft inventory limit",
            "soft": "soft inventory limit",
            "hard": "hard inventory limit",
            "max": "larger of the two values",
            "|q|": "absolute inventory; candidate bid rounds down and ask rounds up before safety adjustments",
        },
    ),
    "standard_error": (
        "SE(x̄) = s / √n",
        {
            "SE": "estimated uncertainty of the sample mean",
            "x̄": "sample mean",
            "s": "sample standard deviation",
            "n": "number of independent observations",
        },
    ),
    "confidence_intervals": (
        "CI = x̄ ± t* SE",
        {
            "CI": "Student-t mean interval",
            "x̄": "sample mean",
            "t*": "critical value at selected confidence and n−1 degrees of freedom",
            "SE": "standard error",
            "n": "independent observations",
        },
    ),
    "correlation": (
        "ρ = cov(X,Y) / (σ_X σ_Y)",
        {
            "ρ": "linear correlation",
            "cov(X,Y)": "covariance of paired observations",
            "X": "first series",
            "Y": "second series",
            "σ_X": "standard deviation of X",
            "σ_Y": "standard deviation of Y",
        },
    ),
    "covariance": (
        "cov(X,Y) = Σᵢ[(Xᵢ−X̄)(Yᵢ−Ȳ)] / (n−1)",
        {
            "cov(X,Y)": "sample covariance",
            "Xᵢ": "first return at observation i",
            "Yᵢ": "synchronous second return",
            "X̄": "mean first return",
            "Ȳ": "mean second return",
            "n": "paired observations",
            "i": "observation index",
            "Σ": "sum across pairs",
        },
    ),
    "portfolio_variance": (
        "v = wᵀΣw",
        {
            "v": "portfolio variance; GBP² for GBP exposures",
            "w": "exposure vector (or weights for return variance)",
            "Σ": "aligned return covariance matrix",
            "ᵀ": "transpose",
        },
    ),
    "delta": (
        "Δ = ∂V/∂S; position Δ = q × m × Δ",
        {
            "Δ": "option price sensitivity per underlying unit",
            "V": "option model value in GBP per unit",
            "S": "stock price in GBP",
            "∂": "local partial derivative holding other inputs fixed",
            "q": "signed contracts",
            "m": "units per contract",
            "position Δ": "stock-equivalent option exposure",
        },
    ),
    "gamma": (
        "Γ = ∂²V/∂S² = ∂Δ/∂S",
        {
            "Γ": "change in delta per GBP stock move",
            "V": "per-unit option value",
            "S": "stock price",
            "Δ": "delta",
            "∂": "local partial derivative",
        },
    ),
    "vega": (
        "ν = ∂V/∂σ",
        {
            "ν": "vega per 1.0 change in volatility",
            "V": "per-unit option value",
            "σ": "annual volatility as a decimal",
            "∂": "partial derivative holding other inputs fixed",
        },
    ),
    "theta": (
        "Θ = ∂V/∂t; daily Θ = Θ / 365",
        {
            "Θ": "value change per year of elapsed time",
            "V": "per-unit option value",
            "t": "elapsed calendar years",
            "∂": "local partial derivative",
            "daily Θ": "ACT/365 time sensitivity per day",
        },
    ),
    "rho": (
        "ρ_option = ∂V/∂r",
        {
            "ρ_option": "rate sensitivity, unrelated to correlation rho",
            "V": "option value per unit",
            "r": "annual rate as a decimal",
            "∂": "local partial derivative",
        },
    ),
    "implied_volatility": (
        "price_model(σ_IV) = P_quote",
        {
            "price_model": "approved option-pricing API with other inputs fixed",
            "σ_IV": "implied annual volatility",
            "P_quote": "chosen market price per unit",
        },
    ),
    "var": (
        "VaR_α = inf{x : F_L(x) ≥ α}; L = −P&L",
        {
            "VaR_α": "loss threshold at confidence α",
            "α": "confidence level",
            "F_L": "loss cumulative distribution",
            "x": "candidate loss in GBP",
            "inf": "lowest qualifying threshold",
            "L": "loss over the specified horizon",
            "P&L": "scenario profit/loss",
        },
    ),
    "expected_shortfall": (
        "ES_α = (1/(1−α)) ∫ₐ¹ VaR_u du",
        {
            "ES_α": "average worst 1−α loss mass",
            "α": "confidence level",
            "u": "tail quantile level",
            "VaR_u": "loss quantile at u",
            "∫": "integration; engine uses exact fractional boundary mass for finite samples",
        },
    ),
    "regression": (
        "Y = α + βX + ε",
        {
            "Y": "response price",
            "X": "predictor price",
            "α": "fitted intercept",
            "β": "fitted slope",
            "ε": "residual",
        },
    ),
    "residual": (
        "e_t = Y_t − (α + βX_t)",
        {
            "e_t": "current residual",
            "Y_t": "current published Y price",
            "X_t": "current published X price",
            "α": "past-only fitted intercept",
            "β": "past-only fitted slope",
            "t": "current observation index",
        },
    ),
    "z_score": (
        "z_t = (e_t − μ_past) / s_past",
        {
            "z_t": "current standardised residual",
            "e_t": "current residual",
            "μ_past": "mean of earlier window residuals",
            "s_past": "sample standard deviation of those earlier residuals",
            "t": "current observation index excluded from normalisation",
        },
    ),
}

USES = {
    "Trading / execution": "Order handling, execution analysis and transaction-cost analysis; live venues have additional fees, latency and order types.",
    "Market mechanics": "Exchange order handling and liquidity assessment; QuantLab models one visible FIFO book.",
    "Market microstructure": "Liquidity provision and execution-quality review; public outcomes alone do not identify private information.",
    "Probability": "Scenario-based decision analysis, pricing and risk; probabilities remain conditional on the chosen model.",
    "Statistics": "Research uncertainty and performance measurement; dependent financial data need appropriate inference methods.",
    "Derivatives": "Option hedging, derivatives market making and portfolio risk; production pricing can use surfaces and richer models.",
    "Risk": "Market-risk measurement, limits and reporting contexts; this educational implementation is not a regulatory capital engine.",
    "Portfolio theory": "Portfolio allocation, factor risk and diversification analysis; real constraints and estimates are more complex.",
    "Statistical arbitrage": "Econometric relationship modelling, factor models and pairs research; regression alone is not a trading edge.",
    "Numerical methods": "Derivatives valuation, calibration and scenario estimation; numerical accuracy is separate from model accuracy.",
    "Research methods": "Strategy evaluation and model validation; untouched evaluation data and prespecified comparisons matter.",
    "Engineering / reproducibility": "Auditable trading and research software, incident reproduction and model governance.",
}


@dataclass(frozen=True)
class Concept:
    id: str
    name: str
    domain: str
    definition: str
    matters: str
    changes: str
    limitation: str

    def public(self):
        parents = PREREQUISITES.get(self.id, ())
        upstream, downstream = [], []
        for chain in CHAINS:
            for a, b in zip(chain, chain[1:], strict=False):
                if b == self.id:
                    upstream.append(a)
                if a == self.id:
                    downstream.append(b)
        formula, variables = FORMULAS.get(self.id, (None, {}))
        assumption = (
            "bsm"
            if self.domain == "Derivatives" or self.id == "implied_volatility"
            else "risk"
            if self.domain in ("Risk", "Portfolio theory")
            else "regression"
            if self.domain == "Statistical arbitrage"
            else "inference"
            if self.domain in ("Probability", "Statistics", "Research methods")
            else "replay"
            if self.domain == "Engineering / reproducibility"
            else "valuation"
            if self.id in ("pnl_attribution", "realised_pnl", "unrealised_pnl", "markouts")
            else "execution"
        )
        locations = [
            {"lab": k, "url": LAB_PATHS[k]} for k, ids in LAB_CONCEPTS.items() if self.id in ids
        ]
        if self.id in ("current_price", "historical_replay", "market_environments"):
            locations = [{"lab": "trading", "url": "/"}]
        return asdict(self) | dict(
            prerequisites=list(parents),
            related=sorted(set(parents) | set(upstream) | set(downstream)),
            affected_by=sorted(set(upstream)),
            affects=sorted(set(downstream)),
            maths={"equation": formula, "variables": variables},
            uses=USES[self.domain],
            locations=locations,
            assumptions=[assumption],
            depths=list(DEPTHS),
            misconception=self.limitation,
            interview=f"For {self.name.lower()}, which input or assumption would you check before trusting the interpretation? Explain your reasoning using the displayed evidence.",
        )


CONCEPTS = {}
for _line in _ROWS.splitlines():
    _c = Concept(*_line.split("|"))
    if _c.id in CONCEPTS:
        raise ValueError("Duplicate explanation concept")
    CONCEPTS[_c.id] = _c

ALIASES = {
    "mid": "midpoint",
    "pnl": "pnl_attribution",
    "p&l": "pnl_attribution",
    "iv": "implied_volatility",
    "es": "expected_shortfall",
    "beta": "regression_beta",
    "z-score": "z_score",
    "zscore": "z_score",
    "look-ahead": "lookahead_bias",
    "se": "standard_error",
    "ci": "confidence_intervals",
    "skew": "quote_skew",
    "markout": "markouts",
}


def resolve(key):
    value = ALIASES.get(key.lower(), key.lower()) if isinstance(key, str) else ""
    if value not in CONCEPTS:
        raise ValueError("Choose an available explanation concept")
    return value


def search(query="", lab=None):
    if not isinstance(query, str) or len(query) > 200:
        raise ValueError("Search is limited to 200 characters")
    if lab is not None and lab not in LAB_CONCEPTS:
        raise ValueError("Unknown lab")
    words = re.findall(r"p&l|[a-z0-9]+(?:-[a-z]+)?", query.lower())
    words = [
        w
        for w in words
        if w
        not in {
            "why",
            "did",
            "my",
            "what",
            "does",
            "the",
            "is",
            "a",
            "current",
            "explain",
            "affect",
            "affects",
            "rise",
            "change",
            "changed",
        }
    ]
    ids = LAB_CONCEPTS[lab] if lab else CONCEPTS
    rows = []
    for key in ids:
        c = CONCEPTS[key]
        text = (key + " " + c.name + " " + c.definition + " " + c.changes).lower()
        score = sum(
            10
            if ALIASES.get(w, w) == key or w == key
            else 2
            if w in c.name.lower()
            else 1
            if w in text
            else 0
            for w in words
        )
        if not words or score:
            rows.append(
                dict(id=key, name=c.name, domain=c.domain, definition=c.definition, score=score)
            )
    return sorted(rows, key=lambda x: (-x["score"], x["name"]))[:80]


def graph(chain=0):
    if type(chain) is not int or not 0 <= chain < len(CHAINS):
        raise ValueError("Choose a concept-map chain")
    nodes = CHAINS[chain]
    return dict(
        nodes=[CONCEPTS[k].public() for k in nodes],
        edges=[
            dict(
                source=a,
                target=b,
                relation="model-dependent contributor / dependency; not real-world causation",
            )
            for a, b in zip(nodes, nodes[1:], strict=False)
        ],
    )
