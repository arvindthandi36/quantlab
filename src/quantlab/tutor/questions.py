"""Parameterized local questions and explicit validators; no open-text pseudo-grading."""

import re
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256

from quantlab.execution import vwap
from quantlab.tutor.catalog import ACTIVE_CONCEPTS as CONCEPTS
from quantlab.tutor.catalog import OPTION_CONCEPTS
from quantlab.tutor.context import PublicContext
from quantlab.tutor.curriculum import ADDITIONAL, REASONING


@dataclass(frozen=True)
class Question:
    concept: str
    difficulty: int
    prompt: str
    answer_type: str
    expected: object
    options: tuple[tuple[str, str], ...]
    hints: tuple[str, str]
    intuition: str
    maths: str
    quantlab: str
    interview: str
    misconception: str
    tolerance: str = "0"
    triggers: tuple[str, ...] = ()

    def validate(self, answer):
        if self.answer_type == "number":
            if type(answer) not in (str, int) or isinstance(answer, bool):
                raise ValueError("Enter a finite number, without a currency symbol")
            try:
                if len(str(answer)) > 100:
                    raise ValueError("Answer is too long")
                exponent = re.search(r"[eE]([+-]?\d+)$", str(answer))
                if exponent and abs(int(exponent.group(1))) > 18:
                    raise ValueError("Exponent outside educational answer range")
                value = Fraction(answer)
            except (ValueError, ZeroDivisionError, OverflowError) as exc:
                raise ValueError("Enter a finite number or fraction") from exc
            return abs(value - Fraction(self.expected)) <= Fraction(self.tolerance)
        valid = {key for key, _ in self.options}
        if self.answer_type == "choices":
            if not isinstance(answer, list) or any(type(x) is not str for x in answer):
                raise ValueError("Select the reasons you consider valid")
            if len(set(answer)) != len(answer) or not set(answer) <= valid or not answer:
                raise ValueError("Select valid choices once each")
            return set(answer) == set(self.expected)
        if not isinstance(answer, str) or answer not in valid:
            raise ValueError("Choose one of the listed answers")
        return answer == self.expected

    def public(self, reveal=False):
        # Vary the answer position without consulting any random generator.
        # Only the public question and choice ID participate, never correctness.
        options = sorted(
            self.options,
            key=lambda option: sha256(
                f"{self.concept}\0{self.difficulty}\0{self.prompt}\0{option[0]}".encode()
            ).digest(),
        )
        result = {
            "concept": self.concept,
            "difficulty": self.difficulty,
            "prompt": self.prompt,
            "answer_type": self.answer_type,
            "options": [{"id": key, "text": text} for key, text in options],
            "prerequisites": CONCEPTS[self.concept].prerequisites,
            "quantlab": self.quantlab,
            "triggers": self.triggers,
            "tolerance": self.tolerance,
        }
        if reveal:
            result["layers"] = {
                "intuition": self.intuition,
                "maths": self.maths,
                "quantlab": self.quantlab,
                "interview": self.interview,
            }
            result["expected"] = self.expected
        return result


def _price(value):
    return (
        "unavailable"
        if value is None
        else f"£{float(Fraction(str(value))):.5f}".rstrip("0").rstrip(".")
    )


