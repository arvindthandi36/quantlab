"""Actual option contracts and book-executed hedges, with limited user decisions."""

from dataclasses import asdict, replace

from quantlab.demos import SEED
from quantlab.demos.build_trading import act
from quantlab.demos.models import Evidence, Moment, choice
from quantlab.demos.projections import calculation, point
from quantlab.options.analytics import curves, realised_volatility
from quantlab.options.iv import implied_volatility
from quantlab.options.session import OptionsConfig, OptionsSession

LIMITS = (
    (
        "European cash-settled options, fixed model assumptions and "
        "finite synthetic dealer quotes."
    ),
    (
        "Stock hedges execute against the existing FIFO book with fees. A "
        "nearest whole-unit hedge leaves residual delta."
    ),
    "A hedge changes exposure; it does not remove gamma, vega, jumps, costs or model risk.",
)


def build(spec, branch="full"):
    s = OptionsSession(OptionsConfig(seed=SEED, steps=10))
    moments = []

    def snap():
        return point(s.snapshot(include_curves=True), "options")

    def event(key, title, action, concept, kind, payload, question=None, **extra):
        before = snap()
        act(s, kind, **payload)
        moments.append(Moment(key, title, action, concept, before, snap(), question, **extra))

    if spec.builder == "solver":
        quote = s.quotes[s.selected]
        x = quote.inputs
        kind = quote.contract.option_type
        before = calculation(
            {"inputs": asdict(x), "observed_quote_midpoint": float(quote.midpoint)},
            note="Existing safeguarded implied-volatility solver on a synthetic option quote.",
        )
        after = calculation(
            {
                "Newton": implied_volatility(kind, x, float(quote.midpoint)).public(),
                "Bisection fallback": implied_volatility(
                    kind, x, float(quote.midpoint), newton_iterations=0
                ).public(),
            }
        )
        moments.append(
            Moment(
                "solve",
                "Recover volatility from a quoted price",
                "Solve the same price with Newton and a forced zero-Newton budget",
                "root_finding",
                before,
                after,
                choice(
                    "root_finding",
                    "Does a solver's convergence prove its pricing model is correct?",
                ),
            )
        )
    elif spec.builder == "option_inputs":
        x = s.quotes[s.selected].inputs
        before = snap()
        after = calculation(
            {"call": curves("call", x, points=21), "put": curves("put", x, points=21)},
            note=(
                "Existing option payoff and Black–Scholes curves; values per "
                "underlying unit, before a contract multiplier."
            ),
            charts=(
                {
                    "title": "Call: value and expiry payoff",
                    "x": "Stock price £",
                    "y": "Option £ per unit",
                    "series": [
                        {
                            "name": "Model value",
                            "points": [
                                [r["spot"], r["value"]] for r in curves("call", x, points=21)
                            ],
                        },
                        {
                            "name": "Expiry payoff",
                            "points": [
                                [r["spot"], r["payoff"]] for r in curves("call", x, points=21)
                            ],
                        },
                    ],
                },
            ),
        )
        moments.append(
            Moment(
                "inputs",
                "A contract and its price inputs",
                "Calculate call and put curves with the existing pricing functions",
                "option_pricing",
                before,
                after,
                choice(
                    "option_pricing", "Is an option's current premium always its expiry payoff?"
                ),
            )
        )
    else:
        event(
            "buy",
            "Own one call contract",
            "Buy one at-the-money call, multiplier 100",
            "option_pricing",
            "option_order",
            dict(
                contract_id=s.selected, side="buy", quantity=1, quote_revision=s.quote_revision
            ),
            choice(
                "delta", "Does one call contract necessarily have the exposure of one share?"
            ),
        )
        q = replace(
            choice(
                "delta_hedging",
                (
                    "How many signed stock units approximately offset the displayed "
                    "option delta? (negative means sell)"
                ),
                context=(
                    "Use the displayed aggregate option delta. Round to a whole stock unit."
                ),
                hints=(
                    "One stock unit contributes +1 delta; a short contributes −1.",
                    "Choose the opposite sign of the aggregate option delta.",
                ),
            ),
            answer_type="number",
            expected=str(round(-s.aggregate_greeks()["option_delta"])),
            options=(),
            tolerance="0.5",
        )
        before = snap()
        if branch == "full":
            act(s, "hedge")
        elif branch == "partial":
            target = round(-s.aggregate_greeks()["option_delta"] / 2)
            if target:
                act(
                    s, "stock_order", side="buy" if target > 0 else "sell", quantity=abs(target)
                )
        elif branch != "none":
            raise ValueError("Choose full, partial or none")
        moments.append(
            Moment(
                "hedge",
                "Choose your initial hedge",
                f"Execute the {branch} hedge choice through the stock book",
                "delta_hedging",
                before,
                snap(),
                q,
                observation=(
                    "Option delta estimates sensitivity to a small stock-price move. "
                    "Aggregate delta includes the 100-unit contract multiplier."
                ),
                result_note=(
                    "Read actual stock fills, fees and resulting aggregate delta. The "
                    "partial and unhedged choices deliberately retain more delta."
                ),
                capture_before="delta-before-hedge",
                capture_after="delta-after-hedge",
                branch=True,
            )
        )
        event(
            "move",
            "Move the underlying market",
            "Advance one model day",
            "gamma",
            "step",
            dict(count=1),
            choice(
                "gamma", "Must the old hedge still offset the option after its inputs change?"
            ),
            result_note=(
                "Gamma describes delta's sensitivity to spot; time and volatility "
                "inputs can also change delta. Use the actual before/after model "
                "values."
            ),
        )
        event(
            "rehedge",
            "Review the new exposure",
            "Re-hedge to the nearest whole stock unit",
            "delta_hedging",
            "hedge",
            {},
            choice("delta_hedging", "Does reducing delta also remove vega?"),
        )
        event(
            "shock",
            "Change the volatility assumption",
            "Raise input implied volatility to 0.30",
            "vega",
            "set_iv",
            dict(volatility=0.30),
            choice(
                "vega",
                (
                    "For a long vanilla option, higher volatility generally moves its "
                    "model value which way, holding other inputs fixed?"
                ),
                correct="up",
                options=(("up", "Up"), ("down", "Down")),
            ),
            capture_after="delta-after-volatility-shock",
        )
        moments[-1].after["measured_volatility"] = {
            "realised": realised_volatility([h["spot"] for h in s.history], float(s.dt)),
            "implied_input": s.current_iv,
            ("note"): (
                "One realised interval is extremely noisy; implied volatility is "
                "a pricing input, not a realised outcome."
            ),
        }
    act(s, "end")
    return Evidence(
        spec,
        moments,
        {"seed": SEED, "options": asdict(s.config), "initial_hedge": branch},
        LIMITS,
        s.journal(),
    )
