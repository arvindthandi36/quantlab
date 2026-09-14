"""Hypothesis → registration → complete sessions → analysis. No trading-specific imports."""

import importlib.metadata
import platform
import time
from datetime import UTC, datetime
from pathlib import Path

from quantlab import __version__
from quantlab.research.analysis import analyse
from quantlab.research.codec import canonical, digest, plain, read_json, write_new
from quantlab.research.models import ExperimentSpec, SimulationAdapter, spec_from_dict
from quantlab.research.registry import claim_evaluation


def versions() -> dict:
    result = {
        "quantlab": __version__,
        "python": platform.python_version(),
        "platform": platform.platform(),
    }
    for package in ("numpy", "scipy", "matplotlib"):
        try:
            result[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            result[package] = "unavailable"
    return result


def outcome_digest(record: dict) -> str:
    return digest({"spec": record["spec"], "runs": record["runs"], "status": record["status"]})


def execute(
    spec: ExperimentSpec,
    adapter: SimulationAdapter,
    destination: str | Path,
    *,
    evaluation_registry: str | Path | None = None,
    progress=None,
) -> dict:
    # Defensive roundtrip isolates the registered hypothesis/config from caller mutation.
    spec = spec_from_dict(plain(spec))
    if adapter.name != spec.adapter:
        raise ValueError("adapter does not match registered design")
    for variant in spec.variants:
        adapter.validate(variant.configuration)
    if spec.paired:
        keys = [adapter.environment_key(v.configuration) for v in spec.variants]
        if any(key != keys[0] for key in keys):
            raise ValueError("paired CRN design requires identical exogenous configurations")
    if spec.seeds.pool == "evaluation" and evaluation_registry is None:
        raise ValueError("evaluation runs require a persistent exposure registry")
    seeds = spec.seeds.seeds()
    path = Path(destination)
    path.mkdir(parents=True, exist_ok=False)
    registration = {
        "schema_version": 1,
        "spec": plain(spec),
        "design_digest": digest(spec),
        "registered_at": datetime.now(UTC).isoformat(),
        "versions": versions(),
        "simulation_seeds": list(seeds),
    }
    write_new(path / "registration.json", registration)
    notices = []
    if spec.seeds.pool == "evaluation":
        notices = claim_evaluation(evaluation_registry, design_digest=digest(spec), seeds=seeds)
    rows = []
    start = time.perf_counter()
    with (path / "runs.jsonl").open("x", encoding="utf-8") as journal:
        for offset, seed in enumerate(seeds):
            environment = None
            for variant in spec.variants:
                row = {
                    "run_index": spec.seeds.start + offset,
                    "variant": variant.name,
                    "simulation_seed": seed,
                }
                try:
                    outcome = adapter.run(seed, plain(variant.configuration))
                    if spec.primary_metric not in outcome.metrics:
                        raise ValueError("adapter omitted primary outcome")
                    if (
                        spec.paired
                        and environment is not None
                        and (environment != outcome.environment_fingerprint)
                    ):
                        raise ValueError("common-random-number exogenous fingerprint mismatch")
                    environment = outcome.environment_fingerprint
                    row.update(
                        status="complete",
                        metrics=outcome.metrics,
                        coverage=outcome.coverage,
                        environment_fingerprint=outcome.environment_fingerprint,
                        trajectory_fingerprint=outcome.trajectory_fingerprint,
                    )
                except Exception as exc:
                    row.update(status="failed", error=f"{type(exc).__name__}: {exc}")
                rows.append(plain(row))
                journal.write(canonical(row) + "\n")
                journal.flush()
            if progress is not None:
                progress(offset + 1, len(seeds))
    complete = all(r["status"] == "complete" for r in rows)
    result = {
        **registration,
        "status": "complete" if complete else "incomplete",
        "runs": rows,
        "finished_at": datetime.now(UTC).isoformat(),
        "elapsed_seconds": time.perf_counter() - start,
        "warnings": notices,
        "metric_units": {v.name: adapter.metric_units(v.configuration) for v in spec.variants},
        "interpretation": "Pending review against the pre-registered hypothesis.",
        "limitations": list(spec.limitations),
        "analysis": None,
    }
    if complete:
        try:
            result["analysis"] = plain(analyse(result))
            observations = []
            for name, group in result["analysis"]["variants"].items():
                outcome = group["distributions"][spec.primary_metric]
                loss_fraction = group["primary_tail"]["probability_below"]["0.0"]
                observations.append(
                    f"{name}: observed mean {spec.primary_metric}={outcome['mean']:.6g}; "
                    f"losing/negative outcomes {loss_fraction:.1%}."
                )
            result["interpretation"] = " ".join(observations) + (
                " Compare the full distributions and paired uncertainty with the original "
                "hypothesis. These conditional model outcomes do not establish real-world "
                "alpha, safety or an optimal parameter. Interpretation remains reviewable."
            )
        except Exception as exc:
            result["status"] = "incomplete"
            result["warnings"].append(
                f"Analysis failed; no inference: {type(exc).__name__}: {exc}"
            )
    result["outcome_digest"] = outcome_digest(result)
    result["record_digest"] = digest(result)
    write_new(path / "experiment.json", result)
    from quantlab.research.reporting import render_report

    (path / "summary.md").write_text(render_report(result), encoding="utf-8")
    return result


def load_experiment(path: str | Path) -> dict:
    path = Path(path)
    if path.is_dir():
        path /= "experiment.json"
    raw = read_json(path)
    if type(raw.get("schema_version")) is not int or raw["schema_version"] != 1:
        raise ValueError("unsupported research schema")
    claimed = raw.pop("record_digest")
    if digest(raw) != claimed:
        raise ValueError("experiment record integrity mismatch")
    raw["record_digest"] = claimed
    spec = spec_from_dict(raw["spec"])
    if digest(spec) != raw["design_digest"] or outcome_digest(raw) != raw["outcome_digest"]:
        raise ValueError("registered design or outcome digest mismatch")
    seeds = spec.seeds.seeds()
    if list(seeds) != raw["simulation_seeds"]:
        raise ValueError("saved seeds differ from registered derivation")
    expected = [
        (spec.seeds.start + i, v.name, seed)
        for i, seed in enumerate(seeds)
        for v in spec.variants
    ]
    actual = [(r["run_index"], r["variant"], r["simulation_seed"]) for r in raw["runs"]]
    if actual != expected:
        raise ValueError("missing, duplicated or reordered requested runs")
    if raw["status"] == "complete" and any(r["status"] != "complete" for r in raw["runs"]):
        raise ValueError("failed sessions cannot form a complete experiment")
    return raw
