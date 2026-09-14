import copy
from fractions import Fraction

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from quantlab.options.models import OptionContract, years_from_days
from quantlab.options.portfolio import OptionPortfolio
from quantlab.options.pricing import greeks
from quantlab.options.session import OptionsConfig, OptionsSession, replay_options
from quantlab.portfolio.accounting import AccountingError


def session(**kwargs):
    return OptionsSession(
        OptionsConfig(
            **({"strikes": (95, 100, 105), "expiries_days": (10,), "steps": 10} | kwargs)
        )
    )


def trade(s, side="buy", quantity=1, key=None):
    return s.command(
        "option_order",
        contract_id=key or s.selected,
        side=side,
        quantity=quantity,
        quote_revision=s.quote_revision,
    )


@pytest.mark.parametrize(
    "kind,side", [("call", "buy"), ("call", "sell"), ("put", "buy"), ("put", "sell")]
)
def test_actual_option_side_quote_cash_and_liability(kind, side):
    s = session()
    c = next(c for c in s.contracts.values() if c.option_type == kind and c.strike_gbp == 100)
    q = s.quotes[c.id]
    expected = q.ask if side == "buy" else q.bid
    result = trade(s, side, key=c.id)
    sign = 1 if side == "buy" else -1
    assert result["premium"] == float(expected)
    assert s.portfolio.cash == -sign * 100 * expected - Fraction(5, 100)
    assert s.portfolio.quantity(c.id) == sign
    assert s.portfolio.realised[c.id] == 0
    assert s.accounts()["total_pnl"] < 0  # Spread/fees, never instant short-premium profit.
    s.portfolio.check(s._marks())


def test_contract_multiplier_exact_hedge_example_and_exposure():
    s = session(multiplier=100)
    trade(s, "sell", 10)
    delta = greeks(s.contracts[s.selected].option_type, s.quotes[s.selected].inputs).delta
    assert s.aggregate_greeks()["option_delta"] == pytest.approx(-10 * 100 * delta)
    assert -10 * 0.60 * 100 == -600
    before = s.stock.book.traded_volume
    result = s.command("hedge")
    assert result["actual_filled"] == round(1000 * delta)
    assert s.stock.book.traded_volume - before == result["actual_filled"]
    assert s.stock.account.inventory == result["actual_filled"]
    assert s.stock.actions[-1]["kind"] == "order"
    s.stock.check_invariants()


def test_finite_option_depth_and_stale_quote_rejection():
    s = session(quote_size=2)
    revision = s.quote_revision
    result = trade(s, quantity=5)
    assert (result["filled"], result["cancelled"]) == (2, 3)
    before = copy.deepcopy(s.portfolio.ledger)
    with pytest.raises(ValueError, match="Stale"):
        s.command(
            "option_order",
            contract_id=s.selected,
            side="buy",
            quantity=1,
            quote_revision=revision,
        )
    assert s.portfolio.ledger == before
    assert trade(s)["filled"] == 0


def test_underlying_partial_hedge_uses_real_available_orders():
    s = session(stock_depth=1)
    trade(s, "sell", 5)
    result = s.command("hedge")
    assert result["actual_filled"] == 5
    assert s.stock.account.inventory == 5
    assert s.stock.book.traded_volume == 5
    assert "cancelled" in result["message"]
    assert abs(s.aggregate_greeks()["delta"]) > 100
    s.stock.check_invariants()


def test_option_portfolio_greeks_sum_quantity_times_multiplier():
    s = session()
    ids = list(s.quotes)[:4]
    for i, key in enumerate(ids):
        trade(s, "buy" if i % 2 else "sell", i + 1, key)
    s.command("stock_order", side="buy", quantity=7)
    total = s.aggregate_greeks()
    for name in ("delta", "gamma", "vega", "theta", "rho"):
        expected = sum(
            getattr(greeks(s.contracts[k].option_type, s.quotes[k].inputs), name)
            * s.portfolio.quantity(k)
            * s.contracts[k].multiplier
            for k in ids
        )
        assert total[name] == pytest.approx(expected + (7 if name == "delta" else 0))


