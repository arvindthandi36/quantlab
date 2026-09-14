"Phase 8 lessons, parameterised from strictly public current derivative observations."

from quantlab.tutor.context import FIELDS, PublicContext


def derivative_context(snapshot, source, event_type="observation", *, solver=None, mc=None):
    q = snapshot["selected"]
    g = q.get("greeks", {})
    position = next((p for p in snapshot["positions"] if p["id"] == q["id"]), None)
    trade = next(
        (t for t in reversed(snapshot["option_trades"]) if t["contract_id"] == q["id"]), {}
    )
    solver = solver or {}
    mc = mc or {}
    f = {
        "contract_id": q["id"],
        "option_type": q["type"],
        "spot": snapshot["spot"],
        "strike": q["strike"],
        "time_years": q["remaining_years"],
        "multiplier": q["multiplier"],
        "quantity": position["quantity"] if position else 0,
        "model_value": q.get("model_value", q.get("payoff")),
        "bid": q.get("bid"),
        "ask": q.get("ask"),
        "midpoint": q.get("midpoint"),
        "volatility": q.get("volatility_input"),
        "implied_volatility": q.get("iv", {}).get("volatility"),
        "rate": snapshot["rate"],
        **{k: g.get(k) for k in ("delta", "gamma", "vega", "theta", "rho")},
        "option_delta": snapshot["greeks"]["option_delta"],
        "portfolio_delta": snapshot["greeks"]["delta"],
        "stock_position": snapshot["stock"]["account"]["position"],
        "option_pnl": snapshot["accounts"]["option_gross_pnl"],
        "hedge_pnl": snapshot["accounts"]["hedge_gross_pnl"],
        "total_pnl": snapshot["accounts"]["total_pnl"],
        "realised_volatility": snapshot["accounts"]["realised_volatility"],
        "event_type": event_type,
        "trade_quantity": trade.get("filled"),
        "trade_premium": trade.get("premium"),
        "premium_cash_flow": trade.get("premium_cash_flow"),
        "fee": trade.get("fee"),
        "trade_side": trade.get("side", ""),
        "solver_method": solver.get("method", ""),
        "solver_iterations": solver.get("iterations"),
        "solver_residual": solver.get("residual"),
        "solver_converged": solver.get("converged"),
        "mc_estimate": mc.get("estimate"),
        "mc_se": mc.get("standard_error"),
        "mc_paths": mc.get("paths"),
    }
    return PublicContext(
        source,
        "derivatives",
        snapshot["revision"],
        snapshot["step"] * 1_000_000,
        {k: f[k] for k in FIELDS["derivatives"]},
    )


