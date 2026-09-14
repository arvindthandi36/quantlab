"""A deterministic mechanics demonstration, with a machine-readable audit output."""

import argparse
import json
import platform
from dataclasses import asdict, dataclass
from enum import Enum

from quantlab import LimitOrder, MarketOrder, OrderBook, PriceGrid, Side, __version__
from quantlab.orderbook import BookSnapshot, ExecutionReport, OrderView
from quantlab.orderbook.display import render_depth


@dataclass(frozen=True, slots=True)
class DemoRun:
    initial_book: BookSnapshot
    after_aggressive_order: BookSnapshot
    final_book: BookSnapshot
    reports: tuple[ExecutionReport, ...]
    cancelled_order: OrderView
    submitted_quantity: int
    traded_volume: int
    resting_quantity: int
    cancelled_quantity: int


def run_demo() -> DemoRun:
    """Run fixed orders and verify priority plus full-session quantity conservation."""
    book = OrderBook()
    initial_orders = (
        LimitOrder("bid-1", Side.BUY, 6, 9998),
        LimitOrder("bid-2", Side.BUY, 4, 9997),
        LimitOrder("ask-worse", Side.SELL, 5, 10004),
        LimitOrder("A", Side.SELL, 3, 10002),
        LimitOrder("B", Side.SELL, 4, 10002),
    )
    reports: list[ExecutionReport] = []
    for order in initial_orders:
        reports.append(book.submit(order))
        book.check_invariants()
    initial = book.snapshot()
    aggressive = book.submit(LimitOrder("buy-aggressive", Side.BUY, 5, 10005))
    book.check_invariants()
    reports.append(aggressive)
    after_aggressive = book.snapshot()
    actual = [
        (trade.maker_order_id, trade.quantity, trade.price_ticks) for trade in aggressive.trades
    ]
    if actual != [("A", 3, 10002), ("B", 2, 10002)]:
        raise AssertionError("demo violated price-time priority or resting-price execution")
    cancelled = book.cancel("B")
    if cancelled is None or cancelled.remaining_quantity != 2:
        raise AssertionError("demo cancellation quantity is incorrect")
    book.check_invariants()
    for market_order in (
        MarketOrder("sell-market", Side.SELL, 8),
        MarketOrder("buy-too-large", Side.BUY, 7),
    ):
        reports.append(book.submit(market_order))
        book.check_invariants()
    final = book.snapshot()
    submitted = sum(report.requested_quantity for report in reports)
    resting = sum(level.quantity for level in final.bids + final.asks)
    cancelled_quantity = cancelled.remaining_quantity + sum(
        r.cancelled_quantity for r in reports
    )
    for report in reports:
        if report.requested_quantity != (
            report.executed_quantity + report.resting_quantity + report.cancelled_quantity
        ):
            raise AssertionError("incoming-order quantity is not conserved")
    if submitted != 2 * book.traded_volume + resting + cancelled_quantity:
        raise AssertionError("session quantity is not conserved")
    return DemoRun(
        initial,
        after_aggressive,
        final,
        tuple(reports),
        cancelled,
        submitted,
        book.traded_volume,
        resting,
        cancelled_quantity,
    )


def _print_book(
    label: str, snapshot: BookSnapshot, grid: PriceGrid, *, expand_orders: bool = False
) -> None:
    print(f"\n{label}")
    print(render_depth(snapshot, grid, expand_orders=expand_orders))
    if snapshot.spread_ticks is None:
        print("  Spread / mid-price: unavailable (one or both sides are empty)")
    else:
        print(f"  Spread: £{grid.to_price(snapshot.spread_ticks):.2f}")
        print(f"  Mid-price: £{grid.to_price(snapshot.mid_price_ticks)}")


def _json_default(value: object) -> str:
    if isinstance(value, Enum):
        return value.value
    raise TypeError(f"Cannot encode {type(value).__name__}")


def main() -> None:
    """Print the book walkthrough, or exact integer-tick JSON with --json."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit deterministic audit data")
    parser.add_argument(
        "--expand-orders", action="store_true", help="expand depth into FIFO orders"
    )
    args = parser.parse_args()
    result = run_demo()
    if args.json:
        payload = {
            "schema_version": 2,
            "simulator_version": __version__,
            "python_version": platform.python_version(),
            "scenario": "phase-1-matching-demo",
            "tick_size": "0.01",
            "currency": "GBP",
            "quantity_unit": "whole units",
            "rng_seed": None,
            "rng_note": "Fixed instructions; no random draws.",
            "result": asdict(result),
        }
        print(
            json.dumps(
                payload, default=_json_default, indent=2, sort_keys=True, allow_nan=False
            )
        )
        return
    grid = PriceGrid()
    print("QuantLab | Arvind Thandi | Phase 1 matching-engine demonstration")
    print("Tick: £0.01 | Whole units | Fixed instructions, no randomness | No P&L model")
    _print_book("Initial book", result.initial_book, grid, expand_orders=args.expand_orders)
    report = result.reports[5]
    print("\nIncoming buy limit: 5 units, maximum price £100.05")
    for trade in report.trades:
        print(
            f"  Trade {trade.trade_id}: {trade.quantity}"
            f" at £{grid.to_price(trade.price_ticks):.2f}"
            f" | maker={trade.maker_order_id} | taker={trade.taker_order_id}"
        )
    _print_book(
        "After aggressive limit order",
        result.after_aggressive_order,
        grid,
        expand_orders=args.expand_orders,
    )
    print("\nCancel B's remaining 2 units; then sell 8 units at market:")
    for trade in result.reports[6].trades:
        print(f"  Sell {trade.quantity} at £{grid.to_price(trade.price_ticks):.2f}")
    oversized = result.reports[7]
    print(
        f"\nBuy 7 at market: executed {oversized.executed_quantity}; "
        f"cancelled {oversized.cancelled_quantity} because sell liquidity ran out."
    )
    _print_book("Final book", result.final_book, grid, expand_orders=args.expand_orders)
    print(
        f"\nConservation PASS: {result.submitted_quantity} submitted order-units = "
        f"2 × {result.traded_volume} traded units + {result.resting_quantity} resting "
        f"+ {result.cancelled_quantity} cancelled."
    )
    print("Priority and book invariants PASS after every operation.")


if __name__ == "__main__":
    main()
