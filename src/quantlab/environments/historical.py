"""Next-observation paper execution and exact core ledgers over revealed bars."""

import copy
from dataclasses import asdict, dataclass
from decimal import Decimal
from fractions import Fraction

import numpy as np

from quantlab import __version__
from quantlab.domain import PriceGrid, Side
from quantlab.environments import EXECUTION_VERSION, SCHEMA
from quantlab.environments.data import amount, compatible, integer
from quantlab.execution import vwap
from quantlab.portfolio.accounting import AccountingError, MakerAccount, MakerFill
from quantlab.research.codec import digest
from quantlab.risk.metrics import empirical_risk
from quantlab.risk.monte_carlo import revalue_returns
from quantlab.risk.portfolio import Portfolio, Position
from quantlab.statarb.statistics import CausalModel
from quantlab.statarb.strategy import Rules, decision


@dataclass(frozen=True)
class Execution:
    participation: str = "0.10"
    slippage_ticks: int = 1
    fee_per_unit: str = "0.001"
    position_limit: int = 100
    initial_cash: str = "10000"

    def __post_init__(self):
        amount(self.participation, "Volume participation", 0.0001, 1)
        amount(self.fee_per_unit, "Fee per unit", 0, 10)
        amount(self.initial_cash, "Initial cash", 1, 1_000_000)
        for name in ("participation", "fee_per_unit", "initial_cash"):
            object.__setattr__(self, name, str(getattr(self, name)))
        integer(self.slippage_ticks, "Adverse slippage ticks", 0, 1000)
        integer(self.position_limit, "Position limit", 1, 1000)


