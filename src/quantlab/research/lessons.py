"""First-principles research exercises and recorded, reproducible demonstrations."""

from pathlib import Path

import numpy as np

from quantlab.research.analysis import rows_for
from quantlab.research.codec import plain, write_new
from quantlab.research.engine import execute
from quantlab.research.models import ExperimentSpec, Variant
from quantlab.research.reporting import pyplot
from quantlab.research.seeds import SeedPlan, derived_seed
from quantlab.research.statistics import paired_analysis, summarise
from quantlab.tutor.market_making import Lesson

RESEARCH_LESSONS = (
    Lesson(
        "If independent sessions increase from 100 to 400, does standard error roughly "
        "halve, quarter, or stay the same?",
        ("halve", "half", "halves"),
        "The uncertainty in an average scales with one over the square root of the count.",
        "It roughly halves: sqrt(400/100)=2. Individual-session volatility need not fall.",
    ),
    Lesson(
        "A strategy has higher average P&L across 100 runs. Is that alone enough to "
        "establish it is better? Answer yes or no.",
        ("no", "n"),
        "Consider the uncertainty of the difference and its downside outcomes.",
        "No. Examine paired differences, uncertainty, downside risk and model limitations.",
    ),
    Lesson(
        "You picked the best of 50 noisy variants. Should you expect its development "
        "average to overstate its typical future performance? Answer yes or no.",
        ("yes", "y"),
        "Selection favours variants that received unusually favourable random outcomes.",
        "Yes: the winner can combine skill with unusually good luck. Untouched evaluation "
        "helps reveal that optimism; repeated test-set peeking undermines it.",
    ),
)


def predict(lesson: Lesson, *, read=input, write=print) -> tuple[str, ...]:
    write("PREDICT — " + lesson.question)
    answers = [read("Your prediction: ")]
    if answers[0].strip().lower() not in lesson.accepted:
        write("Hint: " + lesson.hint)
        answers.append(read("Reconsider: "))
    write("Prediction recorded before the run; explanation follows the observations.")
    return tuple(answers)


def precision_experiment(record: dict, *, sizes=(100, 400, 1600)) -> dict:
    if (
        not sizes
        or any(type(n) is not int or n < 2 for n in sizes)
        or tuple(sorted(set(sizes))) != tuple(sizes)
    ):
        raise ValueError("sample sizes must be increasing unique integers of at least two")
    result = {
        "source_outcome_digest": record["outcome_digest"],
        "nested_prefixes": True,
        "note": "Prefixes overlap; they are not independent replications. "
        "SD describes outcomes; SE describes the estimated mean.",
        "variants": {},
    }
    for variant in record["spec"]["variants"]:
        rows = rows_for(record, variant["name"])
        if max(sizes) > len(rows):
            raise ValueError("not enough completed sessions for the declared prefixes")
        values = [r["metrics"][record["spec"]["primary_metric"]] for r in rows]
        result["variants"][variant["name"]] = {
            "prefixes": {str(n): plain(summarise(values[:n])) for n in sizes},
            "running_means": [
                float(x) for x in np.cumsum(values) / np.arange(1, len(values) + 1)
            ],
            "disjoint_block_means": {},
        }
        for size in (25, 100, 400):
            if len(values) // size >= 2:
                block_means = [
                    float(np.mean(values[i : i + size]))
                    for i in range(0, len(values) - size + 1, size)
                ]
                result["variants"][variant["name"]]["disjoint_block_means"][str(size)] = plain(
                    summarise(block_means)
                )
    return result


def plot_precision(result: dict, path: str | Path) -> None:
    plt = pyplot()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
    for name, group in result["variants"].items():
        values = group["running_means"]
        axes[0].plot(np.arange(1, len(values) + 1), values, label=name, alpha=0.85)
        n = sorted(int(x) for x in group["prefixes"])
        se = [group["prefixes"][str(size)]["standard_error"] for size in n]
        axes[1].plot(n, se, "o-", label=name)
    axes[0].set(
        xlabel="Independent sessions included",
        ylabel="Running mean P&L (GBP)",
        title="Sample averages can settle; not monotonically",
    )
    axes[1].set(
        xlabel="Sessions (log scale)",
        ylabel="Estimated standard error (GBP)",
        xscale="log",
        yscale="log",
        title="Uncertainty in the average",
    )
    for ax in axes:
        ax.grid(alpha=0.2)
        ax.legend()
    fig.suptitle("QuantLab · nested prefixes of development sessions")
    fig.savefig(path, dpi=160)
    plt.close(fig)


