import copy
import json
from datetime import UTC, datetime, timedelta

import pytest

from quantlab.tutor.catalog import CONCEPTS
from quantlab.tutor.progress import Progress


class Calendar:
    def __init__(self):
        self.now = datetime(2026, 9, 11, 12, tzinfo=UTC)

    def __call__(self):
        return self.now

    def advance(self, days):
        self.now += timedelta(days=days)


def grade(
    progress,
    *,
    concept="bid",
    correct=True,
    assisted=False,
    fingerprint="a",
    question_id="q1",
    attempt=1,
    revealed=False,
    level=1,
):
    return progress.grade(
        concept=concept,
        question_id=question_id,
        fingerprint=fingerprint,
        correct=correct,
        assisted=assisted,
        attempt=attempt,
        misconception=concept + ":wrong",
        evidence="Selected the opposite side",
        level=level,
        revealed=revealed,
        source="session",
    )


def test_unassessed_means_no_evidence_in_every_domain():
    view = Progress().dashboard()
    assert all(c["category"] == "Not assessed" and c["score"] is None for c in view["concepts"])
    assert all(d["attempts"] == 0 and d["status"] == "Not assessed" for d in view["domains"])
    assert any(not c["implemented"] for c in view["concepts"])
    assert len(view["domains"]) == 11


def test_encounters_and_time_do_not_raise_mastery():
    calendar = Calendar()
    p = Progress(clock=calendar)
    p.encounter("bid")
    calendar.advance(365)
    assert p.status("bid") == {"category": "Not assessed", "score": None}
    assert p.dashboard()["recent"] == []
    assert p.record_for("bid")["encounters"] == 1


@pytest.mark.parametrize(
    "correct,assisted,category,credit,score",
    [
        (True, False, "correct_first", 1, 65),
        (True, True, "correct_after_hint", 0.5, 50),
        (False, False, "incorrect", 0, 35),
    ],
)
def test_transparent_evidence_arithmetic(correct, assisted, category, credit, score):
    p = Progress()
    entry = grade(p, correct=correct, assisted=assisted)
    assert entry["result"] == category and entry["credit"] == credit
    assert p.status("bid")["score"] == score
    assert p.record_for("bid")["attempts"] == 1
    assert p.record_for("bid")[category] == 1


def test_counts_reconcile_across_retries_and_hints():
    p = Progress()
    grade(p, correct=False)
    grade(p, correct=False, attempt=2)
    grade(p, assisted=True, attempt=3)
    item = p.record_for("bid")
    assert (item["attempts"], item["incorrect"], item["correct_after_hint"]) == (3, 2, 1)
    assert item["credits"] == [0, 0, 0.5]
    assert p.status("bid")["category"] == "Beginning"
    assert len(p.dashboard()["mistakes"][0]["questions"]) == 1


def test_repeated_misconception_requires_distinct_questions_not_retries():
    p = Progress()
    grade(p, correct=False)
    grade(p, correct=False, attempt=2)
    assert p.dashboard()["mistakes"][0]["classification"] == "One-off error"
    grade(p, correct=False, question_id="q2")
    mistake = p.dashboard()["mistakes"][0]
    assert mistake["classification"] == "Repeated misconception"
    assert len(mistake["evidence"]) == 2


@pytest.mark.parametrize(
    "assisted,correct,days", [(False, False, 1), (True, True, 2), (False, True, 3)]
)
def test_review_schedule_uses_learning_clock(assisted, correct, days):
    clock = Calendar()
    p = Progress(clock=clock)
    grade(p, assisted=assisted, correct=correct)
    before = copy.deepcopy(p.status("bid"))
    clock.advance(days)
    assert p.due()[0]["concept"] == "bid"
    assert p.status("bid") == before


