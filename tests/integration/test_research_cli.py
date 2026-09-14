import json

import pytest

from quantlab.research.adapters.control import GaussianControl
from quantlab.research.cli import main, parser
from quantlab.research.codec import read_json
from quantlab.research.engine import execute
from quantlab.research.lessons import (
    RESEARCH_LESSONS,
    precision_experiment,
    predict,
    selection_demo,
    significance_demo,
)
from quantlab.research.reporting import distribution_data, plot_distribution
from tests.integration.test_research_engine import design


def test_discoverable_help_includes_core_research_commands(capsys):
    with pytest.raises(SystemExit) as exc:
        parser().parse_args(["--help"])
    assert exc.value.code == 0
    text = capsys.readouterr().out
    assert all(
        word in text
        for word in ("compare", "sweep", "inspect", "worst", "replay", "selection", "precision")
    )


def test_cli_requires_hypothesis_before_execution(tmp_path):
    with pytest.raises(SystemExit) as exc:
        main(["compare", "--runs", "2", "--out", str(tmp_path / "no")])
    assert exc.value.code == 2 and not (tmp_path / "no").exists()


def test_prediction_hint_retry_does_not_reveal_explanation():
    answers = iter(["quarter", "halve"])
    output = []
    result = predict(RESEARCH_LESSONS[0], read=lambda _: next(answers), write=output.append)
    assert result == ("quarter", "halve")
    assert output[1].startswith("Hint:")
    assert not any("It roughly halves:" in x for x in output)


def test_teaching_compare_order_and_saved_answers(tmp_path):
    answers = iter(["yes", "no"])
    output = []
    path = tmp_path / "compare"
    code = main(
        [
            "compare",
            "--runs",
            "2",
            "--duration",
            "1",
            "--hypothesis",
            "The difference is uncertain.",
            "--out",
            str(path),
            "--teach",
        ],
        read=lambda _: next(answers),
        write=output.append,
    )
    assert code == 0
    text = "\n".join(output)
    assert (
        text.index("PREDICT")
        < text.index("Hint:")
        < text.index("RUN —")
        < text.index("OBSERVE")
        < text.index("INTERPRET")
        < text.index("CRITIQUE")
    )
    assert read_json(path / "teaching.json")["answers_before_run"] == ["yes", "no"]
    assert (path / "distribution.png").stat().st_size > 1000


def test_cli_cancel_before_prediction_starts_no_experiment(tmp_path):
    def end(_):
        raise EOFError

    output = []
    code = main(
        [
            "compare",
            "--runs",
            "2",
            "--hypothesis",
            "h",
            "--out",
            str(tmp_path / "none"),
            "--teach",
        ],
        read=end,
        write=output.append,
    )
    assert code == 130 and not (tmp_path / "none").exists()


@pytest.mark.parametrize(
    "extra",
    [["--runs", "0"], ["--duration", "0"], ["--duration", "nan"], ["--duration", "0.0000001"]],
)
def test_invalid_research_cli_inputs_are_clean_errors(tmp_path, extra):
    output = []
    code = main(
        ["compare", "--hypothesis", "h", "--out", str(tmp_path / "invalid"), *extra],
        write=output.append,
    )
    assert code == 2 and output[-1].startswith("Research error:")


def test_histogram_shared_bins_ecdf_includes_all_ties_and_missing(tmp_path):
    result = execute(design(), GaussianControl(), tmp_path / "source")
    result["runs"][0]["metrics"]["net_pnl"] = None
    result["runs"][2]["metrics"]["net_pnl"] = 0
    result["runs"][4]["metrics"]["net_pnl"] = 0
    data = distribution_data(result, "net_pnl")
    assert data["a"]["count"] == 4 and data["a"]["missing"] == 1
    assert data["a"]["bin_edges"] == data["b"]["bin_edges"]
    assert sum(data["a"]["histogram_counts"]) == 4
    assert data["a"]["ecdf_x"].count(0) == 2
    assert data["a"]["ecdf_y"][-1] == 1
    assert data["a"]["ecdf_x"] == sorted(data["a"]["ecdf_x"])


def test_precision_uses_nested_prefixes_without_new_rng_draws(tmp_path):
    result = execute(design(40), GaussianControl(), tmp_path / "data")
    a = precision_experiment(result, sizes=(10, 20, 40))
    b = precision_experiment(result, sizes=(10, 20, 40))
    assert a == b and a["nested_prefixes"]
    assert a["variants"]["a"]["prefixes"]["10"]["available"] == 10
    with pytest.raises(ValueError):
        precision_experiment(result, sizes=(10, 100))


def test_selection_records_winner_before_evaluation_and_keeps_all_variants(tmp_path):
    result = selection_demo(
        tmp_path / "selection", root=4, variants=5, development_runs=10, evaluation_runs=20
    )
    registration = read_json(tmp_path / "selection" / "selection-before-evaluation.json")
    evaluation = read_json(tmp_path / "selection" / "evaluation" / "registration.json")
    assert registration["selected_variant"] == evaluation["spec"]["variants"][0]
    assert len(result["all_development_means"]) == 5
    winner = max(result["all_development_means"], key=result["all_development_means"].get)
    assert winner == result["selected_variant"]["name"]
    assert result["known_true_mean"] == 0


def test_significance_is_separate_from_practical_effect():
    result = significance_demo()
    tiny = result["tiny_precise"]["analysis"]
    meaningful = result["meaningful_uncertain"]["analysis"]
    assert tiny["p_value_two_sided"] < 0.01
    assert not tiny["mean_exceeds_practical_threshold"]
    assert meaningful["p_value_two_sided"] > 0.05
    assert result["meaningful_uncertain"]["true_effect"] > 0.05


def test_cli_inspect_worst_and_replay(tmp_path):
    out = []
    path = tmp_path / "maker"
    assert (
        main(
            [
                "compare",
                "--runs",
                "3",
                "--duration",
                "2",
                "--hypothesis",
                "h",
                "--out",
                str(path),
            ],
            write=out.append,
        )
        == 0
    )
    assert main(["inspect", str(path)], write=out.append) == 0
    assert main(["worst", str(path), "--count", "1"], write=out.append) == 0
    assert "Run #" in out[-1]
    journal = tmp_path / "run.json"
    assert (
        main(["replay", str(path), "--run", "0", "--out", str(journal)], write=out.append) == 0
    )
    assert json.loads(journal.read_text())["lab_schema_version"] == 1


def test_cli_parameter_sweep_keeps_every_value(tmp_path):
    path = tmp_path / "sweep"
    assert (
        main(
            [
                "sweep",
                "--parameter",
                "k",
                "--values",
                "0,1/2,1",
                "--runs",
                "2",
                "--duration",
                "1",
                "--hypothesis",
                "h",
                "--out",
                str(path),
            ],
            write=lambda _: None,
        )
        == 0
    )
    assert len(read_json(path / "experiment.json")["runs"]) == 6


def test_plot_unavailable_metric_fails_explicitly(tmp_path):
    result = execute(design(), GaussianControl(), tmp_path / "data")
    for row in result["runs"]:
        row["metrics"]["net_pnl"] = None
    with pytest.raises(ValueError, match="no available"):
        plot_distribution(result, tmp_path / "none.png")
