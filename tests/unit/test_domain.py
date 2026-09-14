from dataclasses import FrozenInstanceError
from decimal import Decimal, localcontext
from fractions import Fraction

import pytest

from quantlab import LimitOrder, MarketOrder, PriceGrid, Side


@pytest.mark.parametrize("quantity", [0, -1, -100])
@pytest.mark.parametrize("kind", [LimitOrder, MarketOrder])
def test_nonpositive_quantities_rejected(kind, quantity):
    extra = {"price_ticks": 100} if kind is LimitOrder else {}
    with pytest.raises(ValueError, match="quantity"):
        kind("x", Side.BUY, quantity, **extra)


@pytest.mark.parametrize("value", [True, False, 1.0, float("nan"), float("inf"), "2", None])
@pytest.mark.parametrize("field", ["quantity", "price_ticks"])
def test_noninteger_fields_rejected(field, value):
    kwargs = {"order_id": "x", "side": Side.BUY, "quantity": 1, "price_ticks": 100}
    kwargs[field] = value
    with pytest.raises(TypeError, match=field):
        LimitOrder(**kwargs)


@pytest.mark.parametrize("price", [0, -1])
def test_nonpositive_tick_prices_rejected(price):
    with pytest.raises(ValueError, match="price_ticks"):
        LimitOrder("x", Side.BUY, 1, price)


@pytest.mark.parametrize("order_id", ["", " x", "x ", "\t"])
def test_invalid_identifiers_rejected(order_id):
    with pytest.raises(ValueError, match="order_id"):
        MarketOrder(order_id, Side.BUY, 1)


def test_invalid_identifier_and_side_types_rejected():
    with pytest.raises(TypeError, match="order_id"):
        MarketOrder(123, Side.BUY, 1)
    with pytest.raises(TypeError, match="side"):
        MarketOrder("x", "buy", 1)


def test_instructions_are_immutable():
    order = LimitOrder("x", Side.BUY, 2, 100)
    with pytest.raises(FrozenInstanceError):
        order.quantity = 3


@pytest.mark.parametrize("price", ["0", "-0.01", "NaN", "sNaN", "Infinity", "-Infinity", "bad"])
def test_invalid_decimal_prices_rejected(price):
    with pytest.raises(ValueError):
        PriceGrid().to_ticks(price)


@pytest.mark.parametrize("value", [100.02, 100, True, None])
def test_price_conversion_rejects_implicit_float_or_integer_units(value):
    with pytest.raises(TypeError):
        PriceGrid().to_ticks(value)


@pytest.mark.parametrize("tick", ["0", "-1", "NaN", "sNaN", "Infinity"])
def test_invalid_tick_size_rejected(tick):
    with pytest.raises(ValueError):
        PriceGrid(Decimal(tick))


def test_exact_conversion_and_half_tick_mid_price():
    grid = PriceGrid()
    assert grid.to_ticks("100.02") == 10002
    assert grid.to_ticks(Decimal("0.29")) == 29
    assert grid.to_price(10002) == Decimal("100.02")
    assert grid.to_price(Fraction(20001, 2)) == Decimal("100.005")
    with pytest.raises(ValueError, match="multiple"):
        grid.to_ticks("100.005")


def test_non_decimal_power_tick_and_context_independence():
    grid = PriceGrid(Decimal("0.05"))
    with localcontext() as context:
        context.prec = 3
        assert grid.to_ticks("100.05") == 2001
        assert grid.to_price(2001) == Decimal("100.05")
        with pytest.raises(ValueError, match="multiple"):
            grid.to_ticks("100.050000000000000000000000001")
        assert grid.to_ticks("12345678901234567890.05") == 246913578024691357801


def test_reverse_conversion_validation():
    with pytest.raises(TypeError):
        PriceGrid(0.01)
    for ticks in (True, 1.5, "3"):
        with pytest.raises(TypeError):
            PriceGrid().to_price(ticks)
    for ticks in (0, -1):
        with pytest.raises(ValueError):
            PriceGrid().to_price(ticks)
    with pytest.raises(ValueError, match="finite decimal"):
        PriceGrid().to_price(Fraction(1, 3))
