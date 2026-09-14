"""Loopback-only, dependency-free browser adapter; no financial logic in HTTP handlers."""

import argparse
import json
import logging
import secrets
import threading
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from quantlab.jsonio import loads as strict_loads
from quantlab.trading.navigation import page
from quantlab.trading.replay import dumps, loads, replay
from quantlab.trading.scenarios import SCENARIOS, select_scenario
from quantlab.trading.session import TradingSession
from quantlab.tutor.bridge import Learning


class Controller:
    def __init__(self, save_directory=None, *, learning_path=None, research_directory=None):
        self.lock = threading.RLock()
        self.token = secrets.token_urlsafe(32)
        self.session = TradingSession(select_scenario())
        self.frames = None
        self.frame_index = 0
        self.revision = 0
        self.error = None
        self.save_directory = Path(save_directory) if save_directory is not None else None
        self.saved_path = None
        self.learning = Learning(learning_path, research_directory)
        self.learning_source = "session-" + secrets.token_hex(6)
        self.replay_session = None
        self._options_lab = None
        self._risk_lab = None
        self._statarb_lab = None
        self._demo_hub = None
        from quantlab.explainability.service import Explainer

        self.explanations = Explainer(self)
        from quantlab.environments.application import EnvironmentHub

        self.environments = EnvironmentHub(self)
        self.learning.observe(self.state(), self.learning_source)

    @property
    def demos(self):
        if self._demo_hub is None:
            from quantlab.demos.application import DemoHub

            self._demo_hub = DemoHub(self)
        return self._demo_hub

    @property
    def options_lab(self):
        with self.lock:
            if self._options_lab is None:
                from quantlab.options.application import OptionsLab

                self._options_lab = OptionsLab(self.learning)
            return self._options_lab

    @property
    def risk_lab(self):
        with self.lock:
            if self._risk_lab is None:
                from quantlab.risk.application import RiskLab

                self._risk_lab = RiskLab(self)
            return self._risk_lab

    @property
    def statarb_lab(self):
        with self.lock:
            if self._statarb_lab is None:
                from quantlab.statarb.application import StatArbLab

                self._statarb_lab = StatArbLab(self)
            return self._statarb_lab

    def _save_ended(self):
        if self._risk_lab is not None:
            return
        if self.session.status != "ended" or self.saved_path or self.save_directory is None:
            return
        try:
            self.save_directory.mkdir(parents=True, exist_ok=True)
            name = (
                datetime.now(UTC).strftime("session-%Y%m%d-%H%M%S-")
                + secrets.token_hex(4)
                + ".json"
            )
            path = self.save_directory / name
            data = dumps(self.session)
            with path.open("x", encoding="utf-8") as output:
                output.write(data)
            self.saved_path = str(path.resolve())
        except OSError:
            self.error = (
                "Session ended, but automatic saving failed. Download the replay journal."
            )

    def state(self):
        with self.lock:
            state = (
                dict(self.frames[self.frame_index])
                if self.frames is not None
                else self.session.public_snapshot()
            )
            return {
                **state,
                "server_revision": self.revision,
                "server_error": self.error,
                "replay": self.frames is not None,
                "frame_index": self.frame_index,
                "frame_count": len(self.frames) if self.frames is not None else 0,
                "saved_path": Path(self.saved_path).name
                if self.saved_path and self.frames is None
                else None,
            }

    def command(self, raw):
        with self.lock:
            if self.environments.active is not None:
                raise ValueError("Use the active environment's trading controls")
            kind = raw.get("kind")
            payload = raw.get("payload", {})
            if not isinstance(payload, dict):
                raise ValueError("Command payload must be an object")
            if kind in ("new", "load_replay") and self._risk_lab is not None:
                raise ValueError(
                    "Manage shared accounts from the Risk Lab: Report & replay lets you end, "
                    "then choose a new stock-desk mode and open a new risk session"
                )
            if kind == "new":
                # No silent loss of a user's current trading history.
                if self.frames is None and self.session.status not in ("ended", "failed"):
                    if self.session.actions:
                        raise ValueError("End the current session before opening another")
                config = dict(payload)
                mode = config.pop("mode", "free")
                scenario = select_scenario(**config)
                self.session = TradingSession(scenario, mode)
                self.frames = None
                self.replay_session = None
                self.learning_source = "session-" + secrets.token_hex(6)
                self.error = None
                self.saved_path = None
                result = {"ok": True, "message": "New session is paused and ready"}
            elif kind == "load_replay":
                if (
                    self.frames is None
                    and self.session.actions
                    and self.session.status != "ended"
                ):
                    raise ValueError("End the current session before loading replay")
                if set(payload) == {"journal_text"}:
                    if not isinstance(payload["journal_text"], str):
                        raise ValueError("Journal text must be a string")
                    verified = loads(payload["journal_text"], capture_frames=True)
                else:
                    verified = replay(payload, capture_frames=True)
                self.frames, self.frame_index = verified.frames, 0
                self.replay_session = verified
                self.learning_source = "replay-" + secrets.token_hex(6)
                result = {
                    "ok": True,
                    "message": "Replay verified: every execution and account reconciles",
                }
            elif kind == "replay_step":
                if self.frames is None:
                    raise ValueError("Load a replay first")
                index = payload.get("index", self.frame_index + 1)
                if type(index) is not int or not 0 <= index < len(self.frames):
                    raise ValueError("Replay frame outside range")
                self.frame_index = index
                result = {"ok": True, "message": "Verified replay frame"}
            else:
                if self.frames is not None:
                    raise ValueError("Replay is read-only. Open a new session to trade.")
                if kind == "advance":
                    raise ValueError("Automatic advance is reserved for the server clock")
                executor = getattr(self, "risk_execute", self.session.command)
                result = executor(kind, **payload)
            self._save_ended()
            self.revision += 1
            state = self.state()
            self.learning.observe(
                state,
                self.learning_source,
                order_submitted=kind == "order" and result.get("ok", False),
                new_session=kind in ("new", "load_replay"),
            )
            return {"result": result, "state": state}

    def tick(self):
        with self.lock:
            if self.environments.active is not None:
                self.environments.tick()
                return
            if self.frames is None and self.session.status == "running":
                try:
                    executor = getattr(self, "risk_execute", self.session.command)
                    executor("advance", delta_us=250_000)
                    self._save_ended()
                except Exception as exc:
                    self.error = (
                        f"Session stopped: {type(exc).__name__}. Accounting was not repaired."
                    )
                self.revision += 1
                self.learning.observe(self.state(), self.learning_source)

    def tutor_command(self, raw):
        with self.lock:
            if self.environments.active is not None:
                p = raw.get("payload", {})
                if raw.get("kind") == "answer":
                    return self.environments.tutor.answer(self.environments.state(), **p)
                if raw.get("kind") in ("ask", "quiz"):
                    return self.environments.tutor.ask(
                        self.environments.state(), p.get("concept"), p.get("mode", "learn")
                    )
                raise ValueError(
                    "Use the environment tutor and explicit ended-session reveal controls"
                )
            snapshot = self.state()
            if raw.get("kind") == "observer":
                if snapshot["status"] != "ended" or raw.get("payload") != {"reveal": True}:
                    raise ValueError(
                        "Observer-only analysis requires an ended session and explicit reveal"
                    )
                session = self.replay_session if self.frames is not None else self.session
                rows = []
                for record in session.evidence:
                    market = record.get("market")
                    if market:
                        rows.append(
                            {
                                "time_us": record["time_us"],
                                "latent_before_ticks": market["latent_before_ticks"],
                                "latent_after_ticks": market["latent_after_ticks"],
                                "informed_signal": market["informed"]["signal"]
                                if market["informed"]
                                else None,
                                "signal_error_ticks": market["informed"]["error_ticks"]
                                if market["informed"]
                                else None,
                            }
                        )
                # This response never enters Tutor, progress, scores or public snapshots.
                return {
                    "observer_only": rows[:30],
                    "total_records": len(rows),
                    "label": (
                        "OBSERVER ONLY — unavailable at your decision time; ticks, not pounds"
                    ),
                    "note": (
                        "Showing the first 30 records at most. This cannot "
                        "establish decision quality."
                    ),
                }
            return self.learning.command(raw, snapshot, self.learning_source)


class TradingServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, controller=None):
        self.controller = controller or Controller()
        super().__init__(address, Handler)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _valid_host(self):
        port = self.server.server_port
        return self.headers.get("Host") in (f"127.0.0.1:{port}", f"localhost:{port}")

    def _send(
        self, status, body, content_type="application/json; charset=utf-8", *, download=False
    ):
        if status == 200 and isinstance(body, dict):
            try:
                self.server.controller.explanations.record_response(self.path, body)
            except Exception:
                # Explanation retention cannot undo or conceal an executed financial action.
                logging.getLogger(__name__).debug(
                    "Explanation observation unavailable", exc_info=True
                )
        if not isinstance(body, bytes):
            body = json.dumps(body, allow_nan=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; "
            "style-src 'self'; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'",
        )
        if download:
            self.send_header(
                "Content-Disposition", 'attachment; filename="quantlab-session.json"'
            )
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # All live-account reads use the same lock order as multi-lab mutations.
        with self.server.controller.lock:
            return self._get()

    def _get(self):
        if not self._valid_host():
            return self._send(403, {"error": "Loopback Host required"})
        controller = self.server.controller
        try:
            if self.path == "/api/demos/availability":
                return self._send(
                    200, {"available_sessions": controller.demos.available_sessions()}
                )
            if self.path == "/api/demos":
                return self._send(200, controller.demos.state(include_catalogue=True))
            if self.path == "/api/demos/script.md":
                return self._send(
                    200, controller.demos.export().encode(), "text/markdown; charset=utf-8"
                )
            if self.path == "/api/demos/path.json":
                return self._send(200, controller.demos.path_journal())
            if self.path == "/api/environments":
                return self._send(200, controller.environments.catalogue())
            if self.path == "/api/environments/journal":
                return self._send(200, controller.environments.journal(), download=True)
            if controller.environments.active is not None and self.path in (
                "/api/state",
                "/api/options",
                "/api/risk",
                "/api/statarb",
                "/api/options/journal",
                "/api/risk/journal",
                "/api/statarb/journal",
                "/api/journal",
            ):
                raise ValueError(
                    "The active environment has its own compatible observations, risk "
                    "and replay controls on Trading"
                )
            if self.path == "/api/explanations":
                return self._send(200, controller.explanations.catalog())
            if self.path.startswith("/api/explanations/search?"):
                from quantlab.explainability.registry import search

                query = parse_qs(urlsplit(self.path).query)
                return self._send(
                    200,
                    {"results": search(query.get("q", [""])[0], query.get("lab", [None])[0])},
                )
            if self.path == "/api/risk":
                with controller.lock:
                    return self._send(200, controller.risk_lab.state())
            if self.path == "/api/statarb":
                with controller.lock:
                    return self._send(200, controller.statarb_lab.state())
            if self.path == "/api/statarb/journal":
                with controller.lock:
                    return self._send(200, controller.statarb_lab.journal(), download=True)
            if self.path == "/api/risk/journal":
                with controller.lock:
                    return self._send(200, controller.risk_lab.journal(), download=True)
            if self.path == "/api/options":
                return self._send(200, controller.options_lab.state())
            if self.path == "/api/options/journal":
                return self._send(200, controller.options_lab.journal(), download=True)
            if self.path == "/api/tutor":
                if controller.environments.active is not None:
                    return self._send(200, controller.environments.tutor.view())
                return self._send(200, controller.learning.state())
            if self.path == "/api/learning":
                return self._send(200, controller.learning.dashboard())
            if self.path == "/api/learning/export.json":
                return self._send(200, controller.learning.exports())
            if self.path == "/api/learning/export.md":
                return self._send(
                    200,
                    controller.learning.exports(True).encode(),
                    "text/markdown; charset=utf-8",
                )
            if self.path == "/api/learning/experiments":
                return self._send(200, controller.learning.experiments())
            if self.path == "/api/state":
                return self._send(200, controller.state())
            if self.path == "/api/bootstrap":
                return self._send(
                    200,
                    {
                        "token": controller.token,
                        "scenarios": [
                            {"key": s.key, "title": s.title, "objective": s.objective}
                            for s in SCENARIOS.values()
                        ],
                    },
                )
            if self.path == "/api/journal":
                if controller.state()["status"] != "ended":
                    raise ValueError(
                        "Choose the ended frame before exporting private replay evidence"
                    )
                if controller._risk_lab is not None:
                    raise ValueError(
                        "This account is managed by portfolio risk; export the Risk Lab journal"
                    )
                with controller.lock:
                    data = dumps(controller.session)
                return self._send(200, data.encode(), download=True)
            from quantlab.product.pages import PAGES, render

            if self.path in PAGES:
                return self._send(
                    200, page(render(self.path), self.path).encode(), "text/html; charset=utf-8"
                )
            assets = {
                "/product.js": ("product.js", "text/javascript"),
                "/product.css": ("product.css", "text/css"),
                "/demos": ("demos.html", "text/html"),
                "/demos.js": ("demos.js", "text/javascript"),
                "/demos.css": ("demos.css", "text/css"),
                "/markets.js": ("markets.js", "text/javascript"),
                "/markets.css": ("markets.css", "text/css"),
                "/explain": ("explain.html", "text/html"),
                "/explain.js": ("explain.js", "text/javascript"),
                "/explain.css": ("explain.css", "text/css"),
                "/": ("index.html", "text/html"),
                "/research": ("research.html", "text/html"),
                "/navigation.js": ("navigation.js", "text/javascript"),
                "/app.js": ("app.js", "text/javascript"),
                "/style.css": ("style.css", "text/css"),
                "/learning": ("learning.html", "text/html"),
                "/tutor.js": ("tutor.js", "text/javascript"),
                "/tutor.css": ("tutor.css", "text/css"),
                "/options": ("options.html", "text/html"),
                "/options.js": ("options.js", "text/javascript"),
                "/options.css": ("options.css", "text/css"),
                "/statarb": ("statarb.html", "text/html"),
                "/statarb.js": ("statarb.js", "text/javascript"),
                "/statarb.css": ("statarb.css", "text/css"),
                "/risk": ("risk.html", "text/html"),
                "/risk.js": ("risk.js", "text/javascript"),
                "/risk.css": ("risk.css", "text/css"),
            }
            if self.path not in assets:
                return self._send(404, {"error": "Not found"})
            name, mime = assets[self.path]
            if controller.environments.active is not None and self.path in (
                "/",
                "/options",
                "/risk",
                "/statarb",
            ):
                name = "markets.html"
            data = files("quantlab.trading").joinpath("static", name).read_bytes()
            if mime == "text/html":
                data = page(data.decode(), self.path).encode()
            return self._send(200, data, mime + "; charset=utf-8")
        except ValueError as exc:
            return self._send(400, {"error": str(exc)})
        except Exception:
            logging.getLogger(__name__).debug("Local request failed", exc_info=True)
            return self._send(
                500, {"error": "Session failed reconciliation. Open a new session."}
            )

    def do_POST(self):
        origin = self.headers.get("Origin")
        expected = f"http://{self.headers.get('Host')}"
        if (
            not self._valid_host()
            or origin not in (None, expected)
            or self.headers.get("X-QuantLab-Token") != self.server.controller.token
        ):
            return self._send(403, {"error": "Same-origin session token required"})
        if self.path not in (
            "/api/command",
            "/api/tutor",
            "/api/options",
            "/api/risk",
            "/api/statarb",
            "/api/explanations",
            "/api/environments",
            "/api/demos",
        ):
            return self._send(404, {"error": "Not found"})
        try:
            if self.headers.get("Content-Type") != "application/json":
                raise ValueError("JSON commands required")
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 25_000_000:
                raise ValueError("Command size outside limit")

            raw = strict_loads(self.rfile.read(length))
            if not isinstance(raw, dict) or set(raw) - {"kind", "payload"}:
                raise ValueError("Invalid command envelope")
            with self.server.controller.lock:
                if self.server.controller.environments.active is not None and self.path in (
                    "/api/command",
                    "/api/options",
                    "/api/risk",
                    "/api/statarb",
                ):
                    raise ValueError(
                        "Use the selected environment's controls; its accounts cannot be "
                        "mixed with the synthetic labs"
                    )
                before = None
                lab = {
                    "/api/command": "trading",
                    "/api/options": "options",
                    "/api/risk": "risk",
                    "/api/statarb": "statarb",
                }.get(self.path)
                if lab:
                    try:
                        before = self.server.controller.explanations.snapshot(lab)
                        self.server.controller.explanations.observe(lab, before)
                    except Exception:
                        logging.getLogger(__name__).debug(
                            "Pre-action explanation unavailable", exc_info=True
                        )
                result = (
                    self.server.controller.demos.command(raw)
                    if self.path == "/api/demos"
                    else self.server.controller.environments.command(raw)
                    if self.path == "/api/environments"
                    else self.server.controller.explanations.command(raw)
                    if self.path == "/api/explanations"
                    else self.server.controller.statarb_lab.command(raw)
                    if self.path == "/api/statarb"
                    else self.server.controller.risk_lab.command(raw)
                    if self.path == "/api/risk"
                    else self.server.controller.options_lab.command(raw)
                    if self.path == "/api/options"
                    else self.server.controller.tutor_command(raw)
                    if self.path == "/api/tutor"
                    else self.server.controller.command(raw)
                )
                if before is not None:
                    try:
                        self.server.controller.explanations.record_action(
                            self.path, raw, before, result
                        )
                    except Exception:
                        logging.getLogger(__name__).debug(
                            "Quote explanation unavailable", exc_info=True
                        )
            return self._send(200, result)
        except (ValueError, TypeError, KeyError) as exc:
            return self._send(400, {"error": str(exc)})
        except Exception:
            logging.getLogger(__name__).debug("Local request failed", exc_info=True)
            return self._send(
                500,
                {
                    "error": (
                        "Tutor request failed. Trading is unaffected."
                        if self.path in ("/api/tutor", "/api/explanations")
                        else (
                            "Session stopped after an invariant failure. Do not "
                            "continue this session."
                        )
                    )
                },
            )


def main(argv=None):
    parser = argparse.ArgumentParser(description="QuantLab local manual trading simulator")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument(
        "--learning-path", type=Path, default=Path.cwd() / "runs/learning/progress.json"
    )
    parser.add_argument("--debug", action="store_true", help="Local developer tracebacks")
    args = parser.parse_args(argv)
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    if not 1024 <= args.port <= 65535:
        parser.error("Choose a port from 1024 to 65535")
    server = TradingServer(
        ("127.0.0.1", args.port),
        Controller(Path.cwd() / "runs" / "manual", learning_path=args.learning_path),
    )
    stop = threading.Event()

    def clock():
        while not stop.wait(0.25):
            server.controller.tick()

    threading.Thread(target=clock, daemon=True).start()
    from quantlab.product import VERSION

    print(f"QuantLab {VERSION}: http://127.0.0.1:{args.port}/home (Ctrl+C to stop)", flush=True)
    print(
        "Routes: / Trading · /options · /risk · /statarb · /research · /demos · /explain",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        server.server_close()


if __name__ == "__main__":
    main()
