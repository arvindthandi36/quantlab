"Causal derivatives session: finite option quotes and real stock exchange executions."

import math
import platform
from copy import deepcopy
from dataclasses import asdict, dataclass
from fractions import Fraction

from quantlab import __version__
from quantlab.options.analytics import curves, realised_volatility
from quantlab.options.models import (
    OptionContract,
    OptionType,
    PricingInputs,
    exact,
    number,
    years_from_days,
)
from quantlab.options.portfolio import OptionPortfolio
from quantlab.options.pricing import greeks, payoff
from quantlab.options.quotes import make_quote, quantize
from quantlab.options.underlying import UnderlyingVenue
from quantlab.portfolio.accounting import AccountingError
from quantlab.randomness import RandomStreams
from quantlab.replay_support import ReplayFrames
from quantlab.research.codec import digest, plain


@dataclass(frozen=True)
class OptionsConfig:
    seed: int = 42
    spot: float = 100.0
    strikes: tuple[float, ...] = (90, 95, 100, 105, 110)
    expiries_days: tuple[float, ...] = (30, 60)
    multiplier: int = 100
    steps: int = 60
    step_days: float = 1.0
    implied_volatility: float = 0.20
    process_volatility: float = 0.20
    physical_drift: float = 0.0
    rate: float = 0.0
    dividend_yield: float = 0.0
    skew: float = -0.15
    curvature: float = 0.25
    option_half_spread: float = 0.015
    option_fee: float = 0.05
    quote_size: int = 20
    stock_depth: int = 1000
    stock_fee: float = 0.001
    stock_spread_ticks: int = 1

    def __post_init__(self):
        RandomStreams(self.seed)
        for key, lo, hi in (
            ("spot", 1, 100_000),
            ("step_days", 0.01, 5),
            ("implied_volatility", 0.001, 3),
            ("process_volatility", 0, 3),
            ("physical_drift", -0.5, 0.5),
            ("rate", -0.2, 0.2),
            ("skew", -1, 1),
            ("curvature", 0, 2),
            ("option_half_spread", 0, 5),
            ("option_fee", 0, 100),
            ("stock_fee", 0, 1),
        ):
            object.__setattr__(self, key, number(getattr(self, key), key, lo, hi))
        if number(self.dividend_yield, "live lab dividend yield") != 0:
            raise ValueError(
                "Live lab requires zero dividends; pricing/MC support continuous "
                "yields separately"
            )
        for key, lo, hi in (
            ("multiplier", 1, 1000),
            ("steps", 1, 252),
            ("quote_size", 1, 1000),
            ("stock_depth", 1, 100_000),
            ("stock_spread_ticks", 1, 20),
        ):
            if type(getattr(self, key)) is not int or not lo <= getattr(self, key) <= hi:
                raise ValueError(f"{key} must be an integer in {lo}–{hi}")
        for key, lo, hi, limit in (
            ("strikes", 1, 100_000, 15),
            ("expiries_days", 0.01, 1260, 4),
        ):
            values = tuple(number(x, key, lo, hi) for x in getattr(self, key))
            if not 1 <= len(values) <= limit or len(set(values)) != len(values):
                raise ValueError(f"{key} requires 1–{limit} distinct values")
            object.__setattr__(self, key, tuple(sorted(values)))
        if self.spot * 100 <= self.stock_spread_ticks + 1:
            raise ValueError("initial stock cannot support positive bid prices")
        if any(
            (exact(days) / exact(self.step_days)).denominator != 1
            for days in self.expiries_days
        ):
            raise ValueError(
                "Expiry days must align exactly with the configured simulation step"
            )


