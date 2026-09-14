"""Rebuild Phase 14 recording outlines and audit evidence from fixed existing engines."""

import json
import time
from pathlib import Path

from quantlab.demos.annotations import select, teach
from quantlab.demos.build_trading import act, order_session
from quantlab.demos.builders import build
from quantlab.demos.exports import compact, script
from quantlab.demos.projections import point
from quantlab.demos.registry import FLAGSHIPS, catalogue
from quantlab.research.codec import digest
from quantlab.trading.replay import journal
from quantlab.trading.server import Controller


def run():
    destination = Path("docs/demos/evidence")
    destination.mkdir(exist_ok=True, parents=True)
    scripts = Path("docs/demos/scripts")
    scripts.mkdir(exist_ok=True, parents=True)
    report = {
        "seed_policy": (
            "Root 140042 predetermined before inspecting outcomes; "
            "existing Phase 10 seeds retained."
        ),
        "catalogue": catalogue(),
        "flagships": {},
        "performance": {},
    }
    for key in FLAGSHIPS:
        start = time.perf_counter()
        e = build(key)
        elapsed = time.perf_counter() - start
        text = script(e)
        (scripts / (key + ".md")).write_text(text)
        report["flagships"][key] = {
            "configuration": e.configuration,
            "verification": e.verification,
            "moments": [
                {
                    "id": m.id,
                    "action": m.action,
                    "before": compact(m.before),
                    "result": compact(m.after),
                    "capture_before": m.capture_before,
                    "capture_after": m.capture_after,
                }
                for m in e.moments
            ],
            "limitations": e.limitations,
            "build_seconds": elapsed,
            "script_bytes": len(text.encode()),
        }
        if key == "picked-off":
            report["flagships"][key]["observer_review"] = e.private["review"]
        if key == "winner":
            report["flagships"][key]["selection_lock"] = e.private
        if key in ("order", "delta-hedge", "historical", "picked-off"):
            (destination / (key + "-journal.json")).write_text(
                json.dumps(e.journal, indent=2) + "\n"
            )
    h = Controller().demos
    h.start("winner")
    start = time.perf_counter()
    h.start("winner")
    report["performance"]["cached_winner_restart_seconds"] = time.perf_counter() - start
    start = time.perf_counter()
    for _ in range(20):
        h.state()
    report["performance"]["mean_before_view_seconds"] = (time.perf_counter() - start) / 20
    s = order_session()
    for _ in range(250):
        act(s, "pause")
    act(s, "order", side="buy", quantity=10, order_type="market")
    act(s, "end")
    raw = journal(s)
    start = time.perf_counter()
    e = teach(raw)
    report["performance"]["genuine_252_action_verify_and_teach_seconds"] = (
        time.perf_counter() - start
    )
    report["performance"]["genuine_journal_bytes"] = len(json.dumps(raw).encode())
    report["performance"]["selected_moments"] = len(e.moments)
    frames = [
        point(
            {
                "revision": i,
                "account": {"total_pnl": str(i % 17 - 8), "position": i % 10},
                "orders": [],
            }
        )
        for i in range(10001)
    ]
    actions = [{"kind": "step", "payload": {"count": 1}}] * 10000
    start = time.perf_counter()
    select(frames, actions)
    report["performance"]["10000_transition_selection_seconds"] = time.perf_counter() - start
    before = json.loads((destination / "core_before.json").read_text())
    after = json.loads((destination / "core_after.json").read_text())
    report["core_before_after_equal"] = before == after
    report["core_fingerprint"] = digest(after)
    (destination / "demo-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                "core_equal": before == after,
                "fingerprint": digest(after),
                "performance": report["performance"],
                "flagships": {
                    k: {
                        "build_seconds": v["build_seconds"],
                        "result_digest": v["verification"]["engine_result_digest"],
                    }
                    for k, v in report["flagships"].items()
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    run()
