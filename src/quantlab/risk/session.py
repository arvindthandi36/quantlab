"""Risk session over live Phase 6/8 ledgers; deterministic commands and replay."""

import copy
import importlib.metadata
import platform
from dataclasses import asdict, replace

from quantlab import __version__
from quantlab.options.session import OptionsConfig, OptionsSession
from quantlab.options.underlying import UnderlyingVenue
from quantlab.replay_support import ReplayFrames
from quantlab.research.codec import digest, plain
from quantlab.risk.analytics import FACTORS, RiskSettings, analyse, linear_risk
from quantlab.risk.covariance import estimate_covariance, validate_covariance
from quantlab.risk.limits import Limit, check_limits, reserved_values
from quantlab.risk.optimisation import frontier, optimise
from quantlab.risk.portfolio import from_accounts
from quantlab.risk.scenarios import Scenario, scenario_pnl, validate_horizon
from quantlab.trading.scenarios import scenario_from_dict, select_scenario
from quantlab.trading.session import TradingSession


def risk_versions():
    return {
        "quantlab": __version__,
        "python": platform.python_version(),
        "numpy": importlib.metadata.version("numpy"),
        "scipy": importlib.metadata.version("scipy"),
    }


def unguarded_clone(session):
    guards = [
        getattr(session, "portfolio_risk_guard", None),
        getattr(session, "portfolio_command_guard", None),
    ]
    if hasattr(session, "stock"):
        guards.append(getattr(session.stock, "portfolio_risk_guard", None))

    def no_guard(*args):
        return None

    clone = copy.deepcopy(session, {id(g): no_guard for g in guards if g is not None})
    clone.portfolio_risk_guard = None
    clone.portfolio_command_guard = None
    if hasattr(clone, "stock"):
        clone.stock.portfolio_risk_guard = None
    return clone


