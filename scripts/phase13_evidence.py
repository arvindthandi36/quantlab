"""Deterministic Phase 13 acceptance demonstrations and measured local timings."""

import argparse
import csv
import io
import json
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

from quantlab.environments.application import research_summary
from quantlab.environments.data import load_csv
from quantlab.environments.explanation import explain
from quantlab.environments.fixtures import fixture_inputs, fixtures
from quantlab.environments.historical import HistoricalSession, replay_historical
from quantlab.environments.research import compare_scenarios, historical_study
from quantlab.environments.scenarios import ScenarioSession, replay_scenario
from quantlab.research.codec import digest
from quantlab.trading.server import Controller


def manual_fixture():
    meta = fixture_inputs(2)[0]["metadata"]
    text = (
        "timestamp,open,high,low,close,volume\n"
        + "\n".join(
            f"2020-01-02T09:{30 + i}:00+00:00,{p},100.20,99.80,{p},20"
            for i, p in enumerate(("100", "100.05", "100.02", "100.08", "100.03"))
        )
        + "\n"
    )
    return load_csv(text, meta | {"instrument": "TEACHING-FIXTURE"})


def measured(fn):
    start = time.perf_counter()
    result = fn()
    return result, round((time.perf_counter() - start) * 1000, 3)


def run(destination):
    destination.mkdir(parents=True, exist_ok=True)
    d = manual_fixture()
    s = HistoricalSession([d])
    timeline = []

    def point(event):
        p = s.public()
        timeline.append(
            {
                "event": event,
                "index": s.index,
                "close": p["observations"][s.instruments[0]][-1]["close"],
                "account": p["account"],
                "orders": p["orders"],
            }
        )

    point("09:30 first bar revealed; future bars withheld")
    s.command("order", instrument=s.instruments[0], side="buy", quantity=3)
    point("09:30 market buy 3 accepted; no same-bar fill")
    s.command("step")
    point("09:31 volume budget 2; buy 2 at 100.06; one unit cancels")
    s.command(
        "order",
        instrument=s.instruments[0],
        side="sell",
        quantity=1,
        order_type="limit",
        price="100.04",
    )
    s.command("step")
    point("09:32 sell candidate 100.01 fails limit; high 100.20 does not trigger it")
    s.command("step")
    point("09:33 sell candidate 100.07 satisfies limit; one unit executes")
    public_explanation = explain(s.public(), "vwap")
    tutor = Controller().environments.tutor
    question = tutor.ask(s.public())["current"]["question"]
    s.command("step")
    point("09:34 last close 100.03; remaining long unit marked; session ends")
    replay, frames = replay_historical(s.journal(), [d])
    rejected = False
    try:
        altered = load_csv(d.csv_text.replace("100.05", "100.06"), d.meta)
        replay_historical(s.journal(), [altered])
    except ValueError:
        rejected = True
    pairs = fixtures()
    a = HistoricalSession(pairs)
    a.command("step", count=40)
    # Modify ALL future records; this independent script also checks the test's central claim.
    changed = []
    for dataset in pairs:
        rows = list(csv.DictReader(io.StringIO(dataset.csv_text)))
        for i, row in enumerate(rows):
            if i > 40:
                price = 200 + i % 10
                row.update(
                    open=str(price),
                    close=str(price + 1),
                    high=str(price + 3),
                    low=str(price - 2),
                    volume=str(i * 13),
                    timestamp=(
                        datetime.fromisoformat(row["timestamp"]) + timedelta(days=10)
                    ).isoformat(),
                )
        stream = io.StringIO()
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
        changed.append(load_csv(stream.getvalue(), dataset.meta))
    b = HistoricalSession(changed)
    b.command("step", count=40)
    assert digest(a.public()) == digest(b.public())
    known = ScenarioSession("normal", steps=20)
    for side in ("buy", "sell"):
        known.command("order", side=side, quantity=1, order_type="market")
    known.command("step", count=20)
    hidden = ScenarioSession("liquidity_shock", seed=42, hidden=True, steps=40)
    before = hidden.public()
    hidden.command("step", count=20)
    after = hidden.public()
    hidden.command("step", count=20)
    h_replay, _ = replay_scenario(hidden.journal())
    root = Path(tempfile.mkdtemp(prefix="quantlab-phase13-evidence-"))
    comparison = compare_scenarios(root / "scenarios", runs=3, seconds=10)
    study = historical_study(pairs, root / "historical", training_end=30, evaluation_end=80)
    assert comparison["status"] == study["status"] == "complete"
    big = fixture_inputs(5000)[0]
    bigdata, load_ms = measured(lambda: load_csv(big["csv_text"], big["metadata"]))
    p = HistoricalSession([bigdata])
    _, playback_ms = measured(lambda: [p.command("step") for _ in range(100)])
    p.command("end")
    _, replay_ms = measured(lambda: replay_historical(p.journal(), [bigdata]))
    _, snapshot_ms = measured(lambda: [p.public() for _ in range(20)])
    hub = Controller().environments

    def switch():
        for _ in range(20):
            hub.choose("SCENARIO", scenario="normal")
            hub.choose("SYNTHETIC")

    _, switch_ms = measured(switch)
    result = {
        "disclosure": (
            "Artificial test fixtures only. No real historical market data is bundled."
        ),
        "manual_timeline": timeline,
        "execution_explanation": public_explanation,
        "tutor_question_no_answer_submitted": question,
        "dataset_fingerprint": d.fingerprint,
        "historical_final_digest": digest(s.public()),
        "historical_replay_verified": digest(replay.public()) == digest(s.public()),
        "historical_frame_count": len(frames),
        "modified_dataset_rejected": rejected,
        "future_mutation": {
            "t": 40,
            "public_digest": digest(a.public()),
            "mutated_public_digest": digest(b.public()),
            "changed_fingerprints": [x.fingerprint for x in changed],
        },
        "known_scenario_challenge": known.challenge(),
        "hidden_before": {
            "environment": before["environment"],
            "depths": [m["depth"] for m in before["core"]["markets"]],
        },
        "hidden_after_observation_20": {
            "environment": after["environment"],
            "depths": [m["depth"] for m in after["core"]["markets"]],
        },
        "hidden_reveal": hidden.reveal()["configuration"],
        "hidden_replay_verified": digest(h_replay.public()) == digest(hidden.public()),
        "scenario_comparison": research_summary(root / "scenarios"),
        "historical_study": research_summary(root / "historical"),
        "performance_ms": {
            "load_5000_bars": load_ms,
            "100_progressive_steps": playback_ms,
            "step_average": round(playback_ms / 100, 3),
            "replay_102_frames": replay_ms,
            "20_public_snapshots": snapshot_ms,
            "40_environment_switches": switch_ms,
        },
        "browser_payload_bytes_at_100": len(json.dumps(p.public()).encode()),
        "research_directory": str(root),
    }
    for name, value in [
        ("demo.json", result),
        ("historical_journal.json", s.journal()),
        ("hidden_journal.json", hidden.journal()),
    ]:
        (destination / name).write_text(json.dumps(value, indent=2) + "\n")
    sample = destination.parent / "sample"
    sample.mkdir(exist_ok=True)
    (sample / "artificial_fixture.csv").write_text(d.csv_text)
    (sample / "artificial_fixture.metadata.json").write_text(
        json.dumps(d.meta, indent=2) + "\n"
    )
    print(
        json.dumps(
            {
                k: result[k]
                for k in (
                    "dataset_fingerprint",
                    "historical_replay_verified",
                    "modified_dataset_rejected",
                    "known_scenario_challenge",
                    "performance_ms",
                    "browser_payload_bytes_at_100",
                    "research_directory",
                )
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("docs/markets/evidence"))
    run(parser.parse_args().output)