# Every lesson has a distinct misconception; no unrestricted prose pseudo-grading.
LESSONS = {
    "call": (
        "What does this European call give its holder?",
        "The right, without obligation, to buy at strike at expiry",
        "An obligation to buy stock immediately",
        (
            "A call benefits from the right to buy at a fixed contractual price. This "
            "lab cash-settles the equivalent payoff."
        ),
        (
            "Call payoff = max(S_T − K, 0); S_T is stock at expiry and K is strike, per "
            "underlying unit."
        ),
        "Why is the seller's obligation different from the buyer's right?",
    ),
    "put": (
        "What does this European put give its holder?",
        "The right, without obligation, to sell at strike at expiry",
        "An obligation to sell stock immediately",
        (
            "A put provides the right to sell at a fixed contractual price. This lab "
            "cash-settles the equivalent payoff."
        ),
        (
            "Put payoff = max(K − S_T, 0); K is strike and S_T is stock at expiry, per "
            "underlying unit."
        ),
        "Why can a put gain when stock falls?",
    ),
    "strike": (
        "Which number is fixed by the option contract?",
        "Its strike, the contractual exercise price",
        "The stock price at expiry",
        "Strike is the agreed exercise price; the future stock price is unknown.",
        "K denotes strike in GBP per underlying unit. It is fixed before trading.",
        "Why does the same strike mean different moneyness for a call and a put?",
    ),
    "expiry": (
        "What happens to a held option at its expiry in this lab?",
        "It cash-settles intrinsic payoff once and stops having time value",
        "Its remaining time value continues indefinitely",
        (
            "European exercise occurs at expiry. Cash settlement replaces the option "
            "with its payoff, not a stock trade."
        ),
        (
            "T = max(expiry year fraction − elapsed year fraction, 0); ACT/365 converts "
            "days into years."
        ),
        "Why must settlement align with the simulation clock?",
    ),
    "premium": (
        "A short option receives premium. Is that already realised profit?",
        "No: cash arrives alongside an open option liability",
        "Yes: all premium received is immediately profit",
        (
            "Premium is the execution price paid or received for an option. An open "
            "liability still has to be valued."
        ),
        (
            "Cash flow = −q × m × p; q is signed contracts, m multiplier, p execution "
            "premium per underlying unit. Fees are separate."
        ),
        "Explain how cash can rise while marked P&L falls.",
    ),
    "intrinsic_value": (
        "What is intrinsic value?",
        "The nonnegative payoff if exercise used the current stock price",
        "The entire option premium at every maturity",
        (
            "Intrinsic value measures immediate exercise payoff. European contracts "
            "cannot necessarily be exercised now."
        ),
        (
            "Call intrinsic = max(S−K,0); put intrinsic = max(K−S,0); S is current "
            "stock and K strike."
        ),
        (
            "Can a European option trade below immediate intrinsic under some rates or "
            "dividends?"
        ),
    ),
    "time_value": (
        "How is quoted premium beyond immediate intrinsic defined?",
        (
            "Premium minus immediate intrinsic, which need not always be positive for "
            "European options"
        ),
        "A guaranteed daily profit for the holder",
        (
            "Time value is a descriptive difference, not a guaranteed positive amount "
            "under every carry assumption."
        ),
        (
            "Time value = V − intrinsic; V is current premium. Discounting and "
            "dividends affect European exercise comparisons."
        ),
        ("Why should immediate exercise intuition be used carefully for European contracts?"),
    ),
    "moneyness": (
        "At the same stock and strike, how do call and put moneyness relate?",
        "A stock above strike makes the call ITM and put OTM",
        "Both must be ITM whenever stock rises",
        (
            "Moneyness compares the current stock with the fixed strike. ATM means the "
            "prices coincide, not that profit is guaranteed."
        ),
        (
            "Call ITM: S>K; put ITM: S<K; ATM: S=K. ITM describes intrinsic payoff, not "
            "net trading profit."
        ),
        "Can an ITM option still lose money for its purchaser?",
    ),
    "black_scholes": (
        "Which statement correctly describes Black–Scholes here?",
        (
            "An idealised European model with constant inputs and continuous "
            "frictionless replication"
        ),
        "A guarantee that synthetic quotes equal real-world fair value",
        (
            "The model prices a contingent payoff under restrictive assumptions. Actual "
            "synthetic fills use dealer bid/ask."
        ),
        (
            "V = exp(−rT) E_Q[payoff]; r is rate, T years, E_Q risk-neutral "
            "expectation. The pricing drift is r−q_div, not a forecast return."
        ),
        "Which assumption breaks when you hedge once a day through a spread?",
    ),
    "put_call_parity": (
        "Does an apparent parity gap automatically prove free arbitrage?",
        (
            "No: check identical contracts, rates/dividends and executable prices, "
            "funding and fees"
        ),
        "Yes: any gap between displayed model numbers guarantees profit",
        (
            "Call plus discounted strike and put plus discounted stock have matching "
            "European expiry payoffs under common assumptions."
        ),
        (
            "C−P = S exp(−q_div T)−K exp(−rT); C/P are call/put prices, S stock, K "
            "strike, r rate, q_div dividend yield, T years."
        ),
        ("Why are bid/ask prices more relevant than rounded midpoints to an arbitrage claim?"),
    ),
    "delta": (
        "What does this option's model delta measure first?",
        "Its approximate price sensitivity to a small stock-price change",
        "The literal real-world probability of finishing ITM",
        (
            "Delta is the local slope of option value as stock moves, with other "
            "pricing inputs held fixed."
        ),
        (
            "Delta = ∂V/∂S; V is option value per underlying unit and S stock price. "
            "Small change: dV ≈ delta × dS."
        ),
        "Why is call delta not simply the real-world probability of finishing ITM?",
    ),
    "gamma": (
        "Why can this delta hedge become imperfect after a stock move?",
        "Gamma makes option delta change as stock changes",
        "A delta-neutral position has no remaining risks",
        (
            "Gamma measures how the slope itself changes. A hedge chosen now need not "
            "offset tomorrow's delta."
        ),
        ("Gamma = ∂²V/∂S² = ∂delta/∂S; ddelta ≈ gamma × dS. This is a local approximation."),
        "Why can short gamma hurt after either direction of a large stock move?",
    ),
    "vega": (
        "What does vega measure?",
        "Option-price sensitivity to a change in annual decimal volatility",
        "The guaranteed return from holding an option",
        (
            "A volatility change alters the model's distribution of possible outcomes "
            "and therefore the option value."
        ),
        (
            "Vega = ∂V/∂sigma per 1.00 volatility. For one percentage point, dV ≈ vega "
            "× 0.01; sigma is an annual decimal."
        ),
        "Stock is unchanged but the option rises. How could volatility explain it?",
    ),
    "theta": (
        "What is the theta sign convention in this lab?",
        "Price change per elapsed model year, holding other inputs fixed",
        "Price change per extra year remaining, with the opposite sign",
        (
            "Theta isolates calendar-time passage. Many conventional long options have "
            "negative theta, but not every European option always does."
        ),
        (
            "Theta = −∂V/∂T, where T is remaining years. Displayed daily theta = "
            "theta/365 under ACT/365."
        ),
        "Why does negative theta not imply tomorrow's total option P&L must be negative?",
    ),
    "rho": (
        "What does rho isolate?",
        "Sensitivity to the continuously compounded annual rate",
        "Sensitivity to a one-pound stock-price move",
        "Rates change discounting and carry; rho holds the other model inputs fixed.",
        (
            "Rho = ∂V/∂r per 1.00 annual rate. A one-percentage-point rate move "
            "multiplies rho by 0.01."
        ),
        "Why do European call and put rho often have opposite signs?",
    ),
    "implied_volatility": (
        "What is implied volatility inferred from this synthetic quote?",
        "The volatility that makes this model reproduce its price",
        "A guaranteed forecast of future realised volatility",
        (
            "IV reverses the pricing calculation. It depends on the chosen model and "
            "observed price, not access to the future."
        ),
        (
            "Find sigma with f(sigma)=V(sigma)−observed premium=0, holding stock, "
            "strike, time and rate fixed."
        ),
        "Why can IV be unreliable for a near-bound option price?",
    ),
    "realised_volatility": (
        "How is realised volatility different from the quote's IV?",
        ("It summarises already observed stock returns; IV is inferred from an option price"),
        "It reveals the next stock return before it happens",
        (
            "Realised volatility looks backward over this recorded path. The configured "
            "process volatility is also not an exact realised outcome."
        ),
        (
            "RV = sqrt(sum(log(S_i/S_(i−1))²)/(n×dt)); n is observed intervals and dt "
            "years per interval. This quadratic-variation estimate includes "
            "finite-sample drift effects."
        ),
        "Why does realised above implied not guarantee a profitable long-option trade?",
    ),
    "delta_hedging": (
        "How does a delta hedge happen here?",
        "Submit stock orders through the exchange to offset current option delta",
        "Silently change stock inventory to the mathematical target",
        (
            "Hedging is an actual trade. Whole units, bid/ask, depth and future changes "
            "prevent perfect continuous replication."
        ),
        (
            "Option exposure = sum(q_j × m_j × delta_j); target stock = minus that "
            "exposure, rounded to whole units. q_j is signed contracts and m_j "
            "multiplier."
        ),
        "Why can more frequent hedging reduce exposure yet increase costs?",
    ),
    "contract_multiplier": (
        "What changes when the contract multiplier is 100?",
        ("One contract's cash value and Greeks are 100 times their per-underlying-unit values"),
        "The quoted premium is already 100 contracts' total value",
        (
            "The multiplier specifies how many underlying units each option contract "
            "represents. Quantity and multiplier are separate."
        ),
        "Position Greek = signed contracts × multiplier × per-underlying-unit Greek.",
        (
            "What is the delta exposure of short 10 contracts with delta 0.60 and "
            "multiplier 100?"
        ),
    ),
    "newton_raphson": (
        "Why can Newton's IV step fail when vega is tiny?",
        "Dividing the price error by tiny vega can produce an unstable volatility jump",
        "Tiny vega guarantees rapid convergence",
        (
            "Newton uses the slope to estimate how far to move. A shallow price curve "
            "makes that estimate unreliable; a bracket supplies a safer fallback."
        ),
        (
            "sigma_next = sigma − f(sigma)/vega; f= model price − target price and "
            "vega=∂V/∂sigma."
        ),
        "Why should a small pricing residual alone not always be called a reliable IV?",
    ),
    "root_finding": (
        "What is the IV solver trying to make zero?",
        "Model option price minus the observed option price",
        "The option price itself",
        (
            "Root finding searches for the input where a function crosses zero. Here "
            "the input is volatility."
        ),
        (
            "f(sigma)=model_price(sigma)−market_price. Bisection retains lo/hi with "
            "f(lo)≤0≤f(hi), then halves the bracket."
        ),
        "Why must feasibility and a valid bracket be checked first?",
    ),
    "finite_differences": (
        "Why compare analytic delta with a finite difference?",
        ("It independently checks whether a small price bump gives the expected sensitivity"),
        "It proves the synthetic market matches real markets",
        (
            "Bump an input, reprice, and compare the observed numerical slope with the "
            "analytic formula. Too large or too tiny a bump causes different errors."
        ),
        (
            "delta_FD ≈ [V(S+h)−V(S−h)]/(2h); h is a small stock-price bump. Gamma uses "
            "[V(S+h)−2V(S)+V(S−h)]/h²."
        ),
        "Explain truncation error versus floating-point cancellation.",
    ),
    "monte_carlo_pricing": (
        "Which drift belongs in this risk-neutral option pricing simulation?",
        "Risk-free rate minus continuous dividend yield",
        "An assumed high physical stock return to make the option attractive",
        (
            "Sample possible terminal stock prices under the pricing measure, compute "
            "each payoff, discount and average. Black–Scholes is faster when its closed "
            "form applies."
        ),
        (
            "S_T=S exp((r−q_div−sigma²/2)T+sigma sqrt(T)Z); Z is standard normal. "
            "Estimate V=average(exp(−rT)payoff). SE=s/sqrt(n), with s payoff SD and n "
            "IID paths."
        ),
        ("Why does reducing sampling error tenfold require roughly 100 times as many paths?"),
    ),
}
ALIASES = {
    "option_pricing": "black_scholes",
    "greeks": "delta",
    "volatility": "implied_volatility",
    "hedging": "delta_hedging",
    "derivatives": "delta",
}