class HistoricalSession:
    engine = "historical"

    def __init__(self, datasets, execution=None, *, model=None):
        compatible(datasets)
        self._datasets = tuple(datasets)
        self.execution = Execution(**(execution or {}))
        self.model_config = dict(window=20, z_window=12, mode="rolling", block=10) | (
            model or {}
        )
        self.model = CausalModel(**self.model_config)
        self.accounts, self.counterparties = {}, {}
        for i, d in enumerate(datasets):
            cash = Fraction(self.execution.initial_cash) / d.tick if i == 0 else Fraction(0)
            key = d.meta["instrument"]
            self.accounts[key] = MakerAccount(
                cash, Fraction(d.bars[0].close), hard_limit=self.execution.position_limit
            )
            self.counterparties[key] = MakerAccount(
                Fraction(0), Fraction(d.bars[0].close), hard_limit=1_000_000
            )
        self.index = self.revision = 0
        self.status = "paused"
        self.orders, self.fills, self.actions, self.timeline, self.path = [], [], [], [], []
        self.peak = self.max_drawdown = Fraction(0)
        self.last_result = {
            "ok": True,
            "message": "First bar is revealed; orders wait for the next observation.",
        }
        self._point()

    @property
    def instruments(self):
        return tuple(d.meta["instrument"] for d in self._datasets)

    def _dataset(self, instrument):
        if instrument not in self.instruments:
            raise ValueError("Choose an imported instrument")
        return self._datasets[self.instruments.index(instrument)]

    def _prefix(self):
        return [
            [float(d.bars[i].close * d.tick) for d in self._datasets]
            for i in range(self.index + 1)
        ]

    def portfolio(self):
        cash = realised = unrealised = fees = Fraction(0)
        positions = []
        for key, account in self.accounts.items():
            d = self._dataset(key)
            s = account.snapshot()
            cash += s.cash_ticks * d.tick
            realised += s.realised_trading_pnl_ticks * d.tick
            unrealised += s.unrealised_pnl_ticks * d.tick
            fees += s.fees_ticks * d.tick
            if s.inventory:
                mark = float(s.reference_ticks * d.tick)
                positions.append(Position(key, key, s.inventory, 1, mark, mark))
        return Portfolio(
            tuple(positions),
            float(cash),
            float(realised),
            float(unrealised),
            float(fees),
            initial_capital=float(self.execution.initial_cash),
            drawdown=float(self.max_drawdown),
            source="Simulated account over revealed imported observations",
        )

    def _point(self):
        pnl = sum(
            (
                a.snapshot().total_pnl_ticks * self._dataset(k).tick
                for k, a in self.accounts.items()
            ),
            Fraction(0),
        )
        self.peak = max(self.peak, pnl)
        self.max_drawdown = max(self.max_drawdown, self.peak - pnl)
        self.path.append(
            dict(
                index=self.index,
                pnl=float(pnl),
                drawdown=float(self.peak - pnl),
                position={k: a.inventory for k, a in self.accounts.items()},
            )
        )
        self.check()

    def check(self):
        try:
            self._check()
        except AccountingError:
            self.status = "failed"
            raise

    def _check(self):
        for k, a in self.accounts.items():
            b = self.counterparties[k]
            a.check_invariants()
            b.check_invariants()
            x, y = a.snapshot(), b.snapshot()
            if (
                x.inventory + y.inventory != 0
                or x.execution_cash_ticks + y.execution_cash_ticks != 0
            ):
                raise AccountingError("Paper counterpart cash/quantity conservation failed")
            if len(a.fills) != len(b.fills) or any(
                p.quantity != q.quantity or p.price_ticks != q.price_ticks or p.side == q.side
                for p, q in zip(a.fills, b.fills, strict=True)
            ):
                raise AccountingError("Paper buyer/seller executions do not reconcile")
        all_fills = [f for account in self.accounts.values() for f in account.fills]
        if len(all_fills) != len(self.fills):
            raise AccountingError("Paper ledger/tape count mismatch")
        for k, account in self.accounts.items():
            tape = [f for f in self.fills if f["instrument"] == k]
            for fill, recorded in zip(account.fills, tape, strict=True):
                if (
                    fill.quantity != recorded["quantity"]
                    or fill.side.value != recorded["side"]
                    or fill.price_ticks * self._dataset(k).tick
                    != Fraction(recorded["exact_price"])
                ):
                    raise AccountingError("Paper execution disagrees with recorded tape")
        if sum(o["filled"] for o in self.orders) != sum(f["quantity"] for f in self.fills):
            raise AccountingError("Order fill totals disagree with paper transaction tape")

    def _order(self, *, instrument, side, quantity, order_type="market", price=None):
        d = self._dataset(instrument)
        side = Side(side)
        integer(quantity, "Quantity", 1, 1000)
        if order_type not in ("market", "limit"):
            raise ValueError("Choose market or limit")
        if order_type == "market" and price is not None:
            raise ValueError("Market orders cannot include a limit price")
        limit = (
            PriceGrid(Decimal(d.meta["tick_size"])).to_ticks(price)
            if order_type == "limit"
            else None
        )
        reserved = sum(
            o["remaining"]
            for o in self.orders
            if o["instrument"] == instrument and o["side"] == side.value
        )
        q = self.accounts[instrument].inventory
        future = q + (reserved + quantity) * (1 if side is Side.BUY else -1)
        if abs(future) > self.execution.position_limit:
            raise ValueError("Order and same-side outstanding orders exceed the position limit")
        order = dict(
            order_id=f"paper-{len(self.orders) + 1}",
            instrument=instrument,
            side=side.value,
            type=order_type,
            price=None if limit is None else float(limit * d.tick),
            limit_ticks=limit,
            original=quantity,
            filled=0,
            remaining=quantity,
            cancelled=0,
            submitted_index=self.index,
            status="waiting for next observation",
            vwap=None,
            fills=[],
        )
        self.orders.append(order)
        return {
            "ok": True,
            "message": "Order accepted; no same-observation fill.",
            "order_id": order["order_id"],
        }

    def _cancel(self, order_id):
        order = next((o for o in self.orders if o["order_id"] == order_id), None)
        if order is None or not order["remaining"]:
            raise ValueError("Choose an open paper order")
        order["cancelled"] += order["remaining"]
        order["remaining"] = 0
        order["status"] = "cancelled"
        return {"ok": True, "message": "Unfilled paper quantity cancelled"}

    def _advance(self):
        if self.index == len(self._datasets[0].bars) - 1:
            self._end()
            return
        self.index += 1
        budgets = {}
        for d in self._datasets:
            k, bar = d.meta["instrument"], d.bars[self.index]
            self.accounts[k].mark(Fraction(bar.close))
            self.counterparties[k].mark(Fraction(bar.close))
            budgets[k] = int(bar.volume * Fraction(self.execution.participation))
        for order in self.orders:
            if not order["remaining"] or order["submitted_index"] >= self.index:
                continue
            key = order["instrument"]
            d, a, b = self._dataset(key), self.accounts[key], self.counterparties[key]
            side = Side(order["side"])
            bar = d.bars[self.index]
            price = bar.close + self.execution.slippage_ticks * (1 if side is Side.BUY else -1)
            eligible = price > 0 and (
                order["type"] == "market"
                or (
                    price <= order["limit_ticks"]
                    if side is Side.BUY
                    else price >= order["limit_ticks"]
                )
            )
            size = min(order["remaining"], budgets[key]) if eligible else 0
            if size:
                trade_id = len(self.fills) + 1
                fee = size * Fraction(self.execution.fee_per_unit)
                own = MakerFill(
                    trade_id,
                    bar.time_us,
                    self.index,
                    side,
                    size,
                    price,
                    fee / d.tick,
                    a.reference,
                    None,
                )
                other = MakerFill(
                    trade_id,
                    bar.time_us,
                    self.index,
                    side.opposite,
                    size,
                    price,
                    Fraction(0),
                    b.reference,
                    None,
                )
                a.apply(own)
                b.apply(other)
                fill = dict(
                    trade_id=trade_id,
                    order_id=order["order_id"],
                    instrument=key,
                    side=side.value,
                    quantity=size,
                    price=float(price * d.tick),
                    exact_price=str(PriceGrid(Decimal(d.meta["tick_size"])).to_price(price)),
                    fee=float(fee),
                    reference=float(bar.close * d.tick),
                    timestamp=bar.timestamp,
                    time_us=bar.time_us,
                    index=self.index,
                    execution_model=EXECUTION_VERSION,
                    evidence="SIMULATED HISTORICAL EXECUTION",
                )
                self.fills.append(fill)
                order["fills"].append(dict(fill))
                order["filled"] += size
                order["remaining"] -= size
                budgets[key] -= size
                order["vwap"] = float(
                    vwap((f["exact_price"], f["quantity"]) for f in order["fills"])
                )
                self._point()
            if order["type"] == "market":
                order["cancelled"] += order["remaining"]
                order["remaining"] = 0
            order["status"] = (
                "resting paper instruction"
                if order["remaining"]
                else "filled"
                if not order["cancelled"]
                else "remainder cancelled"
            )
        self.timeline.append(
            {
                "index": self.index,
                "message": (
                    "Next bar revealed; eligible paper instructions evaluated at its close."
                ),
            }
        )
        self._point()
        if self.index == len(self._datasets[0].bars) - 1:
            self._end()

    def _end(self):
        for order in self.orders:
            if order["remaining"]:
                self._cancel(order["order_id"])
        self.status = "ended"

    def command(self, kind, **payload):
        try:
            return self._command(kind, **payload)
        except AccountingError:
            self.status = "failed"
            raise

    def _command(self, kind, **payload):
        if self.status in ("ended", "failed"):
            raise ValueError(
                "Session ended. Replay is read-only; restart creates a fresh account."
            )
        if len(self.actions) >= 1000 and kind != "end":
            raise ValueError("Session action budget reached; end and export")
        allowed = {
            "order": {"instrument", "side", "quantity", "order_type", "price"},
            "cancel": {"order_id"},
            "step": {"count"},
            "step_time": {"seconds"},
            "end": set(),
        }
        if kind not in allowed or set(payload) - allowed[kind]:
            raise ValueError("Unknown historical command or fields")
        if kind == "order":
            result = self._order(**payload)
        elif kind == "cancel":
            result = self._cancel(**payload)
        elif kind == "end":
            self._end()
            result = {
                "ok": True,
                "message": "Session ended; open holdings remain marked, not liquidated.",
            }
        else:
            if kind == "step":
                count = integer(payload.get("count", 1), "Step observations", 1, 200)
            else:
                seconds = integer(payload.get("seconds", 60), "Step seconds", 1, 86400)
                target = self._datasets[0].bars[self.index].time_us + seconds * 1_000_000
                count = 0
                for bar in self._datasets[0].bars[self.index + 1 :]:
                    if bar.time_us > target or count >= 200:
                        break
                    count += 1
            for _ in range(count):
                if self.status == "ended":
                    break
                self._advance()
            result = {
                "ok": True,
                "message": f"Revealed through observation {self.index}; "
                "no future bars are displayed.",
            }
        self.revision += 1
        self.last_result = result
        self.check()
        self.actions.append(
            {
                "kind": kind,
                "payload": copy.deepcopy(payload),
                "state_digest": digest(self.public()),
            }
        )
        return result

    def signal(self):
        if len(self._datasets) != 2:
            return {
                "available": False,
                "reason": "Import two compatible series for a causal pair signal",
            }
        try:
            s = self.model.at(self._prefix(), self.index)
            action, reason = decision(
                Rules(), s, held=False, age=0, pnl=0, gross=0, imbalance=0
            )
            return s | {
                "action": action,
                "decision_reason": reason,
                "label": "Past-only fit; flat-position signal qualification, not an order",
            }
        except ValueError as exc:
            return {"available": False, "reason": str(exc)}

    def risk(self):
        if self.index < 2:
            return {
                "available": False,
                "var": None,
                "es": None,
                "reason": "Need at least two revealed returns",
                "label": "LIVE REPLAY RISK ESTIMATE",
            }
        prices = np.asarray(self._prefix()[-251:])
        returns = prices[1:] / prices[:-1] - 1
        losses, _ = revalue_returns(
            self.portfolio(), self.instruments, returns, days=1, cash_rate=0
        )
        return empirical_risk(losses) | {
            "available": True,
            "label": "LIVE REPLAY RISK ESTIMATE",
            "horizon": "one observed interval, not one calendar day",
            "observed_through": self.index,
            "lookback_returns": len(returns),
            "assumption": (
                "Reapply past revealed close returns to current stock holdings; "
                "fees, future returns and options excluded."
            ),
        }

    def public(self):
        ended = self.status == "ended"
        provenance = [d.provenance(self.index, ended=ended) for d in self._datasets]
        fixture = self._datasets[0].meta["data_kind"] == "artificial_fixture"
        return {
            "schema": SCHEMA,
            "engine": self.engine,
            "status": self.status,
            "revision": self.revision,
            "index": self.index,
            "timestamp": self._datasets[0].bars[self.index].timestamp,
            "environment": {
                "type": "HISTORICAL",
                "id": "historical-session",
                "hidden": False,
                "badge": "HISTORICAL REPLAY · ARTIFICIAL TEST FIXTURE"
                if fixture
                else "HISTORICAL REPLAY",
                "data_kind": "artificial_fixture" if fixture else "recorded",
                "hidden_model_state": False,
                "counterparty_simulation": False,
                "future_stored": True,
                "execution_model": EXECUTION_VERSION,
                "truth": "Artificial historical-style test bars, not real market history."
                if fixture
                else (
                    "Imported recorded market observations. QuantLab does not know "
                    "why the real market moved."
                ),
            },
            "instruments": list(self.instruments),
            "provenance": provenance,
            "observations": {
                d.meta["instrument"]: list(d.prefix(self.index))[-300:] for d in self._datasets
            },
            "chart_note": (
                "Last 300 revealed bars only; axes use this public prefix. No "
                "observed order book is available."
            ),
            "account": self.portfolio().public(),
            "orders": [
                {k: copy.deepcopy(v) for k, v in o.items() if k != "limit_ticks"}
                for o in self.orders
            ],
            "fills": copy.deepcopy(self.fills[-300:]),
            "risk": self.risk(),
            "signal": self.signal(),
            "path": copy.deepcopy(self.path[-300:]),
            "timeline": copy.deepcopy(self.timeline[-12:]),
            "execution": asdict(self.execution),
            "last_result": copy.deepcopy(self.last_result),
            "capabilities": {
                "orders": True,
                "limits": True,
                "cancel": True,
                "options": False,
                "pair_signals": len(self._datasets) == 2,
                "observer": False,
                "quotes": False,
                "risk": True,
            },
            "options_note": (
                "Options unavailable: the imported data contains no observed option chain."
            ),
            "summary": copy.deepcopy(self.summary()) if ended else None,
        }

    def summary(self):
        return {
            "largest_position": max(
                (max((abs(q) for q in p["position"].values()), default=0) for p in self.path),
                default=0,
            ),
            "maximum_drawdown": float(self.max_drawdown),
            "largest_trade": max((f["quantity"] for f in self.fills), default=0),
            "execution_count": len(self.fills),
            "worst_execution": max(
                self.fills,
                key=lambda f: abs(f["price"] - f["reference"]) * f["quantity"] + f["fee"],
                default=None,
            ),
            "execution_ranking": (
                "Cost against the same revealed close plus fees; no unavailable "
                "historical bid/ask benchmark."
            ),
            "major_moves": sorted(
                [
                    {
                        "instrument": d.meta["instrument"],
                        "timestamp": d.bars[i].timestamp,
                        "price_change": float((d.bars[i].close - d.bars[i - 1].close) * d.tick),
                    }
                    for d in self._datasets
                    for i in range(1, self.index + 1)
                ],
                key=lambda r: abs(r["price_change"]),
                reverse=True,
            )[:5],
            "user_decisions": [copy.deepcopy(o) for o in self.orders[-20:]],
            "pnl": self.portfolio().public()["pnl"],
            "note": (
                "Post-session public review; results reflect the paper execution "
                "rule, not actual historical fills."
            ),
        }

    def journal(self):
        if self.status != "ended":
            raise ValueError("End the session before exporting its private replay journal")
        return {
            "schema": SCHEMA,
            "environment": "HISTORICAL",
            "quantlab_version": __version__,
            "execution_version": EXECUTION_VERSION,
            "datasets": [
                {
                    "instrument": d.meta["instrument"],
                    "fingerprint": d.fingerprint,
                    "metadata": d.meta,
                    "timestamp_range": [d.bars[0].timestamp, d.bars[-1].timestamp],
                }
                for d in self._datasets
            ],
            "execution": asdict(self.execution),
            "model": self.model_config,
            "actions": copy.deepcopy(self.actions),
            "final_digest": digest(self.public()),
        }


