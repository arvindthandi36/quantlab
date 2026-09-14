"""Transparent policy over detached observed signals and current positions."""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Rules:
    entry: float = 2
    exit: float = 0.4
    stop: float = 4
    max_holding: int = 40
    max_loss: float = 50
    max_gross: float = 10000
    max_imbalance: float = 2000
    notional: float = 1000
    sizing: str = "hedge_ratio"
    volatility_budget: float = 3
    window: int = 80
    z_window: int = 40
    mode: str = "fixed"
    block: int = 20
    execution_order: str = "y_first"

    def __post_init__(self):
        numeric = (
            self.entry,
            self.exit,
            self.stop,
            self.max_loss,
            self.max_gross,
            self.max_imbalance,
            self.notional,
            self.volatility_budget,
        )
        if any(isinstance(x, bool) or not math.isfinite(x) for x in numeric):
            raise ValueError("Rules require finite numeric values")
        if not 0 <= self.exit < self.entry < self.stop <= 100:
            raise ValueError("Require 0 <= exit < entry < stop <= 100")
        if (
            min(
                self.max_loss,
                self.max_gross,
                self.max_imbalance,
                self.notional,
                self.volatility_budget,
            )
            <= 0
            or self.notional > self.max_gross
        ):
            raise ValueError("Positive limits and notional <= gross limit required")
        if type(self.max_holding) is not int or not 1 <= self.max_holding <= 1000:
            raise ValueError("Holding limit must be 1–1000 observations")
        if self.sizing not in ("hedge_ratio", "fixed_notional", "volatility_scaled"):
            raise ValueError("Unknown sizing rule")
        if self.execution_order not in ("x_first", "y_first"):
            raise ValueError("Choose x_first or y_first")
        from quantlab.statarb.statistics import CausalModel

        CausalModel(
            window=self.window, z_window=self.z_window, mode=self.mode, block=self.block
        )


def sizes(rules, prices, beta, sd):
    x, y = prices
    if not math.isfinite(beta) or not 0.05 <= beta <= 5:
        raise ValueError("Estimated beta outside supported positive unit-hedge range [.05,5]")
    if rules.sizing == "fixed_notional":
        qy, qx = int(rules.notional / 2 / y), -int(rules.notional / 2 / x)
    else:
        qy = int(rules.notional / (y + abs(beta) * x))
        if rules.sizing == "volatility_scaled":
            if sd is None or sd <= 1e-9:
                raise ValueError("Volatility sizing needs a usable past residual SD")
            qy = min(qy, int(rules.volatility_budget / sd))
        qx = -round(beta * qy)
    if min(abs(qx), qy) < 1:
        raise ValueError("Sizing rounds a leg to zero; increase explicit notional")
    # Rounded beta-equivalent leg can marginally exceed nominal budget: fail, don't hide it.
    if abs(qx) * x + qy * y > rules.max_gross:
        raise ValueError("Rounded executable pair exceeds gross limit")
    return (qx, qy)


def decision(rules, signal, *, held=False, age=0, pnl=0, gross=0, imbalance=0):
    if held:
        if gross > rules.max_gross:
            return "close", "gross exposure limit"
        if imbalance > rules.max_imbalance:
            return "close", "leg imbalance limit"
        if pnl <= -rules.max_loss:
            return "close", "pair loss limit"
        if age >= rules.max_holding:
            return "close", "maximum holding period"
    if not signal.get("available") or signal.get("z") is None:
        return "wait", signal.get("reason") or "model unavailable"
    z = signal["z"]
    if abs(z) >= rules.stop:
        return ("close" if held else "wait"), "relationship warning / maximum spread z"
    if held:
        return (
            ("close", "spread near recent mean")
            if abs(z) <= rules.exit
            else ("wait", "holding within rules")
        )
    if z >= rules.entry:
        return "short", "positive residual exceeds prespecified entry"
    if z <= -rules.entry:
        return "long", "negative residual exceeds prespecified entry"
    return "wait", "entry threshold not reached"
