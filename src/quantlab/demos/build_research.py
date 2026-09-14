"""Bounded, cached Phase 5 experiments; predetermined seeds, no attractive-outcome search."""

import copy
import tempfile
from functools import lru_cache
from pathlib import Path

from quantlab.demos import SEED
from quantlab.demos.models import Evidence, Moment, choice
from quantlab.demos.projections import calculation
from quantlab.research.adapters.control import GaussianControl
from quantlab.research.codec import plain
from quantlab.research.lessons import selection_demo
from quantlab.research.seeds import SeedPlan
from quantlab.research.statistics import paired_analysis, summarise

NOTE = "Equal-skill Gaussian statistical control; synthetic payoff units, NOT trading P&L."


@lru_cache(maxsize=1)
def selection():
    with tempfile.TemporaryDirectory(prefix="quantlab-demo-selection-") as parent:
        path = Path(parent) / "control"
        result = selection_demo(
            path, root=SEED, variants=50, development_runs=40, evaluation_runs=400
        )
        import json

        lock = json.loads((path / "selection-before-evaluation.json").read_text())
        evaluation = json.loads((path / "evaluation" / "registration.json").read_text())
        return result, {
            "selection_lock": lock,
            "evaluation_design": evaluation["design_digest"],
            "evaluation_seeds": evaluation["simulation_seeds"],
            "root": SEED,
            ("note"): (
                "Existing selection_demo writes selection-before-evaluation.json "
                "before execute(evaluation)."
            ),
        }


@lru_cache(maxsize=1)
def controls():
    adapter = GaussianControl()
    seeds = SeedPlan(SEED, "development", 400).seeds()
    a = [
        adapter.run(s, {"variant_id": "A", "mean": 0.0, "sd": 1.0}).metrics["net_pnl"]
        for s in seeds
    ]
    b = [
        adapter.run(s, {"variant_id": "B", "mean": 0.0, "sd": 1.0}).metrics["net_pnl"]
        for s in seeds
    ]
    other = SeedPlan(SEED, "development", 400, start=400).seeds()
    unpaired = [
        adapter.run(s, {"variant_id": "B", "mean": 0.0, "sd": 1.0}).metrics["net_pnl"]
        for s in other
    ]
    return a, b, unpaired


def build(spec, branch="full"):
    if spec.builder == "winner":
        data, proof = selection()
        before = calculation(
            {
                "variants": 50,
                "true_expected_payoff_per_variant": 0.0,
                "development_runs": 40,
                "evaluation_runs": 400,
                "root_seed": SEED,
                ("selection_rule"): (
                    "Highest development mean, original registration order breaks ties"
                ),
            },
            note=NOTE,
        )
        development = calculation(
            {
                k: copy.deepcopy(data[k])
                for k in (
                    "selected_variant",
                    "selection_rule",
                    "development",
                    "all_development_means",
                )
            },
            note=NOTE + " Winner locked before evaluation.",
            charts=(
                {
                    "title": "50 equal-skill variants: development means",
                    "x": "Registered variant",
                    "y": "Mean payoff",
                    "series": [
                        {
                            "name": "Development",
                            "points": [
                                [i, v]
                                for i, v in enumerate(data["all_development_means"].values())
                            ],
                        }
                    ],
                },
            ),
        )
        final = calculation(
            data,
            note=NOTE + " " + data["interpretation"],
            charts=(
                {
                    "title": "Locked winner on untouched evaluation",
                    "x": "0: development · 1: evaluation",
                    "y": "Mean payoff",
                    "series": [
                        {
                            "name": "Observed means",
                            "points": [
                                [0, data["development"]["mean"]],
                                [1, data["evaluation"]["mean"]],
                            ],
                        }
                    ],
                },
            ),
        )
        moments = [
            Moment(
                "develop",
                "Test the registered alternatives",
                "Run 50 equal-skill variants on development seeds",
                "selection_bias",
                before,
                development,
                choice(
                    "selection_bias",
                    (
                        "If all variants have true mean zero, must their observed "
                        "averages all be zero?"
                    ),
                ),
                capture_after="winner-before-test",
            ),
            Moment(
                "evaluate",
                "Keep the winner fixed",
                "Evaluate the locked winner on untouched evaluation seeds",
                "selection_bias",
                development,
                final,
                choice(
                    "selection_bias",
                    "Does the largest development average establish a persistent advantage?",
                ),
                result_note=(
                    "All 50 means remain visible. Compare the locked winner’s "
                    "development and evaluation results. Selection favours lucky "
                    "estimates; deterioration is expected across repetitions, not "
                    "guaranteed on every path."
                ),
                capture_after="winner-after-test",
            ),
        ]
        return Evidence(
            spec,
            moments,
            {"root": SEED, "variants": 50, "development_runs": 40, "evaluation_runs": 400},
            (NOTE, data["limitations"], data["interpretation"]),
            private=proof,
        )
    a, b, independent = controls()
    before = calculation({"first_run": a[0], "true_mean": 0.0, "seed": SEED}, note=NOTE)
    if spec.builder == "precision":
        after = calculation(
            {str(n): plain(summarise(a[:n])) for n in (25, 100, 400)},
            note=NOTE
            + (
                " Nested prefixes overlap; SD describes outcomes, SE describes "
                "uncertainty in the mean."
            ),
            charts=(
                {
                    "title": "400 independent control outcomes",
                    "x": "Run",
                    "y": "Payoff",
                    "series": [
                        {"name": "Control A", "points": [[i, v] for i, v in enumerate(a)]}
                    ],
                },
            ),
        )
        q = choice(
            "standard_error",
            (
                "Does increasing the run count necessarily reduce the variability "
                "of an individual run?"
            ),
        )
        concept = "standard_error"
        action = "Summarise 25, 100 and 400 complete control runs"
    else:
        after = calculation(
            {
                "paired_weather": plain(paired_analysis(a, b, seed=SEED, resamples=200)),
                "independent_weather": plain(
                    paired_analysis(a, independent, seed=SEED, resamples=200)
                ),
            },
            note=NOTE
            + (
                " Same run addresses share weather; independent run addresses do "
                "not. CRN can improve precision when it induces positive "
                "covariance; it is not guaranteed for every design."
            ),
        )
        q = choice(
            "common_random_numbers",
            "Does sharing simulated market conditions make two strategies identical?",
        )
        concept = "common_random_numbers"
        action = "Compare differences with shared versus independent weather"
    return Evidence(
        spec,
        [Moment("replicate", "Look beyond one outcome", action, concept, before, after, q)],
        {"seed": SEED, "runs": 400},
        (
            NOTE,
            (
                "Known zero skill, normal payoffs and finite samples; not a "
                "trading strategy validation."
            ),
        ),
    )