class OptionsSession:
    def __init__(self, config=None, *, capture=True, capture_frames=False):
        self.config = config or OptionsConfig()
        self.capture = capture
        self.stock = UnderlyingVenue(
            self.config.spot,
            steps=self.config.steps,
            depth=self.config.stock_depth,
            fee=self.config.stock_fee,
            spread_ticks=self.config.stock_spread_ticks,
            capture=capture,
        )
        self.portfolio = OptionPortfolio()
        self.expiry_spots = {}
        self.contracts = {
            c.id: c
            for days in self.config.expiries_days
            for strike in self.config.strikes
            for kind in OptionType
            for c in [
                OptionContract(kind, strike, years_from_days(days), self.config.multiplier)
            ]
        }
        self.selected = min(
            self.contracts.values(),
            key=lambda c: (
                c.expiry_years,
                abs(float(c.strike_gbp) - self.config.spot),
                c.option_type.value,
            ),
        ).id
        self._rng = RandomStreams(self.config.seed).create("options.stock.innovations-v1")
        self._innovations = []
        self._model_spot = self.config.spot
        self.step_index = self.revision = self.quote_revision = 0
        self.elapsed_years = Fraction(0)
        self.current_iv = self.config.implied_volatility
        self.auto_frequency = 0
        self.status = "active"
        self.quotes = {}
        self.funding = Fraction(0)
        self.funding_ledger = []
        self.option_trades = []
        self.hedges = []
        self.history, self.actions, self.evidence = [], [], []
        self.frames = ReplayFrames() if capture_frames else None
        self.spots = [self.spot]
        self.max_delta = self.max_gamma = self.max_vega = self.max_drawdown = self.peak_pnl = (
            0.0
        )
        self.starting_greeks = None
        self.delta_squared_time = 0.0
        self._refresh_options()
        self._sample("Session opened; all instruments synthetic")

    @property
    def spot(self):
        return float(self.stock.account.reference / 100)

    @property
    def dt(self):
        return years_from_days(self.config.step_days)

    def _refresh_options(self):
        self.quote_revision += 1
        self.quotes = {
            k: make_quote(
                c,
                self.spot,
                self.elapsed_years,
                self.current_iv,
                self.config.rate,
                revision=self.quote_revision,
                size=self.config.quote_size,
                half_spread=self.config.option_half_spread,
                skew=self.config.skew,
                curvature=self.config.curvature,
            )
            for k, c in self.contracts.items()
            if c.remaining(self.elapsed_years) > 0
        }

    def _marks(self):
        return {k: q.midpoint for k, q in self.quotes.items()}

    def aggregate_greeks(self):
        total = {k: 0.0 for k in ("delta", "gamma", "vega", "theta", "rho")}
        for key, c in self.portfolio.contracts.items():
            qty = self.portfolio.quantity(key)
            if not qty:
                continue
            g = greeks(c.option_type, self.quotes[key].inputs)
            for name in total:
                val = getattr(g, name)
                if val is None:
                    raise ArithmeticError("Unsettled option has undefined portfolio Greeks")
                total[name] += val * qty * c.multiplier
        return total | {
            "option_delta": total["delta"],
            "delta": total["delta"] + self.stock.account.inventory,
        }

    def accounts(self):
        options = self.portfolio.snapshot(self._marks())
        stock = self.stock.account.snapshot()
        tick = Fraction(1, 100)
        fees = options["fees"] + stock.fees_ticks * tick
        option_gross = options["realised_gross"] + options["unrealised"]
        hedge_gross = (stock.realised_trading_pnl_ticks + stock.unrealised_pnl_ticks) * tick
        total = option_gross + hedge_gross + self.funding - fees
        cash = options["cash"] + stock.cash_ticks * tick + self.funding
        marked = options["marked_value"] + stock.inventory * stock.reference_ticks * tick
        if total != cash + marked:
            raise AccountingError("combined option/stock equity does not reconcile")
        return {
            "cash": cash,
            "option_cash": options["cash"],
            "stock_cash": stock.cash_ticks * tick,
            "option_value": options["marked_value"],
            "stock_value": stock.inventory * stock.reference_ticks * tick,
            "option_realised_gross": options["realised_gross"],
            "option_unrealised": options["unrealised"],
            "option_gross_pnl": option_gross,
            "hedge_gross_pnl": hedge_gross,
            "stock_realised_gross": stock.realised_trading_pnl_ticks * tick,
            "stock_unrealised": stock.unrealised_pnl_ticks * tick,
            "option_fees": options["fees"],
            "stock_fees": stock.fees_ticks * tick,
            "fees": fees,
            "financing": self.funding,
            "total_pnl": total,
        }

    def _sample(self, message):
        self.stock.check_invariants()
        self.portfolio.check(self._marks())
        if sum((x["cash_flow"] for x in self.funding_ledger), Fraction(0)) != self.funding:
            raise AccountingError("financing cash flows do not reconcile")
        account, g = self.accounts(), self.aggregate_greeks()
        pnl = float(account["total_pnl"])
        self.peak_pnl = max(self.peak_pnl, pnl)
        self.max_drawdown = max(self.max_drawdown, self.peak_pnl - pnl)
        self.max_delta = max(self.max_delta, abs(g["delta"]))
        self.max_gamma = max(self.max_gamma, abs(g["gamma"]))
        self.max_vega = max(self.max_vega, abs(g["vega"]))
        self.history.append(
            {
                "step": self.step_index,
                "elapsed_days": float(self.elapsed_years * 365),
                "spot": self.spot,
                "stock_position": self.stock.account.inventory,
                "total_pnl": pnl,
                "option_pnl": float(account["option_gross_pnl"]),
                "hedge_pnl": float(account["hedge_gross_pnl"]),
                "fees": float(account["fees"]),
                "delta": g["delta"],
                "gamma": g["gamma"],
                "vega": g["vega"],
                "message": message,
            }
        )
        if self.capture:
            self.evidence.append(
                plain(
                    {
                        "step": self.step_index,
                        "accounts": account,
                        "greeks": g,
                        "option_ledger": self.portfolio.ledger,
                        "stock_evidence_digest": digest(self.stock.evidence),
                    }
                )
            )
        if self.frames is not None:
            self.frames.append(self.snapshot())

    def _trade_option(self, key, side, quantity, quote_revision):
        if key not in self.quotes:
            raise ValueError("Choose a live, unexpired contract")
        if side not in ("buy", "sell") or type(quantity) is not int or not 1 <= quantity <= 100:
            raise ValueError("Option order requires buy/sell and 1–100 whole contracts")
        quote = self.quotes[key]
        if type(quote_revision) is not int or quote_revision != quote.revision:
            raise ValueError(
                "Stale option quote; inspect the current bid/ask before submitting"
            )
        sign = 1 if side == "buy" else -1
        available = quote.ask_size if sign == 1 else quote.bid_size
        filled = min(quantity, available)
        if abs(self.portfolio.quantity(key) + sign * filled) > 100:
            raise ValueError("Per-contract position limit is ±100 contracts")
        premium = quote.ask if sign == 1 else quote.bid
        guard = getattr(self, "portfolio_risk_guard", None)
        if guard is not None:
            message = guard(key, side, quantity, quote_revision)
            if message:
                return {"ok": False, "message": message, "filled": 0, "cancelled": quantity}
        if filled:
            self.portfolio.apply(
                quote.contract,
                sign * filled,
                premium,
                exact(self.config.option_fee) * filled,
                f"option-{len(self.portfolio.ledger) + 1}",
            )
            if sign == 1:
                quote.ask_size -= filled
            else:
                quote.bid_size -= filled
        # Any fill changes the quote revision, including the displayed available size.
        self.quote_revision += 1
        for q in self.quotes.values():
            q.revision = self.quote_revision
        result = {
            "contract_id": key,
            "side": side,
            "requested": quantity,
            "filled": filled,
            "cancelled": quantity - filled,
            "premium": float(premium),
            "multiplier": quote.contract.multiplier,
            "premium_cash_flow": float(-sign * filled * premium * quote.contract.multiplier),
            "fee": float(exact(self.config.option_fee) * filled),
            "step": self.step_index,
            "mechanism": "synthetic dealer quote; IOC",
        }
        self.option_trades.append(result)
        if filled and self.starting_greeks is None:
            self.starting_greeks = self.aggregate_greeks()
        return result

    def _stock_order(self, side, quantity, order_type="market", price=None, *, benchmark=False):
        before = len(self.stock.own_trades)
        reference = self.spot
        payload = {"side": side, "quantity": quantity, "order_type": order_type}
        if order_type == "limit":
            payload["price"] = price
        result = self.stock.command("order", **payload)
        fills = self.stock.own_trades[before:]
        if fills:
            self.hedges.append(
                {
                    "step": self.step_index,
                    "side": side,
                    "quantity": sum(f["quantity"] for f in fills),
                    "benchmark": benchmark,
                    "order_id": result["order_id"],
                }
            )
        if reference != self.spot:
            self._refresh_options()
        return result | {"actual_filled": sum(f["quantity"] for f in fills)}

    def hedge(self):
        g = self.aggregate_greeks()
        target = round(-g["option_delta"])
        quantity = target - self.stock.account.inventory
        if not quantity:
            return {
                "ok": True,
                "message": "Already at the nearest whole-unit hedge",
                "actual_filled": 0,
            }
        return self._stock_order(
            "buy" if quantity > 0 else "sell", abs(quantity), benchmark=True
        )

    def _step(self):
        before_cash = self.accounts()["cash"]
        self.delta_squared_time += self.aggregate_greeks()["delta"] ** 2 * float(self.dt)
        interest = quantize(
            before_cash * exact(math.expm1(self.config.rate * float(self.dt))), 8
        )
        self.funding += interest
        self.funding_ledger.append(
            {
                "step": self.step_index,
                "opening_cash": before_cash,
                "dt_years": self.dt,
                "cash_flow": interest,
            }
        )
        z = self._rng.gauss(0, 1)
        self._innovations.append(z)
        self._model_spot *= math.exp(
            (self.config.physical_drift - 0.5 * self.config.process_volatility**2)
            * float(self.dt)
            + self.config.process_volatility * math.sqrt(float(self.dt)) * z
        )
        if not math.isfinite(self._model_spot) or not 0.5 <= self._model_spot <= 1_000_000:
            raise ArithmeticError("Stock process left supported quote range; session failed")
        self.step_index += 1
        self.elapsed_years = self.step_index * self.dt
        before_fills = len(self.stock.own_trades)
        self.stock.refresh(self._model_spot, self.step_index)
        for fill in self.stock.own_trades[before_fills:]:
            self.hedges.append(
                {
                    "step": self.step_index,
                    "side": fill["side"],
                    "quantity": fill["quantity"],
                    "benchmark": False,
                    "order_id": fill["order_id"],
                    "role": "resting stock order filled",
                }
            )
        self.spots.append(self.spot)
        for key, contract in self.contracts.items():
            if contract.remaining(self.elapsed_years) == 0 and key not in self.expiry_spots:
                self.expiry_spots[key] = self.spot
        # Cash settlement uses exact strike and observed tick-grid spot, once per contract.
        for key, c in self.portfolio.contracts.copy().items():
            qty = self.portfolio.quantity(key)
            if qty and c.remaining(self.elapsed_years) == 0:
                intrinsic = max(
                    Fraction(0),
                    (exact(self.spot) - c.strike_gbp)
                    * (1 if c.option_type == OptionType.CALL else -1),
                )
                self.portfolio.apply(
                    c, -qty, intrinsic, 0, f"settlement-{key}", settlement=True
                )
        self._refresh_options()
        self._sample("Observed stock move; option time and quotes updated")
        if self.auto_frequency and (
            self.step_index % self.auto_frequency == 0 or self.step_index == self.config.steps
        ):
            self.hedge()
            self._sample("Automatic benchmark hedge used actual stock matching")
        if self.step_index == self.config.steps:
            self._end()

    def _end(self):
        self.stock.command("end")
        self.status = "ended"

    def command(self, kind, **payload):
        expected = {
            "option_order": {"contract_id", "side", "quantity", "quote_revision"},
            "stock_order": {"side", "quantity", "order_type", "price"},
            "cancel_stock": {"order_id"},
            "hedge": set(),
            "step": {"count"},
            "set_auto": {"frequency"},
            "set_iv": {"volatility"},
            "end": set(),
        }
        if self.status != "active":
            raise ValueError("Options session ended or failed; create a new session")
        if kind not in expected or set(payload) - expected[kind]:
            raise ValueError("Unknown options command or fields")
        required = {
            "option_order": expected["option_order"],
            "stock_order": {"side", "quantity"},
            "cancel_stock": {"order_id"},
            "set_auto": {"frequency"},
            "set_iv": {"volatility"},
        }
        if not required.get(kind, set()) <= set(payload):
            raise ValueError("Missing required options command fields")
        if len(self.actions) >= 3000 and kind != "end":
            raise ValueError("Options command budget reached; end and export this session")
        # Prevalidate predictable input errors before any mutation.
        if kind == "step":
            count = payload.get("count", 1)
            if type(count) is not int or not 1 <= count <= 252:
                raise ValueError("Step count must be 1–252")
        elif kind == "set_auto":
            if type(payload.get("frequency")) is not int or payload["frequency"] not in (
                0,
                1,
                5,
                20,
            ):
                raise ValueError("Hedge frequency must be 0, 1, 5 or 20 steps")
        elif kind == "set_iv":
            number(payload.get("volatility"), "annual decimal IV", 0.001, 3)
        try:
            if kind == "option_order":
                result = self._trade_option(
                    payload["contract_id"],
                    payload["side"],
                    payload["quantity"],
                    payload["quote_revision"],
                )
            elif kind == "stock_order":
                result = self._stock_order(**payload)
            elif kind == "cancel_stock":
                result = self.stock.command("cancel", **payload)
            elif kind == "hedge":
                result = self.hedge()
            elif kind == "step":
                for _ in range(min(count, self.config.steps - self.step_index)):
                    self._step()
                result = {"ok": True, "message": f"Observed step {self.step_index}"}
            elif kind == "set_auto":
                self.auto_frequency = payload["frequency"]
                result = {
                    "ok": True,
                    "message": f"Benchmark hedge interval: {self.auto_frequency or 'off'}",
                }
            elif kind == "set_iv":
                self.current_iv = float(payload["volatility"])
                self._refresh_options()
                result = {"ok": True, "message": "Current synthetic quote volatility changed"}
            else:
                self._end()
                result = {
                    "ok": True,
                    "message": "Session ended; open inventory marked, no invented liquidation",
                }
            self.revision += 1
            self._sample(kind.replace("_", " "))
            self.actions.append(plain({"kind": kind, "payload": payload, "result": result}))
            return result
        except (AccountingError, ArithmeticError):
            self.status = "failed"
            raise

    def metrics(self):
        a = {k: float(v) for k, v in self.accounts().items()}
        g = self.aggregate_greeks()
        return a | {
            "net_pnl": a["total_pnl"],
            "residual_delta": g["delta"],
            "gross_hedging_error": a["option_gross_pnl"]
            + a["hedge_gross_pnl"]
            + a["financing"],
            "rms_delta": math.sqrt(self.delta_squared_time / float(self.elapsed_years))
            if self.elapsed_years
            else abs(g["delta"]),
            "absolute_residual_delta": abs(g["delta"]),
            "max_absolute_delta": self.max_delta,
            "max_absolute_gamma": self.max_gamma,
            "max_absolute_vega": self.max_vega,
            "drawdown": self.max_drawdown,
            "turnover": sum(f.quantity for f in self.stock.account.fills),
            "hedges": len(self.hedges),
            "realised_volatility": realised_volatility(self.spots, float(self.dt)),
        }

    def snapshot(self, selected=None, *, include_curves=False):
        key = selected or self.selected
        if key not in self.contracts:
            raise ValueError("Unknown option contract")
        c = self.contracts[key]
        selected_quote = (
            self.quotes[key].public(self.elapsed_years)
            if key in self.quotes
            else {
                **c.public(self.elapsed_years),
                "expired": True,
                "expiry_spot": self.expiry_spots[key],
                "payoff": payoff(c.option_type, self.expiry_spots[key], float(c.strike_gbp)),
                "time_value": 0,
            }
        )
        positions = []
        for row in self.portfolio.snapshot(self._marks())["positions"]:
            contract = row["contract"]
            qty = row["quantity"]
            g = (
                greeks(contract.option_type, self.quotes[contract.id].inputs)
                .scaled(qty * contract.multiplier)
                .public()
                if qty
                else {name: 0 for name in ("delta", "gamma", "vega", "theta", "rho")}
            )
            positions.append(
                {
                    **contract.public(self.elapsed_years),
                    "quantity": qty,
                    **{
                        k: float(row[k])
                        for k in ("mark", "value", "realised_gross", "unrealised")
                    },
                    "settled": row["settled"],
                    "position_greeks": g,
                }
            )
        state = {
            "revision": self.revision,
            "status": self.status,
            "step": self.step_index,
            "steps": self.config.steps,
            "elapsed_days": float(self.elapsed_years * 365),
            "step_days": self.config.step_days,
            "spot": self.spot,
            "rate": self.config.rate,
            "dividend_yield": 0,
            "current_volatility_input": self.current_iv,
            "starting_volatility_input": self.config.implied_volatility,
            "process_volatility_setting": self.config.process_volatility,
            "auto_frequency": self.auto_frequency,
            "selected": selected_quote,
            "positions": positions,
            "accounts": self.metrics(),
            "ending_quote_iv": selected_quote.get("iv", {}).get("volatility"),
            "greeks": self.aggregate_greeks(),
            "starting_greeks": self.starting_greeks,
            "chain": [q.public(self.elapsed_years) for q in self.quotes.values()],
            "stock": self.stock.public_snapshot(),
            "option_trades": list(self.option_trades),
            "history": list(self.history),
            "hedges": list(self.hedges),
            "settlements": plain(
                [r for r in self.portfolio.ledger if r["kind"] == "settlement"]
            ),
            "mechanism": (
                "Finite synthetic option dealer quotes; stock on Phase 1 FIFO exchange"
            ),
            "greek_units": (
                "Per underlying unit; vega/rho per 1.00 annual decimal; theta per model year"
            ),
            "valuation": (
                "Option midpoint and stock public mark are not guaranteed liquidation prices"
            ),
        }
        if include_curves:
            x = (
                self.quotes[key].inputs
                if key in self.quotes
                else PricingInputs.for_contract(
                    c, self.spot, self.elapsed_years, self.current_iv, self.config.rate
                )
            )
            state["curves"] = curves(c.option_type, x)
        return deepcopy(state)

    def journal(self):
        if self.status != "ended":
            raise ValueError("End the session before exporting its reproducibility seed")
        if not self.capture:
            raise ValueError("Regenerate with full capture for a replay journal")
        body = {
            "schema": "quantlab-options-v1",
            "versions": {"quantlab": __version__, "python": platform.python_version()},
            "configuration": asdict(self.config),
            "actions": self.actions,
            "evidence": self.evidence,
            "stock_evidence": self.stock.evidence,
            "final": self.snapshot(),
        }
        return plain(body | {"digest": digest(body)})


def replay_options(raw, *, capture_frames=False):
    if not isinstance(raw, dict) or set(raw) != {
        "schema",
        "versions",
        "configuration",
        "actions",
        "evidence",
        "stock_evidence",
        "final",
        "digest",
    }:
        raise ValueError("Invalid options replay schema")
    body = {k: v for k, v in raw.items() if k != "digest"}
    if raw["schema"] != "quantlab-options-v1" or digest(body) != raw["digest"]:
        raise ValueError("Options journal integrity mismatch")
    if raw["versions"] != {"quantlab": __version__, "python": platform.python_version()}:
        raise ValueError("Exact options replay requires the recorded simulator/Python versions")
    session = OptionsSession(
        OptionsConfig(**raw["configuration"]), capture_frames=capture_frames
    )
    for action in raw["actions"]:
        result = session.command(action["kind"], **action["payload"])
        if plain(result) != action["result"]:
            raise ValueError("Options action replay mismatch")
    if session.journal() != raw:
        raise ValueError("Options financial evidence replay mismatch")
    return session
