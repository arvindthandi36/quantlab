"""Sequential pair execution, exact account reconciliation, causal decisions and replay."""

import copy
import math
from dataclasses import asdict

import numpy as np

from quantlab.portfolio.accounting import AccountingError
from quantlab.replay_support import ReplayFrames
from quantlab.research.codec import digest, plain
from quantlab.risk.session import risk_versions
from quantlab.statarb.market import MultiMarket
from quantlab.statarb.process import Process, scenario
from quantlab.statarb.risk import analyse_market
from quantlab.statarb.statistics import CausalModel, Fit
from quantlab.statarb.strategy import Rules, decision, sizes


class StatArbSession:
    def __init__(
        self,
        *,
        scenario_name="stable",
        seed=10042,
        steps=240,
        rules=None,
        depth=40,
        fee=0.005,
        spread_ticks=1,
        capital=10000,
        capture=True,
        process_config=None,
    ):
        if type(steps) is not int or not 20 <= steps <= 2000:
            raise ValueError("Choose 20–2000 observations")
        if type(depth) is not int or not 0 <= depth <= 10000:
            raise ValueError("Choose finite depth 0–10000")
        if not math.isfinite(fee) or not 0 <= fee <= 1:
            raise ValueError("Fee per unit must be between 0 and GBP 1")
        if type(spread_ticks) is not int or not 1 <= spread_ticks <= 100:
            raise ValueError("Quoted half-spread requires 1–100 ticks")
        if not math.isfinite(capital) or not 0 < capital <= 1e9:
            raise ValueError("Explicit capital must be positive")
        self.rules = Rules(**(rules or {}))
        self.process = (
            Process.from_config(process_config)
            if process_config
            else scenario(scenario_name, seed=seed, steps=steps)
        )
        self.config = dict(
            scenario_name=scenario_name,
            seed=seed,
            steps=steps,
            rules=asdict(self.rules),
            depth=depth,
            fee=fee,
            spread_ticks=spread_ticks,
            capital=capital,
            process_config=copy.deepcopy(self.process.config),
        )
        self.market = MultiMarket(
            [a.identifier for a in self.process.assets],
            np.round(self.process.prices, 2).tolist(),
            steps=steps,
            depth=depth,
            fee=fee,
            spread_ticks=spread_ticks,
            capture=capture,
        )
        self.model = CausalModel(
            window=self.rules.window,
            z_window=self.rules.z_window,
            mode=self.rules.mode,
            block=self.rules.block,
        )
        self.steps, self.capital, self.capture = steps, capital, capture
        self.status, self.systematic = "active", False
        self.revision = 0
        self.signal = self.model.at(self.pair_history, 0)
        self.pending = []
        self.active = None
        self.trades = []
        self.fills = []
        self.actions = []
        self.timeline = []
        self.decisions = []
        self.path = []
        self.peak = self.drawdown = self.turnover = self.max_gross = self.max_imbalance = 0.0
        self.imbalance_observations = 0.0
        self.attribution = dict(
            spread=0.0, directional=0.0, execution=0.0, fees=0.0, temporary_directional=0.0
        )
        self.fill_counts = dict.fromkeys(self.market.identifiers, 0)
        self.last_result = {
            "ok": True,
            "message": "Collect past observations to fit the relationship",
        }
        self._point()

    @property
    def pair_history(self):
        return [p[:2] for p in self.market.history]

    def _log(self, kind, message, **facts):
        self.timeline.append(
            dict(
                event=self.revision, t=self.market.t, kind=kind, message=message, **plain(facts)
            )
        )

    def _collect(self):
        for i, (k, venue) in enumerate(self.market.venues.items()):
            mark = self.market.history[-1][i]
            for f in venue.own_trades[self.fill_counts[k] :]:
                sign = 1 if f["side"] == "buy" else -1
                price, fee = f["price_ticks"] / 100, float(f["fee_ticks"] / 100)
                shortfall = sign * f["quantity"] * (price - mark)
                row = dict(
                    t=self.market.t,
                    event=self.revision,
                    instrument=k,
                    side=f["side"],
                    quantity=f["quantity"],
                    price=price,
                    reference=mark,
                    execution_shortfall=shortfall,
                    fee=fee,
                    order_id=f["order_id"],
                    trade_id=f["trade_id"],
                    role=f["role"],
                    stage="exit"
                    if self.active and self.active.get("exit_request")
                    else "entry",
                )
                self.fills.append(row)
                self.attribution["execution"] += shortfall
                self.attribution["fees"] += fee
                self.turnover += price * f["quantity"]
                self._log(
                    "execution", f"{k} {f['side']} {f['quantity']} at £{price:.2f}", fill=row
                )
            self.fill_counts[k] = len(venue.own_trades)
        self.market.check()

    def _pnl(self):
        return sum(
            float(v.account.snapshot().total_pnl_ticks / 100)
            for v in self.market.venues.values()
        )

    def _exposure(self):
        q = list(self.market.positions().values())
        p = self.market.history[-1]
        beta = (
            self.active["entry"]["fit"]["beta"]
            if self.active
            else (self.signal["fit"]["beta"] if self.signal.get("available") else 1)
        )
        return dict(
            gross=sum(abs(n * x) for n, x in zip(q, p, strict=True)),
            net=sum(n * x for n, x in zip(q, p, strict=True)),
            imbalance=abs(q[0] + beta * q[1]) * p[0],
            beta=beta,
        )

    def _point(self):
        pnl, exposure = self._pnl(), self._exposure()
        self.peak = max(self.peak, pnl)
        self.drawdown = max(self.drawdown, self.peak - pnl)
        self.max_gross = max(self.max_gross, exposure["gross"])
        self.max_imbalance = max(self.max_imbalance, exposure["imbalance"])
        attributed = (
            self.attribution["spread"]
            + self.attribution["directional"]
            - self.attribution["execution"]
            - self.attribution["fees"]
        )
        if not math.isclose(pnl, attributed, abs_tol=1e-7, rel_tol=1e-10):
            raise AccountingError(
                f"Stat-arb ledger/attribution mismatch: {pnl} != {attributed}"
            )
        row = dict(
            t=self.market.t,
            event=self.revision,
            pnl=pnl,
            drawdown=self.peak - pnl,
            positions=self.market.positions(),
            prices=list(self.market.history[-1]),
            spread=self.signal.get("spread"),
            z=self.signal.get("z"),
            **exposure,
        )
        if not self.path or self.path[-1] != row:
            self.path.append(row)
        if self.active and (not self.active["during"] or self.active["during"][-1] != row):
            self.active["during"].append(copy.deepcopy(row))
        return row

    def _start(self, action, reason):
        if self.active is not None or self.pending or any(self.market.positions().values()):
            raise ValueError(
                "Close existing positions and outstanding pair legs before a new pair"
            )
        if not self.signal.get("available") or self.signal.get("z") is None:
            raise ValueError("An available causal model and nonzero residual SD are required")
        fit = copy.deepcopy(self.signal["fit"])
        self.active = dict(
            id=len(self.trades) + 1,
            action=action,
            entry=dict(
                t=self.market.t,
                event=self.revision,
                fit=fit,
                z=self.signal["z"],
                spread=self.signal["spread"],
                hedge_ratio=fit["beta"],
                positions=self.market.positions(),
                reason=reason,
            ),
            baseline_pnl=self._pnl(),
            baseline_attribution=dict(self.attribution),
            fill_start=len(self.fills),
            during=[],
            exit=None,
        )

    def _pair(self, action, reason):
        if not self.signal.get("available") or self.signal.get("z") is None:
            raise ValueError(
                "Pair unavailable: collect the required past observations and a usable "
                "spread standard deviation first. No order submitted; session remains usable."
            )
        qx, qy = sizes(
            self.rules,
            self.market.history[-1][:2],
            self.signal.get("fit", {}).get("beta", float("nan")),
            self.signal.get("sd"),
        )
        self._start(action, reason)
        direction = 1 if action == "long" else -1
        items = [
            (self.market.identifiers[0], qx * direction),
            (self.market.identifiers[1], qy * direction),
        ]
        if self.rules.execution_order == "y_first":
            items.reverse()
        self.pending = [dict(instrument=k, quantity=n, reason=reason) for k, n in items]
        self._log(
            "pair",
            f"{action} spread requested; legs execute sequentially",
            targets=self.pending,
        )
        self._execute_next()

    def _guard(self, instrument, signed, price=None):
        positions = self.market.positions()
        prices = dict(zip(self.market.identifiers, self.market.history[-1], strict=True))
        proposed = dict(positions)
        proposed[instrument] += signed
        reservations = {}
        for k, venue in self.market.venues.items():
            live = venue._live("user")
            buy = sum(o.remaining_quantity for o in live if o.side.value == "buy")
            sell = sum(o.remaining_quantity for o in live if o.side.value == "sell")
            reservations[k] = (-sell, buy)

        def bounds(q):
            return {k: (q[k] + lo, q[k] + hi) for k, (lo, hi) in reservations.items()}

        before_bounds, after_bounds = bounds(positions), bounds(proposed)
        before = sum(max(abs(lo), abs(hi)) * prices[k] for k, (lo, hi) in before_bounds.items())
        after = sum(max(abs(lo), abs(hi)) * prices[k] for k, (lo, hi) in after_bounds.items())
        if after > self.rules.max_gross and after > before:
            return "New/increased worst-case gross exposure exceeds limit"
        beta = self._exposure()["beta"]
        x, y = self.market.identifiers[:2]

        def leg_extreme(q):
            # A linear exposure reaches its extrema at interval endpoints. Reservations
            # cannot assume that opposite legs fill together or net each other first.
            y_ends = [beta * n for n in q[y]]
            lo = q[x][0] + min(y_ends)
            hi = q[x][1] + max(y_ends)
            return max(abs(lo), abs(hi)) * prices[x]

        before_leg, after_leg = leg_extreme(before_bounds), leg_extreme(after_bounds)
        if after_leg > self.rules.max_imbalance and after_leg > before_leg:
            return "New/increased temporary leg imbalance exceeds limit"
        return None

    def _order(self, instrument, signed, *, order_type="market", price=None):
        if instrument not in self.market.venues or type(signed) is not int or signed == 0:
            raise ValueError("Known instrument and nonzero whole quantity required")
        venue = self.market.venues[instrument]
        blocked = self._guard(instrument, signed, price)
        if blocked:
            self._log("blocked", blocked, instrument=instrument)
            return {"ok": False, "message": blocked}
        result = venue.command(
            "order",
            side="buy" if signed > 0 else "sell",
            quantity=abs(signed),
            order_type=order_type,
            **({"price": price} if order_type == "limit" else {}),
        )
        self._collect()
        self._point()
        return result

    def _execute_next(self):
        if not self.pending:
            return {"ok": True, "message": "No queued leg"}
        row = self.pending.pop(0)
        result = self._order(row["instrument"], row["quantity"])
        self._log(
            "leg",
            result["message"],
            instrument=row["instrument"],
            requested=row["quantity"],
            positions=self.market.positions(),
            imbalance=self._exposure()["imbalance"],
        )
        self._finish_if_flat()
        return result

    def _close(self, reason):
        self.pending.clear()
        for venue in self.market.venues.values():
            venue.command("cancel_all")
        if self.active:
            self.active["exit_request"] = dict(
                t=self.market.t, reason=reason, z=self.signal.get("z")
            )
        items = [(k, -n) for k, n in self.market.positions().items() if n]
        if self.rules.execution_order == "y_first":
            items.reverse()
        self.pending = [dict(instrument=k, quantity=n, reason=reason) for k, n in items]
        self._log("close", f"Close requested: {reason}; actual liquidity still required")
        self._execute_next()
        self._finish_if_flat()

    def _finish_if_flat(self):
        if (
            not self.active
            or self.pending
            or any(self.market.positions().values())
            or any(v._live("user") for v in self.market.venues.values())
        ):
            return
        a = self.active
        pnl = self._pnl() - a["baseline_pnl"]
        att = {k: self.attribution[k] - a["baseline_attribution"][k] for k in self.attribution}
        current = self.model.with_fit(
            self.pair_history, self.market.t, Fit(**a["entry"]["fit"])
        )
        a["exit"] = dict(
            t=self.market.t,
            reason=a.get("exit_request", {}).get("reason", "flat / no fills"),
            z=current["z"],
            spread=current["spread"],
            net_pnl=pnl,
            gross_pnl=pnl + att["execution"] + att["fees"],
            execution_cost=att["execution"],
            fees=att["fees"],
            holding=self.market.t - a["entry"]["t"],
            attribution=att,
            relationship_reverted=abs(current["z"]) <= self.rules.exit
            if current["z"] is not None
            else None,
            assumptions_warning=abs(current["z"]) >= self.rules.stop
            if current["z"] is not None
            else True,
        )
        a["fills"] = copy.deepcopy(self.fills[a["fill_start"] :])
        a["entry"]["executions"] = [f for f in a["fills"] if f["stage"] == "entry"]
        self.trades.append(a)
        self.active = None

    def publish(self, prices):
        """Accept one newly observed research row, never a future path."""
        old = np.array(self.market.history[-1])
        q = np.array(list(self.market.positions().values()))
        beta = self._exposure()["beta"]
        delta = np.asarray(prices) - old
        spread = float(q[1] * (delta[1] - beta * delta[0]))
        directional = float(q @ delta) - spread
        self.attribution["spread"] += spread
        self.attribution["directional"] += directional
        if self.pending or self._exposure()["imbalance"] > 0.01:
            self.attribution["temporary_directional"] += (
                directional  # subset, NOT additive again.
            )
        self.imbalance_observations += self._exposure()["imbalance"]
        self.market.publish(prices)
        self._collect()
        try:
            self.signal = self.model.at(self.pair_history, self.market.t)
        except ValueError as exc:
            self.signal = {"available": False, "reason": str(exc), "t": self.market.t}
        self._point()
        if self.pending:
            self._execute_next()
        held = self.active is not None
        active_signal = self.signal
        if held:
            active_signal = self.model.with_fit(
                self.pair_history, self.market.t, Fit(**self.active["entry"]["fit"])
            )
        exposure = self._exposure()
        action, reason = decision(
            self.rules,
            active_signal,
            held=held,
            age=self.market.t - self.active["entry"]["t"] if held else 0,
            pnl=self._pnl() - self.active["baseline_pnl"] if held else 0,
            gross=exposure["gross"],
            imbalance=exposure["imbalance"],
        )
        self.decisions.append(
            dict(
                t=self.market.t,
                signal=copy.deepcopy(active_signal),
                action=action,
                reason=reason,
                enabled=self.systematic,
                estimation_fit=self.signal.get("fit"),
            )
        )
        if self.systematic:
            if action == "close":
                self._close(reason)
            elif action in ("long", "short"):
                try:
                    self._pair(action, reason)
                except ValueError as exc:
                    self._log("blocked", str(exc))
        self._point()

    def command(self, kind, **p):
        if self.status != "active":
            raise ValueError("Session is not active")
        if len(self.actions) >= 4000 and kind != "end":
            raise ValueError("Session action budget reached; end and export this session")
        before = self.revision
        try:
            return self._dispatch_command(kind, **p)
        except ValueError as exc:
            # A rejected user request is part of replay; no account repair or fake fill.
            self.revision = before + 1
            result = {"ok": False, "message": str(exc)}
            self.last_result = result
            self._log("rejected", str(exc))
            self._point()
            self.actions.append(
                dict(
                    kind=kind, payload=plain(p), result=result, fingerprint=digest(self.audit())
                )
            )
            return result
        except Exception:
            self.status = "failed"
            raise

    def _dispatch_command(self, kind, **p):
        if self.status != "active":
            raise ValueError("Session is not active")
        allowed = {
            "step": {"count"},
            "pair": {"action"},
            "next_leg": set(),
            "close": set(),
            "wait": set(),
            "auto": {"enabled"},
            "order": {"instrument", "side", "quantity", "order_type", "price"},
            "liquidity": {"instrument", "depth"},
            "cancel": {"instrument", "order_id"},
            "end": set(),
        }
        if kind not in allowed or set(p) - allowed[kind]:
            raise ValueError("Unknown stat-arb command or fields")
        self.revision += 1
        result = {"ok": True, "message": kind.replace("_", " ")}
        if kind == "step":
            count = p.get("count", 1)
            if type(count) is not int or not 1 <= count <= 200:
                raise ValueError("Step 1–200 observations at a time")
            if self.market.t + count > self.steps:
                raise ValueError("Requested observations exceed this session horizon")
            for _ in range(count):
                self.publish(self.process.step())
        elif kind == "pair":
            if p.get("action") not in ("long", "short"):
                raise ValueError("Choose long or short spread")
            self._pair(p["action"], "manual choice using current public information")
        elif kind == "next_leg":
            result = self._execute_next()
        elif kind == "close":
            self._close("manual close")
        elif kind == "wait":
            self._log("decision", "Manual WAIT: no order submitted, no time advanced")
        elif kind == "auto":
            if type(p.get("enabled")) is not bool:
                raise ValueError("Systematic mode requires a boolean")
            self.systematic = p["enabled"]
            self._log(
                "mode", f"Prespecified strategy {'enabled' if self.systematic else 'paused'}"
            )
        elif kind == "order":
            if (
                p.get("side") not in ("buy", "sell")
                or type(p.get("quantity")) is not int
                or p["quantity"] <= 0
            ):
                raise ValueError("Manual leg requires buy/sell and positive whole quantity")
            if p.get("instrument") not in self.market.venues:
                raise ValueError("Unknown instrument")
            if not self.active:
                self._start("manual_leg", "manual individual leg")
            result = self._order(
                p["instrument"],
                p["quantity"] * (1 if p["side"] == "buy" else -1),
                order_type=p.get("order_type", "market"),
                price=p.get("price"),
            )
            self._finish_if_flat()
        elif kind == "liquidity":
            if p.get("instrument") not in self.market.venues:
                raise ValueError("Unknown instrument")
            self.market.venues[p["instrument"]].liquidity(p["depth"])
            self._collect()
            self._log(
                "liquidity", f"{p['instrument']} best-level external depth set to {p['depth']}"
            )
        elif kind == "cancel":
            result = self.market.venues[p["instrument"]].command(
                "cancel", order_id=p["order_id"]
            )
        elif kind == "end":
            self.pending.clear()
            self.systematic = False
            for venue in self.market.venues.values():
                venue.command("end")
            self.status = "ended"
            self._log(
                "end",
                (
                    "Ended: resting orders cancelled; residual positions still "
                    "marked, not fake-liquidated"
                ),
            )
        self._point()
        self.last_result = result
        self.actions.append(
            dict(
                kind=kind,
                payload=plain(p),
                result=plain(result),
                fingerprint=digest(self.audit()),
            )
        )
        return result

    def metrics(self):
        closed = [t["exit"] for t in self.trades if t.get("fills")]
        pnls = [t["net_pnl"] for t in closed]
        return dict(
            net_pnl=self._pnl(),
            return_on_capital=self._pnl() / self.capital,
            capital=self.capital,
            drawdown=self.drawdown,
            trade_count=len(closed),
            win_rate=sum(p > 0 for p in pnls) / len(pnls) if pnls else None,
            average_trade=float(np.mean(pnls)) if pnls else None,
            median_trade=float(np.median(pnls)) if pnls else None,
            turnover=self.turnover,
            mean_holding=float(np.mean([t["holding"] for t in closed])) if closed else None,
            execution_cost=self.attribution["execution"],
            fees=self.attribution["fees"],
            costs=self.attribution["execution"] + self.attribution["fees"],
            max_gross=self.max_gross,
            max_imbalance=self.max_imbalance,
            imbalance_observations=self.imbalance_observations,
            probability_loss=sum(p < 0 for p in pnls) / len(pnls) if pnls else None,
            worst_trade=min(pnls) if pnls else None,
            mean_entry_z=float(
                np.mean([t["entry"]["z"] for t in self.trades if t.get("fills")])
            )
            if pnls
            else None,
            mean_exit_z=float(np.mean([t["z"] for t in closed if t["z"] is not None]))
            if closed and any(t["z"] is not None for t in closed)
            else None,
            residual_inventory=sum(abs(n) for n in self.market.positions().values()),
        )

    def audit(self):
        return dict(
            t=self.market.t,
            positions=self.market.positions(),
            signal=self.signal,
            pending=self.pending,
            metrics=self.metrics(),
            attribution=self.attribution,
            fills=self.fills,
            status=self.status,
        )

    def state(self):
        markets = []
        for i, (k, v) in enumerate(self.market.venues.items()):
            snap = v.public_snapshot()
            markets.append(
                dict(
                    instrument=k,
                    price=self.market.history[-1][i],
                    position=v.account.inventory,
                    bids=snap["bids"],
                    asks=snap["asks"],
                    orders=snap["orders"],
                    tape=snap["tape"][-8:] if "tape" in snap else v.tape[-8:],
                    depth=v.depth,
                )
            )
        return plain(
            dict(
                status=self.status,
                revision=self.revision,
                t=self.market.t,
                steps=self.steps,
                systematic=self.systematic,
                rules=asdict(self.rules),
                signal=self.signal,
                markets=markets,
                history=self.market.history,
                decisions=self.decisions[-20:],
                pending=self.pending,
                active=self.active,
                trades=self.trades,
                fills=self.fills,
                metrics=self.metrics(),
                exposure=self._exposure(),
                attribution=self.attribution,
                path=self.path[-500:],
                timeline=self.timeline[-14:],
                risk=analyse_market(self.market, capital=self.capital, drawdown=self.drawdown),
                last_result=self.last_result,
                warning=(
                    "Synthetic teaching market. Correlation, R² and z-scores are not "
                    "profit guarantees. "
                    "Current prices are published reference marks; "
                    "trades pay actual book prices."
                ),
            )
        )

    def journal(self):
        if self.status != "ended":
            raise ValueError("End the session before exporting private market seeds")
        return plain(
            dict(
                schema="quantlab-statarb-v1",
                versions=risk_versions(),
                config=self.config,
                actions=self.actions,
                evidence=self.process.evidence,
                history=self.market.history,
                trades=self.trades,
                fills=self.fills,
                final=self.audit(),
            )
        )


def replay(journal, *, frames=False):
    if (
        journal.get("schema") != "quantlab-statarb-v1"
        or journal.get("versions") != risk_versions()
    ):
        raise ValueError("Replay schema/runtime version differs")
    s = StatArbSession(**journal["config"])
    views = ReplayFrames([s.state()]) if frames else []
    for row in journal["actions"]:
        result = s.command(row["kind"], **row["payload"])
        if result != row["result"] or s.actions[-1]["fingerprint"] != row["fingerprint"]:
            raise ValueError("Replay diverged: command, fill, signal or account differs")
        if frames:
            views.append(s.state())
    if digest(s.journal()) != digest(journal):
        raise ValueError("Replay evidence/history/final state differs")
    return (s, views) if frames else s
