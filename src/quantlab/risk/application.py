"""Local risk UI adapter; shares the existing live options and manual desks."""

import copy
import json
from pathlib import Path

from quantlab.jsonio import loads as strict_loads
from quantlab.options.session import OptionsSession
from quantlab.risk.session import RiskSession, replay_risk
from quantlab.trading.public import research_view
from quantlab.trading.scenarios import select_scenario
from quantlab.trading.session import TradingSession


class RiskLab:
    def __init__(self, controller):
        self.controller = controller
        if controller.frames is not None or controller.options_lab.frames is not None:
            raise ValueError("Open live desk sessions before attaching portfolio risk")
        self.frames = None
        self.frame_index = 0
        self.saved_path = None
        self.research = {"status": "idle"}
        self._research_record = None
        self.session = RiskSession(controller.options_lab.session, controller.session)
        self._connect()

    def _connect(self):
        self.controller.risk_execute = lambda kind, **p: self.external("desk", kind, p)
        self.controller.options_lab.risk_execute = lambda kind, **p: self.external(
            "options", kind, p
        )
        self.controller.options_lab.risk_owner = self

    def external(self, target, kind, p):
        if self.frames is not None:
            raise ValueError("Risk replay is read-only")
        response = self.session.execute(target, kind, **p)
        self._teach()
        return response["result"]

    def _teach(self, *, new_session=False):
        learning = self.controller.learning
        if hasattr(learning, "observe_risk"):
            learning.observe_risk(self.state(), "risk-session", new_session=new_session)

    def state(self):
        state = (
            copy.deepcopy(self.frames[self.frame_index])
            if self.frames is not None
            else self.session.state()
        )
        linked = None
        statarb = getattr(self.controller, "_statarb_lab", None)
        if statarb is not None and statarb.frames is None and self.frames is None:
            from quantlab.risk.analytics import FACTORS
            from quantlab.statarb.risk import consolidated

            linked = consolidated(
                self.session.portfolio(),
                FACTORS,
                self.session.covariance
                if self.session.covariance is not None
                else self.session.settings.covariance(),
                statarb.session.market,
                capital=statarb.session.capital,
            )
        return state | {
            "linked_statarb": linked,
            "replay": self.frames is not None,
            "frame_index": self.frame_index,
            "frame_count": len(self.frames or []),
            "saved_path": Path(self.saved_path).name if self.saved_path else None,
            "research": research_view(self.research),
        }

    def journal(self):
        if self.frames is not None and self.frames[self.frame_index]["status"] != "ended":
            raise ValueError("Choose ended replay frame before exporting market seeds")
        return self.session.journal()

    def command(self, raw):
        if not isinstance(raw, dict) or set(raw) - {"kind", "payload"}:
            raise ValueError("Invalid risk command")
        kind, p = raw.get("kind"), raw.get("payload", {})
        if not isinstance(p, dict):
            raise ValueError("Risk payload must be an object")
        with self.controller.lock, self.controller.options_lab.lock:
            if kind == "research":
                return self._research(p)
            if kind == "study_research":
                if self.research.get("status") != "complete":
                    raise ValueError("Complete a registered experiment first")
                from quantlab.tutor.adapters import research_contexts

                with self.controller.learning.lock:
                    self.controller.learning.tutor.study(
                        research_contexts(self.research["path"])
                    )
                return {"result": {"ok": True}, "state": self.state()}
            if kind == "load_replay":
                if self.session.status != "ended":
                    raise ValueError("End the risk session before loading replay")
                if set(p) != {"journal_text"} or not isinstance(p["journal_text"], str):
                    raise ValueError("Supply original journal JSON text")
                verified, frames = replay_risk(strict_loads(p["journal_text"]), frames=True)
                self.session = verified
                self.frames = frames
                self.frame_index = 0
                self._teach(new_session=True)
                return {
                    "result": {"ok": True, "message": "Risk replay verified"},
                    "state": self.state(),
                }
            if kind == "replay_frame":
                i = p.get("index")
                if self.frames is None or type(i) is not int or not 0 <= i < len(self.frames):
                    raise ValueError("Invalid replay frame")
                self.frame_index = i
                self._teach()
                return {"result": {"ok": True}, "state": self.state()}
            if kind == "new":
                if self.session.status != "ended":
                    raise ValueError("End current risk session before replacing accounts")
                if set(p) - {"desk_mode"}:
                    raise ValueError("New risk session accepts only desk_mode")
                self.controller.session = TradingSession(
                    select_scenario(), mode=p.get("desk_mode", "free")
                )
                lab = self.controller.options_lab
                lab.session = OptionsSession()
                lab.frames = None
                lab.selected = lab.session.selected
                lab.analysis = {}
                lab.saved_path = None
                self.session = RiskSession(lab.session, self.controller.session)
                self.frames = None
                self.saved_path = None
                self.frame_index = 0
                self._connect()
                self._teach(new_session=True)
                return {"result": {"ok": True}, "state": self.state()}
            if self.frames is not None:
                raise ValueError("Replay is read-only; open a new risk session")
            if kind == "trade":
                if set(p) != {"target", "command", "fields"}:
                    raise ValueError("Trade requires venue, command and fields")
                response = self.session.execute(p["target"], p["command"], **p["fields"])
            else:
                response = self.session.execute("risk", kind, **p)
            if kind == "end":
                directory = Path.cwd() / "runs/risk"
                directory.mkdir(parents=True, exist_ok=True)
                from quantlab.research.codec import digest

                journal = self.session.journal()
                path = directory / (digest(journal)[:20] + ".json")
                try:
                    path.write_text(json.dumps(journal, indent=2) + "\n")
                    self.saved_path = str(path.resolve())
                except OSError:
                    response["result"]["save_warning"] = (
                        "Session ended; automatic save failed. Download the journal."
                    )
            self._teach()
            return response | {"state": self.state()}

    def _research(self, p):
        import threading
        from datetime import UTC, datetime

        from quantlab.research.engine import execute
        from quantlab.risk.research import RiskAdapter, experiment_spec

        if self.research["status"] == "running":
            raise ValueError("A risk experiment is already running")
        if set(p) - {"experiment", "runs", "root", "pool", "paths"}:
            raise ValueError("Unknown experiment fields")
        runs = p.get("runs", 32)
        if type(runs) is not int or not 2 <= runs <= 1000:
            raise ValueError("Choose 2–1,000 research seeds")
        spec = experiment_spec(**p)
        path = (
            Path.cwd() / "runs/risk/research" / (datetime.now(UTC).strftime("%Y%m%d-%H%M%S-%f"))
        )
        self.research = {
            "status": "running",
            "question": spec.question,
            "hypothesis": spec.hypothesis,
            "completed": 0,
            "total": runs,
        }

        def work():
            try:
                result = execute(
                    spec,
                    RiskAdapter(),
                    path,
                    evaluation_registry=Path.cwd() / "runs/risk/evaluation-registry.jsonl",
                    progress=lambda n, total: self.research.update(completed=n, total=total),
                )
                self._research_record = result
                self.research = {
                    "status": result["status"],
                    "path": str(path / "experiment.json"),
                    "question": spec.question,
                    "hypothesis": spec.hypothesis,
                    "analysis": result.get("analysis"),
                    "warnings": result["warnings"],
                    "elapsed_seconds": result["elapsed_seconds"],
                    "pool": spec.seeds.pool,
                }
            except Exception as exc:
                self.research = {"status": "failed", "message": str(exc)}

        threading.Thread(target=work, daemon=True).start()
        return {
            "result": {
                "ok": True,
                "message": (
                    "Hypothesis registered before outcomes; research uses "
                    "fresh executed portfolios"
                ),
            },
            "state": self.state(),
        }