def replay_historical(raw, datasets):
    if (
        raw.get("schema") != SCHEMA
        or raw.get("environment") != "HISTORICAL"
        or raw.get("quantlab_version") != __version__
        or raw.get("execution_version") != EXECUTION_VERSION
    ):
        raise ValueError("Unsupported historical journal or engine/execution version")
    if [d.fingerprint for d in datasets] != [d["fingerprint"] for d in raw["datasets"]]:
        raise ValueError(
            "Dataset fingerprint mismatch: import the exact original source files and metadata"
        )
    for d, recorded in zip(datasets, raw["datasets"], strict=True):
        if recorded != {
            "instrument": d.meta["instrument"],
            "fingerprint": d.fingerprint,
            "metadata": d.meta,
            "timestamp_range": [d.bars[0].timestamp, d.bars[-1].timestamp],
        }:
            raise ValueError("Dataset provenance mismatch")
    if not isinstance(raw.get("actions"), list) or len(raw["actions"]) > 1001:
        raise ValueError("Replay action budget exceeded")
    s = HistoricalSession(datasets, raw["execution"], model=raw["model"])
    frames = [s.public()]
    for action in raw["actions"]:
        s.command(action["kind"], **action["payload"])
        if digest(s.public()) != action["state_digest"]:
            raise ValueError(
                "Historical replay mismatch in execution, account or public evidence"
            )
        frames.append(s.public())
    if s.status != "ended" or digest(s.public()) != raw["final_digest"]:
        raise ValueError("Historical replay final fingerprint mismatch")
    return s, frames