class RiskSession:
    def __init__(self, options=None, desk=None, *, settings=None, capture=True):
        self.options = options or OptionsSession()
        self.desk = desk or TradingSession(select_scenario())
        self.second = UnderlyingVenue(100, steps=252)
        self.settings = settings or RiskSettings()
        self.initial_settings = self.settings
        self.capture = capture
        self.baseline = plain(
            {
                "options_config": asdict(self.options.config),
                "options_actions": self.options.actions,
                "desk_scenario": asdict(self.desk.scenario),
                "desk_mode": self.desk.mode,
                "desk_actions": self.desk.actions,
            }
        )
        self.actions = []
        self.status = "active"
        self.revision = 0
        self.limits = []
        self.observations = None
        self.covariance = None
        self.scenario = None
        self.optimisation = None
        self.challenge = None
        self.warnings = []
        self.last_result = {
            "ok": True,
            "message": "Risk session attached to actual trading accounts",
        }
        self.peak = self.portfolio().equity - self.portfolio().initial_capital
        self.drawdown = 0.0
        self._cache_key = None
        self._cache = None
        self._attach()

    def portfolio(self, options=None, stocks=None):
        return from_accounts(
            options or self.options,
            stocks or {"QL-DESK": self.desk, "QL-SECOND": self.second},
            drawdown=getattr(self, "drawdown", 0),
        )

    def venues(self):
        return {"QL-STOCK": self.options.stock, "QL-DESK": self.desk, "QL-SECOND": self.second}

    def _attach(self):
        self.options.portfolio_risk_guard = self._option_guard
        self.options.stock.portfolio_risk_guard = lambda side, n, p: self._stock_guard(
            "QL-STOCK", side, n, p
        )
        self.desk.portfolio_command_guard = self._quote_guard
        self.desk.portfolio_risk_guard = lambda side, n, p: self._stock_guard(
            "QL-DESK", side, n, p
        )
        self.second.portfolio_risk_guard = lambda side, n, p: self._stock_guard(
            "QL-SECOND", side, n, p
        )

    def _evaluate_proposal(self, portfolio, venues):
        if not self.limits:
            return None
        before = reserved_values(
            self.portfolio(), self.settings, self.venues(), self.covariance
        )
        portfolio = replace(
            portfolio,
            drawdown=max(
                self.drawdown, self.peak - (portfolio.equity - portfolio.initial_capital)
            ),
        )
        after = reserved_values(portfolio, self.settings, venues, self.covariance)
        warnings = check_limits(self.limits, after, before=before)
        self.warnings.extend(warnings)
        blocked = [w["message"] for w in warnings if w["blocked"]]
        return "; ".join(blocked) or None

    def _quote_guard(self, kind, payload):
        if not self.limits:
            return None
        clone = unguarded_clone(self.desk)
        result = clone.command(kind, **payload)
        if not result.get("ok", True):
            return result.get("message")
        return self._evaluate_proposal(
            self.portfolio(stocks={"QL-DESK": clone, "QL-SECOND": self.second}),
            self.venues() | {"QL-DESK": clone},
        )

    def _option_guard(self, key, side, n, revision):
        if not self.limits:
            return None
        clone = unguarded_clone(self.options)
        clone._trade_option(key, side, n, revision)
        return self._evaluate_proposal(
            self.portfolio(options=clone), self.venues() | {"QL-STOCK": clone.stock}
        )

    def _stock_guard(self, name, side, n, price):
        if not self.limits:
            return None
        if name == "QL-STOCK":
            clone = unguarded_clone(self.options)
            clone._stock_order(
                side.value,
                n,
                "market" if price is None else "limit",
                None if price is None else str(price / 100),
            )
            p = self.portfolio(options=clone)
            venue = clone.stock
        else:
            venue = unguarded_clone(self.venues()[name])
            venue._submit("user", side, n, price)
            venue._mark()
            p = self.portfolio(
                stocks={"QL-DESK": self.desk, "QL-SECOND": self.second} | {name: venue}
            )
        return self._evaluate_proposal(p, self.venues() | {name: venue})

    def report(self):
        p = self.portfolio()
        key = digest(
            {
                "portfolio": p.public(),
                "settings": asdict(self.settings),
                "observations": self.observations,
                "covariance": self.covariance,
            }
        )
        if key != self._cache_key:
            self._cache = analyse(
                p, self.settings, observations=self.observations, covariance=self.covariance
            )
            self._cache_key = key
        return copy.deepcopy(self._cache)

    def state(self):
        report = self.report()
        risk = reserved_values(self.portfolio(), self.settings, self.venues(), self.covariance)
        breaches = check_limits(self.limits, risk)
        # State breaches are warnings: only pre-trade proposals can be prohibited.
        for w in breaches:
            w["blocked"] = False
        challenge = None
        if self.challenge:
            k = self.challenge["kind"]
            target = self.challenge["target"]
            p = report["portfolio"]
            actual = {
                "var": report["monte_carlo"]["full"]["var"],
                "delta": risk["delta"],
                "concentration": p["largest_position_share"],
                "volatility": scenario_pnl(self.portfolio(), Scenario(volatility_change=0.20))[
                    "loss"
                ],
            }[k]
            passed = actual is not None and actual <= target
            if k == "delta":
                passed &= risk["vega"] <= self.challenge["vega_max"]
            if k == "concentration":
                passed &= abs(p["delta_gbp"]) >= self.challenge["minimum_delta_gbp"]
            challenge = self.challenge | {
                "actual": actual,
                "passed": bool(passed),
                "message": "Result follows your actual positions; no automatic hedge",
            }
        return {
            "revision": self.revision,
            "status": self.status,
            "report": report,
            "limits": [asdict(x) for x in self.limits],
            "reserved_risk": risk,
            "breaches": breaches,
            "last_warnings": copy.deepcopy(self.warnings),
            "last_result": copy.deepcopy(self.last_result),
            "scenario": copy.deepcopy(self.scenario),
            "optimisation": copy.deepcopy(self.optimisation),
            "challenge": challenge,
            "trading": {
                "option_quote_revision": self.options.quote_revision,
                "selected": self.options.selected,
                "chain": [
                    q.public(self.options.elapsed_years) for q in self.options.quotes.values()
                ],
                "stock_orders": self.options.stock.public_snapshot()["orders"],
                "desk_orders": self.desk.public_snapshot()["orders"],
                "second_orders": self.second.public_snapshot()["orders"],
                "option_fills": len(self.options.option_trades),
                "stock_fills": len(self.options.stock.own_trades),
                "desk_fills": len(self.desk.own_trades),
                "second_fills": len(self.second.own_trades),
            },
        }

    def execute(self, target, kind, /, **payload):
        if self.status != "active":
            raise ValueError("Risk session ended; replay is read-only")
        if len(self.actions) >= 3000 and kind != "end":
            raise ValueError("Risk action budget reached; end and export")
        self.warnings = []
        payload = copy.deepcopy(payload)
        recorded_payload = copy.deepcopy(payload)
        if target in ("options", "desk", "second"):
            session = {"options": self.options, "desk": self.desk, "second": self.second}[
                target
            ]
            result = session.command(kind, **payload)
        elif target == "risk":
            result = self._risk_command(kind, payload)
        else:
            raise ValueError("Unknown portfolio venue")
        p = self.portfolio()
        pnl = p.equity - p.initial_capital
        self.peak = max(self.peak, pnl)
        self.drawdown = max(self.drawdown, self.peak - pnl)
        if target in ("options", "desk", "second") and self.scenario is not None:
            previous_scenario = Scenario(**self.scenario["scenario"])
            try:
                self.scenario = scenario_pnl(
                    self.portfolio(), previous_scenario, cash_rate=self.settings.cash_rate
                )
            except ValueError as exc:
                self.scenario = {
                    "scenario": asdict(previous_scenario),
                    "unavailable": str(exc),
                    "full_pnl": None,
                    "approximate_pnl": None,
                    "residual": None,
                    "contributions": {},
                    "positions": [],
                    "warnings": [str(exc)],
                }
            if previous_scenario.correlation is not None:
                self.scenario["correlation_risk"] = linear_risk(
                    self.portfolio(),
                    self.settings,
                    self.settings.covariance(previous_scenario.correlation),
                )
        self.revision += 1
        self.last_result = result
        self._cache_key = None
        state = self.state()
        if self.capture:
            self.actions.append(
                plain(
                    {
                        "target": target,
                        "kind": kind,
                        "payload": recorded_payload,
                        "result": result,
                        "state_digest": digest(state),
                    }
                )
            )
        return {"result": result, "state": state}

    def _risk_command(self, kind, p):
        if kind == "settings":
            new = RiskSettings(**(asdict(self.settings) | p))
            # Validate horizon and resource bounds against actual positions before committing.
            validate_horizon(self.portfolio(), new.days)
            analyse(
                self.portfolio(),
                new,
                observations=self.observations,
                covariance=self.covariance,
            )
            self.settings = new
            self.scenario = self.optimisation = None
        elif kind == "reset_inputs":
            if p:
                raise ValueError("Reset inputs takes no fields")
            self.observations = self.covariance = None
            self.scenario = self.optimisation = None
        elif kind == "sample":
            if set(p) - {"returns", "missing", "use_estimated_covariance"}:
                raise ValueError("Unknown sample fields")
            import numpy as np

            data = np.asarray(p["returns"], dtype=float)
            info = estimate_covariance(data, missing=p.get("missing", "reject"))
            data = data[np.isfinite(data).all(axis=1)]
            if data.shape[1] != len(FACTORS):
                raise ValueError("Three synchronised factor return columns required")
            candidate = data.tolist()
            covariance = (
                info["covariance"]
                if p.get("use_estimated_covariance", False)
                else self.covariance
            )
            analyse(
                self.portfolio(), self.settings, observations=candidate, covariance=covariance
            )
            self.observations = candidate
            self.covariance = covariance
            return {
                "ok": True,
                "message": "Empirical sample accepted with explicit missing-data policy",
                **info,
            }
        elif kind == "covariance":
            if set(p) != {"matrix"}:
                raise ValueError("Supply a covariance matrix")
            c, info = validate_covariance(p["matrix"])
            if c.shape != (3, 3):
                raise ValueError("Three named factor covariance required")
            candidate = c.tolist()
            analyse(
                self.portfolio(),
                self.settings,
                observations=self.observations,
                covariance=candidate,
            )
            self.covariance = candidate
            return {"ok": True, **info}
        elif kind == "limits":
            if (
                set(p) != {"limits"}
                or not isinstance(p["limits"], list)
                or len(p["limits"]) > 8
            ):
                raise ValueError("Supply at most eight limits")
            proposed = [Limit(**r) for r in p["limits"]]
            if len({x.metric for x in proposed}) != len(proposed):
                raise ValueError("One limit per metric")
            self.limits = proposed
        elif kind == "scenario":
            s = Scenario(**p)
            self.scenario = scenario_pnl(self.portfolio(), s, cash_rate=self.settings.cash_rate)
            if s.correlation is not None:
                self.scenario["correlation_risk"] = linear_risk(
                    self.portfolio(), self.settings, self.settings.covariance(s.correlation)
                )
        elif kind == "optimise":
            means = p.pop("means", [0.0003, 0.0002, 0.0001])
            frontier_points = p.pop("frontier_points", 0)
            c = self.settings.covariance() if self.covariance is None else self.covariance
            result = optimise(c, means, **p)
            if frontier_points:
                result["frontier"] = frontier(c, means, points=frontier_points, **p)
            self.optimisation = result
        elif kind == "challenge":
            from quantlab.options.models import number

            if set(p) - {"kind", "target", "vega_max", "minimum_delta_gbp"}:
                raise ValueError("Unknown challenge fields")
            if p.get("kind") not in ("var", "delta", "concentration", "volatility"):
                raise ValueError("Unknown challenge")
            self.challenge = {
                "kind": p["kind"],
                "target": number(p["target"], "target", 0),
                "vega_max": number(p.get("vega_max", 10000), "vega maximum", 0),
                "minimum_delta_gbp": number(
                    p.get("minimum_delta_gbp", 1000), "minimum delta GBP", 0
                ),
            }
        elif kind == "end":
            if p:
                raise ValueError("End takes no fields")
            if self.options.status == "active":
                self.options.command("end")
            if self.desk.status != "ended":
                self.desk.command("end")
            if self.second.status != "ended":
                self.second.command("end")
            self.status = "ended"
        else:
            raise ValueError("Unknown risk command")
        return {"ok": True, "message": kind.replace("_", " ") + " updated"}

    def journal(self):
        if self.status != "ended":
            raise ValueError("End the risk session before exporting market seeds")
        body = {
            "schema": "quantlab-risk-v1",
            "versions": risk_versions(),
            "baseline": self.baseline,
            "initial_settings": asdict(self.initial_settings),
            "actions": self.actions,
            "final": self.state(),
            "evidence": {
                "options": self.options.evidence,
                "stock": self.options.stock.evidence,
                "desk": self.desk.evidence,
                "second": self.second.evidence,
            },
        }
        return plain(body | {"digest": digest(body)})


