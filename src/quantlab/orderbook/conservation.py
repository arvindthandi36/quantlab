"""Always-on reconciliation of independently measured execution quantities."""


def verify_conservation(
    buyer_filled: int, seller_filled: int, recorded: int, context: str
) -> None:
    """Fail loudly, including under python -O; do not repair inconsistent accounting."""
    values = buyer_filled, seller_filled, recorded
    if any(type(value) is not int or value < 0 for value in values) or not (
        buyer_filled == seller_filled == recorded
    ):
        raise AssertionError(
            f"fill conservation failed ({context}): "
            f"buyer={buyer_filled}, seller={seller_filled}, recorded={recorded}"
        )
