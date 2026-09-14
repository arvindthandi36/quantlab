"""One local environment coordinator; the approved synthetic controller remains intact."""

import copy
import secrets
from pathlib import Path

from quantlab import __version__
from quantlab.environments import SCHEMA
from quantlab.environments.contract import MarketEnvironment
from quantlab.environments.data import integer, load_csv
from quantlab.environments.explanation import explain, what_if
from quantlab.environments.fixtures import fixtures
from quantlab.environments.historical import HistoricalSession, replay_historical
from quantlab.environments.learning import EnvironmentTutor
from quantlab.environments.scenarios import SPECS, ScenarioSession, catalog, replay_scenario
from quantlab.research.codec import digest


class EnvironmentHub:
    def __init__(self, controller):
        self.controller = controller
        from quantlab.environments.synthetic import SyntheticEnvironment

        self.synthetic = SyntheticEnvironment(controller)
        self.active: MarketEnvironment | None = None
        self.datasets = {}
        self.frames = None
        self.frame_index = 0
        self.previous = None
        self.observed = None
        self.playing = False
        self.speed = 1
        self.credit = 0
        self.tutor = EnvironmentTutor(controller.learning)
        self.research = {"status": "idle"}
        self.error = None

    def catalogue(self):
        return {
            "schema": SCHEMA,
            "playing": self.playing,
            "speed": self.speed,
            "error": self.error,
            "selected": "SYNTHETIC"
            if self.active is None
            else self.active.public()["environment"]["type"],
            "state": self.state() if self.active is not None else None,
            "scenarios": catalog(),
            "datasets": [
                {
                    "id": k,
                    "instrument": d.meta["instrument"],
                    "source": d.meta["source"],
                    "data_kind": d.meta["data_kind"],
                }
                for k, d in self.datasets.items()
            ],
            "historical_note": (
                "Import local GBP OHLCV plus provenance. The bundled artificial "
                "fixture is not real market history."
            ),
            "research": copy.deepcopy(self.research),
        }

    def state(self):
        if self.active is None:
            return self.synthetic.public()
        state = (
            copy.deepcopy(self.frames[self.frame_index])
            if self.frames is not None
            else self.active.public()
        )
        state.update(
            replay=self.frames is not None,
            frame_index=self.frame_index,
            frame_count=len(self.frames) if self.frames else 0,
        )
        # Playback controls stay outside model fingerprints.
        return state

    def _observe(self):
        s = self.state()
        if self.frames is None and (
            self.observed is None or digest(s) != digest(self.observed)
        ):
            self.previous, self.observed = self.observed, s

    def _can_switch(self):
        if self.active is not None:
            if (
                self.frames is None
                and self.active.status not in ("ended", "failed")
                and self.active.actions
            ):
                raise ValueError(
                    "End this session before switching environments; its trades must "
                    "not disappear"
                )
        elif (
            self.controller._risk_lab is not None
            and self.controller._risk_lab.state()["status"] != "ended"
        ):
            raise ValueError(
                "End the shared Risk Lab session before switching; reload a "
                "separate local session for environment trading"
            )
        elif self.controller.session.actions and self.controller.session.status != "ended":
            raise ValueError("End the synthetic session before switching environments")

    def choose(self, environment, **p):
        self._can_switch()
        if environment == "SYNTHETIC":
            if p:
                raise ValueError("Synthetic setup remains in its existing session controls")
            target = None
        elif environment == "HISTORICAL":
            if set(p) - {"dataset_ids", "execution", "model"}:
                raise ValueError("Unknown historical setup fields")
            ids = p.get("dataset_ids", [])
            if not isinstance(ids, list) or not ids or any(k not in self.datasets for k in ids):
                raise ValueError("Import and select one or two datasets first")
            target = HistoricalSession(
                [self.datasets[k] for k in ids], p.get("execution"), model=p.get("model")
            )
        elif environment == "SCENARIO":
            if set(p) - {"scenario", "hidden", "seed", "steps", "mode"}:
                raise ValueError("Unknown scenario setup fields")
            hidden = p.get("hidden", False)
            if type(hidden) is not bool:
                raise ValueError("Hidden mode must be true or false")
            if hidden:
                if "scenario" in p or "seed" in p:
                    raise ValueError(
                        "Hidden selection is server-owned; omit a known name and seed"
                    )
                key = secrets.choice(tuple(SPECS))
                seed = secrets.randbelow(2**32)
            else:
                key = p.get("scenario", "normal")
                seed = p.get("seed", 42)
            target = ScenarioSession(
                key,
                seed=seed,
                hidden=hidden,
                steps=p.get("steps", 60),
                mode=p.get("mode", "free"),
            )
        else:
            raise ValueError("Choose SYNTHETIC, HISTORICAL or SCENARIO")
        self.active = target
        self.frames = None
        self.frame_index = 0
        self.playing = False
        self.credit = 0
        self.previous = self.observed = None
        self.tutor.active = None
        self.error = None
        if target is not None:
            self._observe()
        return {
            "ok": True,
            "message": "Environment selected. A new account starts at its first observation.",
        }

    def _live(self):
        if self.active is None:
            raise ValueError("Use the existing synthetic desk controls")
        if self.frames is not None:
            raise ValueError("Verified replay is read-only; restart creates a new session")
        if self.error:
            raise ValueError(self.error)

    def act(self, kind, **p):
        self._live()
        self._observe()
        if kind == "step_time" and self.active.engine != "historical":
            seconds = integer(p.get("seconds", 1), "Step time", 1, 200)
            if self.active.engine != "trading":
                raise ValueError("This engine uses model observations; choose Step observation")
            kind, p = "step", {"count": seconds}
        result = self.active.command(kind, **p)
        if self.active.status == "ended":
            self.playing = False
        self._observe()
        return result

    def tick(self):
        if not self.playing or self.frames is not None or self.active is None:
            return
        self.credit += self.speed / 4
        count = int(self.credit)
        self.credit -= count
        if count:
            try:
                self.act("step", count=count)
            except Exception as exc:
                self.playing = False
                self.error = (
                    f"Environment stopped: {type(exc).__name__}; no account repair performed."
                )

    def explain(
        self,
        concept,
        *,
        depth="beginner",
        mode="live",
        selector=None,
        reveal=False,
        source=None,
        **unused,
    ):
        s = self.state()
        if source is not None and source.upper() != s["environment"]["type"]:
            raise ValueError("Explanation source is determined by the active environment")
        if mode == "observer":
            if reveal is not True:
                raise ValueError("Explicit ended-session reveal is required")
            from quantlab.explainability import SCHEMA as EXPLANATION_SCHEMA
            from quantlab.explainability.registry import CONCEPTS, resolve

            observer = self.reveal()
            return {
                "schema": EXPLANATION_SCHEMA,
                "mode": "observer",
                "label": observer["label"],
                "observer": observer,
                "concept": CONCEPTS[resolve(concept)].public(),
                "quiz_allowed": False,
            }
        if self.frames is not None:
            previous = self.frames[self.frame_index - 1] if self.frame_index else None
        else:
            self._observe()
            previous = self.previous
        return explain(s, concept, depth=depth, mode=mode, selector=selector, previous=previous)

    def reveal(self):
        if self.active is None or self.active.engine == "historical":
            raise ValueError("Historical observations have no hidden model truth to reveal")
        if self.state()["status"] != "ended":
            raise ValueError("Select the ended frame before explicit configuration reveal")
        return self.active.reveal()

    def journal(self):
        if self.active is None:
            from quantlab.trading.replay import journal

            if self.controller.state()["status"] != "ended":
                raise ValueError("End the synthetic session before export")
            return {
                "schema": SCHEMA,
                "environment": "SYNTHETIC",
                "quantlab_version": __version__,
                "execution_version": "approved-fifo-core-1.0",
                "timestamp_range_us": [0, self.controller.session.now_us],
                "source": "QuantLab controlled synthetic agents and matching engine",
                "journal": journal(self.controller.session),
            }
        if self.state()["status"] != "ended":
            raise ValueError("Choose the ended frame before exporting private replay metadata")
        return self.active.journal()

    def load_replay(self, raw):
        self._can_switch()
        if not isinstance(raw, dict):
            raise ValueError("Replay must be a JSON object")
        if raw.get("environment") == "HISTORICAL":
            datasets = []
            for row in raw.get("datasets", []):
                matches = [
                    d for d in self.datasets.values() if d.fingerprint == row["fingerprint"]
                ]
                if not matches:
                    raise ValueError(
                        "Dataset fingerprint mismatch: import the exact original data and "
                        "provenance"
                    )
                datasets.append(matches[0])
            session, frames = replay_historical(raw, datasets)
        elif raw.get("environment") == "SCENARIO":
            session, frames = replay_scenario(raw)
        elif raw.get("environment") == "SYNTHETIC":
            if raw.get("schema") != SCHEMA or raw.get("quantlab_version") != __version__:
                raise ValueError("Unsupported synthetic wrapper version")
            from quantlab.trading.replay import replay

            replay(raw["journal"], capture_frames=True)
            if self.controller._risk_lab is not None:
                raise ValueError(
                    "Synthetic replay must be opened outside the shared Risk session"
                )
            self.active = None
            self.frames = None
            return self.controller.command({"kind": "load_replay", "payload": raw["journal"]})[
                "result"
            ]
        else:
            raise ValueError("Choose a supported environment journal")
        self.active, self.frames, self.frame_index = session, frames, 0
        self.playing = False
        self.previous = self.observed = None
        self.tutor.active = None
        return {
            "ok": True,
            "message": (
                "Replay verified against its original data/configuration and "
                "every recorded state"
            ),
        }

    def hook(self):
        if self.frames is None:
            raise ValueError("Load a verified environment replay first")
        s = self.state()
        previous = self.frames[self.frame_index - 1] if self.frame_index else None
        return {
            "schema": SCHEMA,
            "environment": s["environment"],
            "frame_index": self.frame_index,
            "event_type": "public environment transition",
            "pre": previous,
            "post": s,
            "concept_ids": ["current_price", "vwap", "pnl_attribution", "var"],
            "note": (
                "Selected public frame and predecessor only; no later state or "
                "private configuration."
            ),
        }

    def command(self, raw):
        if not isinstance(raw, dict) or set(raw) - {"kind", "payload"}:
            raise ValueError("Invalid environment command envelope")
        kind, p = raw.get("kind"), raw.get("payload", {})
        if not isinstance(p, dict):
            raise ValueError("Environment payload must be an object")
        controls = {
            "pause": set(),
            "restart": set(),
            "replay_hook": set(),
            "load_replay": {"journal"},
            "replay_frame": {"index"},
            "quiz": {"concept", "mode"},
            "answer": {"question_id", "answer"},
            "what_if": {"kind", "inputs"},
        }
        if kind in controls and set(p) - controls[kind]:
            raise ValueError("Unknown environment control fields")
        if kind == "choose":
            result = self.choose(**p)
        elif kind == "import":
            if set(p) != {"csv_text", "metadata"}:
                raise ValueError("Supply CSV text and provenance metadata")
            if len(self.datasets) >= 8:
                raise ValueError("Eight datasets are the local import budget")
            d = load_csv(**{"text": p["csv_text"], "metadata": p["metadata"]})
            key = f"dataset-{len(self.datasets) + 1}"
            self.datasets[key] = d
            result = {
                "ok": True,
                "dataset_id": key,
                "message": "Dataset validated; no bars sent to the browser before selection",
            }
        elif kind == "fixture":
            if p:
                raise ValueError("No fixture parameters")
            if len(self.datasets) > 6:
                raise ValueError("Dataset import budget exceeded")
            ids = []
            for d in fixtures():
                k = f"dataset-{len(self.datasets) + 1}"
                self.datasets[k] = d
                ids.append(k)
            result = {
                "ok": True,
                "dataset_ids": ids,
                "message": (
                    "Artificial test fixture loaded. It is NOT real historical market data."
                ),
            }
        elif kind == "play":
            if p:
                raise ValueError("No play parameters")
            self._live()
            if self.active.status == "ended":
                raise ValueError("Session ended")
            self.playing = True
            result = {"ok": True, "message": "Playback started"}
        elif kind == "pause":
            self.playing = False
            result = {"ok": True, "message": "Playback paused"}
        elif kind == "speed":
            if set(p) != {"observations_per_second"}:
                raise ValueError("Choose observations per second")
            self.speed = integer(p["observations_per_second"], "Playback speed", 1, 10)
            result = {"ok": True}
        elif kind == "restart":
            self._can_switch()
            if self.active is None:
                raise ValueError("Use synthetic session setup")
            if self.active.engine == "historical":
                new = HistoricalSession(
                    self.active._datasets,
                    asdict_execution(self.active),
                    model=self.active.model_config,
                )
            else:
                c = dict(self.active.config)
                if c["hidden"]:
                    c["key"] = secrets.choice(tuple(SPECS))
                    c["seed"] = secrets.randbelow(2**32)
                new = ScenarioSession(**c)
            self.active = new
            self.frames = None
            self.frame_index = 0
            self.credit = 0
            self.error = None
            self.previous = self.observed = None
            self.playing = False
            self.tutor.active = None
            self._observe()
            result = {
                "ok": True,
                "message": (
                    "New session and account at the start. Prior knowledge cannot be "
                    "erased; this is not a blind first trial."
                ),
            }
        elif kind == "load_replay":
            result = self.load_replay(p.get("journal"))
        elif kind == "replay_frame":
            if self.frames is None:
                raise ValueError("Load replay first")
            self.frame_index = integer(p.get("index"), "Replay frame", 0, len(self.frames) - 1)
            self.tutor.active = None
            result = {"ok": True, "message": "Read-only public replay frame"}
        elif kind == "reveal":
            if p != {"confirm": True}:
                raise ValueError("Explicit post-session reveal required")
            return self.reveal()
        elif kind == "explain":
            return self.explain(**p)
        elif kind == "what_if":
            return what_if(self.state(), p["kind"], p.get("inputs", {}))
        elif kind == "quiz":
            return self.tutor.ask(self.state(), p.get("concept"), p.get("mode", "learn"))
        elif kind == "answer":
            return self.tutor.answer(self.state(), p["question_id"], p["answer"])
        elif kind == "replay_hook":
            return self.hook()
        elif kind == "compare":
            from quantlab.environments.research import compare_scenarios

            if self.active is not None and self.state()["status"] != "ended":
                raise ValueError("End the session before starting separate scenario research")
            directory = self._research_directory()
            record = compare_scenarios(directory, **p)
            # Private paths in records remain on disk; the public summary is an allowlist.
            self.research = {
                "status": record["status"],
                "environment": "SCENARIO",
                "experiment_id": directory.name,
                "runs": len(record["runs"]),
                "summary": research_summary(directory),
            }
            result = {
                "ok": True,
                "message": "Registered controlled scenario comparison complete",
            }
        elif kind == "historical_research":
            from quantlab.environments.research import historical_study

            if (
                self.active is None
                or self.active.engine != "historical"
                or self.state()["status"] != "ended"
            ):
                raise ValueError(
                    "Historical full-data research requires an ended imported session"
                )
            directory = self._research_directory()
            record = historical_study(self.active._datasets, directory, **p)
            self.research = {
                "status": record["status"],
                "environment": "HISTORICAL",
                "label": "POST-SESSION FULL-DATA ANALYSIS",
                "runs": len(record["runs"]),
                "experiment_id": directory.name,
                "summary": research_summary(directory),
            }
            result = {
                "ok": True,
                "message": (
                    "Separate registered historical comparison complete; one path is "
                    "not independent trials"
                ),
            }
        else:
            result = self.act(kind, **p)
        return {
            "result": result,
            **self.catalogue(),
            "playing": self.playing,
            "speed": self.speed,
            "error": self.error,
        }

    def _research_directory(self):
        base = (
            self.controller.save_directory.parent
            if self.controller.save_directory
            else Path.cwd() / "runs"
        )
        base = base / "environments"
        base.mkdir(parents=True, exist_ok=True)
        return base / ("study-" + secrets.token_hex(6))


def asdict_execution(s):
    from dataclasses import asdict

    return asdict(s.execution)


def research_summary(directory):
    from quantlab.research.engine import load_experiment

    record = load_experiment(directory)
    return {
        "status": record["status"],
        "paired": record["spec"]["paired"],
        "variants": record.get("analysis", {}).get("variants", {})
        if record.get("analysis")
        else {},
        "outcomes": [
            {k: row[k] for k in ("variant", "status", "metrics", "coverage") if k in row}
            for row in record["runs"]
        ],
        "limitations": record["limitations"],
        "fingerprint": record["outcome_digest"],
    }
