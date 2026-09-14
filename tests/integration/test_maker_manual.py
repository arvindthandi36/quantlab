import subprocess
import sys
from fractions import Fraction as F

import pytest

from quantlab.maker_demo import manual_session
from quantlab.market.config import SimulationConfig
from quantlab.market_making.config import MakerConfig, Strategy
from quantlab.market_making.journal import replay_lab
from quantlab.tutor.market_making import LESSONS, Prediction


def test_wrong_prediction_gets_hint_retry_and_delayed_explanation():
    prediction = Prediction(LESSONS[0])
    with pytest.raises(ValueError, match="prediction"):
        prediction.explain()
    first = prediction.answer("up")
    assert first.startswith("Hint:") and not prediction.ready
    assert LESSONS[0].explanation not in first
    second = prediction.answer("down")
    assert prediction.ready and prediction.correct
    assert "Down:" not in second
    assert "Down:" in prediction.explain()
    with pytest.raises(ValueError, match="already"):
        prediction.answer("down")


def test_second_wrong_prediction_then_explanation_without_awarding_mastery():
    prediction = Prediction(LESSONS[1])
    prediction.answer("no")
    prediction.answer("no")
    assert prediction.ready and not prediction.correct
    assert prediction.explain().startswith("Reconsider this:")


def test_scripted_manual_teaching_loop_orders_observe_predict_decide_result_explain():
    answers = iter(["up", "down", "invalid", "2 3 1 2", "", "no", "yes", "", "", "rise", ""])
    output = []
    result = manual_session(
        SimulationConfig(informed_rate_per_second=1),
        MakerConfig(strategy=Strategy.MANUAL),
        teach=True,
        read=lambda prompt: next(answers),
        write=output.append,
    )
    text = "\n".join(output)
    assert "Invalid quote input" in text
    assert text.index("OBSERVE") < text.index("PREDICT") < text.index("Hint:")
    assert (
        text.index("Hint:")
        < text.index("DECIDE: posted")
        < text.index("RESULT:")
        < text.index("EXPLAIN:")
    )
    assert text.count("PREDICT:") == text.count("EXPLAIN:") == 3
    assert "latent" not in text.lower() and "signal" not in text.lower()
    for record in result.records:
        if record.request:
            assert record.request.ask_distance_ticks == F(3)
            assert record.request.bid_size == 1
    assert replay_lab(result) == result


def test_manual_quit_does_not_claim_a_completed_run():
    with pytest.raises(EOFError, match="stopped"):
        manual_session(
            SimulationConfig(),
            MakerConfig(strategy=Strategy.MANUAL),
            read=lambda _: "q",
            write=lambda _: None,
        )


def test_cli_demo_and_replay_smoke(tmp_path):
    path = tmp_path / "lab.json"
    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "quantlab.maker_demo",
            "--strategy",
            "inventory",
            "--save",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    replay = subprocess.run(
        [sys.executable, "-m", "quantlab.maker_demo", "--replay", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Total marked P&L" in run.stdout
    assert "Replay verified" in replay.stdout
    assert "signal" not in replay.stdout.lower()


@pytest.mark.parametrize(
    "args",
    [
        ["--teach"],
        ["--manual", "--strategy", "fixed"],
        ["--compare", "--seed", "42"],
        ["--duration", "0"],
        ["--compare", "--runs", "0"],
    ],
)
def test_invalid_cli_combinations_fail_clearly(args):
    run = subprocess.run(
        [sys.executable, "-m", "quantlab.maker_demo", *args], capture_output=True, text=True
    )
    assert run.returncode == 2
    assert "Traceback" not in run.stderr
