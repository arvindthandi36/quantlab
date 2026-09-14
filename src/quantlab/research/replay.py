"""Connect an extreme session's statistics back to verified full event evidence."""

import platform
from pathlib import Path

from quantlab import __version__
from quantlab.research.codec import plain, write_new


def reproduce_run(record: dict, adapter, variant: str, run_index: int):
    if type(run_index) is not int:
        raise ValueError("run index must be an integer")
    if record["versions"]["quantlab"] != __version__ or (
        record["versions"]["python"] != platform.python_version()
    ):
        raise ValueError("exact regeneration requires recorded simulator and Python versions")
    if adapter.name != record["spec"]["adapter"]:
        raise ValueError("incorrect replay adapter")
    matches = [
        r for r in record["runs"] if r["variant"] == variant and r["run_index"] == run_index
    ]
    if len(matches) != 1 or matches[0]["status"] != "complete":
        raise ValueError("exactly one completed run must identify the replay target")
    row = matches[0]
    configuration = next(
        v["configuration"] for v in record["spec"]["variants"] if v["name"] == variant
    )
    outcome = adapter.run(row["simulation_seed"], configuration, full=True)
    if (
        outcome.metrics != row["metrics"]
        or plain(outcome.coverage) != row["coverage"]
        or outcome.trajectory_fingerprint != row["trajectory_fingerprint"]
        or outcome.environment_fingerprint != row["environment_fingerprint"]
    ):
        raise ValueError("extreme-run regeneration differs from saved outcome/evidence")
    return outcome


def save_reproduced_maker(record, variant, run_index, destination):
    from quantlab.market_making.journal import lab_json, replay_lab
    from quantlab.research.adapters.maker import MakerAdapter

    outcome = reproduce_run(record, MakerAdapter(), variant, run_index)
    replayed = replay_lab(outcome.journal)
    if replayed != outcome.journal:
        raise ValueError("full replay differs from regenerated journal")
    path = Path(destination)
    with path.open("x", encoding="utf-8") as target:
        target.write(lab_json(replayed))
    write_new(
        path.with_suffix(".provenance.json"),
        {
            "experiment_outcome_digest": record["outcome_digest"],
            "variant": variant,
            "run_index": run_index,
            "trajectory_fingerprint": outcome.trajectory_fingerprint,
            "verification": (
                "batch metrics/hash matched full regeneration; full journal replay verified"
            ),
        },
    )
    return replayed
