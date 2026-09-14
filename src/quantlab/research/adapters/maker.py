"""Market-making adapter with transient event observation and bounded markout history."""

import hashlib
import math
from collections import defaultdict
from dataclasses import asdict
from fractions import Fraction

from quantlab import Side
from quantlab.market.config import SimulationConfig
from quantlab.market_making.config import MakerConfig, Strategy
from quantlab.market_making.lab import MarketMakingLab
from quantlab.research.codec import plain
from quantlab.research.models import SimulationOutcome


def maker_configuration(*, duration_us=30_000_000, strategy="fixed", **maker_changes) -> dict:
    market = asdict(SimulationConfig(duration_us=duration_us, informed_rate_per_second=1))
    del market["seed"]
    return plain(
        {
            "market": market,
            "strategy": asdict(MakerConfig(strategy=Strategy(strategy), **maker_changes)),
        }
    )


def configurations(seed, configuration):
    if set(configuration) != {"market", "strategy"} or "seed" in configuration["market"]:
        raise ValueError(
            "maker adapter requires market/strategy config; seed belongs to engine"
        )
    market = dict(configuration["market"])
    market["markout_horizons_events"] = tuple(market["markout_horizons_events"])
    maker = dict(configuration["strategy"])
    maker["strategy"] = Strategy(maker["strategy"])
    if maker["strategy"] is Strategy.MANUAL:
        raise ValueError("Monte Carlo requires an automatic strategy")
    return SimulationConfig(seed=seed, **market), MakerConfig(**maker)


class MakerAccumulator:
    """Keep sufficient statistics and not-yet-mature marks, never full book histories.

    Accounting and matching checks remain in the actual lab. This sink draws no RNG.
    A transient record fingerprint permits exact full-mode regeneration checks.
    """

    def __init__(self, horizons):
        self.horizons = horizons
        self.history_hash = hashlib.sha256()
        self.environment_hash = hashlib.sha256()
        self.last = None
        self.last_public_number = 0
        self.final_account = None
        self.ended = False
        self.events = 0
        self.area = self.abs_area = self.square_area = self.quote_area = self.quote_time = 0
        self.posted = self.buy_fills = self.sell_fills = self.buy_units = self.sell_units = 0
        self.turnover = self.covered_units = 0
        self.effective_sum = Fraction(0)
        self.peak = self.drawdown = Fraction(0)
        self.pending = defaultdict(list)
        self.marks = {
            h: {
                "weighted_sum_ticks": Fraction(0),
                "available_units": 0,
                "missing_units": 0,
                "pending_units": 0,
            }
            for h in horizons
        }

    def __call__(self, record):
        self.events += 1
        self.history_hash.update(repr(record).encode())
        self.history_hash.update(b"\n")
        if (market := record.market) is not None:
            exogenous = (
                market.event.time_us,
                market.event.sequence,
                market.event.kind,
                market.latent_before_ticks,
                market.latent_after_ticks,
                None if market.informed is None else market.informed.signal,
            )
            self.environment_hash.update(repr(exogenous).encode())
            self.environment_hash.update(b"\n")
        public = record.kind != "market" or (market is not None and market.order is not None)
        if not public:
            return
        if self.last is None and record.time_us != 0:
            raise ValueError("batch diagnostics require a time-zero observation")
        if self.last is not None:
            before_time, q, quotes = self.last
            dt = record.time_us - before_time
            if dt < 0:
                raise ValueError("batch observations moved backwards")
            self.area += dt * q
            self.abs_area += dt * abs(q)
            self.square_area += dt * q * q
            bids = [o for o in quotes if o.side is Side.BUY]
            asks = [o for o in quotes if o.side is Side.SELL]
            if bids and asks:
                self.quote_time += dt
                self.quote_area += dt * (asks[0].price_ticks - bids[0].price_ticks)
        if record.public_event_number > self.last_public_number:
            mid = record.book_after.mid_price_ticks
            for h, sign, size, price in self.pending.pop(record.public_event_number, ()):
                group = self.marks[h]
                group["pending_units"] -= size
                if mid is None:
                    group["missing_units"] += size
                else:
                    group["available_units"] += size
                    group["weighted_sum_ticks"] += size * sign * (mid - price)
            self.last_public_number = record.public_event_number
        if record.plan is not None:
            self.posted += record.plan.bid_size + record.plan.ask_size
        for fill in record.fills:
            sign = 1 if fill.side is Side.BUY else -1
            if sign == 1:
                self.buy_fills += 1
                self.buy_units += fill.quantity
            else:
                self.sell_fills += 1
                self.sell_units += fill.quantity
            self.turnover += fill.quantity * fill.price_ticks
            if fill.midpoint_before_ticks is not None:
                self.covered_units += fill.quantity
                self.effective_sum += (
                    2 * fill.signed_quantity * (fill.midpoint_before_ticks - fill.price_ticks)
                )
            for h in self.horizons:
                self.pending[fill.public_event_number + h].append(
                    (h, sign, fill.quantity, fill.price_ticks)
                )
                self.marks[h]["pending_units"] += fill.quantity
        account = record.account
        self.peak = max(self.peak, account.total_pnl_ticks)
        self.drawdown = max(self.drawdown, self.peak - account.total_pnl_ticks)
        self.last = (record.time_us, account.inventory, record.own_quotes)
        self.final_account = account
        self.ended = record.kind == "end"

    def outcome(self, tick_size, *, journal=None) -> SimulationOutcome:
        if not self.ended or self.last is None:
            raise ValueError("batch session did not reach its complete horizon")
        tick = Fraction(tick_size)
        account = self.final_account
        duration = self.last[0]

        def money(x):
            return None if x is None else float(x * tick)

        metrics = {
            "net_pnl": money(account.total_pnl_ticks),
            "realised_pnl": money(account.realised_pnl_ticks),
            "gross_realised_pnl": money(account.realised_trading_pnl_ticks),
            "unrealised_pnl": money(account.unrealised_pnl_ticks),
            "execution_edge": money(account.spread_capture_ticks),
            "inventory_movement": money(account.inventory_movement_ticks),
            "fees": money(account.fees_ticks),
            "turnover": money(self.turnover),
            "maximum_drawdown": money(self.drawdown),
            "average_inventory": self.area / duration,
            "average_absolute_inventory": self.abs_area / duration,
            "rms_inventory": math.sqrt(self.square_area / duration),
            "maximum_absolute_inventory": account.maximum_absolute_inventory,
            "final_inventory": account.inventory,
            "fill_rate": (self.buy_units + self.sell_units) / self.posted
            if self.posted
            else None,
            "buy_fills": self.buy_fills,
            "sell_fills": self.sell_fills,
            "buy_units": self.buy_units,
            "sell_units": self.sell_units,
            "average_quoted_spread": money(Fraction(self.quote_area, self.quote_time))
            if self.quote_time
            else None,
            "two_sided_quote_time_fraction": self.quote_time / duration,
            "average_effective_spread": money(self.effective_sum / self.covered_units)
            if self.covered_units
            else None,
        }
        for h, group in self.marks.items():
            metrics[f"markout_{h}"] = (
                money(group["weighted_sum_ticks"] / group["available_units"])
                if group["available_units"]
                else None
            )
        return SimulationOutcome(
            metrics,
            self.environment_hash.hexdigest(),
            self.history_hash.hexdigest(),
            plain(
                {
                    "markouts": self.marks,
                    "effective_spread_units": self.covered_units,
                    "posted_units": self.posted,
                    "observed_records": self.events,
                }
            ),
            journal,
        )


