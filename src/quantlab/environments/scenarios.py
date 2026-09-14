"""Presets and scheduled validated inputs; no scenario-specific pricing or P&L."""

import copy
from dataclasses import asdict

from quantlab import __version__
from quantlab.environments import SCHEMA
from quantlab.environments.data import integer
from quantlab.options.session import OptionsConfig, OptionsSession
from quantlab.research.codec import digest, plain
from quantlab.statarb.process import Link, Process
from quantlab.statarb.session import StatArbSession
from quantlab.trading.scenarios import select_scenario
from quantlab.trading.session import TradingSession

SPECS = {
    "normal": {
        "title": "Normal market",
        "engine": "trading",
        "preset": "normal",
        "mechanism": "Baseline noise, liquidity and informed arrivals",
        "challenge": "drawdown",
    },
    "high_volatility": {
        "title": "High volatility",
        "engine": "trading",
        "preset": "volatile",
        "mechanism": "Latent increment sigma rises from 2 to 8 ticks / square-root second",
        "challenge": "drawdown",
    },
    "low_liquidity": {
        "title": "Low liquidity",
        "engine": "trading",
        "preset": "thin",
        "mechanism": (
            "Opening displayed quantities are one unit; maker disabled; lower "
            "noise arrival rate"
        ),
        "challenge": "drawdown",
    },
    "toxic_flow": {
        "title": "Toxic / informed flow",
        "engine": "trading",
        "preset": "toxic",
        "mechanism": "Informed arrival rate 4/second; noisy-signal SD 1 tick",
        "challenge": "drawdown",
    },
    "position_management": {
        "title": "Reduce opening inventory",
        "engine": "trading",
        "preset": "position",
        "mechanism": "Eight endowed long units under the existing accounting convention",
        "challenge": "flatten",
    },
    "trending": {
        "title": "Trending market",
        "engine": "statarb",
        "preset": "drift",
        "mechanism": (
            "A drifting residual from observation 1; this is a relationship "
            "trend, not a promised rise in every price"
        ),
        "challenge": "drawdown",
    },
    "mean_reverting": {
        "title": "Mean-reverting market",
        "engine": "statarb",
        "preset": "stable",
        "mechanism": (
            "Stable AR(1) residual; levels need not revert and convergence is not guaranteed"
        ),
        "challenge": "drawdown",
    },
    "volatility_shock": {
        "title": "Volatility shock",
        "engine": "statarb",
        "preset": "volatility",
        "mechanism": (
            "Existing residual-volatility break multiplies sigma by four at the midpoint"
        ),
        "challenge": "drawdown",
    },
    "liquidity_shock": {
        "title": "Liquidity shock",
        "engine": "statarb",
        "preset": "stable",
        "mechanism": (
            "Existing venue liquidity command reduces both books to two units at the midpoint"
        ),
        "challenge": "observe_liquidity",
    },
    "correlation_breakdown": {
        "title": "Correlation breakdown",
        "engine": "statarb",
        "preset": "positive",
        "mechanism": (
            "Existing covariance factor changes from correlation +0.9 to -0.8 at the midpoint"
        ),
        "challenge": "drawdown",
    },
    "relationship_breakdown": {
        "title": "Relationship breakdown",
        "engine": "statarb",
        "preset": "decouple",
        "mechanism": "Existing residual persistence changes to one at the midpoint",
        "challenge": "drawdown",
    },
    "option_volatility_shock": {
        "title": "Option volatility shock",
        "engine": "options",
        "preset": "options",
        "mechanism": (
            "Existing set_iv command changes base quote volatility from 20% "
            "to 40% at the midpoint"
        ),
        "challenge": "delta_band",
    },
}


def catalog():
    return [{"id": k, **v} for k, v in SPECS.items()]