def test_success_intervals_increase_without_duplicate_credit():
    clock = Calendar()
    p = Progress(clock=clock)
    for index, days in enumerate((3, 7, 14, 30)):
        grade(p, fingerprint=str(index), question_id=str(index))
        assert datetime.fromisoformat(p.record_for("bid")["due"]) - clock.now == timedelta(
            days=days
        )
    score = p.status("bid")
    grade(p, fingerprint="3", question_id="duplicate")
    assert p.status("bid") == score
    assert not p.dashboard()["recent"][-1]["credited"]


def test_due_priority_counts_repetition_and_foundations():
    clock = Calendar()
    p = Progress(clock=clock)
    grade(p, concept="bid", correct=False, question_id="a")
    grade(p, concept="bid", correct=False, question_id="b")
    grade(p, concept="tail_outcomes", correct=False)
    clock.advance(2)
    rows = p.due()
    assert rows[0]["concept"] == "bid" and rows[0]["priority"] > rows[1]["priority"]


def test_difficulty_requires_success_and_assessed_prerequisites():
    p = Progress()
    for n in range(3):
        grade(p, concept="spread", fingerprint=str(n), question_id=str(n))
    assert p.record_for("spread")["level"] == 1
    grade(p, concept="bid")
    grade(p, concept="ask")
    grade(p, concept="spread", fingerprint="new", question_id="new")
    assert p.record_for("spread")["level"] == 2
    grade(p, concept="spread", correct=False, fingerprint="wrong1", question_id="bad1", level=2)
    grade(p, concept="spread", correct=False, fingerprint="wrong2", question_id="bad2", level=2)
    assert p.record_for("spread")["level"] == 1


def test_credit_window_bounded_and_categories_require_evidence():
    p = Progress()
    for n in range(20):
        grade(p, fingerprint=str(n), question_id=str(n))
    assert len(p.record_for("bid")["credits"]) == 10
    assert p.status("bid")["category"] == "Strong"
    assert 0 <= p.status("bid")["score"] <= 100


def test_revealed_answer_never_counts_as_unassisted_success():
    p = Progress()
    grade(p, revealed=True)
    assert p.status("bid")["category"] == "Not assessed"
    assert p.record_for("bid")["correct_after_hint"] == 1


def test_persistence_reset_and_readable_exports(tmp_path):
    path = tmp_path / "learning.json"
    p = Progress(path)
    grade(p, correct=False)
    restored = Progress(path)
    assert restored.data == p.data
    assert restored.export()["learning"]["weak"] == ["bid"]
    markdown = restored.export(True)
    assert "Weak concepts" in markdown and "Strong concepts" in markdown
    assert "Recent questions" in markdown and "Selected the opposite side" in markdown
    restored.reset()
    assert Progress(path).dashboard()["recent"] == []
    assert path.exists()


@pytest.mark.parametrize("corruption", ["{", '{"schema":2}', '{"schema":1,"latent_ticks":123}'])
def test_corrupt_progress_fails_loudly_without_overwriting(tmp_path, corruption):
    path = tmp_path / "learning.json"
    path.write_text(corruption)
    with pytest.raises(ValueError, match="corrupt"):
        Progress(path)
    assert path.read_text() == corruption


def test_accounting_counts_corruption_is_detected(tmp_path):
    p = Progress()
    grade(p)
    p.data["concepts"]["bid"]["attempts"] = 9
    path = tmp_path / "learning.json"
    path.write_text(json.dumps(p.data))
    with pytest.raises(ValueError, match="corrupt"):
        Progress(path)


def test_prerequisite_graph_has_only_known_concepts_and_no_cycles():
    def visit(key, trail):
        assert key not in trail
        for parent in CONCEPTS[key].prerequisites:
            assert parent in CONCEPTS
            visit(parent, trail | {key})

    for key in CONCEPTS:
        visit(key, set())


@pytest.mark.parametrize("value", [[], None, True, "text", 123])
def test_nonobject_progress_cannot_break_the_trading_controller(tmp_path, value):
    from quantlab.trading.server import Controller

    path = tmp_path / "learning.json"
    path.write_text(json.dumps(value))
    controller = Controller(learning_path=path)
    assert controller.learning.state()["error"]
    assert controller.session.status == "paused"
