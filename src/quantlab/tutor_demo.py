"""Reproducible Phase 7 teaching evidence, using a separate demonstration learner."""

import argparse
import copy
import json
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

from quantlab.research.codec import digest
from quantlab.trading.replay import dumps, loads
from quantlab.trading.scenarios import select_scenario
from quantlab.trading.session import TradingSession
from quantlab.tutor.adapters import research_contexts
from quantlab.tutor.progress import Progress
from quantlab.tutor.service import Tutor


class DemoCalendar:
    def __init__(self):
        self.now = datetime(2026, 9, 11, 12, tzinfo=UTC)

    def __call__(self):
        return self.now


def demonstrate(research_path=None):
    calendar = DemoCalendar()
    with tempfile.TemporaryDirectory(prefix="quantlab-tutor-demo-") as directory:
        path = Path(directory) / "learning.json"
        t = Tutor(Progress(path, clock=calendar))
        session = TradingSession(select_scenario(seed=42, duration_seconds=5))
        source = "demonstration-session"
        t.observe(session.public_snapshot(), source)
        result = session.command("order", side="buy", order_type="market", quantity=6)
        t.observe(session.public_snapshot(), source)
        original = copy.deepcopy(t.view()["current"])
        wrong = copy.deepcopy(t.answer(t.active["id"], "mid")["current"])
        corrected = copy.deepcopy(t.answer(t.active["id"], "weighted")["current"])

        # A fresh Tutor instance reads persisted progress. Market state is independent.
        t = Tutor(Progress(path, clock=calendar))
        restored_attempts = t.progress.record_for("vwap")["attempts"]
        calendar.now += timedelta(days=3)
        due = copy.deepcopy(t.progress.due())
        revisit = copy.deepcopy(t.ask("vwap")["current"])
        repeated = copy.deepcopy(t.answer(t.active["id"], "mid")["current"])
        t.explain()

        # Assessment of the prerequisite unlocks a calculation challenge.
        t.ask("liquidity")
        t.answer(t.active["id"], "orders")
        interview = copy.deepcopy(t.ask("vwap", mode="interview")["current"])
        delayed = copy.deepcopy(t.answer(t.active["id"], "100.01667")["current"])
        debrief = copy.deepcopy(t.explain()["current"])
        defence = copy.deepcopy(t.ask("architecture", mode="defence")["current"])
        t.answer(t.active["id"], "ui")
        t.explain()

        session.command("step_interval", delta_us=1_000_000)
        t.observe(session.public_snapshot(), source)
        session.command("end")
        t.observe(session.public_snapshot(), source)
        review = t.review(session.public_snapshot(), source)
        journal = dumps(session)
        assert loads(journal).evidence == session.evidence

        baseline = TradingSession(select_scenario(seed=42, duration_seconds=5))
        baseline.command("order", side="buy", order_type="market", quantity=6)
        baseline.command("step_interval", delta_us=1_000_000)
        baseline.command("end")
        assert dumps(baseline) == journal

        research = None
        if research_path is not None:
            contexts = research_contexts(research_path)
            t.study(contexts)
            question = copy.deepcopy(t.view()["current"])
            hint = copy.deepcopy(t.answer(t.active["id"], "sd")["current"])
            t.answer(t.active["id"], "se")
            research = {
                "summaries": [c.public()["facts"] for c in contexts],
                "question": question,
                "hint": hint,
            }

        exported = t.progress.export()
        serial = json.dumps(exported, sort_keys=True)
        for key in (
            "latent_after_ticks",
            "signal_error_ticks",
            "next_event_time_us",
            "informed_arrival",
            "simulation_seed",
        ):
            assert key not in serial
        return {
            "learner": "Demonstration only; not Arvind's mastery record",
            "seed": 42,
            "market_duration_used_us": session.now_us,
            "order": result,
            "question": original,
            "wrong_answer": wrong,
            "corrected_answer": corrected,
            "restored_attempts": restored_attempts,
            "due_after_three_days": due,
            "revisited_question": revisit,
            "repeated_error": repeated,
            "interview": interview,
            "interview_before_debrief": delayed,
            "interview_debrief": debrief,
            "project_defence": defence,
            "session_review": review,
            "research": research,
            "learning_export": exported,
            "privacy": "No observer fields in learning export",
            "market_independence": {
                "identical_journals": True,
                "evidence_digest": digest(session.evidence),
                "replay_verified": True,
            },
            "revision_notes": t.progress.export(True),
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional local evidence directory")
    parser.add_argument(
        "--research", type=Path, default=Path.cwd() / "docs/learning/phase_05/development"
    )
    args = parser.parse_args()
    result = demonstrate(args.research)
    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "demo.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n"
        )
        (args.output / "revision.md").write_text(result["revision_notes"])
    print(result["learner"])
    print("LIVE:", result["order"]["message"])
    print("WRONG:", result["wrong_answer"]["feedback"])
    print("EXPLAIN:", result["corrected_answer"]["question"]["layers"]["maths"])
    print("RESTART:", result["restored_attempts"], "VWAP attempts restored")
    print(
        "REVISIT:", len(result["due_after_three_days"]), "concept due after three learning days"
    )
    print(
        "INTERVIEW: level",
        result["interview"]["question"]["difficulty"],
        "; debrief hidden until requested",
    )
    print("SESSION:", result["session_review"]["what_happened"])
    if result["research"]:
        for summary in result["research"]["summaries"]:
            print(
                "RESEARCH:",
                summary["variant"],
                "n",
                summary["n"],
                "mean",
                round(summary["mean"], 6),
                "SE",
                round(summary["se"], 6),
                summary["unit"],
            )
    print("CHECK:", result["privacy"])
    print("CHECK: identical market journals with/without tutoring; recorded replay verified")


if __name__ == "__main__":
    main()
