"""Local application adapter for causal trading, research and verified replay."""

import copy
import json
import threading
from datetime import UTC, datetime
from pathlib import Path

from quantlab.jsonio import loads as strict_loads
from quantlab.research.codec import digest
from quantlab.research.engine import execute
from quantlab.statarb.research import StatArbAdapter, experiment_spec
from quantlab.statarb.session import StatArbSession, replay
from quantlab.trading.public import research_view


class StatArbLab:
    def __init__(self, controller):
        self.controller = controller
        self.session = StatArbSession()
        self.frames = None
        self.frame_index = 0
        self.saved_path = None
        self.research = {"status": "idle"}
        self.examples = None

    def state(self):
        state = (
            copy.deepcopy(self.frames[self.frame_index])
            if self.frames is not None
            else self.session.state()
        )
        return state | dict(
            replay=self.frames is not None,
            frame_index=self.frame_index,
            frame_count=len(self.frames or []),
            saved_path=Path(self.saved_path).name if self.saved_path else None,
            research=research_view(self.research),
            examples=copy.deepcopy(self.examples),
        )

    def journal(self):
        if self.frames is not None and self.frames[self.frame_index]["status"] != "ended":
            raise ValueError("Choose the ended frame before exporting private seeds")
        return self.session.journal()

    def _teach(self, *, new_session=False):
        self.controller.learning.observe_statarb(
            self.state(), "statarb-session", new_session=new_session
        )

    def command(self, raw):
        if not isinstance(raw, dict) or set(raw) - {"kind", "payload"}:
            raise ValueError("Invalid stat-arb command envelope")
        kind, p = raw.get("kind"), raw.get("payload", {})
        if not isinstance(p, dict):
            raise ValueError("Payload must be an object")
        if kind == "diagnostic":
            return self._diagnostic(p)
        if kind == "research":
            return self._research(p)
        if kind == "examples":
            if p:
                raise ValueError("Teaching datasets take no fields")
            from quantlab.statarb.examples import teaching_cases

            self.examples = teaching_cases()
            return dict(
                result={
                    "ok": True,
                    "message": "Completed independent teaching datasets loaded",
                },
                state=self.state(),
            )
        if kind == "study_research":
            from quantlab.tutor.adapters import research_contexts

            if self.research["status"] != "complete":
                raise ValueError("Complete a registered study first")
            with self.controller.learning.lock:
                self.controller.learning.tutor.study(research_contexts(self.research["path"]))
            return dict(result={"ok": True}, state=self.state())
        if kind == "new":
            if self.session.status != "ended" and self.session.actions:
                raise ValueError("End this session before replacing its accounts")
            if set(p) - {
                "scenario_name",
                "steps",
                "rules",
                "depth",
                "fee",
                "spread_ticks",
                "capital",
            }:
                raise ValueError("Unknown new-session field")
            new = StatArbSession(**p)
            self.session, self.frames, self.frame_index, self.saved_path = new, None, 0, None
            self._teach(new_session=True)
            return dict(
                result={"ok": True, "message": "New causal market ready"}, state=self.state()
            )
        if kind == "load_replay":
            if self.session.status != "ended":
                raise ValueError("End the current session before loading replay")
            if set(p) != {"journal_text"} or not isinstance(p["journal_text"], str):
                raise ValueError("Supply original JSON journal text")
            verified, frames = replay(strict_loads(p["journal_text"]), frames=True)
            self.session, self.frames, self.frame_index = verified, frames, 0
            self._teach(new_session=True)
            return dict(
                result={
                    "ok": True,
                    "message": "Replay verified against every action, signal and fill",
                },
                state=self.state(),
            )
        if kind == "replay_frame":
            i = p.get("index")
            if self.frames is None or type(i) is not int or not 0 <= i < len(self.frames):
                raise ValueError("Invalid replay frame")
            self.frame_index = i
            self._teach()
            return dict(result={"ok": True}, state=self.state())
        if self.frames is not None:
            raise ValueError("Replay is read-only; open a new session")
        result = self.session.command(kind, **p)
        if kind == "end" and result["ok"]:
            path = Path.cwd() / "runs/statarb"
            path.mkdir(parents=True, exist_ok=True)
            journal = self.session.journal()
            target = path / (digest(journal)[:20] + ".json")
            try:
                target.write_text(json.dumps(journal, indent=2) + "\n")
                self.saved_path = str(target.resolve())
            except OSError:
                result["message"] += "; automatic save failed, download journal"
        self._teach()
        return dict(result=result, state=self.state())

    def _research(self, p):
        if self.research["status"] == "running":
            raise ValueError("A stat-arb study is already running")
        if set(p) - {"experiment", "runs", "root", "pool"}:
            raise ValueError("Unknown research fields")
        if type(p.get("runs", 16)) is not int or not 2 <= p.get("runs", 16) <= 128:
            raise ValueError("Choose 2–128 independent research seeds")
        spec = experiment_spec(**p)
        directory = (
            Path.cwd()
            / "runs/statarb/research"
            / datetime.now(UTC).strftime("%Y%m%d-%H%M%S-%f")
        )
        self.research = dict(
            status="running",
            question=spec.question,
            hypothesis=spec.hypothesis,
            completed=0,
            total=spec.seeds.runs * len(spec.variants),
        )

        def work():
            try:
                result = execute(
                    spec,
                    StatArbAdapter(),
                    directory,
                    evaluation_registry=Path.cwd() / "runs/statarb/evaluation-registry.jsonl",
                    progress=lambda n, total: self.research.update(completed=n, total=total),
                )
                self.research = dict(
                    status=result["status"],
                    question=spec.question,
                    hypothesis=spec.hypothesis,
                    analysis=result.get("analysis"),
                    warnings=result["warnings"],
                    elapsed_seconds=result["elapsed_seconds"],
                    path=str(directory / "experiment.json"),
                    pool=spec.seeds.pool,
                )
            except Exception as exc:
                self.research = dict(status="failed", message=str(exc))

        threading.Thread(target=work, daemon=True).start()
        return dict(
            result={
                "ok": True,
                "message": (
                    "Study registered before outcomes; all candidates and failures retained"
                ),
            },
            state=self.state(),
        )

    def _diagnostic(self, p):
        if self.research["status"] == "running":
            raise ValueError("Wait for the active study")
        if set(p) != {"experiment"} or p["experiment"] not in ("sweep", "mining", "lookahead"):
            raise ValueError("Choose a named teaching experiment")
        directory = (
            Path.cwd()
            / "runs/statarb/diagnostics"
            / datetime.now(UTC).strftime("%Y%m%d-%H%M%S-%f")
        )
        directory.mkdir(parents=True)
        registration = dict(
            experiment=p["experiment"],
            seed=201042,
            split=160,
            steps=240,
            selection="training only; test never changes choice",
        )
        (directory / "registration.json").write_text(json.dumps(registration, indent=2))
        self.research = dict(status="running", question=p["experiment"], completed=0, total=1)

        def work():
            from quantlab.statarb.research import (
                backtest,
                evaluate_selection,
                generate,
                invalid_lookahead,
                mining_universe,
                select_pair,
                sweep,
            )

            try:
                if p["experiment"] == "lookahead":
                    data, _ = generate(201042, steps=240)
                    output = dict(
                        invalid=invalid_lookahead(data), valid=backtest(data).metrics()
                    )
                else:
                    mining = p["experiment"] == "mining"
                    data, _ = (
                        mining_universe(201042, steps=240)
                        if mining
                        else generate(201042, steps=240)
                    )
                    selection = select_pair(data[:160]) if mining else sweep(data[:160])
                    evaluation = evaluate_selection(
                        data,
                        selection,
                        split=160,
                        registry=Path.cwd() / "runs/statarb/evaluation-registry.jsonl",
                        destination=directory / "holdout",
                        seed=201042,
                        pair=selection["selected"] if mining else None,
                    )
                    output = dict(selection=selection, evaluation=evaluation)
                (directory / "result.json").write_text(json.dumps(output, indent=2))
                self.research = dict(
                    status="complete",
                    question=p["experiment"],
                    diagnostic=output,
                    path=str(directory / "result.json"),
                )
            except Exception as exc:
                self.research = dict(status="failed", message=str(exc), path=str(directory))

        threading.Thread(target=work, daemon=True).start()
        return dict(
            result={"ok": True, "message": "Registered teaching experiment started"},
            state=self.state(),
        )
