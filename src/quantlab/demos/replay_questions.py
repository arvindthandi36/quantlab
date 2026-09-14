"""Prospective questions use only the public BEFORE point and the chosen instruction."""

from dataclasses import replace

from quantlab.demos.models import choice


def question(before, action):
    kind = action.get("kind", "")
    p = action.get("payload", {})
    c = before.get("core", before)
    if kind in ("order", "stock_order", "option_order"):
        if before["engine"] == "historical":
            return choice(
                "historical_replay",
                (
                    "Does submitting this paper order prove a fill at the currently "
                    "displayed close?"
                ),
            )
        if kind == "option_order":
            return choice(
                "delta",
                "Does one option contract always have the price sensitivity of one stock unit?",
            )
        side = p.get("side")
        if side in ("buy", "sell"):
            return choice(
                "inventory",
                "If this order fills, which way will its signed position move?",
                correct="up" if side == "buy" else "down",
                options=(("up", "Increases"), ("down", "Decreases")),
                context=(
                    "Buy adds units; sell subtracts units. This asks about the effect "
                    "of a fill, not whether the order will fill."
                ),
            )
    if kind == "hedge" and before["engine"] == "options":
        q = choice(
            "delta_hedging",
            "What signed stock adjustment approximately offsets the displayed aggregate delta?",
            context=(
                "Use only the displayed aggregate delta, including the existing stock hedge."
            ),
        )
        return replace(
            q,
            answer_type="number",
            expected=str(round(-c["greeks"]["delta"])),
            options=(),
            tolerance="0.5",
        )
    if kind in ("pair", "next_leg"):
        return choice(
            "leg_risk",
            "Does completing one leg guarantee that the next venue supplies the hedge?",
        )
    if "cancel" in kind:
        return choice(
            "limit_orders",
            "Can cancelling an unfilled remainder undo executions that already happened?",
        )
    if kind in ("step", "step_event", "step_interval", "advance"):
        return choice(
            "current_price", "Must the next observed price move in the direction you expect?"
        )
    return choice(
        "model_risk",
        "Would a profitable result by itself establish that this decision process was sound?",
    )
