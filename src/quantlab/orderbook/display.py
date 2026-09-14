"""A depth view over actual FIFO queues; presentation never modifies the book."""

from quantlab.domain import PriceGrid
from quantlab.orderbook.models import BookSnapshot


def render_depth(
    snapshot: BookSnapshot, grid: PriceGrid, *, expand_orders: bool = False
) -> str:
    """Show asks descending above bids descending, with the best quotes adjacent.

    Engine snapshots remain best-first on each side. Reversing only the ask
    display is a ladder convention; it cannot change matching priority.
    """
    lines: list[str] = []
    for name, levels in (("ASKS", tuple(reversed(snapshot.asks))), ("BIDS", snapshot.bids)):
        lines.extend((name, "Price | Total Quantity | Order Count"))
        if not levels:
            lines.append("(empty)")
        for level in levels:
            plural = "order" if level.order_count == 1 else "orders"
            lines.append(
                f"£{grid.to_price(level.price_ticks)} | {level.quantity}"
                f" | {level.order_count} {plural}"
            )
            if expand_orders:
                fifo = ", ".join(
                    f"{order.order_id}: {order.remaining_quantity}" for order in level.orders
                )
                lines.append(f"  FIFO oldest first: {fifo}")
    return "\n".join(lines)
