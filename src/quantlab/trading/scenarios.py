"""Reusable, uncalibrated scenario data; no prescribed future trades or rewards."""

from dataclasses import dataclass, replace
from fractions import Fraction

from quantlab.domain import Side, positive_integer
from quantlab.market.config import SimulationConfig
from quantlab.market_making.config import exact


@dataclass(frozen=True)
class Scenario:
    key: str
    title: str
    objective: str
    market: SimulationConfig
    initial_book: tuple[tuple[str, int, int], ...]
    initial_position: int = 0
    position_limit: int = 20
    cash_ticks: Fraction = Fraction(1_000_000)
    fee_ticks: Fraction = Fraction(1, 10)
    automated_maker: bool = True
    target_position: int | None = None
    drawdown_budget_ticks: Fraction = Fraction(100)

    def __post_init__(self):
        positive_integer(self.position_limit, "position limit")
        if type(self.initial_position) is not int:
            raise ValueError("initial position must be an integer")
        if abs(self.initial_position) > self.position_limit:
            raise ValueError("opening position exceeds limit")
        for name in ("cash_ticks", "fee_ticks", "drawdown_budget_ticks"):
            object.__setattr__(self, name, exact(getattr(self, name), name))
        if type(self.automated_maker) is not bool:
            raise ValueError("automated_maker must be boolean")
        if self.target_position is not None and (
            type(self.target_position) is not int
            or abs(self.target_position) > self.position_limit
        ):
            raise ValueError("target position is outside risk limit")
        bids, asks = [], []
        for side, price, quantity in self.initial_book:
            side = Side(side)
            positive_integer(price, "initial price")
            positive_integer(quantity, "initial quantity")
            (bids if side is Side.BUY else asks).append(price)
        if bids and asks and max(bids) >= min(asks):
            raise ValueError("initial book must not be crossed")


BASE = SimulationConfig(
    duration_us=60_000_000,
    noise_rate_per_second=3,
    liquidity_rate_per_second=1.5,
    informed_rate_per_second=0.5,
    noise_price_radius_ticks=5,
    latent_sigma_ticks=2,
)
DEPTH = (
    ("sell", 10001, 2),
    ("sell", 10002, 5),
    ("sell", 10003, 8),
    ("buy", 9999, 5),
    ("buy", 9998, 5),
    ("buy", 9997, 8),
)
SCENARIOS = {
    "normal": Scenario(
        "normal",
        "Normal market",
        "Trade for 60 seconds with maximum drawdown no greater than £1.",
        BASE,
        DEPTH,
    ),
    "volatile": Scenario(
        "volatile",
        "High volatility",
        "Observe a more volatile value process; finish within the £1 drawdown budget.",
        replace(BASE, latent_sigma_ticks=8),
        DEPTH,
    ),
    "toxic": Scenario(
        "toxic",
        "Toxic flow",
        "Manage your exposure with more informed trading; keep drawdown within £1.",
        replace(BASE, informed_rate_per_second=4, signal_noise_ticks=1),
        DEPTH,
    ),
    "thin": Scenario(
        "thin",
        "Thin liquidity",
        "Acquire 5 units by session end while watching execution cost.",
        replace(BASE, noise_rate_per_second=1),
        tuple((s, p, 1) for s, p, _ in DEPTH),
        target_position=5,
        automated_maker=False,
    ),
    "position": Scenario(
        "position",
        "Position management",
        "Reduce your opening long or short position to zero by session end.",
        BASE,
        DEPTH,
        initial_position=8,
        target_position=0,
    ),
}


def scenario_from_dict(raw: dict) -> Scenario:
    market = dict(raw["market"])
    market["markout_horizons_events"] = tuple(market["markout_horizons_events"])
    return Scenario(
        **{
            **raw,
            "market": SimulationConfig(**market),
            "initial_book": tuple(tuple(x) for x in raw["initial_book"]),
        }
    )


def select_scenario(
    key="normal", *, seed=42, position_limit=20, initial_position=None, duration_seconds=60
) -> Scenario:
    if key not in SCENARIOS:
        raise ValueError("unknown scenario")
    positive_integer(duration_seconds, "duration seconds")
    if (
        duration_seconds > 300
        or type(position_limit) is not int
        or not 2 <= position_limit <= 1000
    ):
        raise ValueError("use duration 1–300 seconds and position limit 2–1000")
    source = SCENARIOS[key]
    initial = source.initial_position if initial_position is None else initial_position
    if key != "position" and initial != 0:
        raise ValueError("opening position is configured in Position management")
    return replace(
        source,
        objective=source.objective.replace("60 seconds", f"{duration_seconds} seconds"),
        market=replace(source.market, seed=seed, duration_us=duration_seconds * 1_000_000),
        initial_position=initial,
        position_limit=position_limit,
    )
