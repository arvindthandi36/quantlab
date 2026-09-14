"""One deterministic manual session, sharing the existing exchange and accounting."""

from dataclasses import dataclass, field
from decimal import Decimal
from fractions import Fraction

from quantlab import LimitOrder, MarketOrder, OrderBook, PriceGrid, Side
from quantlab.domain import positive_integer
from quantlab.execution import vwap
from quantlab.market.simulation import MarketEnvironment
from quantlab.market_making.config import MakerConfig
from quantlab.market_making.quotes import MakerObservation, QuoteRequest, plan_quotes
from quantlab.market_making.records import public_reference
from quantlab.portfolio.accounting import AccountingError, MakerAccount, MakerFill
from quantlab.replay_support import ReplayFrames
from quantlab.research.codec import plain
from quantlab.trading.analytics import GLOSSARY, money, quant_metrics
from quantlab.trading.scenarios import Scenario


class CommandError(ValueError):
    """An expected, nonmutating user-command rejection."""


@dataclass
class TrackedOrder:
    order: LimitOrder | MarketOrder
    time_us: int
    filled: int = 0
    cancelled: int = 0
    fills: list = field(default_factory=list)
    ever_partial: bool = False

    @property
    def remaining(self):
        return self.order.quantity - self.filled - self.cancelled

    @property
    def vwap(self):
        return vwap((f["price_ticks"], f["quantity"]) for f in self.fills)

    @property
    def status(self):
        if self.remaining:
            return "partial · resting" if self.filled else "resting"
        if self.cancelled:
            return "partial · remainder cancelled" if self.filled else "cancelled"
        return "filled"


