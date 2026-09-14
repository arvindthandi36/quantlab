"""No what-if result may enter a ledger, stream, research record or learner record."""

import copy

import pytest

from quantlab.explainability.sandbox import (
    correlation,
    inventory,
    order_size,
    threshold,
    volatility,
)
from quantlab.options.models import PricingInputs
from quantlab.options.pricing import greeks, price
from quantlab.risk.analytics import RiskSettings
from quantlab.trading.server import Controller


@pytest.fixture
def c():
    c = Controller()
    c.options_lab.state()
    c.risk_lab.session.settings = RiskSettings(paths=100, sample_size=80)
    c.risk_lab.state()
    c.statarb_lab.session.command("step", count=85)
    return c


def frozen(c):
    return copy.deepcopy(
        dict(
            desk=c.session.public_snapshot(),
            options=c.options_lab.state(),
            risk=c.risk_lab.state(),
            statarb=c.statarb_lab.state(),
            learning=c.learning.tutor.progress.data,
            actions=[
                c.session.actions,
                c.options_lab.session.actions,
                c.risk_lab.session.actions,
                c.statarb_lab.session.actions,
            ],
        )
    )


@pytest.mark.parametrize(
    "kind,lab,inputs",
    [
        ("volatility", "options", {"volatility": 0.3}),
        ("correlation", "risk", {"correlation": 0.9}),
        ("order_size", "trading", {"quantity": 20}),
        ("inventory", "trading", {"inventory": 20}),
        ("entry_threshold", "statarb", {"entry": 2.5}),
    ],
)
def test_each_sandbox_leaves_all_sessions_research_and_learning_unchanged(c, kind, lab, inputs):
    before = frozen(c)
    a = c.explanations.what_if(kind, lab=lab, inputs=inputs)
    b = c.explanations.what_if(kind, lab=lab, inputs=inputs)
    assert a == b
    assert a["label"] == "HYPOTHETICAL SNAPSHOT ANALYSIS"
    assert frozen(c) == before


def test_what_if_and_explanations_do_not_perturb_next_random_market_events():
    a, b = Controller(), Controller()
    a.options_lab.state()
    b.options_lab.state()
    for _ in range(6):
        a.explanations.what_if("order_size", inputs={"quantity": 20})
        a.explanations.what_if("volatility", lab="options", inputs={"volatility": 0.3})
        a.explanations.explain("midpoint")
        for c in (a, b):
            c.command({"kind": "step_event"})
            c.options_lab.session.command("step", count=1)
        assert a.session.evidence == b.session.evidence
        assert a.options_lab.session.snapshot() == b.options_lab.session.snapshot()
        assert a.options_lab.session.actions == b.options_lab.session.actions


def test_frozen_book_partial_fill_is_real_matching_without_live_changes(c):
    s = c.state()
    before = copy.deepcopy(s)
    r = order_size(s, {"quantity": 20})
    assert r["filled"] == 15 and r["unfilled"] == 5
    assert r["fills"] == [
        {"price": "100.01", "quantity": 2},
        {"price": "100.02", "quantity": 5},
        {"price": "100.03", "quantity": 8},
    ]
    assert s == before and c.session.account.inventory == 0


def test_volatility_reuses_model_greeks_and_honours_decimal_units(c):
    s = c.options_lab.state()
    r = volatility(s, {"volatility": 0.3})
    x = PricingInputs(**r["after"]["inputs"])
    assert r["after"]["value"] == price(s["selected"]["type"], x)
    assert r["after"]["greeks"] == greeks(s["selected"]["type"], x).public()
    assert r["after"]["value"] > r["before"]["value"]


def test_correlation_uses_actual_multi_factor_holdings_and_changes_diversification(c):
    c.session.command("order", side="buy", quantity=5, order_type="market")
    c.options_lab.session.command("stock_order", side="buy", quantity=5, order_type="market")
    r = correlation(c.risk_lab.state(), {"correlation": 0.9})
    assert r["after"]["linear_risk"]["loss_sd"] > r["before"]["linear_risk"]["loss_sd"]
    assert r["after"]["portfolio"] == r["before"]["portfolio"]


def test_inventory_uses_core_nonlinear_soft_limit_and_outward_safety(c):
    r = inventory(c.state(), {"inventory": 20})
    assert r["after"]["plan"]["bid_size"] == 0
    assert float(r["after"]["plan"]["centre_ticks"]) < float(
        r["before"]["plan"]["centre_ticks"]
    )
    assert r["after"]["request"]["centre_shift_ticks"] == "-20"


def test_threshold_scan_higher_entry_only_filters_qualifying_flat_signals(c):
    r = threshold(c.statarb_lab.state(), {"entry": 2.5})
    assert r["rows"]
    for row in r["rows"]:
        if row["after"] in ("long", "short"):
            assert row["before"] == row["after"]


@pytest.mark.parametrize(
    "kind,lab,inputs",
    [
        ("order_size", "trading", {"quantity": 0}),
        ("order_size", "trading", {"quantity": 10001}),
        ("order_size", "trading", {"quantity": True}),
        ("inventory", "trading", {"inventory": 21}),
        ("volatility", "options", {"volatility": float("nan")}),
        ("volatility", "options", {"volatility": -0.1}),
        ("correlation", "risk", {"correlation": -0.9}),
        ("entry_threshold", "statarb", {"entry": 5}),
        ("order_size", "options", {"quantity": 2}),
        ("volatility", "options", {"volatility": 0.3, "seed": 4}),
    ],
)
def test_invalid_hypothetical_does_not_poison_session(c, kind, lab, inputs):
    before = frozen(c)
    with pytest.raises((ValueError, TypeError)):
        c.explanations.what_if(kind, lab=lab, inputs=inputs)
    assert frozen(c) == before


def test_explanation_observation_budget_and_new_session_identity():
    c = Controller()
    e = c.explanations
    for _ in range(5):
        e.explain("pnl")
        c.command({"kind": "step_event"})
    assert len(e.observed["trading"]) == 2
    e.max_bytes_per_lab = 1
    e.explain("pnl")
    assert "trading" not in e.observed
    e.max_bytes_per_lab = 2_000_000
    e.explain("pnl")
    c.command({"kind": "end"})
    c.command({"kind": "new"})
    assert not e.explain("pnl")["change"]["available"]