def selection_demo(
    destination,
    *,
    root=20260911,
    variants=50,
    development_runs=40,
    evaluation_runs=400,
    registry=None,
    progress=None,
) -> dict:
    from quantlab.research.adapters.control import GaussianControl

    if type(variants) is not int or variants < 2:
        raise ValueError("selection demonstration requires multiple variants")
    path = Path(destination)
    path.mkdir(parents=True, exist_ok=False)
    adapter = GaussianControl()
    selection_root = derived_seed(root, "selection-control")
    choices = tuple(
        Variant(f"variant-{i:02d}", {"variant_id": str(i), "mean": 0.0, "sd": 1.0})
        for i in range(variants)
    )
    spec = ExperimentSpec(
        "Can selecting the best of equal-skill variants create apparent skill?",
        "The selected development winner will tend to overstate its untouched evaluation mean; "
        "all variants have known true mean zero. This is a statistical control, not trade P&L.",
        SeedPlan(selection_root, "development", development_runs),
        choices,
        adapter.name,
        paired=False,
        bootstrap_resamples=2000,
    )
    development = execute(spec, adapter, path / "development", progress=progress)
    if development["status"] != "complete":
        raise ValueError("selection control development failed; no winner can be selected")
    # Max ties break by original registration order; evaluation does not exist yet.
    winner = max(
        choices,
        key=lambda v: development["analysis"]["variants"][v.name]["distributions"]["net_pnl"][
            "mean"
        ],
    )
    decision = {
        "selected_variant": plain(winner),
        "development_outcome_digest": development["outcome_digest"],
        "selection_rule": "highest development mean; original order breaks ties",
        "evaluation_runs": evaluation_runs,
    }
    write_new(path / "selection-before-evaluation.json", decision)
    evaluation_spec = ExperimentSpec(
        "Does the development winner retain its measured advantage on untouched sessions?",
        spec.hypothesis,
        SeedPlan(selection_root, "evaluation", evaluation_runs),
        (winner,),
        adapter.name,
        paired=False,
    )
    evaluation = execute(
        evaluation_spec,
        adapter,
        path / "evaluation",
        evaluation_registry=registry or path / "evaluation-access.jsonl",
        progress=progress,
    )
    if evaluation["status"] != "complete":
        raise ValueError("selection control evaluation failed")
    before = development["analysis"]["variants"][winner.name]["distributions"]["net_pnl"]
    after = evaluation["analysis"]["variants"][winner.name]["distributions"]["net_pnl"]
    result = {
        **decision,
        "known_true_mean": 0.0,
        "development": before,
        "evaluation": after,
        "observed_deterioration": before["mean"] - after["mean"],
        "all_development_means": {
            name: x["distributions"]["net_pnl"]["mean"]
            for name, x in development["analysis"]["variants"].items()
        },
        "interpretation": "Selection optimism is expected over repetitions, not guaranteed "
        "in each sample. No root seeds were searched to force deterioration.",
        "limitations": "Gaussian payoffs have known equal true skill; these are not "
        "simulated executions. One demo is not a performance study.",
    }
    write_new(path / "selection-result.json", result)
    plt = pyplot()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
    means = result["all_development_means"]
    axes[0].bar(
        range(len(means)),
        list(means.values()),
        color=["#ce6733" if name == winner.name else "#176b91" for name in means],
    )
    axes[0].set(
        xlabel="Equal-skill variant",
        ylabel="Observed mean payoff",
        title="Select the largest of many noisy means",
    )
    axes[1].bar(
        ["Development winner", "Untouched evaluation"],
        [before["mean"], after["mean"]],
        color=["#ce6733", "#176b91"],
    )
    axes[1].set(ylabel="Mean payoff", title=winner.name + " · true expected payoff = 0")
    for ax in axes:
        ax.axhline(0, color="#555555", linewidth=1)
    fig.suptitle("Selection-bias control · synthetic payoff units, not trading P&L")
    fig.savefig(path / "selection.png", dpi=160)
    plt.close(fig)
    return result


def significance_demo(*, root=20260911) -> dict:
    """Predeclared independent Gaussian effects, not repeated copies of the same data."""
    result = {}
    for label, n, mu, sd in (
        ("tiny_precise", 200_000, 0.001, 0.05),
        ("meaningful_uncertain", 20, 0.10, 0.40),
    ):
        seed = derived_seed(root, "significance:" + label)
        rng = np.random.Generator(np.random.PCG64(seed))
        differences = rng.normal(mu, sd, n)
        result[label] = plain(
            {
                "seed": seed,
                "n": n,
                "true_effect": mu,
                "individual_sd": sd,
                "analysis": paired_analysis(
                    np.zeros(n),
                    differences,
                    seed=derived_seed(seed, "bootstrap"),
                    resamples=200,
                    practical_threshold=0.05,
                ),
            }
        )
    return result