def describe(context):
    f = context.facts
    if context.kind == "statarb":
        return f"{context.source}, observed event {context.event}: " + ", ".join(
            f"{k}={v}" for k, v in f.items()
        )
    if context.kind == "risk":
        f = context.facts
        return (
            f"{context.source}, risk event {context.event}: equity GBP {f['equity']:.4f}, "
            f"delta {f['delta']:.6f}, vega {f['vega']:.6f}; "
            f"{100 * f['confidence']:.2f}% VaR {f['var']}, ES {f['es']}, "
            f"variance {f['variance']:.8f}, sample {f['sample_n']}; hypothetical model risk."
        )
    f = context.facts
    at = f"{context.source}, public event {context.event}, {context.time_us / 1e6:.6f}s"
    if context.kind == "derivatives":
        delta = "undefined" if f["delta"] is None else f"{f['delta']:.6f}"
        execution = (
            (
                f" Latest selected-contract execution: {f['trade_side']} "
                f"{f['trade_quantity']} × {f['multiplier']} at £{f['trade_premium']:.6f}; "
                f"premium cash flow £{f['premium_cash_flow']:.4f}, fee £{f['fee']:.4f}."
            )
            if f["trade_premium"] is not None
            else ""
        )
        return (
            f"{context.source}, derivatives event {context.event}: {f['option_type']} "
            f"strike £{f['strike']:g}, {f['time_years'] * 365:.3f} ACT/365 days remaining, "
            f"stock £{f['spot']:.4f}; {f['quantity']} contracts × {f['multiplier']}. "
            f"Current model delta {delta}; stock position {f['stock_position']}." + execution
        )
    if context.kind == "execution":
        executions = "; ".join(f"{x['quantity']} @ {_price(x['price'])}" for x in f["fills"])
        return (
            f"{at}: {f['order_id']} {f['side']} {f['original']} {f['type']}; "
            f"{f['filled']} filled, {f['remaining']} waiting, {f['cancelled']} cancelled. "
            + (f"Actual fills: {executions}." if executions else "No executions yet.")
        )
    if context.kind == "book":
        return f"{at}: best bid {_price(f['bid'])}; best ask {_price(f['ask'])}."
    if context.kind == "position":
        return (
            f"{at}: position {f['position']}, limit ±{f['limit']}, "
            f"public reference {_price(f['reference'])}, net P&L {_price(f['pnl'])}."
        )
    if context.kind == "markout":
        return (
            f"{at}: trade {f['trade_id']}, {f['role']}, matured "
            f"{f['horizon']}-event markout {_price(f['value'])} per unit."
        )
    if context.kind == "quotes":
        return (
            f"{at}: position {f['position']}, reference {_price(f['reference'])}; "
            f"own bids {list(f['bids'])}, asks {list(f['asks'])}."
        )
    result = (
        f"{context.source}: {f['variant']}, {f['n']} sessions, mean {f['mean']:.6g}, "
        f"SD {f['sd']:.6g}, SE {f['se']:.6g} ({f['unit']}); "
        f"range {f['minimum']:.6g} to {f['maximum']:.6g}."
    )
    if f["paired"]:
        result += (
            f" Paired difference mean {f['mean_difference']:.6g}; "
            f"paired SE {f['paired_se']:.6g}; "
            f"independent-sample SE benchmark {f['unpaired_se']:.6g}."
        )
    return result


