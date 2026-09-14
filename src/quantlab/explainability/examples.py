"""Small reusable engine-backed examples, always separate from a user's session."""

from dataclasses import asdict, replace

from quantlab.explainability.evidence import trading
from quantlab.explainability.sandbox import inventory, order_size
from quantlab.options.models import PricingInputs
from quantlab.options.pricing import greeks, price
from quantlab.research.statistics import summarise
from quantlab.risk.analytics import diversification, tail_example
from quantlab.trading.scenarios import select_scenario
from quantlab.trading.session import TradingSession

EXAMPLES = {
    "sweep": ("Market order sweeps levels", "market_orders"),
    "vwap": ("Unequal fill quantities", "vwap"),
    "limit": ("A limit order waits", "limit_orders"),
    "short": ("A rising mark hurts a short", "position"),
    "markout": ("Negative markout is an outcome, not an identity test", "markouts"),
    "inventory": ("Long inventory lowers the configured centre", "quote_skew"),
    "se": ("Four times as many independent observations", "standard_error"),
    "winner": ("Best-of-many selects some noise", "selection_bias"),
    "hedge": ("A stock hedge goes stale", "delta_hedging"),
    "vega": ("Delta-neutral still has volatility risk", "vega"),
    "tails": ("Same VaR, different tails", "expected_shortfall"),
    "correlation": ("Correlation and diversification", "correlation"),
    "residual": ("High correlation and an unstable residual", "regression"),
    "lookahead": ("Tomorrow cannot rewrite today's signal", "lookahead_bias"),
}


def example(id):
    if id not in EXAMPLES:
        raise ValueError("Choose an available guided example")
    name, concept = EXAMPLES[id]
    note = "Independent educational inputs; no user-session values or results are invented."
    if id in ("sweep", "vwap", "limit", "inventory"):
        s = TradingSession(select_scenario())
        if id == "sweep":
            data = order_size(s.public_snapshot(), {"quantity": 20})
        elif id == "inventory":
            data = inventory(s.public_snapshot(), {"inventory": 20})
        else:
            s.command(
                "order",
                side="buy",
                quantity=6 if id == "vwap" else 1,
                order_type="market" if id == "vwap" else "limit",
                **({} if id == "vwap" else {"price": "99.98"}),
            )
            data = trading("vwap" if id == "vwap" else "limit_orders", s.public_snapshot())
    elif id == "short":
        from fractions import Fraction

        from quantlab.domain import Side
        from quantlab.portfolio.accounting import MakerAccount, MakerFill

        a = MakerAccount(Fraction(1000000), Fraction(10000), hard_limit=20)
        a.apply(
            MakerFill(
                1, 0, 1, Side.SELL, 2, 10000, Fraction(0), Fraction(10000), Fraction(10000)
            )
        )
        before = asdict(a.snapshot())
        a.mark(Fraction(10100))
        after = asdict(a.snapshot())
        data = {
            "before_ticks": {k: str(v) for k, v in before.items()},
            "after_ticks": {k: str(v) for k, v in after.items()},
        }
        note = (
            "The same core account holds −2 units. Raising the public mark from "
            "£100 to £101 reduces marked P&L by £2 while sale cash stays "
            "unchanged."
        )
    elif id == "markout":
        data = {
            "reasoning": (
                "A seller can receive a negative later markout after an unrelated "
                "public price move. Counterparty identity cannot be recovered from "
                "that one outcome."
            ),
            "counterfactual": (
                "Both noise and informed traders can be followed by favourable or "
                "adverse price movements."
            ),
        }
    elif id == "se":
        data = {
            "four_observations": asdict(summarise([-3.0, -1.0, 1.0, 3.0])),
            "sixteen_observations": asdict(summarise([-7.0, -1.0] + [0.0] * 12 + [1.0, 7.0])),
        }
        note = (
            "Two controlled illustrative lists with identical sample standard "
            "deviation, evaluated by the core statistics API. The "
            "sixteen-observation standard error is exactly half the "
            "four-observation one. In research this scaling requires independent "
            "observations and stable dispersion; these constructed lists are not "
            "new empirical evidence."
        )
    elif id == "winner":
        data = {
            "training_means": {"A": 0.2, "B": 0.1, "C": 0.8},
            "untouched_example_means": {"A": 0.2, "B": 0.1, "C": -0.1},
            "selected_on_training": "C",
        }
        note = (
            "A deliberately constructed reasoning example, not a QuantLab "
            "experiment or empirical estimate. Picking C on the training means "
            "does not make its untouched mean positive. Every attempted candidate"
            " belongs in a research record."
        )
    elif id in ("hedge", "vega"):
        x = PricingInputs(100, 100, 30 / 365, 0.2)
        y = replace(x, spot=102) if id == "hedge" else replace(x, volatility=0.3)
        data = {
            "before": {
                "inputs": asdict(x),
                "value": price("call", x),
                "greeks": greeks("call", x).public(),
            },
            "after": {
                "inputs": asdict(y),
                "value": price("call", y),
                "greeks": greeks("call", y).public(),
            },
        }
        note = (
            "One independent call, per underlying unit, repriced by the approved "
            "model. A fixed stock hedge cannot follow a changing delta or offset "
            "a volatility sensitivity. Multiply by the explicit contract size for"
            " contract exposure."
        )
    elif id == "tails":
        data = tail_example()
    elif id == "correlation":
        data = diversification()
    else:
        from quantlab.statarb.examples import teaching_cases
        from quantlab.statarb.statistics import CausalModel

        if id == "residual":
            data = teaching_cases()
        else:
            from quantlab.statarb.research import generate

            points, _ = generate(201042, steps=120)
            a = CausalModel().at(points, 80)
            other = points.copy()
            other[81:] = other[81:] * 1.7
            b = CausalModel().at(other, 80)
            data = {
                "before_future_mutation": a,
                "after_future_mutation": b,
                "identical": a == b,
            }
            note = (
                "The core causal model slices to the available prefix before fitting."
                " Changing unpublished rows after observation 80 leaves observation "
                "80's signal identical."
            )
    return dict(
        id=id,
        title=name,
        concept=concept,
        label="INDEPENDENT GUIDED EXAMPLE — NOT YOUR SESSION",
        note=note,
        result=data,
    )