def replay_risk(raw, *, frames=False):
    if not isinstance(raw, dict) or set(raw) != {
        "schema",
        "versions",
        "baseline",
        "initial_settings",
        "actions",
        "final",
        "evidence",
        "digest",
    }:
        raise ValueError("Invalid risk journal schema")
    body = {k: v for k, v in raw.items() if k != "digest"}
    if raw["schema"] != "quantlab-risk-v1" or digest(body) != raw["digest"]:
        raise ValueError("Risk journal integrity mismatch")
    if raw["versions"] != risk_versions():
        raise ValueError("Risk replay requires recorded versions")
    if len(raw["actions"]) > 3001:
        raise ValueError("Risk replay action budget exceeded")
    b = raw["baseline"]
    o = OptionsSession(OptionsConfig(**b["options_config"]))
    d = TradingSession(scenario_from_dict(b["desk_scenario"]), b["desk_mode"])
    for session, actions in ((o, b["options_actions"]), (d, b["desk_actions"])):
        if len(actions) > 20000:
            raise ValueError("Risk baseline action budget exceeded")
        for a in actions:
            if plain(session.command(a["kind"], **a["payload"])) != a["result"]:
                raise ValueError("Baseline account replay mismatch")
    s = RiskSession(o, d, settings=RiskSettings(**raw["initial_settings"]))
    public_frames = ReplayFrames([s.state()]) if frames else []
    for action in raw["actions"]:
        s.execute(action["target"], action["kind"], **copy.deepcopy(action["payload"]))
        if s.actions[-1] != action:
            raise ValueError("Risk action/result/frame replay mismatch")
        if frames:
            public_frames.append(s.state())
    if s.journal() != raw:
        raise ValueError("Risk account evidence replay mismatch")
    return s, public_frames
