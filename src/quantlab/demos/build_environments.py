"""Phase 13 source labels, historical execution and hidden-scenario reveal rules."""

from quantlab.demos import SEED
from quantlab.demos.build_trading import act
from quantlab.demos.models import Evidence, Moment, choice
from quantlab.demos.projections import labelled
from quantlab.environments.fixtures import fixtures
from quantlab.environments.historical import HistoricalSession
from quantlab.environments.scenarios import ScenarioSession


def build(spec, branch="full"):
    moments = []
    historical = spec.builder == "historical"
    hidden = spec.builder == "hidden"
    s = (
        HistoricalSession(fixtures())
        if historical
        else ScenarioSession("liquidity_shock", seed=SEED, steps=40, hidden=hidden)
    )

    def event(key, title, action, concept, kind, payload, question, **extra):
        before = labelled(s.public())
        act(s, kind, **payload)
        moments.append(
            Moment(key, title, action, concept, before, labelled(s.public()), question, **extra)
        )

    if historical:
        event(
            "request",
            "An observation and a paper order",
            "Submit a BUY 3 MARKET instruction for FIXTURE-X",
            "historical_replay",
            "order",
            dict(instrument="FIXTURE-X", side="buy", quantity=3, order_type="market"),
            choice(
                "historical_replay",
                (
                    "Do these bars prove where your order would actually have filled "
                    "on an exchange?"
                ),
            ),
            observation=(
                "These artificial OHLCV bars exercise historical replay. They are "
                "NOT real market observations. Your instruction waits for the "
                "next revealed close."
            ),
            capture_before="historical-before-order",
        )
        event(
            "next-close",
            "Reveal the next observation",
            "Advance one bar; apply the documented paper execution rule",
            "vwap",
            "step",
            dict(count=1),
            choice(
                "historical_replay",
                (
                    "Does OHLCV contain the queue and order-book depth needed to "
                    "prove a historical fill?"
                ),
            ),
            result_note=(
                "The next recorded fixture close is an input. The paper fill adds "
                "configured slippage, uses a volume cap and books fees. No real "
                "historical fill or hidden cause is established."
            ),
            capture_after="historical-after-paper-fill",
        )
        limits = (
            "ARTIFICIAL TEST FIXTURE, not actual historical market data.",
            (
                "SIMULATED HISTORICAL EXECUTION: next revealed close, adverse "
                "tick, shared volume cap and fees; OHLC contains no queue truth."
            ),
            "Recorded movements alone do not establish why a real market moved.",
        )
    else:
        for i, count in enumerate((19, 2, 3)):
            event(
                f"public-{i}",
                "Observe the next part of the scenario",
                "Advance public observations",
                "market_environments",
                "step",
                dict(count=count),
                choice(
                    "market_environments",
                    "Does a change in public liquidity establish a unique hidden cause?",
                )
                if i == 0
                else None,
                observation=(
                    "Use visible prices and quantities to form a hypothesis. Hidden "
                    "configuration stays unavailable until explicit ended-session "
                    "hindsight."
                )
                if hidden
                else (
                    "A known controlled scenario changes an existing engine input; "
                    "observe its public consequences."
                ),
            )
        limits = (
            "Controlled synthetic scenario; not a real-market forecast.",
            (
                "A public pattern supports hypotheses, not a unique "
                "identification of a hidden scenario."
            ),
        )
    act(s, "end")
    return Evidence(
        spec,
        moments,
        {"fixture": "Phase 13 fixture_inputs; 100 bars"}
        if historical
        else {"description": "Hidden scenario configuration withheld"}
        if hidden
        else {"scenario": "liquidity_shock", "seed": SEED},
        limits,
        s.journal(),
        private={} if historical else s.reveal(),
    )