class TradingSession:
    MODES = ("free", "manual_maker", "challenge")
    MAX_ACTIONS = 5_000

    def __init__(
        self, scenario: Scenario, mode="free", *, environment_factory=None, capture_frames=False
    ):
        if mode not in self.MODES:
            raise ValueError("unknown trading mode")
        self.scenario, self.mode = scenario, mode
        self.book = OrderBook()
        self.grid = PriceGrid(Decimal(scenario.market.tick_size))
        self.now_us = self.public_number = self.revision = 0
        self.status = "paused"
        self.started = False
        self.failure = None
        self.orders: dict[str, TrackedOrder] = {}
        self.owners: dict[str, str] = {}
        self.accounts = {
            "user": MakerAccount(
                scenario.cash_ticks,
                scenario.market.opening_reference_ticks,
                hard_limit=scenario.position_limit,
                initial_position=scenario.initial_position,
            ),
            "auto": MakerAccount(
                Fraction(1_000_000), scenario.market.opening_reference_ticks, hard_limit=20
            ),
        }
        self._ids = {"user": 0, "auto": 0}
        self._next_quote_us = 1_000_000
        self._submitted = self._cancelled = 0
        self.tape, self.own_trades, self.markouts = [], [], []
        self.actions, self.evidence, self.timeline, self.history = [], [], [], []
        self.frames = ReplayFrames() if capture_frames else None
        self.last_trade = None
        self.peak_pnl = self.max_drawdown = Fraction(0)
        self.max_long = max(0, scenario.initial_position)
        self.max_short = min(0, scenario.initial_position)
        self.exposure_unit_us = self.exposure_tick_us = Fraction(0)
        self.tutor = {"stage": "idle"}
        for i, (side, price, qty) in enumerate(scenario.initial_book):
            report = self.book.submit(LimitOrder(f"opening-{i}", Side(side), qty, price))
            if report.executed_quantity:
                raise AccountingError("opening book crossed")
            self._submitted += qty
        factory = environment_factory or (lambda c, b: MarketEnvironment(c, b))
        self.environment = factory(scenario.market, self.book)
        self._sample()
        self._checkpoint("opening")

    @property
    def account(self):
        return self.accounts["user"]

    def _owned(self, owner):
        return {oid for oid, who in self.owners.items() if who == owner}

    def _live(self, owner):
        ids = self._owned(owner)
        snap = self.book.snapshot()
        return tuple(
            o for level in snap.bids + snap.asks for o in level.orders if o.order_id in ids
        )

    def _reference(self, owner="user"):
        return public_reference(
            self.book.snapshot(),
            self._owned(owner),
            self.last_trade,
            self.scenario.market.opening_reference_ticks,
        )

    def _mark(self):
        for owner, account in self.accounts.items():
            account.mark(self._reference(owner)[0])

    def _time(self, target):
        elapsed = target - self.now_us
        if elapsed < 0:
            raise AccountingError("session clock moved backwards")
        self.exposure_unit_us += abs(self.account.inventory) * elapsed
        self.exposure_tick_us += abs(self.account.inventory) * self.account.reference * elapsed
        self.now_us = target

    def _sample(self):
        self._mark()
        snapshot = self.account.snapshot()
        self.peak_pnl = max(self.peak_pnl, snapshot.total_pnl_ticks)
        self.max_drawdown = max(self.max_drawdown, self.peak_pnl - snapshot.total_pnl_ticks)
        point = {
            "time_us": self.now_us,
            "position": snapshot.inventory,
            "pnl": self._money(snapshot.total_pnl_ticks),
            "reference": self._money(snapshot.reference_ticks),
        }
        if not self.history or self.history[-1] != point:
            self.history.append(point)
        self.check_invariants()

    def _money(self, ticks):
        return money(ticks, self.scenario.market.tick_size)

    def _checkpoint(self, kind, **detail):
        self.evidence.append(
            plain(
                {
                    "time_us": self.now_us,
                    "kind": kind,
                    "public_number": self.public_number,
                    **detail,
                    "book": self.book.snapshot(),
                    "accounts": {k: a.snapshot() for k, a in self.accounts.items()},
                    "submitted": self._submitted,
                    "cancelled": self._cancelled,
                }
            )
        )

    def _public_event(self, message, observed=None):
        self._sample()
        midpoint = self.book.snapshot().mid_price_ticks
        for mark in self.markouts:
            if mark["status"] == "pending" and mark["due_event"] == self.public_number:
                mark["status"] = "matured" if midpoint is not None else "missing midpoint"
                mark["observed_time_us"] = self.now_us
                mark["value_ticks"] = (
                    mark["sign"] * (midpoint - mark["price_ticks"])
                    if midpoint is not None
                    else None
                )
        self.timeline.append(
            {
                "time_us": self.now_us,
                "event": self.public_number,
                "message": message,
                "reference": self._money(self.account.reference),
                "position": self.account.inventory,
            }
        )
        if observed is not None:
            self.timeline[-1]["observed_before"] = {
                "best_bid": self._money(observed["best_bid"]),
                "best_ask": self._money(observed["best_ask"]),
                "reference": self._money(observed["reference"]),
                "position": observed["position"],
            }
        if self.frames is not None:
            self.frames.append(self.public_snapshot())

    def _fills(self, report, midpoint):
        self._submitted += report.requested_quantity
        self._cancelled += report.cancelled_quantity
        if report.order_id in self.orders:
            self.orders[report.order_id].cancelled += report.cancelled_quantity
        for trade in report.trades:
            self.last_trade = trade.price_ticks
            self.tape.append(
                {
                    "trade_id": trade.trade_id,
                    "time_us": self.now_us,
                    "price_ticks": trade.price_ticks,
                    "quantity": trade.quantity,
                    "aggressor_side": trade.aggressor_side.value,
                }
            )
            for oid, side in ((trade.buy_order_id, Side.BUY), (trade.sell_order_id, Side.SELL)):
                owner = self.owners.get(oid)
                if owner is None:
                    continue
                account = self.accounts[owner]
                fee = self.scenario.fee_ticks * trade.quantity
                fill = MakerFill(
                    trade.trade_id,
                    self.now_us,
                    self.public_number,
                    side,
                    trade.quantity,
                    trade.price_ticks,
                    fee,
                    account.reference,
                    midpoint,
                )
                account.apply(fill)
                if owner != "user":
                    continue
                details = {
                    "order_id": oid,
                    "trade_id": trade.trade_id,
                    "time_us": self.now_us,
                    "side": side.value,
                    "quantity": trade.quantity,
                    "price_ticks": trade.price_ticks,
                    "fee_ticks": fee,
                    "role": "provider" if trade.maker_order_id == oid else "aggressor",
                }
                tracked = self.orders[oid]
                tracked.filled += trade.quantity
                tracked.fills.append(details)
                # Catch transient partial fills, even if a later match completes the order.
                tracked.ever_partial |= 0 < tracked.filled < tracked.order.quantity
                self.own_trades.append(details)
                self.max_long = max(self.max_long, account.inventory)
                self.max_short = min(self.max_short, account.inventory)
                for horizon in self.scenario.market.markout_horizons_events:
                    self.markouts.append(
                        {
                            "trade_id": trade.trade_id,
                            "role": details["role"],
                            "horizon": horizon,
                            "due_event": self.public_number + horizon,
                            "sign": 1 if side is Side.BUY else -1,
                            "price_ticks": trade.price_ticks,
                            "status": "pending",
                            "value_ticks": None,
                            "observed_time_us": None,
                        }
                    )
        self.environment.record_external_execution(report)

    def _validate_risk(self, owner, side, quantity, price):
        account = self.accounts[owner]
        live = self._live(owner)
        reserved = sum(o.remaining_quantity for o in live if o.side is side)
        capacity = (
            account.hard_limit - account.inventory
            if side is Side.BUY
            else account.hard_limit + account.inventory
        )
        if quantity + reserved > capacity:
            raise CommandError(
                f"Position limit: {capacity - reserved} {side.value} units available "
                "after reserving your open orders."
            )
        for order in live:
            crosses = price is None or (
                price >= order.price_ticks if side is Side.BUY else price <= order.price_ticks
            )
            if order.side is side.opposite and crosses:
                raise CommandError("This could trade against your own order. Cancel it first.")

    def _submit(self, owner, side, quantity, price=None):
        self._validate_risk(owner, side, quantity, price)
        guard = getattr(self, "portfolio_risk_guard", None)
        if owner == "user" and guard is not None:
            message = guard(side, quantity, price)
            if message:
                raise CommandError(message)
        self._ids[owner] += 1
        oid = f"{owner}-{self._ids[owner]}"
        order = (
            MarketOrder(oid, side, quantity)
            if price is None
            else LimitOrder(oid, side, quantity, price)
        )
        self.owners[oid] = owner
        if owner == "user":
            self.orders[oid] = TrackedOrder(order, self.now_us)
        self._mark()
        midpoint = self.book.snapshot().mid_price_ticks
        report = self.book.submit(order)
        self._fills(report, midpoint)
        return order, report

    def _cancel(self, oid):
        removed = self.book.cancel(oid)
        if removed is not None:
            self._cancelled += removed.remaining_quantity
            if oid in self.orders:
                self.orders[oid].cancelled += removed.remaining_quantity
        return removed

    def _quote(self, owner, request):
        self._mark()
        reference, source, bid, ask = self._reference(owner)
        account = self.accounts[owner]
        config = MakerConfig(
            hard_limit=account.hard_limit, soft_limit=max(1, account.hard_limit // 2)
        )
        observation = MakerObservation(
            self.now_us,
            self.book.best_bid,
            self.book.best_ask,
            bid,
            ask,
            reference,
            source,
            account.snapshot(),
            self._live(owner),
            account.fills[-10:],
        )
        plan = plan_quotes(observation, request, config)
        cancelled = [self._cancel(o.order_id) for o in self._live(owner)]
        self.public_number += 1
        placed = []
        for side, price, quantity in (
            (Side.BUY, plan.bid_ticks, plan.bid_size),
            (Side.SELL, plan.ask_ticks, plan.ask_size),
        ):
            if quantity:
                order, report = self._submit(owner, side, quantity, price)
                if report.executed_quantity:
                    raise AccountingError("passive quote planner crossed the book")
                placed.append((order, report))
        label = (
            "Your two-sided quotes refreshed" if owner == "user" else "Public quotes refreshed"
        )
        self._public_event(label)
        self._checkpoint(
            "quote",
            owner=owner,
            request=request,
            plan=plan,
            cancelled_orders=cancelled,
            placed=placed,
        )
        return {"ok": True, "message": label, "adjustments": list(plan.adjustments)}

    def _next_time(self):
        times = [
            t
            for t in (
                self.environment.next_event_time_us,
                self._next_quote_us if self.scenario.automated_maker else None,
            )
            if t is not None and t <= self.scenario.market.duration_us
        ]
        return min(times) if times else None

    def _next(self):
        next_time = self._next_time()
        if next_time is None:
            return False
        self._time(next_time)
        if self.environment.next_event_time_us == next_time:
            self._mark()
            midpoint = self.book.snapshot().mid_price_ticks
            record = self.environment.step()
            if record.report is not None:
                self.public_number += 1
                self._fills(record.report, midpoint)
                side, qty = record.order.side.value, record.order.quantity
                kind = "limit" if isinstance(record.order, LimitOrder) else "market"
                self._public_event(
                    f"Participant submits {side} {qty} {kind}; "
                    f"{record.report.executed_quantity} units execute"
                )
            self._checkpoint("market", market=record)
            return record.report is not None
        self._quote("auto", QuoteRequest())
        self._next_quote_us += 1_000_000
        return True

    def _advance(self, target, one_event=False):
        target = min(target, self.scenario.market.duration_us)
        while (upcoming := self._next_time()) is not None and upcoming <= target:
            if self._next() and one_event:
                self._sample()
                if (
                    self.now_us == self.scenario.market.duration_us
                    and self._next_time() is None
                ):
                    self._end()
                return
        self._time(target)
        self._sample()
        if self.now_us == self.scenario.market.duration_us:
            self._end()

    def _end(self):
        # Complete ties at the current clock before closing the exchange session.
        # This includes private events but never moves into a future timestamp.
        while self._next_time() == self.now_us:
            self._next()
        removed = [self._cancel(o.order_id) for who in self.accounts for o in self._live(who)]
        if removed:
            self.public_number += 1
        self.status = "ended"
        self._public_event("Session ended; open orders cancelled, remaining position marked")
        self._checkpoint("end", cancelled_orders=removed)

    def command(self, kind, **payload):
        """Apply and record one command. Unexpected failures poison the session."""
        if self.failure:
            raise RuntimeError("session failed; create a fresh session")
        if self.status == "ended":
            return {"ok": False, "message": "Session has ended. Open a new session to trade."}
        before = self.now_us
        try:
            if len(self.actions) >= self.MAX_ACTIONS - 1 and kind != "end":
                self._end()
                result = {
                    "ok": False,
                    "message": "Session action budget reached; session ended "
                    "and pending orders cancelled. The requested action was not applied.",
                }
            else:
                guard = getattr(self, "portfolio_command_guard", None)
                if kind == "quotes" and guard is not None:
                    message = guard(kind, payload)
                    if message:
                        raise CommandError(message)
                result = self._dispatch(kind, payload)
        except CommandError as exc:
            result = {"ok": False, "message": str(exc)}
        except Exception as exc:
            self.failure = type(exc).__name__
            self.status = "failed"
            raise
        self.revision += 1
        self.actions.append(
            plain({"at_us": before, "kind": kind, "payload": payload, "result": result})
        )
        self._checkpoint("command", command=kind, result=result)
        if self.frames is not None:
            self.frames.append(self.public_snapshot())
        return result

    def _dispatch(self, kind, payload):
        if not isinstance(kind, str):
            raise CommandError("Command kind must be text")
        if self.status == "ended":
            raise CommandError("Session has ended. Open a new session to trade.")
        expected = {
            "order": {"side", "quantity", "order_type", "price"},
            "cancel": {"order_id"},
            "cancel_all": set(),
            "start": set(),
            "resume": set(),
            "pause": set(),
            "end": set(),
            "step_event": set(),
            "step_interval": {"delta_us"},
            "advance": {"delta_us"},
            "quotes": {"bid_distance", "ask_distance", "bid_size", "ask_size", "shift"},
            "learn": set(),
            "predict": {"answer"},
        }
        if kind not in expected or not set(payload) <= expected[kind]:
            raise CommandError("Unknown command or fields")
        if kind in ("start", "resume", "pause"):
            self.status = "paused" if kind == "pause" else "running"
            self.started |= kind != "pause"
        elif kind in ("step_event", "step_interval", "advance"):
            if kind == "advance" and self.status != "running":
                return {"ok": True, "message": "Paused; no time advanced"}
            if kind != "advance" and self.status != "paused":
                raise CommandError("Pause before stepping.")
            delta = payload.get("delta_us", 1_000_000)
            if type(delta) is not int or not 1 <= delta <= 5_000_000:
                raise CommandError("Step interval must be 1–5,000,000 integer microseconds")
            target = (
                self.scenario.market.duration_us
                if kind == "step_event"
                else self.now_us + delta
            )
            self._advance(target, kind == "step_event")
        elif kind == "end":
            self._end()
        elif kind == "order":
            try:
                side = Side(payload["side"])
                quantity = payload["quantity"]
                positive_integer(quantity, "quantity")
                order_type = payload["order_type"]
                if order_type not in ("market", "limit"):
                    raise ValueError("order type must be market or limit")
                price = self.grid.to_ticks(payload["price"]) if order_type == "limit" else None
            except (ValueError, TypeError, KeyError) as exc:
                raise CommandError(str(exc)) from exc
            self._validate_risk("user", side, quantity, price)
            observed = self._decision_state()
            self.public_number += 1
            order, report = self._submit("user", side, quantity, price)
            text = (
                f"You {side.value} {quantity} {order_type}: {report.executed_quantity} filled, "
                f"{report.resting_quantity} resting, {report.cancelled_quantity} cancelled"
            )
            if report.vwap_ticks is not None:
                text += f"; VWAP £{self._money(report.vwap_ticks)}"
            if self.tutor.get("stage") == "trade":
                self.tutor.update(
                    stage="explain",
                    result=text,
                    explanation="Fills use opposite-side resting prices, best first and FIFO. "
                    "Your limit bounds the price; it does not guarantee a fill. "
                    "Future gains or losses do not tell us whether your reasoning was sound.",
                )
            self._public_event(text, observed)
            self._checkpoint("order", observed=observed, order=order, report=report)
            return {"ok": True, "message": text, "order_id": order.order_id}
        elif kind in ("cancel", "cancel_all"):
            if kind == "cancel" and not isinstance(payload.get("order_id"), str):
                raise CommandError("Choose an order ID to cancel")
            ids = (
                [payload.get("order_id")]
                if kind == "cancel"
                else [o.order_id for o in self._live("user")]
            )
            if any(oid not in self.orders for oid in ids):
                raise CommandError("That is not one of your orders")
            removed = [o for oid in ids if (o := self._cancel(oid)) is not None]
            if removed:
                self.public_number += 1
                self._public_event(f"You cancel {len(removed)} open order(s)")
            self._checkpoint("cancel", cancelled_orders=removed)
            return {
                "ok": bool(removed),
                "message": f"Cancelled {len(removed)} live order(s)",
                "cancelled": [o.order_id for o in removed],
            }
        elif kind == "quotes":
            if self.mode != "manual_maker":
                raise CommandError("Select Manual market making to refresh two-sided quotes")
            try:
                request = QuoteRequest(
                    payload["bid_distance"],
                    payload["ask_distance"],
                    payload["bid_size"],
                    payload["ask_size"],
                    payload.get("shift", "0"),
                )
            except (ValueError, TypeError, KeyError, ZeroDivisionError) as exc:
                raise CommandError(str(exc)) from exc
            if max(request.bid_size, request.ask_size) > 1000:
                raise CommandError("Quote sizes must be at most 1000")
            return self._quote("user", request)
        elif kind == "learn":
            ask = self.book.best_ask
            if ask is None or ask <= 1:
                raise CommandError("Wait for an ask before this exercise")
            self.tutor = {
                "stage": "predict",
                "ask": self._money(ask),
                "limit": self._money(ask - 1),
                "attempts": 0,
                "question": f"Observe best ask £{self._money(ask)}. Would a buy limit at "
                f"£{self._money(ask - 1)} execute immediately in this book?",
            }
        elif kind == "predict":
            if self.tutor.get("stage") != "predict":
                raise CommandError("Start a checkpoint first")
            if payload.get("answer") not in ("yes", "no"):
                raise CommandError("Choose yes or no")
            if payload["answer"] == "no" or self.tutor["attempts"] >= 1:
                self.tutor.update(
                    stage="trade",
                    instruction="Now submit an order of your choice. "
                    "A buy below the best ask waits in this book. The live book may change.",
                )
            else:
                self.tutor.update(
                    attempts=1,
                    hint="Compare your maximum price with the cheapest seller. Try again.",
                )
        self._sample()
        return {"ok": True, "message": kind.replace("_", " ")}

    def _decision_state(self):
        snapshot = self.book.snapshot()
        return {
            "best_bid": snapshot.best_bid,
            "best_ask": snapshot.best_ask,
            "reference": self.account.reference,
            "position": self.account.inventory,
        }

    def check_invariants(self):
        self.book.check_invariants()
        snap = self.book.snapshot()
        resting = sum(level.quantity for level in snap.bids + snap.asks)
        if self._submitted != 2 * self.book.traded_volume + resting + self._cancelled:
            raise AccountingError("whole-session quantity conservation failed")
        if sum(t["quantity"] for t in self.tape) != self.book.traded_volume:
            raise AccountingError("transaction tape does not reconcile with the exchange")
        live = {o.order_id: o for level in snap.bids + snap.asks for o in level.orders}
        for oid, order in self.orders.items():
            if (
                order.filled != sum(t["quantity"] for t in order.fills)
                or order.remaining != (live[oid].remaining_quantity if oid in live else 0)
                or min(order.filled, order.cancelled, order.remaining) < 0
            ):
                raise AccountingError("manual order accounting does not reconcile")
        for owner, account in self.accounts.items():
            account.check_invariants()
            for side in Side:
                quantity = sum(
                    o.remaining_quantity for o in self._live(owner) if o.side is side
                )
                worst = account.inventory + (quantity if side is Side.BUY else -quantity)
                if abs(worst) > account.hard_limit:
                    raise AccountingError(
                        "outstanding orders breach reserved position capacity"
                    )
        if len(self.own_trades) != len(self.account.fills):
            raise AccountingError("manual execution ledger disagrees with account")
        actual = [
            (f.trade_id, f.side.value, f.quantity, f.price_ticks, f.fee_ticks)
            for f in self.account.fills
        ]
        displayed = [
            (f["trade_id"], f["side"], f["quantity"], f["price_ticks"], f["fee_ticks"])
            for f in self.own_trades
        ]
        if actual != displayed:
            raise AccountingError("displayed executions disagree with the account fills")

    def _public_order(self, tracked):
        order = tracked.order
        return {
            "order_id": order.order_id,
            "time_us": tracked.time_us,
            "side": order.side.value,
            "type": "limit" if isinstance(order, LimitOrder) else "market",
            "price": self._money(getattr(order, "price_ticks", None)),
            "original": order.quantity,
            "filled": tracked.filled,
            "remaining": tracked.remaining,
            "cancelled": tracked.cancelled,
            "status": tracked.status,
            "vwap": self._money(tracked.vwap),
            "vwap_exact_ticks": str(tracked.vwap) if tracked.vwap is not None else None,
            "fills": [self._public_fill(f) for f in tracked.fills],
        }

    def _public_fill(self, fill):
        return {
            k: fill[k] for k in ("order_id", "trade_id", "time_us", "side", "quantity", "role")
        } | {"price": self._money(fill["price_ticks"]), "fee": self._money(fill["fee_ticks"])}

    def report(self):
        account = self.account.snapshot()
        volume = sum(f.quantity for f in self.account.fills)
        turnover = sum(f.quantity * f.price_ticks for f in self.account.fills)
        limits = [o for o in self.orders.values() if isinstance(o.order, LimitOrder)]
        requested = sum(o.order.quantity for o in limits)
        target = self.scenario.target_position
        challenge = None
        if self.mode == "challenge":
            challenge = {
                "completed_duration": self.now_us >= self.scenario.market.duration_us,
                "target_position": target,
                "target_met": account.inventory == target if target is not None else None,
                "drawdown_within_budget": self.max_drawdown
                <= self.scenario.drawdown_budget_ticks,
                "budget": self._money(self.scenario.drawdown_budget_ticks),
            }
        return {
            "final_pnl": self._money(account.total_pnl_ticks),
            "realised_pnl": self._money(account.realised_pnl_ticks),
            "unrealised_pnl": self._money(account.unrealised_pnl_ticks),
            "maximum_drawdown": self._money(self.max_drawdown),
            "turnover": self._money(turnover),
            "trade_count": len(self.account.fills),
            "filled_units": volume,
            "pooled_execution_vwap": self._money(
                vwap((f.price_ticks, f.quantity) for f in self.account.fills)
            ),
            "buy_vwap": self._side_vwap(Side.BUY),
            "sell_vwap": self._side_vwap(Side.SELL),
            "fees": self._money(account.fees_ticks),
            "limit_fill_rate": sum(o.filled for o in limits) / requested if requested else None,
            "cancelled_orders": sum(o.cancelled > 0 for o in self.orders.values()),
            "orders_ever_partially_filled": sum(o.ever_partial for o in self.orders.values()),
            "max_long_units": self.max_long,
            "max_short_units": self.max_short,
            "average_absolute_position": float(self.exposure_unit_us / self.now_us)
            if self.now_us
            else None,
            "average_absolute_notional": self._money(self.exposure_tick_us / self.now_us)
            if self.now_us
            else None,
            "challenge": challenge,
            "markouts": self._public_marks(),
            "decisions": list(self.timeline),
            "valuation_note": "Remaining inventory is marked, not liquidated. "
            "Markouts are diagnostics, never additional P&L. Outcomes do not grade reasoning.",
        }

    def _side_vwap(self, side):
        fills = [f for f in self.account.fills if f.side is side]
        return self._money(vwap((f.price_ticks, f.quantity) for f in fills))

    def _public_marks(self):
        return [
            {
                "trade_id": m["trade_id"],
                "role": m["role"],
                "horizon": m["horizon"],
                "status": m["status"],
                "observed_time_us": m["observed_time_us"],
                "value": self._money(m["value_ticks"]),
            }
            for m in self.markouts
        ]

    def public_snapshot(self):
        """Explicit public allowlist. Never serialize self, environment or evidence here."""
        snapshot = self.book.snapshot()

        def levels(side):
            return [
                {
                    "price": self._money(level.price_ticks),
                    "quantity": level.quantity,
                    "order_count": level.order_count,
                    "own_quantity": sum(
                        o.remaining_quantity
                        for o in level.orders
                        if self.owners.get(o.order_id) == "user"
                    ),
                    "queue": [
                        {
                            "id": o.order_id
                            if self.owners.get(o.order_id) == "user"
                            else f"order-{o.arrival_sequence}",
                            "quantity": o.remaining_quantity,
                            "yours": self.owners.get(o.order_id) == "user",
                        }
                        for o in level.orders
                    ],
                }
                for level in side
            ]

        account = self.account.snapshot()
        lots = self.account.lots
        entry = None
        if account.inventory:
            entry = Fraction(
                sum(abs(lot.signed_quantity) * lot.entry_price_ticks for lot in lots),
                abs(account.inventory),
            )
        return {
            "revision": self.revision,
            "status": self.status,
            "failure": self.failure,
            "time_us": self.now_us,
            "duration_us": self.scenario.market.duration_us,
            "public_event": self.public_number,
            "mode": self.mode,
            "scenario": self.scenario.title,
            "objective": self.scenario.objective,
            "best_bid": self._money(snapshot.best_bid),
            "best_ask": self._money(snapshot.best_ask),
            "spread": self._money(snapshot.spread_ticks),
            "mid": self._money(snapshot.mid_price_ticks),
            "reference": self._money(account.reference_ticks),
            "reference_source": self._reference()[1],
            "last_price": self._money(self.last_trade),
            "bids": levels(snapshot.bids),
            "asks": levels(snapshot.asks),
            "account": {
                "cash": self._money(account.cash_ticks),
                "position": account.inventory,
                "average_entry": self._money(entry),
                "realised": self._money(account.realised_pnl_ticks),
                "unrealised": self._money(account.unrealised_pnl_ticks),
                "total_pnl": self._money(account.total_pnl_ticks),
                "fees": self._money(account.fees_ticks),
                "exposure": self._money(account.inventory * account.reference_ticks),
                "position_limit": self.scenario.position_limit,
                "drawdown": self._money(self.peak_pnl - account.total_pnl_ticks),
                "max_drawdown": self._money(self.max_drawdown),
                "buy_capacity": self.scenario.position_limit
                - account.inventory
                - sum(o.remaining_quantity for o in self._live("user") if o.side is Side.BUY),
                "sell_capacity": self.scenario.position_limit
                + account.inventory
                - sum(o.remaining_quantity for o in self._live("user") if o.side is Side.SELL),
            },
            "orders": [self._public_order(o) for o in self.orders.values()],
            "trades": [self._public_fill(f) for f in self.own_trades],
            "tape": [
                {
                    "time_us": t["time_us"],
                    "price": self._money(t["price_ticks"]),
                    "quantity": t["quantity"],
                    "side": t["aggressor_side"],
                }
                for t in self.tape
            ],
            "history": list(self.history),
            "timeline": self.timeline[-30:],
            "markouts": self._public_marks()[-30:],
            "quant": quant_metrics(snapshot, self.tape),
            "tutor": dict(self.tutor),
            "glossary": GLOSSARY,
            "report": self.report() if self.status == "ended" else None,
        }
