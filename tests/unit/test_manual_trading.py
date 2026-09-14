from fractions import Fraction

import pytest

from quantlab import Side
from quantlab.portfolio.accounting import AccountingError, MakerAccount, MakerFill
from quantlab.research.codec import plain
from quantlab.trading.analytics import money, quant_metrics
from quantlab.trading.scenarios import SCENARIOS, scenario_from_dict, select_scenario
from quantlab.trading.session import TradingSession
from tests.trading_helpers import order, quiet, scripted


@pytest.mark.parametrize("side,qty,expected", [("buy", 6, 6), ("sell", 6, -6)])
def test_market_orders_real_engine(side, qty, expected):
    s = TradingSession(quiet())
    assert order(s, side, qty)["ok"]
    assert s.account.inventory == expected
    assert s.book.traded_volume == qty
    s.check_invariants()


def test_requested_multilevel_example_exact_vwap_and_cash():
    s = TradingSession(quiet())
    order(s, quantity=6)
    o = s.orders["user-1"]
    assert [(f["price_ticks"], f["quantity"]) for f in o.fills] == [(10001, 2), (10002, 4)]
    assert o.vwap == Fraction(30005, 3)
    assert s.book.snapshot().asks[0].quantity == 1
    a = s.account.snapshot()
    assert a.cash_ticks == 1_000_000 - 60010 - Fraction(6, 10)
    assert a.total_pnl_ticks == a.realised_pnl_ticks + a.unrealised_pnl_ticks
    assert s.public_snapshot()["account"]["average_entry"] == "100.01667"


@pytest.mark.parametrize("side,price", [("buy", "99.98"), ("sell", "100.02")])
def test_limit_resting_aggregated_depth_fifo(side, price):
    s = TradingSession(quiet())
    order(s, side, 5, price)
    snap = s.public_snapshot()
    level = next(
        item
        for item in snap["bids" if side == "buy" else "asks"]
        if Fraction(item["price"]) == Fraction(price)
    )
    assert level["quantity"] == 10 and level["order_count"] == 2
    assert level["own_quantity"] == 5
    assert level["queue"][-1]["id"] == "user-1"
    assert not level["queue"][0]["yours"]
    assert not s.account.fills


@pytest.mark.parametrize("side,price", [("buy", "100.02"), ("sell", "99.98")])
def test_marketable_limits_stop_at_their_price(side, price):
    s = TradingSession(quiet())
    order(s, side, 12, price)
    o = s.orders["user-1"]
    expected = 7 if side == "buy" else 10
    assert (o.filled, o.remaining) == (expected, 12 - expected)
    assert o.status == "partial · resting"
    assert all(
        f["price_ticks"] <= 10002 if side == "buy" else f["price_ticks"] >= 9998
        for f in o.fills
    )


@pytest.mark.parametrize("side,filled", [("buy", 15), ("sell", 18)])
def test_market_exhaustion_cancels_remainder(side, filled):
    s = TradingSession(quiet())
    order(s, side, 20)
    o = s.orders["user-1"]
    assert (o.filled, o.cancelled, o.remaining) == (filled, 20 - filled, 0)
    assert o.status == "partial · remainder cancelled"


@pytest.mark.parametrize("side", ["buy", "sell"])
def test_no_liquidity_means_no_fill_fee_or_vwap(side):
    s = TradingSession(quiet(initial_book=()))
    order(s, side, 5)
    o = s.orders["user-1"]
    assert (o.filled, o.cancelled, o.vwap) == (0, 5, None)
    assert s.account.inventory == 0 and s.account.fees == 0


def test_fifo_partial_passive_fill_then_cancel_then_later_matching():
    s = scripted(
        [(100, "sell", 7), (200, "sell", 5)],
        initial_book=(("buy", 9998, 5), ("sell", 10002, 5)),
    )
    order(s, quantity=5, price="99.98")
    order(s, quantity=2, price="99.98")
    s.command("step_event")
    assert (s.orders["user-1"].filled, s.orders["user-1"].remaining) == (2, 3)
    assert s.orders["user-2"].filled == 0
    assert s.account.inventory == 2
    assert s.command("cancel", order_id="user-1")["ok"]
    s.command("step_event")
    assert s.orders["user-1"].filled == 2
    assert s.orders["user-2"].filled == 2
    assert s.account.inventory == 4
    assert all(t["role"] == "provider" for t in s.own_trades)


