"""Maker-specific presentation over generic, immutable experiment outcomes."""

from fractions import Fraction
from pathlib import Path

from quantlab.research.analysis import rows_for
from quantlab.research.reporting import pyplot


def markout_coverage(record):
    result = {}
    for variant in record["spec"]["variants"]:
        rows = rows_for(record, variant["name"])
        tick = Fraction(variant["configuration"]["market"]["tick_size"])
        groups = {}
        for row in rows:
            for h, coverage in row["coverage"]["markouts"].items():
                group = groups.setdefault(
                    h,
                    {
                        "available_units": 0,
                        "missing_units": 0,
                        "pending_units": 0,
                        "weighted_sum": Fraction(0),
                    },
                )
                for key in ("available_units", "missing_units", "pending_units"):
                    group[key] += coverage[key]
                group["weighted_sum"] += Fraction(coverage["weighted_sum_ticks"]) * tick
        result[variant["name"]] = {
            h: {
                **g,
                "pooled_mean": float(g["weighted_sum"] / g["available_units"])
                if g["available_units"]
                else None,
            }
            for h, g in groups.items()
        }
    return result


def plot_sweep(record, path: str | Path, *, parameter=("strategy", "inventory_skew_ticks")):
    points = []
    for variant in record["spec"]["variants"]:
        setting = variant["configuration"]
        for key in parameter:
            setting = setting[key]
        points.append((float(Fraction(setting)), variant["name"]))
    points.sort()
    parameter_label = {
        ("strategy", "inventory_skew_ticks"): "Inventory sensitivity k (ticks/unit)",
        ("strategy", "half_spread_ticks"): "Quote half-spread (ticks)",
        ("strategy", "soft_limit"): "Soft inventory limit (units)",
        ("market", "latent_sigma_ticks"): "Latent volatility (ticks / sqrt(second))",
        ("market", "signal_noise_ticks"): "Signal noise (ticks)",
        ("market", "informed_rate_per_second"): "Informed arrivals per second",
    }.get(tuple(parameter), parameter[-1].replace("_", " "))
    plt = pyplot()
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
    risk_metric = (
        "maximum_drawdown" if parameter[0] == "market" else "average_absolute_inventory"
    )
    risk_label = (
        "Mean maximum drawdown (GBP)"
        if parameter[0] == "market"
        else "Mean absolute inventory (units)"
    )
    for ax, metric, label in zip(
        axes.flat,
        ("net_pnl", risk_metric, "fill_rate", "markout_1"),
        (
            "Mean P&L (GBP)",
            risk_label,
            "Mean posted-unit fill rate",
            "Mean available 1-event markout (GBP/unit)",
        ),
        strict=True,
    ):
        x = []
        y = []
        low = []
        high = []
        for setting, name in points:
            s = record["analysis"]["variants"][name]["distributions"][metric]
            if s["mean"] is None:
                continue
            x.append(setting)
            y.append(s["mean"])
            ci = s["mean_ci"]
            low.append(s["mean"] - ci["low"] if ci else 0)
            high.append(ci["high"] - s["mean"] if ci else 0)
        ax.errorbar(x, y, yerr=[low, high], fmt="o-", capsize=4, color="#176b91")
        ax.set(xlabel=parameter_label, ylabel=label)
        ax.grid(alpha=0.2)
        if metric in ("net_pnl", "markout_1"):
            ax.axhline(0, color="#888888", linestyle=":")
    fig.suptitle(
        f"Parameter sweep · {record['spec']['seeds']['runs']} "
        f"{record['spec']['seeds']['pool']} sessions/value\n"
        "Marginal 95% t intervals; exploratory trade-offs, no optimum selected"
    )
    fig.savefig(path, dpi=160)
    plt.close(fig)