def test_delta_neutrality_decays_after_actual_observed_move():
    s = session()
    trade(s, "sell", 2)
    s.command("hedge")
    assert abs(s.aggregate_greeks()["delta"]) <= 0.5
    s.command("step", count=3)
    assert abs(s.aggregate_greeks()["delta"]) > 0.5
    before = s.stock.book.traded_volume
    s.command("hedge")
    assert s.stock.book.traded_volume > before
    assert abs(s.aggregate_greeks()["delta"]) <= 0.5


@pytest.mark.parametrize("side", ["buy", "sell"])
def test_expiry_cash_settles_once_and_has_no_time_value(side):
    s = session(steps=2, expiries_days=(1, 2))
    key = s.selected
    trade(s, side, 2)
    s.command("step", count=1)
    assert s.portfolio.quantity(key) == 0 and key in s.portfolio.settled
    assert key not in s.quotes
    settlements = [r for r in s.portfolio.ledger if r["kind"] == "settlement"]
    assert len(settlements) == 1
    s.command("step", count=1)
    assert len([r for r in s.portfolio.ledger if r["kind"] == "settlement"]) == 1
    assert s.snapshot(selected=key)["selected"]["expired"]
    s.portfolio.check(s._marks())


def test_ending_before_expiry_marks_positions_without_invented_liquidation():
    s = session()
    trade(s)
    s.command("hedge")
    qty = s.stock.account.inventory
    s.command("end")
    assert s.portfolio.quantity(s.selected) == 1 and s.stock.account.inventory == qty
    assert not s.portfolio.settled


def test_expired_contract_payoff_does_not_follow_later_stock_moves():
    s = session(expiries_days=(1, 3), steps=3, process_volatility=0, physical_drift=0.5)
    key = s.selected
    trade(s)
    s.command("step", count=1)
    at_expiry = s.snapshot(key)["selected"]
    s.command("step", count=2)
    later = s.snapshot(key)["selected"]
    assert s.spot > at_expiry["expiry_spot"]
    assert later["payoff"] == at_expiry["payoff"]
    assert later["expiry_spot"] == at_expiry["expiry_spot"] and later["time_value"] == 0


def test_cash_funding_and_pnl_components_reconcile_without_double_counting():
    s = session(rate=0.05)
    trade(s, "sell", 2)
    s.command("hedge")
    s.command("step", count=2)
    a = s.accounts()
    assert a["financing"] < 0  # Borrowing to hold the long stock hedge.
    assert a["total_pnl"] == (
        a["option_realised_gross"]
        + a["option_unrealised"]
        + a["stock_realised_gross"]
        + a["stock_unrealised"]
        + a["financing"]
        - a["fees"]
    )
    assert a["total_pnl"] == a["cash"] + a["option_value"] + a["stock_value"]


def test_replay_verifies_quotes_fills_cash_greeks_and_all_underlying_evidence():
    s = session()
    trade(s, "sell", 2)
    s.command("hedge")
    s.command("set_auto", frequency=5)
    s.command("step", count=10)
    journal = s.journal()
    assert replay_options(journal).journal() == journal
    bad = copy.deepcopy(journal)
    bad["final"]["accounts"]["total_pnl"] += 1
    with pytest.raises(ValueError, match="integrity"):
        replay_options(bad)


def test_future_steps_and_rng_are_absent_from_public_state():
    s = session()
    snapshot = s.snapshot()
    assert not {"seed", "innovations", "future_spots", "rng", "model_spot"} & set(snapshot)
    assert len(snapshot["history"]) == 1
    with pytest.raises(ValueError, match="End"):
        s.journal()


def test_expiry_must_align_exactly_with_model_step():
    with pytest.raises(ValueError, match="align"):
        OptionsConfig(expiries_days=(1,), step_days=0.3)
    assert OptionsConfig(expiries_days=(1,), step_days=0.1).step_days == 0.1


