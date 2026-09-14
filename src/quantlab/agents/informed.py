"""A one-signal Gaussian belief and a conservative, executable-edge decision."""

import math
from dataclasses import dataclass

from quantlab.agents.basic import PublicObservation
from quantlab.domain import LimitOrder, Side
from quantlab.market.config import finite_nonnegative


@dataclass(frozen=True, slots=True)
class PrivateSignal:
    """Only the measurement is disclosed; no latent truth, error or future state."""

    time_us: int
    value_ticks: float
    noise_sd_ticks: float

    def __post_init__(self) -> None:
        if type(self.time_us) is not int or self.time_us < 0:
            raise ValueError("signal time must be nonnegative integer microseconds")
        if type(self.value_ticks) not in (int, float) or not math.isfinite(self.value_ticks):
            raise ValueError("signal measurement must be finite")
        finite_nonnegative(self.noise_sd_ticks, "noise_sd_ticks")
        if self.noise_sd_ticks == 0:
            raise ValueError("signal noise must be positive; perfect signals are not supported")


@dataclass(frozen=True, slots=True)
class InformedDecision:
    """Private diagnostics; only the chosen order may enter a public projection."""

    order: LimitOrder | None
    reason: str
    prior_ticks: float
    signal_weight: float
    estimated_value_ticks: float
    posterior_sd_ticks: float
    threshold_ticks: float
    buy_edge_ticks: float | None
    sell_edge_ticks: float | None


@dataclass(frozen=True, slots=True)
class InformedTrader:
    """Subjective normal prior around a public reference; one-unit aggressive limits.

    No position model, memory of past signals, or access to future information.
    Cost allowance is per unit; it is a decision input, not booked P&L or a fee ledger.
    """

    prior_sd_ticks: float = 8.0
    cost_ticks: float = 0.25
    minimum_edge_ticks: float = 0.25
    uncertainty_multiplier: float = 0.5

    def __post_init__(self) -> None:
        for name in (
            "prior_sd_ticks",
            "cost_ticks",
            "minimum_edge_ticks",
            "uncertainty_multiplier",
        ):
            finite_nonnegative(getattr(self, name), name)
        if self.prior_sd_ticks == 0:
            raise ValueError("prior_sd_ticks must be positive")

    def decide(
        self, order_id: str, public: PublicObservation, signal: PrivateSignal, *, now_us: int
    ) -> InformedDecision:
        """Use a current signal only. Gross estimated edge must strictly exceed the hurdle."""
        if type(now_us) is not int or now_us < 0 or signal.time_us != now_us:
            raise ValueError("informed decisions require a fresh signal at the current time")
        if public.best_bid is not None and public.best_ask is not None:
            if public.best_bid >= public.best_ask:
                raise ValueError("informed decision requires an uncrossed public book")
        prior, _ = public.reference()
        scale = math.hypot(self.prior_sd_ticks, signal.noise_sd_ticks)
        weight = (self.prior_sd_ticks / scale) ** 2
        uncertainty = (self.prior_sd_ticks / scale) * signal.noise_sd_ticks
        estimate = (1 - weight) * prior + weight * signal.value_ticks
        threshold = (
            self.cost_ticks
            + self.minimum_edge_ticks
            + self.uncertainty_multiplier * uncertainty
        )
        if (
            not all(math.isfinite(x) for x in (estimate, uncertainty, threshold))
            or uncertainty <= 0
        ):
            raise ValueError("nonfinite or numerically degenerate informed estimate")
        buy_edge = None if public.best_ask is None else estimate - public.best_ask
        sell_edge = None if public.best_bid is None else public.best_bid - estimate
        order = None
        reason = "hold: no available quote clears costs, minimum edge and uncertainty buffer"
        if buy_edge is not None and buy_edge > threshold:
            order = LimitOrder(order_id, Side.BUY, 1, public.best_ask)
            reason = "buy: estimated value minus executable ask strictly exceeds the hurdle"
        elif sell_edge is not None and sell_edge > threshold:
            order = LimitOrder(order_id, Side.SELL, 1, public.best_bid)
            reason = "sell: executable bid minus estimated value strictly exceeds the hurdle"
        return InformedDecision(
            order,
            reason,
            float(prior),
            weight,
            estimate,
            uncertainty,
            threshold,
            buy_edge,
            sell_edge,
        )
