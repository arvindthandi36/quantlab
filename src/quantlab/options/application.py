"""Local Options Lab integration. Financial work remains in reusable Python modules."""

import copy
import json
import secrets
import threading
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from quantlab.jsonio import loads as strict_loads
from quantlab.options.analytics import shock
from quantlab.options.iv import implied_volatility
from quantlab.options.pricing import finite_differences, greeks, parity_residual, price
from quantlab.options.session import OptionsConfig, OptionsSession, replay_options
from quantlab.research.codec import digest
from quantlab.trading.public import research_view


class OptionsLab:
    def __init__(self, learning, *, directory=None):
        self.learning = learning
        self.directory = Path(directory or Path.cwd() / "runs/options")
        self.lock = threading.RLock()
        self.session = OptionsSession()
        self.selected = self.session.selected
        self.source = "options-" + secrets.token_hex(6)
        self.analysis = {}
        self.saved_path = None
        self.save_warning = None
        self.frames = None
        self.frame_index = 0
        self.research = {"status": "idle"}
        self._research_lock = threading.RLock()
        self._research_record = None
        self._teach("new")

    def _snapshot(self):
        return (
            copy.deepcopy(self.frames[self.frame_index])
            if self.frames is not None
            else self.session.snapshot(self.selected, include_curves=True)
        )

    def _teach(self, event_type, *, solver=None, mc=None):
        self.learning.observe_derivatives(
            self._snapshot(),
            self.source,
            event_type,
            solver=solver,
            mc=mc,
            new_session=event_type in ("new", "load_replay"),
        )

    def state(self):
        with self.lock:
            with self._research_lock:
                research = research_view(self.research)
            return self._snapshot() | {
                "analysis": copy.deepcopy(self.analysis),
                "research": research,
                "saved_path": Path(self.saved_path).name if self.saved_path else None,
                "save_warning": self.save_warning,
                "replay": self.frames is not None,
                "frame_index": self.frame_index,
                "frame_count": len(self.frames or []),
            }

    def journal(self):
        if getattr(self, "risk_owner", None) is not None:
            raise ValueError(
                "This account is managed by portfolio risk; export the Risk Lab journal"
            )
        with self.lock:
            if self.frames is not None and self.frames[self.frame_index]["status"] != "ended":
                raise ValueError("Jump to the ended replay frame before exporting its journal")
            return self.session.journal()

    def _save(self):
        if getattr(self, "risk_owner", None) is not None:
            return
        if self.session.status == "ended" and self.saved_path is None and self.frames is None:
            try:
                self.directory.mkdir(parents=True, exist_ok=True)
                p = self.directory / (
                    datetime.now(UTC).strftime("session-%Y%m%d-%H%M%S-")
                    + secrets.token_hex(4)
                    + ".json"
                )
                p.write_text(
                    json.dumps(self.session.journal(), sort_keys=True, indent=2) + "\n"
                )
                self.saved_path = str(p.resolve())
                self.save_warning = None
            except OSError as exc:
                self.save_warning = (
                    f"Session ended correctly, but automatic journal saving failed: {exc}. "
                    "Use Export ended-session replay to download the in-memory journal."
                )

    def command(self, raw):
        if not isinstance(raw, dict) or set(raw) - {"kind", "payload"}:
            raise ValueError("Options command requires kind and payload")
        kind, p = raw.get("kind"), raw.get("payload", {})
        if not isinstance(p, dict):
            raise ValueError("Options payload must be an object")
        with self.lock:
            result = {"ok": True}
            if kind in ("new", "load_replay") and getattr(self, "risk_owner", None) is not None:
                raise ValueError(
                    "Manage shared accounts from the Risk Lab: end, then open a new risk "
                    "session"
                )
            if kind == "new":
                if (
                    self.frames is None
                    and self.session.actions
                    and self.session.status == "active"
                ):
                    raise ValueError("End the current options session before opening another")
                config = OptionsConfig(**p)
                self.session = OptionsSession(config)
                self.selected = self.session.selected
                self.source = "options-" + secrets.token_hex(6)
                self.frames = None
                self.analysis = {}
                self.saved_path = None
                self.save_warning = None
            elif kind == "load_replay":
                if set(p) not in ({"journal"}, {"journal_text"}):
                    raise ValueError("Supply one options journal or its original JSON text")
                if "journal_text" in p:
                    if not isinstance(p["journal_text"], str):
                        raise ValueError("Options journal text must be a string")
                    raw_journal = strict_loads(p["journal_text"])
                else:
                    raw_journal = p["journal"]
                if (
                    self.frames is None
                    and self.session.actions
                    and self.session.status == "active"
                ):
                    raise ValueError("End the current options session before loading replay")
                verified = replay_options(raw_journal, capture_frames=True)
                self.session = verified
                self.frames = verified.frames
                self.frame_index = 0
                self.selected = verified.selected
                self.source = "options-replay-" + digest(raw_journal)[0:12]
                self.analysis = {}
                self.saved_path = None
                self.save_warning = None
            elif kind == "replay_frame":
                if (
                    self.frames is None
                    or set(p) != {"index"}
                    or type(p["index"]) is not int
                    or not 0 <= p["index"] < len(self.frames)
                ):
                    raise ValueError("Choose an available public replay frame")
                self.frame_index = p["index"]
                self.analysis = {}
            elif self.frames is not None:
                raise ValueError(
                    "Replay is read-only; create a new options session to trade or analyse"
                )
            elif kind == "select":
                if set(p) != {"contract_id"} or p["contract_id"] not in self.session.contracts:
                    raise ValueError("Select an available contract")
                self.selected = p["contract_id"]
                self.analysis = {}
            elif kind in ("iv", "mc", "shock", "greek_check"):
                if self.selected not in self.session.quotes:
                    raise ValueError("Choose an unexpired option for model analysis")
                quote = self.session.quotes[self.selected]
                option_type = quote.contract.option_type
                x = quote.inputs
                allowed = {
                    "iv": {"market_price", "initial", "newton_iterations"},
                    "mc": {"paths", "seed"},
                    "shock": {
                        "spot_change",
                        "volatility_change",
                        "elapsed_days",
                        "rate_change",
                    },
                    "greek_check": set(),
                }
                if set(p) - allowed[kind]:
                    raise ValueError("Unknown analysis field")
                if kind == "iv":
                    data = implied_volatility(
                        option_type,
                        x,
                        p.get("market_price", float(quote.midpoint)),
                        initial=p.get("initial", 0.2),
                        newton_iterations=p.get("newton_iterations", 8),
                    ).public()
                elif kind == "mc":
                    from quantlab.options.monte_carlo import monte_carlo_price

                    data = monte_carlo_price(option_type, x, **p)
                elif kind == "shock":
                    data = shock(option_type, x, **p)
                else:
                    data = {
                        "analytic": greeks(option_type, x).public(),
                        "finite_difference": finite_differences(option_type, x).public(),
                        "call": price("call", x),
                        "put": price("put", x),
                        "parity_residual": parity_residual(
                            price("call", x), price("put", x), x
                        ),
                    }
                self.analysis[kind] = {
                    "data": data,
                    "contract_id": self.selected,
                    "quote_revision": self.session.quote_revision,
                }
                self._teach(
                    kind,
                    solver=data if kind == "iv" else None,
                    mc=data if kind == "mc" else None,
                )
                result = {"ok": True, "analysis": data}
            elif kind == "research":
                if set(p) - {"experiment", "runs", "root", "quantity"}:
                    raise ValueError("Unknown research field")
                self._start_research(**p)
            elif kind == "study_research":
                if p:
                    raise ValueError("No fields needed to study the completed experiment")
                from quantlab.tutor.adapters import research_contexts

                with self._research_lock:
                    if self.research["status"] != "complete":
                        raise ValueError("Wait for a complete derivatives experiment")
                    path = self.research["path"]
                with self.learning.lock:
                    self.learning._healthy()
                    self.learning.tutor.study(research_contexts(path))
            else:
                executor = getattr(self, "risk_execute", self.session.command)
                result = executor(kind, **p)
                self.analysis = {}
                self._save()
            if kind not in ("iv", "mc", "shock", "greek_check", "research", "study_research"):
                self._teach(kind)
            return {"result": result, "state": self.state()}

    def _start_research(self, experiment="frequency", runs=32, root=88042, quantity=1):
        from quantlab.options.research import OptionsAdapter
        from quantlab.research.engine import execute
        from quantlab.research.models import ExperimentSpec, Variant
        from quantlab.research.seeds import SeedPlan

        if type(runs) is not int or not 2 <= runs <= 1000:
            raise ValueError("Choose 2–1,000 complete paired paths")
        if experiment not in ("frequency", "volatility"):
            raise ValueError("Choose frequency or volatility experiment")
        selected = self.session.contracts[self.selected]
        cfg = asdict(self.session.config)
        cfg.update(
            strikes=(float(selected.strike_gbp),),
            expiries_days=(float(selected.expiry_years * 365),),
        )
        base = {
            "market": cfg,
            "option_type": selected.option_type.value,
            "strike": float(selected.strike_gbp),
            "expiry_days": float(selected.expiry_years * 365),
            "quantity": quantity,
            "hedge_frequency": 1,
        }
        if experiment == "frequency":
            variants = tuple(
                Variant(f"every-{n}" if n else "no-hedge", base | {"hedge_frequency": n})
                for n in (1, 5, 20, 0)
            )
            hypothesis = (
                "More frequent hedging is expected to reduce interval delta exposure "
                "while increasing execution costs; net P&L need not improve."
            )
        else:
            variants = tuple(
                Variant(
                    f"process-vol-{v:g}",
                    base
                    | {"market": cfg | {"process_volatility": v, "implied_volatility": 0.2}},
                )
                for v in (0.15, 0.2, 0.3)
            )
            hypothesis = (
                "At fixed initial 20% IV, long delta-hedged option outcomes should "
                "depend on realised variance, discrete trading and costs; no guaranteed "
                "ordering per path."
            )
        adapter = OptionsAdapter()
        for variant in variants:
            adapter.validate(variant.configuration)
        spec = ExperimentSpec(
            f"Derivatives {experiment}: fresh sessions with the selected contract",
            hypothesis,
            SeedPlan(root, "development", runs),
            variants,
            adapter.name,
            bootstrap_resamples=500,
            relationships=(("fees", "turnover"),),
        )
        with self._research_lock:
            if self.research["status"] == "running":
                raise ValueError("A registered derivatives experiment is already running")
            path = self.directory / ("research-" + experiment + "-" + secrets.token_hex(6))
            self.research = {
                "status": "running",
                "completed": 0,
                "runs": runs,
                "experiment": experiment,
                "hypothesis": hypothesis,
                "path": str(path.resolve()),
                "quantity": quantity,
            }

        def progress(done, total):
            with self._research_lock:
                self.research.update(completed=done, runs=total)

        def work():
            try:
                record = execute(spec, adapter, path, progress=progress)
                selected_metrics = (
                    "net_pnl",
                    "fees",
                    "gross_hedging_error",
                    "rms_delta",
                    "drawdown",
                    "turnover",
                    "realised_volatility",
                )
                summaries = {
                    name: {k: row["distributions"][k] for k in selected_metrics}
                    for name, row in (record["analysis"] or {}).get("variants", {}).items()
                }
                with self._research_lock:
                    self._research_record = record
                    self.research.update(
                        status=record["status"],
                        summaries=summaries,
                        paired=(record["analysis"] or {}).get("paired", {}),
                        elapsed_seconds=record["elapsed_seconds"],
                        warnings=record["warnings"],
                    )
            except Exception as exc:
                with self._research_lock:
                    self.research.update(status="failed", error=f"{type(exc).__name__}: {exc}")

        threading.Thread(target=work, daemon=True).start()
