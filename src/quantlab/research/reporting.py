"""Readable reports and standalone scientific plots of all observed outcomes."""

import math
import os
import tempfile
from pathlib import Path

import numpy as np

from quantlab.research.analysis import extremes, rows_for
from quantlab.research.codec import write_new


def number(value):
    return "unavailable" if value is None else f"{value:.6g}"


def render_report(record: dict) -> str:
    spec = record["spec"]
    lines = [
        "# QuantLab synthetic research experiment",
        "",
        spec["question"],
        "",
        "**Prediction registered before execution:** " + spec["hypothesis"],
        "",
        f"Status: {record['status']}. Pool: {spec['seeds']['pool']}. "
        f"Sessions per variant: {spec['seeds']['runs']}. "
        f"Root seed: {spec['seeds']['root']}.",
        "",
        "Synthetic performance is not evidence of real-world alpha.",
        "",
    ]
    if record["analysis"] is None:
        lines += ["Incomplete: inference disabled; every attempted row is retained.", ""]
    else:
        for variant in spec["variants"]:
            name = variant["name"]
            result = record["analysis"]["variants"][name]
            lines += [
                f"## {name}",
                "",
                "| Metric | Unit | Available/total | Mean | Median | SD | SE "
                "| P05 | P25 | P75 | P95 |",
                "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
            for key, s in result["distributions"].items():
                entries = [
                    number(s[k])
                    for k in (
                        "mean",
                        "median",
                        "standard_deviation",
                        "standard_error",
                        "p05",
                        "p25",
                        "p75",
                        "p95",
                    )
                ]
                lines.append(
                    f"| {key} | {record['metric_units'][name].get(key, 'unspecified')} | "
                    f"{s['available']}/{s['requested']} | " + " | ".join(entries) + " |"
                )
            primary = result["distributions"][spec["primary_metric"]]
            lines += [
                "",
                f"Mean interval: {primary['mean_ci']}",
                f"Bootstrap: {result['primary_bootstrap']}",
                f"Lower tail: {result['primary_tail']}",
                "",
                "Exploratory correlations (not causal effects):",
                "",
            ]
            for key, value in result["correlations"].items():
                lines.append(f"- {key}: {value}")
            lines += ["", "Worst primary outcomes:", ""]
            for row in extremes(record, name, spec["primary_metric"]):
                lines.append(
                    f"- Run #{row['run_index']}: "
                    f"{number(row['metrics'][spec['primary_metric']])}; "
                    f"simulation seed {row['simulation_seed']}"
                )
            lines.append("")
        for name, result in record["analysis"]["paired"].items():
            lines += [
                f"## Paired: {name}",
                "",
                f"Summary: {result['summary']}",
                f"Bootstrap: {result['bootstrap']}",
                f"Positive / negative / tied: {result['proportion_positive']:.3%} / "
                f"{result['proportion_negative']:.3%} / {result['proportion_zero']:.3%}.",
                f"t = {number(result['t_statistic'])}; "
                f"two-sided p = {number(result['p_value_two_sided'])}; "
                f"paired standardised effect = {number(result['standardised_paired_effect'])}.",
                result["note"],
                "",
            ]
    lines += ["## Interpretation", "", record["interpretation"], "", "## Limitations", ""]
    lines += ["- " + line for line in record["limitations"] + record["warnings"]]
    lines += [
        "",
        "Quantiles use linear interpolation; SD uses n−1. Markout distributions use "
        "per-session available-unit means, with session and unit coverage retained. "
        "A confidence interval concerns the model's mean, not the range of future outcomes.",
        "",
    ]
    return "\n".join(lines)


def pyplot():
    os.environ.setdefault(
        "MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "quantlab-matplotlib")
    )
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    return plt


def distribution_data(record: dict, metric: str) -> dict:
    values = {}
    for v in record["spec"]["variants"]:
        rows = rows_for(record, v["name"])
        if metric not in rows[0]["metrics"]:
            raise ValueError("unknown distribution metric")
        x = np.array([r["metrics"][metric] for r in rows if r["metrics"][metric] is not None])
        values[v["name"]] = x
    nonempty = [x for x in values.values() if len(x)]
    if not nonempty:
        raise ValueError("no available values for this distribution")
    all_values = np.concatenate(nonempty)
    bins = np.histogram_bin_edges(
        all_values, bins=min(40, max(5, math.ceil(math.sqrt(len(all_values)))))
    )
    return {
        name: {
            "count": len(x),
            "missing": record["spec"]["seeds"]["runs"] - len(x),
            "bin_edges": bins.tolist(),
            "histogram_counts": np.histogram(x, bins=bins)[0].tolist(),
            "ecdf_x": np.sort(x).tolist(),
            "ecdf_y": (np.arange(1, len(x) + 1) / len(x)).tolist() if len(x) else [],
        }
        for name, x in values.items()
    }


def plot_distribution(record: dict, path: str | Path, metric="net_pnl") -> dict:
    data = distribution_data(record, metric)
    plt = pyplot()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), constrained_layout=True)
    colours = ("#176b91", "#ce6733", "#56804c", "#865ba6", "#9c8140")
    for index, (name, group) in enumerate(data.items()):
        x = group["ecdf_x"]
        if not x:
            continue
        label = f"{name} (n={len(x)})"
        colour = colours[index % len(colours)]
        axes[0].hist(
            x,
            bins=group["bin_edges"],
            histtype="step",
            linewidth=1.8,
            color=colour,
            label=label,
        )
        axes[1].step([x[0]] + x, [0] + group["ecdf_y"], where="post", label=label, color=colour)
    unit = next(iter(record["metric_units"].values())).get(metric, "units")
    for ax in axes:
        ax.set_xlabel(f"{metric.replace('_', ' ')} ({unit})")
        ax.axvline(0, color="#777777", linestyle=":", linewidth=1)
        ax.grid(alpha=0.18)
        ax.legend(fontsize=8)
    axes[0].set(ylabel="Number of sessions", title="Observed outcomes · shared histogram bins")
    axes[1].set(
        ylabel="Fraction of sessions at or below value",
        ylim=(0, 1.02),
        title="Empirical cumulative distribution",
    )
    fig.suptitle("QuantLab · synthetic outcomes, not evidence of real-world alpha", fontsize=12)
    path = Path(path)
    fig.savefig(path, dpi=160)
    plt.close(fig)
    write_new(path.with_suffix(".data.json"), data)
    return data