# Conceptual distractors are intentionally explicit. Selecting them supplies evidence;
# ungraded prose never supplies evidence for a misconception.
LESSONS = {
    "vwap": (
        "Which average describes this order's execution price?",
        "weighted",
        (
            ("weighted", "Weight each actual price by the units executed there"),
            ("mid", "Use the displayed midpoint"),
            ("equal", "Give each price level equal weight"),
        ),
        "VWAP gives each executed unit equal weight, so larger fills count more.",
        "VWAP = Σ(pᵢqᵢ)/Σqᵢ; pᵢ is execution price and qᵢ its quantity. Fees are separate.",
        "Why can a large order's VWAP be worse than the best displayed ask?",
        "vwap_is_mid_or_unweighted",
    ),
    "liquidity": (
        "Your order encounters limited visible quantity. What determines its fills?",
        "orders",
        (
            ("orders", "Actual eligible opposite orders, at their resting prices"),
            ("mid", "The midpoint supplies any requested quantity"),
            ("guaranteed", "All market orders must fill fully"),
        ),
        "Liquidity is actual quantity someone is willing to trade at a price.",
        "Filled quantity ≤ eligible available quantity; remainder = requested − filled.",
        "Why does displayed depth not guarantee execution after a delay?",
        "market_order_guarantees_liquidity",
    ),
    "slippage": (
        "Why can an order's VWAP be worse than the first execution price?",
        "depth",
        (
            ("depth", "Later units may consume worse prices deeper in the book"),
            ("fee", "VWAP automatically adds all fees"),
            ("bug", "Every multi-price fill is a bug"),
        ),
        "As nearby quantity runs out, further units may require worse prices.",
        (
            "Buy execution slippage = VWAP − chosen pre-trade ask benchmark; sell sign "
            "reverses. State the benchmark."
        ),
        "What benchmark and timing would make a slippage comparison fair?",
        "slippage_is_fee_or_bug",
    ),
    "limit_orders": (
        "What does your limit price mean?",
        "boundary",
        (
            (
                "boundary",
                "A maximum buy price or minimum sell price; a better resting price is allowed",
            ),
            ("exact", "Every fill must occur exactly at my limit"),
            ("promise", "The whole order is guaranteed to fill"),
        ),
        (
            "A limit is your price boundary. It does not guarantee execution or require "
            "that exact price."
        ),
        "Buy fill p ≤ L; sell fill p ≥ L. L is your limit and p the resting execution price.",
        "How can a limit order be an aggressor now and a liquidity provider later?",
        "limit_price_must_be_paid",
    ),
    "queue_priority": (
        "At the same eligible price, which resting order goes first?",
        "earlier",
        (
            ("earlier", "The order accepted earlier"),
            ("larger", "The larger order"),
            ("mine", "My manual order"),
        ),
        "Price priority comes first; equal prices retain arrival order.",
        "Within a price level, smaller arrival sequence executes first (FIFO).",
        "What happens to priority when you cancel and re-enter a quote?",
        "manual_order_skips_fifo",
    ),
    "partial_fills": (
        "Your order filled some units. What can cancelling it remove?",
        "waiting",
        (
            ("waiting", "Only units still waiting in the book"),
            ("all", "All original units including executions"),
            ("nothing", "Partial fills can never have a cancellable remainder"),
        ),
        "An execution has happened; cancellation only removes waiting quantity.",
        (
            "Original = filled + resting + cancelled; each executed unit has both a "
            "buyer and seller."
        ),
        "How does an unfilled market remainder differ from an unfilled limit remainder?",
        "cancel_reverses_executions",
    ),
    "inventory": (
        "What does a negative position mean?",
        "short",
        (
            ("short", "You are short; buying moves the position toward zero"),
            ("long", "You own extra units"),
            ("cash", "It proves your cash is negative"),
        ),
        "Position counts signed units. Buying adds; selling subtracts. Cash is separate.",
        "q_after = q_before + buys − sells, with quantities measured in units.",
        "Can selling increase cash while making total P&L worse?",
        "position_is_cash",
    ),
    "exposure": (
        "With the position held fixed, what determines sensitivity to a public price move?",
        "signed",
        (
            ("signed", "Signed position multiplied by the price change"),
            ("cash", "Cash received from the latest sale alone"),
            ("safe", "A short position benefits from rising prices"),
        ),
        "A long gains when its reference rises; a short loses. More units magnify the change.",
        "ΔP&L = qΔR for fixed position q and reference change ΔR, excluding new trades/fees.",
        "Why does lower inventory not automatically guarantee lower total risk?",
        "short_benefits_from_rise",
    ),
    "markouts": (
        "What does this matured markout measure?",
        "diagnostic",
        (
            ("diagnostic", "Later signed midpoint change from execution price; a diagnostic"),
            ("profit", "Additional profit to add to account P&L"),
            ("future", "A known future price available before the trade"),
        ),
        (
            "A markout compares an execution with a later observed reference; it is not "
            "account profit."
        ),
        (
            "mₕ = s(Mₜ₊ₕ − P), where s is +1 buy/−1 sell, P execution, M later public "
            "mid, h public actions."
        ),
        "How should provider and aggressor markouts be interpreted differently?",
        "markout_is_pnl",
    ),
    "adverse_selection": (
        "Does a negative provider markout prove the buyer or seller was informed?",
        "no",
        (
            ("no", "No; informed selection is one possible explanation among others"),
            ("yes", "Yes; the sign identifies an informed counterparty"),
            ("profit", "No; it is automatically a realised profit"),
        ),
        "A later adverse move can be consistent with information asymmetry without proving it.",
        (
            "Negative provider mₕ means the later mid moved against that resting side "
            "relative to its fill; causation is not identified."
        ),
        "Give two explanations for negative marks besides informed trading.",
        "negative_mark_proves_informed",
    ),
    "spread_capture": (
        (
            "Can providing liquidity lose money despite selling above and buying below "
            "a reference?"
        ),
        "yes",
        (
            ("yes", "Yes; inventory movement, selection and fees can outweigh spread capture"),
            ("no", "No; a positive quoted spread guarantees profit"),
            ("double", "Only if markouts are added to P&L"),
        ),
        "A spread is an opportunity, not locked-in profit; inventory remains exposed.",
        (
            "Net P&L = spread-capture attribution + inventory-movement attribution − "
            "fees; do not add markouts."
        ),
        "Why is a high maker fill rate not sufficient evidence of good quotes?",
        "positive_spread_guarantees_profit",
    ),
    "sample_mean": (
        "Does the observed mean guarantee the next simulated result?",
        "no",
        (
            ("no", "No; individual outcomes vary and the sample mean is uncertain"),
            ("yes", "Yes; the next run must equal the average"),
            ("alpha", "A positive mean proves real-market alpha"),
        ),
        "A sample average summarises these runs; it is not a promise for the next one.",
        "x̄ = Σxᵢ/n; xᵢ is one session outcome and n the session count.",
        "What else do you need before treating a positive mean as attractive?",
        "expectation_is_guaranteed",
    ),
    "standard_error": (
        "Which quantity describes uncertainty in the estimated mean?",
        "se",
        (
            ("se", "Standard error"),
            ("sd", "Standard deviation of individual outcomes"),
            ("none", "A sample mean has no uncertainty"),
        ),
        "SD measures dispersion among runs; SE measures uncertainty in their average.",
        (
            "SE ≈ s/√n for independent identically distributed sessions; s is sample SD "
            "and n count."
        ),
        "Why does SE scale with 1/√n, and when can that fail?",
        "sd_confused_with_se",
    ),
    "correlation": (
        "Why can pairing comparable random market paths reduce uncertainty in a difference?",
        "cov",
        (
            ("cov", "Positive covariance cancels some shared noise in the difference"),
            ("always", "Pairing always reduces error, whatever the covariance"),
            ("same", "Paired strategies are forced to have identical trades"),
        ),
        (
            "Shared weather can make two outcomes move together; subtracting removes "
            "some shared variation."
        ),
        "Var(B−A)=Var(B)+Var(A)−2Cov(A,B); positive covariance can reduce difference variance.",
        "When might common random numbers fail to improve precision?",
        "pairing_always_helps",
    ),
    "selection_bias": (
        "After selecting the best of several noisy variants, what should you do?",
        "fresh",
        (
            ("fresh", "Use genuinely untouched evaluation and report the selection process"),
            ("winner", "Declare the largest development mean optimal"),
            ("peek", "Keep inspecting the same evaluation seeds until the answer improves"),
        ),
        (
            "Picking a winner also picks favourable noise; repeated evaluation peeking "
            "weakens independence."
        ),
        (
            "max(sample means) selects on both true effects and estimation errors; "
            "fresh evaluation estimates the selected rule."
        ),
        "Why does adding more variants increase selection optimism?",
        "development_winner_is_optimal",
    ),
    "hypothesis_testing": (
        "Does statistical significance alone establish a useful trading improvement?",
        "no",
        (
            ("no", "No; effect size, costs, downside and model error still matter"),
            ("yes", "Yes; any small p-value makes a strategy attractive"),
            ("certainty", "It gives the probability that the strategy will profit next"),
        ),
        "An effect can be measured precisely yet be too small or risky to matter.",
        (
            "t = mean difference / SE under the test assumptions; compare effect "
            "magnitude with a stated practical threshold."
        ),
        "How can a tiny significant effect and a large uncertain effect both be unattractive?",
        "significance_is_economic_value",
    ),
    "drawdown": (
        "What does maximum drawdown retain after a recovery?",
        "fall",
        (
            ("fall", "The largest earlier fall from a previous equity/P&L peak"),
            ("final", "Only the final P&L"),
            ("erase", "Nothing; recovery erases prior risk"),
        ),
        "Drawdown tracks a painful decline even if you later recover.",
        "DDₜ = max_{u≤t}(P&Lᵤ) − P&Lₜ; maximum drawdown is maxₜ DDₜ, including opening zero.",
        "Why can the best mean outcome still have undesirable tail risk?",
        "drawdown_is_final_pnl",
    ),
    "decision_quality": (
        "Does this trade's financial result alone establish whether the decision was sound?",
        "no",
        (
            (
                "no",
                "No; judge reasoning using information available then, and outcomes separately",
            ),
            ("win", "A profitable trade proves a good decision"),
            ("loss", "A losing trade proves a bad decision"),
        ),
        "Sound reasoning can lose through chance; weak reasoning can get lucky.",
        (
            "Decision quality and outcome quality are separate axes: good/good, "
            "good/bad, bad/good, bad/bad."
        ),
        "What contemporaneous evidence would let you assess reasoning without hindsight?",
        "profit_scores_decision_quality",
    ),
    "reproducibility": (
        "What does deterministic replay let you check?",
        "audit",
        (
            ("audit", "Reproduce actions and verify the resulting book, fills and accounts"),
            ("profit", "Guarantee profits on a future live market"),
            ("same", "Force unchanged trades after changing your orders"),
        ),
        "Replay makes an observed result inspectable and a bug repeatable.",
        (
            "Same version + source events (or seed) + ordered actions → same "
            "deterministic exchange transitions."
        ),
        "Why keep recorded-event replay as well as seed regeneration?",
        "seed_guarantees_unchanged_outcomes",
    ),
    "architecture": (
        "Why keep the UI separate from the matching engine?",
        "truth",
        (
            ("truth", "One financial source of truth, independently testable and replayable"),
            ("ui", "So the UI can invent convenient fills"),
            ("tests", "So UI tests can replace conservation checks"),
        ),
        "One engine determines trades; every interface observes and commands that engine.",
        (
            "Requested quantity = filled + resting + cancelled; buyer fills = seller "
            "fills = trade quantity."
        ),
        "Walk through submit → matching → actual fills → accounting → public UI projection.",
        "ui_may_fabricate_fills",
    ),
    "model_criticism": (
        "What limits conclusions from this synthetic market?",
        "limits",
        (
            (
                "limits",
                (
                    "Simplified arrivals, signals, latency/capital assumptions and "
                    "endogenous marking"
                ),
            ),
            ("none", "A passing test suite proves realistic economics"),
            ("perfect", "Informed traders have perfect future knowledge"),
        ),
        "Correct implementation can still describe an unrealistic economic model.",
        (
            "Simulation inference is conditional on the model; it does not estimate all "
            "real-world model error."
        ),
        "Which informed-signal and execution assumptions would you challenge first?",
        "tests_prove_market_realism",
    ),
    "research_integrity": (
        "What can positive synthetic performance establish?",
        "conditional",
        (
            (
                "conditional",
                "An outcome conditional on the tested model and experimental design",
            ),
            ("alpha", "Real-world alpha and demonstrated trading skill"),
            ("ignore", "Permission to omit losing runs"),
        ),
        "Synthetic profits are evidence about a model experiment, not real-market skill.",
        "Report the complete sample, uncertainty, selection process and model assumptions.",
        "Why are 1,000 complete runs more useful than one selected profitable run?",
        "synthetic_profit_is_real_alpha",
    ),
}