class ScenarioSession:
    def __init__(self, key="normal", *, seed=42, hidden=False, steps=60, mode="free"):
        if key not in SPECS:
            raise ValueError("Choose an available scenario")
        integer(seed, "Seed", 0, 2**256)
        integer(steps, "Duration/observations", 20, 120)
        if type(hidden) is not bool or mode not in ("free", "manual_maker"):
            raise ValueError("Invalid scenario visibility or trading profile")
        self.key, self.seed, self.hidden, self.steps, self.mode = key, seed, hidden, steps, mode
        self.spec = SPECS[key]
        self.engine = self.spec["engine"]
        self.actions = []
        self.revision = 0
        self.shock_applied = False
        self.acknowledged = False
        self.max_abs_delta = 0.0
        self.config = dict(key=key, seed=seed, hidden=hidden, steps=steps, mode=mode)
        if self.engine == "trading":
            self.session = TradingSession(
                select_scenario(self.spec["preset"], seed=seed, duration_seconds=steps), mode
            )
        elif self.engine == "options":
            self.session = OptionsSession(OptionsConfig(seed=seed, steps=steps))
        else:
            config = None
            if key == "trending":
                config = Process(
                    seed=seed, links=(Link(phi=1, break_at=1, break_kind="drift"),)
                ).config
            self.session = StatArbSession(
                scenario_name=self.spec["preset"],
                seed=seed,
                steps=steps,
                process_config=config,
                rules={"window": 20, "z_window": 12, "block": 10},
            )
        self.last_result = {
            "ok": True,
            "message": "Scenario ready. Public observations determine your decisions.",
        }

    @property
    def status(self):
        return (
            "ended"
            if self.session.status == "ended"
            else "failed"
            if self.session.status == "failed"
            else "paused"
        )

    @property
    def index(self):
        return (
            self.session.now_us // 1_000_000
            if self.engine == "trading"
            else self.session.step_index
            if self.engine == "options"
            else self.session.market.t
        )

    def _scheduled(self):
        if self.shock_applied or self.index < self.steps // 2:
            return
        if self.key == "liquidity_shock":
            for k in self.session.market.identifiers:
                self.session.command("liquidity", instrument=k, depth=2)
        elif self.key == "correlation_breakdown":
            p = self.session.process
            updated = Process(seed=self.seed, assets=p.assets, correlation=-0.8)
            # Only the approved covariance factor input changes; current prices and RNG persist.
            p.factor = updated.factor
            p.factor_info = updated.factor_info
            p.config["correlation"] = -0.8
        elif self.key == "option_volatility_shock":
            self.session.command("set_iv", volatility=0.4)
        self.shock_applied = True

    def command(self, kind, **p):
        if self.status in ("ended", "failed"):
            raise ValueError("Scenario ended; use read-only replay or a fresh session")
        if len(self.actions) >= 1000 and kind != "end":
            raise ValueError("Scenario action budget reached; end and export")
        if kind == "step":
            if set(p) - {"count"}:
                raise ValueError("Unknown step fields")
            count = integer(p.get("count", 1), "Observations", 1, 200)
            for _ in range(count):
                if self.status == "ended":
                    break
                if self.engine == "trading":
                    self.session.command("step_interval", delta_us=1_000_000)
                else:
                    self.session.command("step", count=1)
                self._scheduled()
                if self.engine == "options":
                    self.max_abs_delta = max(
                        self.max_abs_delta, abs(self.session.aggregate_greeks()["delta"])
                    )
                if self.index >= self.steps and self.status != "ended":
                    self.session.command("end")
            result = {"ok": True, "message": "Observed the next public market state"}
        elif kind == "acknowledge_liquidity":
            if p:
                raise ValueError("No acknowledgement payload is required")
            self.acknowledged = self.index >= self.steps // 2
            result = {
                "ok": True,
                "message": "Observation recorded for post-session objective review",
            }
        else:
            if kind not in (
                "order",
                "cancel",
                "quotes",
                "cancel_all",
                "end",
                "option_order",
                "stock_order",
                "cancel_stock",
                "hedge",
                "pair",
                "next_leg",
                "close",
            ):
                raise ValueError("This action is not available in scenario trading")
            allowed = {
                "trading": ("order", "cancel", "quotes", "cancel_all", "end"),
                "options": ("option_order", "stock_order", "cancel_stock", "hedge", "end"),
                "statarb": ("order", "cancel", "pair", "next_leg", "close", "end"),
            }
            if kind not in allowed[self.engine]:
                raise ValueError("Choose an action supported by this engine")
            # Core adapters can advance a revision before rejecting malformed input.
            # Commit a detached engine only after success, so rejected requests cannot
            # create an unjournalled transition or change its random stream.
            candidate = copy.deepcopy(self.session)
            result = candidate.command(kind, **p)
            if result.get("ok") is False:
                raise ValueError(result.get("message", "The engine rejected this action"))
            self.session = candidate
        if self.engine == "options":
            self.max_abs_delta = self.session.max_delta
        self.revision += 1
        self.last_result = result
        self.actions.append(
            {"kind": kind, "payload": copy.deepcopy(p), "state_digest": digest(self.public())}
        )
        return result

    def public_core(self):
        if self.engine == "trading":
            raw = self.session.public_snapshot()
            safe = {
                k: copy.deepcopy(raw[k])
                for k in (
                    "status",
                    "revision",
                    "time_us",
                    "public_event",
                    "account",
                    "reference",
                    "reference_source",
                    "best_bid",
                    "best_ask",
                    "mid",
                    "spread",
                    "bids",
                    "asks",
                    "orders",
                    "trades",
                    "markouts",
                    "tape",
                    "timeline",
                    "quant",
                    "history",
                    "mode",
                )
                if k in raw
            }
            # Opening timeline text can name the scenario; orders/fills have separate fields.
            safe["timeline"] = []
            return safe
        if self.engine == "options":
            raw = self.session.snapshot(include_curves=True)
            safe = {
                k: copy.deepcopy(raw[k])
                for k in (
                    "status",
                    "revision",
                    "step",
                    "spot",
                    "selected",
                    "chain",
                    "account",
                    "accounts",
                    "positions",
                    "portfolio_greeks",
                    "tape",
                    "path",
                    "stock",
                    "greeks",
                    "rate",
                    "dividend_yield",
                    "curves",
                    "quote_revision",
                    "option_trades",
                    "history",
                    "elapsed_days",
                    "step_days",
                )
                if k in raw
            }
            return safe
        raw = self.session.state()
        return {
            k: copy.deepcopy(raw[k])
            for k in (
                "status",
                "revision",
                "t",
                "history",
                "signal",
                "rules",
                "markets",
                "fills",
                "metrics",
                "exposure",
                "pending",
                "path",
                "decisions",
                "attribution",
            )
            if k in raw
        }

    def configuration(self):
        actual = (
            asdict(self.session.scenario)
            if self.engine == "trading"
            else asdict(self.session.config)
            if self.engine == "options"
            else self.session.config
        )
        return plain(
            {
                "scenario": self.key,
                "title": self.spec["title"],
                "seed": self.seed,
                "engine": self.engine,
                "mechanism": self.spec["mechanism"],
                "configuration": actual,
                "scheduled_input": self.spec["mechanism"],
            }
        )

    def challenge(self):
        core = self.public_core()
        if self.engine == "trading":
            a = core["account"]
            pnl = float(a["total_pnl"])
            dd = float(a["max_drawdown"])
            q = a["position"]
        elif self.engine == "options":
            a = self.session.accounts()
            pnl = float(a["total_pnl"])
            dd = float(self.session.metrics().get("drawdown", 0))
            q = self.session.stock.account.inventory
        else:
            a = core["metrics"]
            pnl = a["net_pnl"]
            dd = a["drawdown"]
            q = sum(abs(v) for v in self.session.market.positions().values())
        # Hidden objectives must not name the concealed regime.
        target = "drawdown" if self.hidden else self.spec["challenge"]
        descriptions = {
            "drawdown": "Finish the configured duration with maximum drawdown at most £1.",
            "flatten": "Reduce endowed inventory to zero by the end; P&L is separate.",
            "observe_liquidity": "Record liquidity deterioration after it becomes observable.",
            "delta_band": (
                "Keep observed absolute portfolio delta within 10 units through the session."
            ),
        }
        completed = self.status == "ended" and self.index >= self.steps
        success = completed and (
            dd <= 1
            if target == "drawdown"
            else q == 0
            if target == "flatten"
            else self.acknowledged
            if target == "observe_liquidity"
            else self.max_abs_delta <= 10
        )
        return {
            "objective": descriptions[target],
            "complete": completed,
            "success": success if self.status == "ended" else None,
            "pnl": pnl,
            "drawdown": dd,
            "note": (
                "Objective success and profitability are separate. Early ending "
                "does not complete the duration."
            ),
        }

    def public(self):
        core = self.public_core()
        kind = "SCENARIO"
        return {
            "schema": SCHEMA,
            "engine": self.engine,
            "status": self.status,
            "revision": self.revision,
            "index": self.index,
            "environment": {
                "type": kind,
                "id": "scenario-session",
                "hidden": self.hidden,
                "badge": "SCENARIO — HIDDEN"
                if self.hidden
                else "SCENARIO — " + self.spec["title"],
                "title": "Scenario Session" if self.hidden else self.spec["title"],
                "hidden_model_state": True,
                "counterparty_simulation": True,
                "future_stored": False,
                "execution_model": "Existing " + self.engine + " engine",
                "truth": (
                    "Controlled synthetic model; prices and fills are not historical "
                    "observations."
                ),
            },
            "core": core,
            "configuration": None if self.hidden else self.configuration(),
            "challenge": self.challenge(),
            "last_result": copy.deepcopy(self.last_result),
            "capabilities": {
                "orders": True,
                "quotes": self.engine == "trading",
                "options": self.engine == "options",
                "pair_signals": self.engine == "statarb",
                "observer": self.status == "ended",
            },
        }

    def reveal(self):
        if self.status != "ended":
            raise ValueError(
                "Hidden configuration requires explicit reveal after the session ends"
            )
        return {
            "label": (
                "POST-SESSION SCENARIO CONFIGURATION — unavailable during hidden decisions"
            ),
            "configuration": self.configuration(),
            "what_you_could_observe": self.public_core(),
            "quiz_allowed": False,
            "note": (
                "Configuration explains this controlled model. It is not a market "
                "forecast or proof of a real-market cause."
            ),
        }

    def journal(self):
        if self.status != "ended":
            raise ValueError("End the scenario before exporting private replay evidence")
        return {
            "schema": SCHEMA,
            "environment": "SCENARIO",
            "quantlab_version": __version__,
            "execution_version": "approved-core-scenario-v1",
            "configuration": copy.deepcopy(self.config),
            "model_configuration": self.configuration(),
            "source": "QuantLab controlled synthetic engines",
            "timestamp_range": [0, self.index],
            "actions": copy.deepcopy(self.actions),
            "final_digest": digest(self.public()),
        }


def replay_scenario(raw):
    if (
        raw.get("schema") != SCHEMA
        or raw.get("environment") != "SCENARIO"
        or raw.get("quantlab_version") != __version__
        or raw.get("execution_version") != "approved-core-scenario-v1"
    ):
        raise ValueError("Unsupported scenario journal or version")
    if not isinstance(raw.get("actions"), list) or len(raw["actions"]) > 1001:
        raise ValueError("Scenario replay action budget exceeded")
    s = ScenarioSession(**raw["configuration"])
    frames = [s.public()]
    for a in raw["actions"]:
        s.command(a["kind"], **a["payload"])
        if digest(s.public()) != a["state_digest"]:
            raise ValueError("Scenario replay fingerprint mismatch")
        frames.append(s.public())
    if (
        raw.get("model_configuration") != s.configuration()
        or raw.get("timestamp_range") != [0, s.index]
        or raw.get("source") != "QuantLab controlled synthetic engines"
    ):
        raise ValueError("Scenario provenance/configuration mismatch")
    if s.status != "ended" or digest(s.public()) != raw["final_digest"]:
        raise ValueError("Scenario replay final mismatch")
    return s, frames