def test_passive_fills_accumulate_vwap_with_immediate_fills():
    s = scripted([(100, "sell", 2)], initial_book=(("sell", 10001, 2), ("buy", 9999, 3)))
    order(s, quantity=4, price="100.02")
    s.command("step_event")
    o = s.orders["user-1"]
    assert o.filled == 4 and o.remaining == 0
    assert o.vwap == Fraction(20003, 2)
    assert [f["role"] for f in o.fills] == ["aggressor", "provider"]


def test_cancel_success_matches_underlying_book_and_noop_is_honest():
    s = TradingSession(quiet())
    order(s, quantity=5, price="99.98")
    assert s.command("cancel", order_id="user-1")["ok"]
    assert s.orders["user-1"].cancelled == 5
    assert not s._live("user")
    assert not s.command("cancel", order_id="user-1")["ok"]
    assert not s.command("cancel", order_id="opening-0")["ok"]


def test_cancel_all_removes_multiple_orders_and_releases_capacity():
    s = TradingSession(quiet())
    order(s, quantity=10, price="99.98")
    order(s, quantity=10, price="99.97")
    assert s.public_snapshot()["account"]["buy_capacity"] == 0
    assert len(s.command("cancel_all")["cancelled"]) == 2
    assert s.public_snapshot()["account"]["buy_capacity"] == 20


@pytest.mark.parametrize("side,price", [("buy", "99.98"), ("sell", "100.02")])
def test_multiple_orders_cannot_evade_reserved_limits(side, price):
    s = TradingSession(quiet())
    assert order(s, side, 15, price)["ok"]
    before = s.book.snapshot()
    assert not order(s, side, 6, price)["ok"]
    assert s.book.snapshot() == before
    assert order(s, side, 5, price)["ok"]


def test_opposite_reservations_do_not_net_and_market_is_conservative():
    s = TradingSession(quiet())
    order(s, "buy", 20, "99.00")
    order(s, "sell", 20, "101.00")
    assert not order(s, "buy", 1)["ok"]
    assert not order(s, "sell", 1)["ok"]
    assert s.account.inventory == 0


@pytest.mark.parametrize("side,price", [("buy", "101.00"), ("sell", "99.00")])
def test_self_trade_is_rejected_without_changes(side, price):
    s = TradingSession(quiet(initial_book=()))
    order(s, "sell" if side == "buy" else "buy", 2, "100.00")
    before = s.book.snapshot()
    assert not order(s, side, 2, price)["ok"]
    assert s.book.snapshot() == before and not s.account.fills


def test_closing_long_and_crossing_to_short_fifo_pnl():
    s = TradingSession(quiet())
    order(s, quantity=6)
    order(s, "sell", 8)
    a = s.account.snapshot()
    assert a.inventory == -2
    # Buy costs 60010 ticks; close 5@9999 + 1@9998 = 59993, loss 17.
    assert a.realised_trading_pnl_ticks == -17
    assert a.realised_pnl_ticks == -17 - Fraction(14, 10)
    assert s.account.lots[0].entry_price_ticks == 9998
    assert s.account.lots[0].signed_quantity == -2
    assert a.total_pnl_ticks == a.cash_ticks + a.inventory * a.reference_ticks - 1_000_000


@pytest.mark.parametrize("initial", [-8, 0, 8])
def test_opening_endowment_has_zero_pnl_no_fake_fills(initial):
    s = TradingSession(quiet(initial_position=initial))
    assert not s.account.fills and s.account.fees == 0
    assert s.account.inventory == initial
    assert s.account.snapshot().total_pnl_ticks == 0
    assert s.account.snapshot().cash_ticks == 1_000_000
    assert s.report()["turnover"] == "0.00000"


@pytest.mark.parametrize(
    "initial,move,pnl", [(8, 2, 16), (8, -2, -16), (-8, 2, -16), (-8, -2, 16)]
)
def test_directional_gain_loss_is_exact_mark_movement(initial, move, pnl):
    a = MakerAccount(1_000_000, 10000, hard_limit=20, initial_position=initial)
    a.mark(10000 + move)
    assert a.snapshot().total_pnl_ticks == pnl
    assert a.snapshot().unrealised_pnl_ticks == pnl


def test_endowment_close_realises_without_counting_initial_value_as_profit():
    a = MakerAccount(1_000_000, 10000, hard_limit=20, initial_position=-3)
    a.apply(MakerFill(1, 1, 1, Side.BUY, 3, 9998, Fraction(3, 10), Fraction(10000), None))
    assert a.inventory == 0
    assert a.snapshot().total_pnl_ticks == Fraction(57, 10)


