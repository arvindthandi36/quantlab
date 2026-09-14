import subprocess
import sys
from dataclasses import replace
from fractions import Fraction as F

import pytest

from quantlab import Side
from quantlab.portfolio.accounting import AccountingError, MakerAccount, MakerFill


def fill(account, number, side, quantity, price, fee=F(0)):
    item = MakerFill(
        number, number, number, side, quantity, price, fee, account.reference, account.reference
    )
    account.apply(item)
    return item


@pytest.mark.parametrize("side,inventory,cash", [(Side.BUY, 3, -300), (Side.SELL, -3, 300)])
def test_execution_cash_and_inventory_signs(side, inventory, cash):
    account = MakerAccount(1000, 100, hard_limit=8)
    fill(account, 1, side, 3, 100, F(3, 10))
    state = account.snapshot()
    assert state.inventory == inventory
    assert state.execution_cash_ticks == cash
    assert state.cash_ticks == 1000 + cash - F(3, 10)
    assert state.realised_pnl_ticks == -F(3, 10)
    assert state.unrealised_pnl_ticks == 0
    assert state.total_pnl_ticks == -F(3, 10)


def test_fifo_partial_close_and_open_inventory_are_hand_calculable():
    account = MakerAccount(1000, 100, hard_limit=8)
    fill(account, 1, Side.BUY, 2, 99, F(1, 5))
    fill(account, 2, Side.BUY, 1, 101, F(1, 10))
    fill(account, 3, Side.SELL, 2, 103, F(1, 5))
    account.mark(F(102))
    state = account.snapshot()
    assert state.execution_cash_ticks == -93  # -198 -101 +206
    assert state.inventory == 1
    assert state.realised_trading_pnl_ticks == 8  # FIFO: two units bought at 99
    assert state.realised_pnl_ticks == F(15, 2)  # immediate expense of all fees
    assert state.unrealised_pnl_ticks == 1
    assert state.total_pnl_ticks == F(17, 2)
    assert state.spread_capture_ticks == 7
    assert state.inventory_movement_ticks == 2
    assert state.spread_capture_ticks + state.inventory_movement_ticks - state.fees_ticks == F(
        17, 2
    )


@pytest.mark.parametrize(
    "opening,closing,entry,exit_price,expected",
    [
        (Side.SELL, Side.BUY, 103, 99, 8),
        (Side.BUY, Side.SELL, 99, 103, 8),
        (Side.SELL, Side.BUY, 99, 103, -8),
        (Side.BUY, Side.SELL, 103, 99, -8),
    ],
)
def test_long_and_short_round_trips(opening, closing, entry, exit_price, expected):
    account = MakerAccount(1000, 100, hard_limit=8)
    fill(account, 1, opening, 2, entry)
    fill(account, 2, closing, 2, exit_price)
    state = account.snapshot()
    assert state.inventory == 0 and account.lots == ()
    assert state.realised_trading_pnl_ticks == state.total_pnl_ticks == expected
    assert state.unrealised_pnl_ticks == 0
    assert state.cash_ticks == 1000 + expected


@pytest.mark.parametrize("side", list(Side))
def test_trade_through_zero_closes_then_opens_opposite_lot(side):
    sign = 1 if side is Side.BUY else -1
    account = MakerAccount(1000, 100, hard_limit=8)
    fill(account, 1, side, 2, 100 - sign)
    fill(account, 2, side.opposite, 3, 100 + sign)
    state = account.snapshot()
    assert state.inventory == -sign
    assert state.realised_trading_pnl_ticks == 4
    assert state.unrealised_pnl_ticks == 1
    assert state.total_pnl_ticks == 5
    assert len(account.lots) == 1
    assert account.lots[0].entry_price_ticks == 100 + sign


def test_inventory_rally_can_be_entire_profit_without_spread_capture():
    account = MakerAccount(1000, 100, hard_limit=8)
    fill(account, 1, Side.BUY, 3, 100)
    account.mark(F(110))
    state = account.snapshot()
    assert state.total_pnl_ticks == state.inventory_movement_ticks == 30
    assert state.spread_capture_ticks == state.realised_pnl_ticks == 0
    assert state.unrealised_pnl_ticks == 30


def test_exact_fractional_fees_and_marks_do_not_round_away():
    account = MakerAccount(F(1000, 3), F(201, 2), hard_limit=8)
    fill(account, 1, Side.BUY, 3, 100, F(1, 3))
    account.mark(F(302, 3))
    state = account.snapshot()
    assert state.total_pnl_ticks == F(5, 3)
    assert state.marked_value_ticks == state.cash_ticks + 3 * F(302, 3)


def test_duplicate_fill_is_rejected_before_mutation():
    account = MakerAccount(1000, 100, hard_limit=8)
    execution = fill(account, 1, Side.BUY, 1, 100)
    before = account.snapshot()
    with pytest.raises(ValueError, match="duplicate"):
        account.apply(execution)
    assert account.snapshot() == before


@pytest.mark.parametrize("side", list(Side))
def test_breaching_actual_fill_fails_loudly_and_disables_account(side):
    account = MakerAccount(1000, 100, hard_limit=2)
    fill(account, 1, side, 2, 100)
    with pytest.raises(AccountingError, match="hard inventory"):
        fill(account, 2, side, 1, 100)
    with pytest.raises(AccountingError, match="discard"):
        account.mark(F(101))


@pytest.mark.parametrize(
    "attribute", ["inventory", "execution_cash", "fees", "realised", "capture", "movement"]
)
def test_corrupted_accounting_is_never_repaired(attribute):
    account = MakerAccount(1000, 100, hard_limit=8)
    fill(account, 1, Side.BUY, 1, 100)
    setattr(account, attribute, getattr(account, attribute) + 1)
    with pytest.raises(AccountingError, match="reconcile"):
        account.check_invariants()
    with pytest.raises(AccountingError, match="discard"):
        fill(account, 2, Side.SELL, 1, 100)


def test_wrong_pretrade_reference_fails_instead_of_changing_attribution():
    account = MakerAccount(1000, 100, hard_limit=8)
    item = MakerFill(1, 1, 1, Side.BUY, 1, 99, F(0), F(101), F(100))
    with pytest.raises(AccountingError, match="reference"):
        account.apply(item)


@pytest.mark.parametrize(
    "change",
    [
        {"fee_ticks": 0.1},
        {"fee_ticks": -1},
        {"quantity": True},
        {"time_us": -1},
        {"side": "buy"},
        {"reference_before_ticks": 0},
    ],
)
def test_invalid_fill_inputs_fail_before_accounting(change):
    item = MakerFill(1, 1, 1, Side.BUY, 1, 100, F(0), F(100), None)
    with pytest.raises((TypeError, ValueError)):
        replace(item, **change)


def test_attribution_offsets_cannot_hide_a_corrupted_execution_edge():
    account = MakerAccount(1000, 100, hard_limit=8)
    fill(account, 1, Side.BUY, 1, 99)
    account.capture += 1
    account.movement -= 1
    with pytest.raises(AccountingError, match="reconcile"):
        account.check_invariants()


def test_accounting_guards_remain_active_under_optimised_python():
    script = """
from quantlab.portfolio.accounting import MakerAccount, AccountingError
a = MakerAccount(1000, 100, hard_limit=8)
a.execution_cash = 1
try:
    a.check_invariants()
except AccountingError:
    print('reconciliation active')
else:
    raise RuntimeError('accounting checks disappeared')
"""
    run = subprocess.run(
        [sys.executable, "-O", "-c", script], capture_output=True, text=True, check=True
    )
    assert "reconciliation active" in run.stdout