LESSONS.update(ADDITIONAL)


def question_for(concept, context: PublicContext, difficulty=1, *, prediction=False):
    from quantlab.tutor.catalog import RISK_CONCEPTS, STATARB_CONCEPTS

    if concept in STATARB_CONCEPTS and context.kind == "statarb":
        from quantlab.tutor.statarb import statarb_question

        return statarb_question(concept, context, difficulty)
    if concept in STATARB_CONCEPTS and concept not in LESSONS and concept not in RISK_CONCEPTS:
        raise ValueError("This later phase topic requires an actual stat-arb context")

    if concept in RISK_CONCEPTS and context.kind == "risk":
        from quantlab.tutor.risk import risk_question

        return risk_question(concept, context, difficulty)
    if concept in RISK_CONCEPTS and (
        concept not in LESSONS or concept in ("var", "expected_shortfall", "stress_testing")
    ):
        raise ValueError("This later phase topic requires an actual risk context")
    if concept in OPTION_CONCEPTS:
        if context.kind != "derivatives":
            raise ValueError("This later phase topic requires an actual derivatives context")
        from quantlab.tutor.derivatives import option_question

        return option_question(concept, context, difficulty)
    if concept not in CONCEPTS or not CONCEPTS[concept].implemented:
        raise ValueError("This concept belongs to a later phase")
    if difficulty not in (1, 2, 3, 4):
        raise ValueError("Unknown difficulty")
    key = concept
    prompt, answer, choices, intuition, maths, interview, misconception = LESSONS[key]
    hints = (
        "Separate the quantity being asked about from the tempting alternative. "
        "Use the recorded facts, not a future price.",
        "Check the definition and units: execution, position, average and uncertainty "
        "are different quantities. Trace this example one step at a time.",
    )
    if key == "vwap":
        hints = (
            (
                "Treat each executed unit as one observation; price levels can contain "
                "unequal quantities."
            ),
            (
                "Calculate the money exchanged in each fill, add it, then compare with "
                "total executed units."
            ),
        )
    elif key == "limit_orders":
        hints = (
            "Compare a price you are willing to accept with a price somebody already offered.",
            "Would accepting a cheaper resting sell violate a buyer's maximum price?",
        )
    elif key in ("adverse_selection", "markouts"):
        hints = (
            "Separate an observed association from identifying its cause.",
            (
                "Other public orders, cancellations or unrelated price movements can "
                "change the later mid."
            ),
        )
    elif key == "standard_error":
        hints = (
            "Distinguish variation among individual runs from uncertainty about their average.",
            (
                "Averaging independent runs reduces uncertainty about the mean, not the "
                "variability of each run."
            ),
        )
    elif key == "exposure":
        hints = (
            "A short position is negative units; keep that sign when prices change.",
            "Multiply signed units by the reference-price change, not by cash received.",
        )
    f = context.facts
    kind, tolerance = "choice", "0"
    if prediction and context.kind == "book" and f["ask"] is not None:
        below = Fraction(f["ask"]) - Fraction("0.01")
        prompt = (
            f"In this observed book, would a buy limit at {_price(below)} "
            f"cross the best ask {_price(f['ask'])}?"
        )
        answer = "no"
        choices = (
            ("yes", "Yes, it crosses now"),
            ("no", "No, it waits unless the book changes"),
        )
        intuition = (
            "A buy below the cheapest current seller does not cross this "
            "book. Future changes are unknown."
        )
        maths = (
            "Immediate buy eligibility requires limit L ≥ current best ask A. "
            "No future ask is assumed."
        )
        misconception = "limit_guarantees_immediate_fill"
    elif difficulty == 2:
        numeric = None
        if concept == "vwap" and context.kind == "execution" and f["fills"]:
            numeric = vwap((x["price"], x["quantity"]) for x in f["fills"])
            prompt, tolerance = (
                "Calculate this order's VWAP in pounds (five decimal places is enough).",
                "0.000005",
            )
        elif concept == "partial_fills" and context.kind == "execution":
            numeric = f["remaining"]
            prompt = (
                f"After {f['filled']} fills and {f['cancelled']} cancellations "
                f"from {f['original']} units, how many remain waiting?"
            )
        elif concept in ("inventory", "exposure"):
            numeric = Fraction(f["position"]) * Fraction("0.05")
            prompt = (
                f"Hypothetical, not a forecast: with your recorded {f['position']} units "
                "fixed, price rises £0.05. What is Δ marked P&L (£), ignoring trades/fees?"
            )
            maths = (
                "ΔP&L = qΔR; q is signed units, ΔR the hypothetical reference change in pounds."
            )
        elif (
            concept in ("spread", "midpoint")
            and context.kind == "book"
            and f["bid"] is not None
            and f["ask"] is not None
        ):
            numeric = (
                Fraction(f["ask"]) - Fraction(f["bid"])
                if concept == "spread"
                else (Fraction(f["ask"]) + Fraction(f["bid"])) / 2
            )
            prompt = (
                "Calculate the recorded "
                f"{'spread' if concept == 'spread' else 'midpoint'} in pounds."
            )
            maths = "Spread = ask − bid; midpoint = (ask + bid)/2. Quotes are in pounds."
        elif concept == "standard_error" and context.kind == "research":
            numeric = Fraction(str(f["se"])) / 2
            prompt = (
                f"These {f['n']} independent sessions have SD {f['sd']:.6g}. Hypothetically "
                "quadruple the session count with the same SD. "
                "Calculate the new SE (4 decimals)."
            )
            tolerance = "0.0001"
        if numeric is not None:
            kind, answer, choices = "number", str(numeric), ()
            intuition += f" For this calculation the answer is {float(numeric):.6g}."
        else:
            # Do not label an intuition question as a calculation or grant level-2 evidence.
            difficulty = 1
    if difficulty >= 3:
        kind = "choices"
        if difficulty == 3 and key in REASONING:
            prompt, right1, right2, wrong1, wrong2 = REASONING[key]
        else:
            prompt = (
                f"Defend {CONCEPTS[concept].title.lower()} using this recorded context: "
                "which claims survive scrutiny?"
            )
            right1 = intuition
            right2 = (
                "This explanation depends on the stated model, reference, "
                "units and observation time."
            )
            wrong1 = choices[1][1]
            wrong2 = (
                "A favourable realised outcome alone validates the reasoning "
                "and guarantees future performance."
            )
        prompt += " Select both defensible claims."
        choices = (
            ("mechanism", right1),
            ("scope", right2),
            ("mistake", wrong1),
            ("guarantee", wrong2),
        )
        answer = ("mechanism", "scope")
        intuition = right1 + " " + right2
        # Numerical/definition hints must not inadvertently disclose a higher-level answer.
        hints = (
            "Check the mechanism separately from the assumptions that make it valid.",
            (
                "Distinguish conditional reasoning from guarantees; consider timing and "
                "what is measured."
            ),
        )
    if concept == "pnl_attribution" and context.kind == "position":
        maths += (
            f" Recorded realised {_price(f['realised'])} + unrealised {_price(f['unrealised'])}"
            f" = net {_price(f['pnl'])}."
        )
    if concept == "vwap" and context.kind == "execution" and f["fills"]:
        quantity = sum(fill["quantity"] for fill in f["fills"])
        average = vwap((fill["price"], fill["quantity"]) for fill in f["fills"])
        terms = " + ".join(f"{fill['quantity']}×{_price(fill['price'])}" for fill in f["fills"])
        maths += f" Your order: ({terms})/{quantity} = £{float(average):.5f}."
    return Question(
        concept,
        difficulty,
        prompt,
        kind,
        answer,
        choices,
        hints,
        intuition,
        maths,
        describe(context),
        interview,
        misconception,
        tolerance,
        (context.kind,),
    )


