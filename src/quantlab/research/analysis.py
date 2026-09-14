"""Distributions and paired inference over complete experiment records."""

from quantlab.research.seeds import derived_seed
from quantlab.research.statistics import (
    bootstrap,
    paired_analysis,
    relationship,
    summarise,
    tail_risk,
)


def rows_for(record: dict, variant: str) -> list[dict]:
    if record["status"] != "complete":
        raise ValueError("incomplete experiment: no survivor-only inference is permitted")
    rows = sorted(
        (r for r in record["runs"] if r["variant"] == variant), key=lambda r: r["run_index"]
    )
    if not rows:
        raise ValueError("unknown or empty variant")
    return rows


def analyse(record: dict) -> dict:
    spec = record["spec"]
    primary = spec["primary_metric"]
    root = spec["seeds"]["root"]
    pool = spec["seeds"]["pool"]
    names = [v["name"] for v in spec["variants"]]
    results = {"variants": {}, "paired": {}}
    for name in names:
        rows = rows_for(record, name)
        keys = set(rows[0]["metrics"])
        if any(set(r["metrics"]) != keys for r in rows):
            raise ValueError("metric schema changed within a variant")
        values = {key: [r["metrics"][key] for r in rows] for key in sorted(keys)}
        if primary not in keys or any(x is None for x in values[primary]):
            raise ValueError("primary outcome must be available for every requested run")
        results["variants"][name] = {
            "distributions": {key: summarise(x) for key, x in values.items()},
            "primary_tail": tail_risk(values[primary]),
            "primary_bootstrap": bootstrap(
                values[primary],
                seed=derived_seed(root, f"bootstrap:{pool}:{name}:{primary}"),
                resamples=spec["bootstrap_resamples"],
            )
            if len(rows) > 1
            else None,
            "correlations": {},
        }
        for first, second in spec["relationships"]:
            if first in keys and second in keys:
                results["variants"][name]["correlations"][f"{first} vs {second}"] = (
                    relationship(values[first], values[second])
                )
    if spec["paired"] and len(names) > 1:
        baseline = rows_for(record, names[0])
        for name in names[1:]:
            other = rows_for(record, name)
            if [(r["run_index"], r["simulation_seed"]) for r in baseline] != [
                (r["run_index"], r["simulation_seed"]) for r in other
            ]:
                raise ValueError("paired run addresses do not align")
            first = [r["metrics"][primary] for r in baseline]
            second = [r["metrics"][primary] for r in other]
            results["paired"][f"{name} minus {names[0]}"] = paired_analysis(
                first,
                second,
                seed=derived_seed(root, f"bootstrap:{pool}:pairs:{name}"),
                resamples=spec["bootstrap_resamples"],
                practical_threshold=spec["practical_threshold"],
            )
    return results


def extremes(
    record: dict,
    variant: str,
    metric: str = "net_pnl",
    *,
    largest: bool = False,
    count: int = 3,
) -> list[dict]:
    if type(count) is not int or count < 1:
        raise ValueError("count must be positive")
    rows = rows_for(record, variant)
    if metric not in rows[0]["metrics"]:
        raise ValueError("unknown metric")
    usable = [r for r in rows if r["metrics"][metric] is not None]
    sign = -1 if largest else 1
    return sorted(usable, key=lambda r: (sign * r["metrics"][metric], r["run_index"]))[:count]