@pytest.mark.parametrize("initial", [True, 1.5, "2", 21, -21])
def test_invalid_opening_position_rejected(initial):
    with pytest.raises(ValueError):
        MakerAccount(1_000_000, 10000, hard_limit=20, initial_position=initial)


@pytest.mark.parametrize(
    "payload",
    [
        {"quantity": 0},
        {"quantity": -1},
        {"quantity": True},
        {"quantity": 1.5},
        {"side": "bad"},
        {"order_type": "stop"},
        {"order_type": "limit", "price": "99.999"},
        {"order_type": "limit", "price": 99.98},
        {"order_type": "limit", "price": "NaN"},
        {"order_type": "limit", "price": "0"},
        {"unknown": 2},
    ],
)
def test_bad_order_is_nonmutating_and_does_not_poison(payload):
    s = TradingSession(quiet())
    before = s.book.snapshot()
    result = s.command(
        "order", **{"quantity": 1, "side": "buy", "order_type": "market", **payload}
    )
    assert not result["ok"]
    assert s.book.snapshot() == before and s.failure is None
    assert order(s)["ok"]


@pytest.mark.parametrize("corrupt", ["quantity", "tape", "order", "fee"])
def test_conservation_discrepancies_fail_loudly(corrupt):
    s = TradingSession(quiet())
    order(s)
    if corrupt == "quantity":
        s._submitted += 1
    elif corrupt == "tape":
        s.tape[0]["quantity"] += 1
    elif corrupt == "order":
        s.orders["user-1"].cancelled += 1
    else:
        s.own_trades[0]["fee_ticks"] += 1
    with pytest.raises(AccountingError):
        s.check_invariants()


@pytest.mark.parametrize("key", list(SCENARIOS))
def test_scenario_roundtrip_and_opening_market(key):
    scenario = select_scenario(key, seed=7)
    assert scenario_from_dict(plain(scenario)) == scenario
    s = TradingSession(scenario, "challenge")
    assert s.public_snapshot()["scenario"] == scenario.title
    s.command("end")
    assert s.report()["challenge"]["completed_duration"] is False


@pytest.mark.parametrize(
    "payload",
    [
        {"key": "missing"},
        {"duration_seconds": 0},
        {"duration_seconds": 301},
        {"position_limit": 1},
        {"position_limit": True},
        {"initial_position": 2},
        {"key": "position", "initial_position": 21},
        {"seed": True},
    ],
)
def test_scenario_bad_configuration(payload):
    with pytest.raises((ValueError, TypeError)):
        select_scenario(**payload)


def test_quant_metrics_hand_calculation_and_missing_data():
    s = TradingSession(quiet())
    q = quant_metrics(s.book.snapshot(), [])
    assert q["depth_imbalance_top_5"] == pytest.approx(3 / 33)
    assert q["last_log_return"] is None and q["flow_imbalance"] is None
    prices = [
        {"price_ticks": 100, "quantity": 2, "aggressor_side": "buy"},
        {"price_ticks": 200, "quantity": 1, "aggressor_side": "sell"},
        {"price_ticks": 100, "quantity": 1, "aggressor_side": "sell"},
    ]
    q = quant_metrics(s.book.snapshot(), prices)
    import math

    assert q["last_log_return"] == pytest.approx(-math.log(2))
    assert q["realised_volatility_trade_window"] == pytest.approx(math.sqrt(2) * math.log(2))
    assert q["flow_imbalance"] == 0 and q["return_observations"] == 2


def test_money_rounding_is_only_presentation():
    value = Fraction(30005, 3)
    assert money(value) == "100.01667" and value == Fraction(30005, 3)


def test_crossed_scenario_is_invalid():
    with pytest.raises(ValueError, match="crossed"):
        quiet(initial_book=(("buy", 10000, 1), ("sell", 9999, 1)))


def test_cancellation_and_reentry_lose_time_priority():
    s = scripted([(100, "sell", 6)], initial_book=(("buy", 9998, 5), ("sell", 10002, 5)))
    order(s, quantity=1, price="99.98")
    order(s, quantity=1, price="99.98")
    s.command("cancel", order_id="user-1")
    order(s, quantity=1, price="99.98")
    s.command("step_event")
    assert s.orders["user-2"].filled == 1
    assert s.orders["user-3"].filled == 0