def relevant(context):
    if context.kind == "statarb":
        from quantlab.tutor.statarb import statarb_relevance

        return statarb_relevance(context)
    if context.kind == "risk":
        from quantlab.tutor.risk import risk_relevance

        return risk_relevance(context)
    if context.kind == "derivatives":
        from quantlab.tutor.derivatives import option_relevance

        return option_relevance(context)
    f = context.facts
    if context.kind == "execution":
        result = []
        if len({x["price"] for x in f["fills"]}) > 1:
            result += [("vwap", 100), ("slippage", 85), ("liquidity", 80)]
        if 0 < f["filled"] < f["original"]:
            result += [("partial_fills", 95)]
        if f["remaining"]:
            result += [("limit_orders", 75), ("queue_priority", 70)]
        if f["filled"]:
            result += [("decision_quality", 40), ("pnl_attribution", 45)] + (
                [("market_orders", 30)] if f["type"] == "market" else []
            )
        return result
    if context.kind == "position":
        return (
            [
                ("exposure", 90 if abs(f["position"]) >= f["limit"] * 0.7 else 60),
                ("inventory", 55),
            ]
            if f["position"]
            else []
        ) + (
            [("drawdown", 45)]
            if f["drawdown"] is not None and Fraction(f["drawdown"]) > 0
            else []
        )
    if context.kind == "markout":
        return [("markouts", 65)] + (
            [("adverse_selection", 98)]
            if f["role"] == "provider" and Fraction(f["value"]) < 0
            else []
        )
    if context.kind == "quotes":
        return (
            [("quote_skew", 80), ("spread_capture", 65), ("inventory", 60)]
            if f["bids"] or f["asks"]
            else []
        )
    if context.kind == "research":
        return (
            [
                ("standard_error", 95),
                ("sample_mean", 90),
                ("hypothesis_testing", 60),
                ("research_integrity", 55),
                ("tail_outcomes", 50),
                ("random_variables", 30),
                ("expectation", 30),
                ("variance", 30),
                ("standard_deviation", 30),
                ("distributions", 30),
                ("confidence_intervals", 35),
                ("law_of_large_numbers", 30),
                ("monte_carlo", 30),
                ("randomness", 30),
                ("reproducibility", 30),
            ]
            + ([("selection_bias", 85)] if f["variant_count"] > 2 else [])
            + ([("correlation", 70)] if f["paired"] else [])
        )
    return [
        ("bid", 10),
        ("ask", 10),
        ("spread", 10),
        ("midpoint", 10),
        ("liquidity", 10),
        ("limit_orders", 10),
    ]