def option_question(concept, context, difficulty=1):
    from quantlab.tutor.questions import Question, describe

    key = ALIASES.get(concept, concept)
    prompt, correct, wrong, intuition, maths, interview = LESSONS[key]
    f = context.facts
    if key == "premium" and f["trade_side"] == "buy":
        prompt = "You paid premium for this option. Is it all immediately a realised loss?"
        correct = "No: cash falls but you also hold an option asset"
        wrong = "Yes: the entire premium becomes a realised loss immediately"
        intuition = (
            "Premium buys an option asset. Its marked value, subsequent gains or losses "
            "and fees determine P&L; paying cash is not itself the same as losing it."
        )
    expected = "mechanism"
    options = (("mechanism", correct), ("mistake", wrong))
    level, answer_type, tolerance = 1, "choice", "0"
    if difficulty == 2:
        number = None
        if key in ("delta", "contract_multiplier") and f["delta"] is not None:
            number = f["quantity"] * f["multiplier"] * f["delta"]
            prompt = (
                f"The selected position is {f['quantity']} contracts, multiplier "
                f"{f['multiplier']}, delta {f['delta']:.8f}. What is its approximate "
                "signed option delta in stock units?"
            )
        elif key == "delta_hedging":
            number = round(-f["option_delta"]) - f["stock_position"]
            prompt = (
                f"All options have delta {f['option_delta']:.8f}; you hold "
                f"{f['stock_position']} stock units. What signed whole-unit stock trade "
                "reaches the nearest delta-neutral target (positive = buy)?"
            )
        elif key in ("vega", "theta", "rho") and f[key] is not None:
            divisor = 365 if key == "theta" else 100
            number = f[key] / divisor
            convention = (
                "the daily theta convention"
                if key == "theta"
                else "sensitivity per one percentage-point change"
            )
            prompt = (
                f"Per-unit annual {key} is {f[key]:.8f}. Convert it to {convention} "
                "in GBP per underlying unit."
            )
        elif key in ("call", "put", "intrinsic_value"):
            sign = (
                1
                if (key == "call" or (key == "intrinsic_value" and f["option_type"] == "call"))
                else -1
            )
            number = max(0, sign * (f["spot"] - f["strike"]))
            kind = f["option_type"] if key == "intrinsic_value" else key
            prompt = (
                f"Hypothetical exercise at the currently observed stock £{f['spot']:g}, "
                f"strike £{f['strike']:g}: what is the per-unit {kind} intrinsic payoff?"
            )
        elif key == "premium" and f["trade_premium"] is not None:
            number = f["premium_cash_flow"]
            prompt = (
                f"Your actual {f['trade_side']} filled {f['trade_quantity']} contracts "
                f"at £{f['trade_premium']}, multiplier {f['multiplier']}. What was the "
                "signed premium cash flow, before fees (received positive)?"
            )
        elif key == "expiry":
            number = f["time_years"]
            prompt = (
                f"The selected option has {f['time_years'] * 365:.8f} ACT/365 days "
                "remaining. Express this in model years."
            )
        elif key == "monte_carlo_pricing" and f["mc_se"] is not None:
            number = f["mc_se"] / 2
            prompt = (
                f"The actual pricing run used {f['mc_paths']} IID paths and SE "
                f"{f['mc_se']:.8f}. Hypothetically quadrupling paths with unchanged "
                "payoff SD gives approximately what SE?"
            )
        if number is not None:
            expected = str(number)
            maths += f" In this recorded example, the calculation gives {number:.8f}."
            level, answer_type, options, tolerance = 2, "number", (), "0.00001"
    elif difficulty >= 3:
        level = min(4, difficulty)
        prompt = (
            "Defend this interpretation"
            if level == 3
            else "Criticise the model and generalise cautiously"
        ) + f" for {concept.replace('_', ' ')}. Select both defensible claims."
        expected = ("mechanism", "limits")
        options = (
            ("mechanism", correct),
            (
                "limits",
                (
                    "The conclusion is conditional on current inputs, explicit units "
                    "and model assumptions"
                ),
            ),
            ("mistake", wrong),
            ("future", "The next underlying move is already known from this observation"),
        )
        answer_type = "choices"
    return Question(
        concept,
        level,
        prompt,
        answer_type,
        expected,
        options,
        (
            (
                "Separate what is observed now, what the contract promises, and what "
                "the model estimates."
            ),
            intuition,
        ),
        intuition,
        maths,
        describe(context),
        interview,
        f"{concept}: incorrect explicit claim",
        tolerance,
        ("derivatives",),
    )