@pytest.mark.parametrize(
    "values",
    [
        {"volatility": 20},
        {"multiplier": True},
        {"steps": 0},
        {"dividend_yield": 0.02},
        {"quote_size": -1},
        {"strikes": (100, 100)},
    ],
)
def test_options_config_rejects_invalid_units_and_states(values):
    if "volatility" in values:
        values = {"implied_volatility": values["volatility"]}
    with pytest.raises((ValueError, TypeError)):
        OptionsConfig(**values)


def test_option_fifo_realisation_and_corruption_fail_loudly():
    c = OptionContract("put", 100, years_from_days(30), 100)
    p = OptionPortfolio()
    p.apply(c, 2, 3, 0.1, "a")
    p.apply(c, 1, 4, 0.05, "b")
    p.apply(c, -2, 5, 0.1, "c")
    assert p.realised[c.id] == 400 and p.quantity(c.id) == 1
    p.check({c.id: 4})
    p.cash += 1
    with pytest.raises(AccountingError, match="reconcile"):
        p.check({c.id: 4})


@given(
    st.lists(
        st.tuples(st.integers(-4, 4).filter(bool), st.integers(0, 1000)),
        min_size=1,
        max_size=30,
    )
)
@settings(max_examples=40)
def test_generated_option_account_operations_conserve_equity(operations):
    c = OptionContract("call", 100, years_from_days(30), 37)
    p = OptionPortfolio()
    for i, (qty, premium) in enumerate(operations):
        p.apply(c, qty, Fraction(premium, 100), Fraction(abs(qty), 100), str(i))
        p.check({c.id: Fraction(7, 2)})
    assert p.quantity(c.id) == sum(q for q, _ in operations)


def test_passive_stock_limit_fill_is_real_and_included_in_hedge_report():
    s = session(physical_drift=0.5, process_volatility=0)
    result = s.command(
        "stock_order", side="sell", quantity=3, order_type="limit", price="100.10"
    )
    assert result["actual_filled"] == 0
    s.command("step", count=1)
    assert s.stock.account.inventory == -3
    assert s.metrics()["turnover"] == 3 and s.metrics()["hedges"] >= 1
    s.stock.check_invariants()


def test_public_snapshot_mutation_cannot_change_execution_or_history():
    s = session()
    trade(s)
    snapshot = s.snapshot()
    snapshot["history"][0]["spot"] = 999
    snapshot["option_trades"][0]["filled"] = 999
    assert s.snapshot()["history"][0]["spot"] == 100
    assert s.snapshot()["option_trades"][0]["filled"] == 1


@pytest.mark.parametrize(
    "field,value", [("cash_flow", 999), ("multiplier", 99), ("premium", Fraction(5))]
)
def test_option_execution_unit_corruption_is_detected_independently(field, value):
    s = session()
    trade(s)
    s.portfolio.ledger[0][field] = value
    with pytest.raises(AccountingError, match="premium, quantity and multiplier"):
        s.portfolio.check(s._marks())


def test_command_budget_still_allows_end_and_export():
    s = session()
    s.actions = [{"test_budget_sentinel": True}] * 3000
    with pytest.raises(ValueError, match="budget"):
        s.command("hedge")
    s.command("end")
    assert s.journal()["final"]["status"] == "ended"


@pytest.mark.parametrize(
    "kind,payload",
    [
        ("option_order", {"side": "buy", "quantity": 1}),
        ("stock_order", {"side": "buy", "quantity": -1}),
        ("set_auto", {"frequency": 3}),
        ("set_iv", {"volatility": 20}),
        ("step", {"count": True}),
        ("hedge", {"future_spot": 999}),
    ],
)
def test_invalid_commands_leave_financial_state_and_clock_unchanged(kind, payload):
    s = session()
    before = s.snapshot()
    if kind == "stock_order":
        # Phase 6 retains a rejected-order audit entry, but creates no fill or cash flow.
        result = s.command(kind, **payload)
        assert not result["ok"] and result["actual_filled"] == 0
        assert s.snapshot()["accounts"] == before["accounts"]
        assert s.step_index == 0 and not s._innovations
        return
    with pytest.raises(ValueError):
        s.command(kind, **payload)
    assert s.snapshot() == before and not s.actions and not s._innovations