class MakerAdapter:
    name = "market-making-v1"

    def validate(self, configuration):
        configurations(0, configuration)

    def environment_key(self, configuration):
        return configuration["market"]

    def run(self, seed, configuration, *, full=False):
        market, maker = configurations(seed, configuration)
        sink = MakerAccumulator(market.markout_horizons_events)
        lab = MarketMakingLab(market, maker, retain_records=full, record_sink=sink)
        lab.run_to_completion()
        return sink.outcome(market.tick_size, journal=lab.result() if full else None)

    def metric_units(self, configuration):
        units = {
            key: "GBP"
            for key in (
                "net_pnl",
                "realised_pnl",
                "gross_realised_pnl",
                "unrealised_pnl",
                "execution_edge",
                "inventory_movement",
                "fees",
                "turnover",
                "maximum_drawdown",
            )
        }
        units.update(
            {
                key: "units"
                for key in (
                    "average_inventory",
                    "average_absolute_inventory",
                    "rms_inventory",
                    "maximum_absolute_inventory",
                    "final_inventory",
                    "buy_units",
                    "sell_units",
                )
            }
        )
        units.update(
            {key: "fraction" for key in ("fill_rate", "two_sided_quote_time_fraction")}
        )
        units.update({key: "execution records" for key in ("buy_fills", "sell_fills")})
        units.update(
            {key: "GBP/unit" for key in ("average_quoted_spread", "average_effective_spread")}
        )
        units.update(
            {
                f"markout_{h}": "GBP/unit"
                for h in configuration["market"]["markout_horizons_events"]
            }
        )
        return units