def option_relevance(context):
    f = context.facts
    keys = [
        f["option_type"],
        "strike",
        "expiry",
        "moneyness",
        "intrinsic_value",
        "time_value",
        "black_scholes",
        "put_call_parity",
        "option_pricing",
        "volatility",
        "contract_multiplier",
    ]
    if f["delta"] is not None:
        keys += [
            "delta",
            "gamma",
            "vega",
            "theta",
            "rho",
            "greeks",
            "derivatives",
            "finite_differences",
            "implied_volatility",
        ]
    if f["trade_premium"] is not None:
        keys += ["premium"]
    if f["quantity"] or f["stock_position"]:
        keys += ["delta_hedging", "hedging"]
    if f["realised_volatility"] is not None:
        keys += ["realised_volatility"]
    if f["solver_iterations"] is not None:
        keys += ["root_finding", "newton_raphson"]
    if f["mc_paths"] is not None:
        keys += ["monte_carlo_pricing"]
    target = {
        "option_order": "premium",
        "hedge": "delta_hedging",
        "stock_order": "delta_hedging",
        "step": "gamma",
        "iv": "newton_raphson",
        "mc": "monte_carlo_pricing",
        "set_iv": "vega",
    }.get(f["event_type"], f["option_type"])
    return [(k, 100 if k == target else 40) for k in keys]
