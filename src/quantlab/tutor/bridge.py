"""Local application boundary. Tutor failures never become exchange failures."""

import copy
import threading
from pathlib import Path

from quantlab.tutor.adapters import research_contexts
from quantlab.tutor.progress import Progress
from quantlab.tutor.service import Tutor


class Learning:
    def __init__(self, path=None, research_directory=None):
        self.lock = threading.RLock()
        self.path = Path(path) if path is not None else None
        self.research_directory = Path(
            research_directory or Path.cwd() / "docs/learning/phase_05"
        )
        self.error = None
        self.tutor = None
        try:
            self.tutor = Tutor(Progress(path))
        except (ValueError, OSError) as exc:
            self.error = str(exc)

    def _healthy(self):
        if self.error or self.tutor is None:
            raise ValueError(
                "Learning progress unavailable. Trading is unaffected. "
                "Export/preserve the local file and reset learning explicitly."
            )

    def observe(self, snapshot, source, *, order_submitted=False, new_session=False):
        with self.lock:
            if self.error or self.tutor is None:
                return
            try:
                if new_session:
                    self.tutor.active = None
                if order_submitted:
                    self.tutor.trading_result(snapshot, source)
                self.tutor.observe(snapshot, source)
            except Exception as exc:
                # Do not repair/retry or roll the exchange back. Learning has its own error.
                self.error = (
                    f"Learning stopped: {type(exc).__name__}. Trading remains available."
                )

    def state(self):
        with self.lock:
            if self.error:
                return {"error": self.error, "enabled": False, "current": None}
            return copy.deepcopy(self.tutor.view())

    def observe_derivatives(
        self,
        snapshot,
        source,
        event_type="observation",
        *,
        solver=None,
        mc=None,
        new_session=False,
    ):
        from quantlab.tutor.derivatives import derivative_context

        with self.lock:
            if self.error or self.tutor is None:
                return
            try:
                if new_session:
                    self.tutor.active = None
                    previous = [
                        k for k, c in self.tutor.contexts.items() if c.kind == "derivatives"
                    ]
                    for key in previous:
                        self.tutor.contexts.pop(key)
                        self.tutor.progress.data["contexts"].pop(key, None)
                    self.tutor.seen.clear()
                self.tutor.observe_derivative(
                    derivative_context(snapshot, source, event_type, solver=solver, mc=mc)
                )
                if new_session:
                    self.tutor._persist()
            except Exception as exc:
                self.error = (
                    f"Learning stopped: {type(exc).__name__}. Trading remains available."
                )

    def observe_risk(self, snapshot, source, *, new_session=False):
        from quantlab.tutor.risk import risk_context

        with self.lock:
            if self.error or self.tutor is None:
                return
            try:
                if new_session:
                    self.tutor.active = None
                    # A new consolidated session/replay supersedes every live desk context.
                    # Keep answer evidence and mastery, but no later-frame question context.
                    self.tutor.contexts.clear()
                    self.tutor.progress.data["contexts"].clear()
                    self.tutor.seen.clear()
                self.tutor.observe_derivative(risk_context(snapshot, source))
                if new_session:
                    self.tutor._persist()
            except Exception as exc:
                self.error = (
                    f"Learning stopped: {type(exc).__name__}. Trading remains available."
                )

    def observe_statarb(self, snapshot, source, *, new_session=False):
        from quantlab.tutor.statarb import statarb_context

        with self.lock:
            if self.error or self.tutor is None:
                return
            try:
                if new_session:
                    self.tutor.active = None
                    # A new consolidated session/replay supersedes every live desk context.
                    # Keep answer evidence and mastery, but no later-frame question context.
                    self.tutor.contexts.clear()
                    self.tutor.progress.data["contexts"].clear()
                    self.tutor.seen.clear()
                self.tutor.observe_derivative(statarb_context(snapshot, source))
                if new_session:
                    self.tutor._persist()
            except Exception as exc:
                self.error = (
                    f"Learning stopped: {type(exc).__name__}. Trading remains available."
                )

    def dashboard(self):
        with self.lock:
            self._healthy()
            return copy.deepcopy(self.tutor.progress.dashboard())

    def exports(self, markdown=False):
        with self.lock:
            self._healthy()
            return copy.deepcopy(self.tutor.progress.export(markdown))

    def experiments(self):
        return [
            {"id": name, "title": title}
            for name, title in (
                ("development", "Phase 5 · fixed vs inventory · 1,600 development sessions"),
                ("evaluation", "Phase 5 · already inspected evaluation results"),
                ("sensitivity", "Phase 5 · registered parameter sensitivity"),
            )
            if (self.research_directory / name / "experiment.json").is_file()
        ]

    def command(self, raw, snapshot, source):
        with self.lock:
            kind, payload = raw.get("kind"), raw.get("payload", {})
            if not isinstance(payload, dict):
                raise ValueError("Tutor payload must be an object")
            if kind == "reset":
                if payload != {"confirmation": "RESET LEARNING"}:
                    raise ValueError(
                        "Type RESET LEARNING to clear only local learning progress"
                    )
                # Preserve an unreadable file before an explicitly requested reset.
                if self.error and self.path and self.path.exists():
                    backup = self.path.with_suffix(self.path.suffix + ".unreadable")
                    if backup.exists():
                        raise ValueError(
                            "Preserved unreadable backup already exists; move it "
                            "before resetting"
                        )
                    self.path.rename(backup)
                if self.tutor is None or self.error:
                    self.tutor = Tutor(Progress(self.path))
                self.tutor.reset()
                self.error = None
                return self.state()
            self._healthy()
            tutor = self.tutor
            fields = {
                "answer": {"question_id", "answer"},
                "hint": set(),
                "explain": set(),
                "deeper": set(),
                "quiz": {"concept", "mode"},
                "predict": set(),
                "configure": {"enabled", "event_gap", "max_attempts"},
                "review": set(),
                "research": {"experiment", "variant", "concept"},
            }
            if kind not in fields or set(payload) - fields[kind]:
                raise ValueError("Unknown tutor command or fields")
            if not tutor.progress.data["settings"]["enabled"] and kind not in (
                "configure",
                "review",
            ):
                raise ValueError("Tutor is disabled; enable it before answering")
            try:
                if kind == "answer":
                    result = tutor.answer(payload["question_id"], payload["answer"])
                elif kind == "hint":
                    result = tutor.hint()
                elif kind in ("explain", "deeper"):
                    result = tutor.explain(deeper=kind == "deeper")
                elif kind == "quiz":
                    result = tutor.ask(**payload)
                elif kind == "predict":
                    from quantlab.tutor.context import trading_contexts

                    context = trading_contexts(snapshot, source)[0]
                    if snapshot["status"] == "ended" or context.facts["ask"] is None:
                        raise ValueError("Prediction needs an active public book with an ask")
                    result = tutor.ask("limit_orders", context=context, prediction=True)
                elif kind == "configure":
                    result = tutor.configure(**payload)
                elif kind == "review":
                    return {"review": tutor.review(snapshot, source)}
                else:
                    if payload.get("experiment") not in {e["id"] for e in self.experiments()}:
                        raise ValueError("Select an available verified Phase 5 experiment")
                    contexts = research_contexts(
                        self.research_directory / payload["experiment"]
                    )
                    variants = [c.facts["variant"] for c in contexts]
                    if "variant" in payload:
                        contexts = tuple(
                            c for c in contexts if c.facts["variant"] == payload["variant"]
                        )
                    if not contexts:
                        raise ValueError("Unknown experiment variant")
                    result = tutor.study(contexts, payload.get("concept"))
                    return {
                        **result,
                        "research": [c.public() for c in contexts],
                        "variants": variants,
                    }
                return copy.deepcopy(result)
            except OSError as exc:
                self.error = (
                    f"Learning storage failed: {type(exc).__name__}. Trading remains available."
                )
                raise ValueError(self.error) from exc
