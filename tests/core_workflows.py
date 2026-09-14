"""Executable release acceptance workflows; use real orders and independent identities."""

import json
import math
import tempfile
from pathlib import Path

from quantlab.research.adapters.maker import MakerAdapter, maker_configuration
from quantlab.research.engine import execute
from quantlab.research.models import ExperimentSpec, Variant
from quantlab.research.seeds import SeedPlan
from quantlab.risk.analytics import FACTORS, RiskSettings
from quantlab.risk.session import RiskSession, replay_risk
from quantlab.statarb.risk import consolidated
from quantlab.statarb.session import StatArbSession, replay
from quantlab.tutor.adapters import research_contexts
from quantlab.tutor.service import Tutor


def reconcile(p):
    assert math.isclose(p["equity"], p["cash"] + p["market_value"], abs_tol=1e-7)
    assert math.isclose(
        p["pnl"],
        p["realised_gross"] + p["unrealised"] + p["financing"] - p["fees"],
        abs_tol=1e-7,
    )
    for key in ("delta", "gamma", "vega", "theta", "rho"):
        assert math.isclose(
            p["greeks"][key], sum(r["greeks"][key] for r in p["positions"]), abs_tol=1e-8
        )
    return {key: p[key] for key in ("cash", "market_value", "equity", "pnl", "fees")}


def portfolio_workflow():
    s = RiskSession(settings=RiskSettings(paths=200, sample_size=80))
    rows = []

    def event(label, target, kind, **payload):
        result = s.execute(target, kind, **payload)
        assert result["result"].get("ok", True), result["result"]
        if kind == "option_order":
            assert result["result"]["filled"] == payload["quantity"]
        rows.append(dict(event=label, **reconcile(s.portfolio().public())))

    event(
        "A1 buy three manual-desk stock units",
        "desk",
        "order",
        side="buy",
        quantity=3,
        order_type="market",
    )
    event(
        "A2 buy one call, multiplier 100",
        "options",
        "option_order",
        contract_id=s.options.selected,
        side="buy",
        quantity=1,
        quote_revision=s.options.quote_revision,
    )
    event("A3 sell actual stock delta hedge", "options", "hedge")
    before = s.options.accounts()
    event(
        "D1 inspect spot -5%, IV +10 percentage points",
        "risk",
        "scenario",
        stock_return=-0.05,
        volatility_change=0.10,
    )
    assert s.options.accounts() == before
    shock = s.state()["scenario"]
    tails = s.state()["report"]["monte_carlo"]["full"]
    assert tails["es"] >= tails["var"]
    event("A4 observe one day", "options", "step", count=1)
    event(
        "A5 close call at its current bid",
        "options",
        "option_order",
        contract_id=s.options.selected,
        side="sell",
        quantity=1,
        quote_revision=s.options.quote_revision,
    )
    for target, venue in [("options", s.options.stock), ("desk", s.desk)]:
        q = venue.account.inventory
        if q:
            event(
                "A6 close stock through its own book",
                target,
                "stock_order" if target == "options" else "order",
                side="sell" if q > 0 else "buy",
                quantity=abs(q),
                order_type="market",
            )
        venue.check_invariants()
    final = s.portfolio().public()
    assert not final["positions"] and abs(final["unrealised"]) < 1e-9
    event("A7 end and verify replay", "risk", "end")
    journal = s.journal()
    assert replay_risk(json.loads(json.dumps(journal)))[0].journal() == journal
    return dict(events=rows, stress=shock, var=tails["var"], es=tails["es"], replay=True)


def maker_workflow(directory):
    adapter = MakerAdapter()
    config = maker_configuration(duration_us=2_000_000)
    a, b = adapter.run(111042, config, full=True), adapter.run(111042, config, full=False)
    assert a.metrics == b.metrics and a.trajectory_fingerprint == b.trajectory_fingerprint
    spec = ExperimentSpec(
        "Do full and light modes agree?",
        "Logging does not alter executions or accounting.",
        SeedPlan(111042, "development", 4),
        (Variant("fixed", config),),
        adapter.name,
        bootstrap_resamples=40,
    )
    record = execute(spec, adapter, directory)
    assert record["status"] == "complete"
    contexts = research_contexts(directory)
    tutor = Tutor()
    tutor.study(contexts)
    assert tutor.active is not None
    assert a.metrics == b.metrics
    return dict(
        runs=len(record["runs"]),
        full_light_identical=True,
        outcome_digest=record["outcome_digest"],
        tutor_concept=tutor.active["concept"],
    )


def pair_workflow():
    s = StatArbSession(seed=111042)
    assert s.command("step", count=80)["ok"]
    assert s.command("liquidity", instrument="SA-X", depth=0)["ok"]
    assert s.command("pair", action="long")["ok"]
    assert s.command("next_leg")["ok"]
    assert s.market.venues["SA-X"].account.inventory == 0
    assert s.market.venues["SA-Y"].account.inventory > 0
    risk = RiskSession(settings=RiskSettings(paths=100, sample_size=20))
    combined = consolidated(risk.portfolio(), FACTORS, risk.settings.covariance(), s.market)
    before = reconcile(combined["portfolio"])
    assert combined["linear"]["es"] >= combined["linear"]["var"]
    assert s.command("liquidity", instrument="SA-X", depth=40)["ok"]
    assert s.command("close")["ok"]
    if s.pending:
        assert s.command("next_leg")["ok"]
    for venue in s.market.venues.values():
        venue.check_invariants()
        assert venue.account.inventory == 0
    assert s.command("end")["ok"]
    assert replay(s.journal()).journal() == s.journal()
    return dict(
        incomplete_position=before,
        stress=combined["stress"],
        final=s.metrics(),
        attribution=s.attribution,
        replay=True,
    )


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as directory:
        output = dict(
            A_and_D=portfolio_workflow(),
            B=maker_workflow(Path(directory) / "research"),
            C=pair_workflow(),
        )
    print(json.dumps(output, indent=2, allow_nan=False))
