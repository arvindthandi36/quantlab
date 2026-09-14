"""Adapters for existing Phase 4 observations and verified Phase 5 results."""

import math
from fractions import Fraction

from quantlab.tutor.context import PublicContext


def research_contexts(path):
    # Optional research dependencies are loaded only when research is opened.
    from quantlab.research.engine import load_experiment
    from quantlab.research.statistics import summarise

    raw = load_experiment(path)
    if raw["status"] != "complete":
        raise ValueError("Incomplete experiment: no survivor-only tutoring statistics")
    metric = raw["spec"]["primary_metric"]
    variants = [v["name"] for v in raw["spec"]["variants"]]
    values = {}
    for name in variants:
        rows = sorted(
            (r for r in raw["runs"] if r["variant"] == name), key=lambda r: r["run_index"]
        )
        sample = [r["metrics"][metric] for r in rows]
        if len(sample) < 2 or any(v is None for v in sample):
            raise ValueError("Tutor needs at least two complete non-missing session outcomes")
        values[name] = sample
    # Recompute from verified run rows; never trust an edited saved summary.
    summaries = {name: summarise(sample) for name, sample in values.items()}
    contexts = []
    first = variants[0]
    for name in variants:
        summary = summaries[name]
        paired_se = unpaired_se = mean_difference = None
        paired = raw["spec"]["paired"] and name != first
        if paired:
            difference = summarise(
                [b - a for a, b in zip(values[first], values[name], strict=True)]
            )
            paired_se, mean_difference = difference.standard_error, difference.mean
            unpaired_se = math.sqrt(
                summaries[first].standard_error ** 2 + summary.standard_error**2
            )
        facts = {
            "variant": name,
            "n": summary.available,
            "mean": summary.mean,
            "sd": summary.standard_deviation,
            "se": summary.standard_error,
            "ci_low": summary.mean_ci.low,
            "ci_high": summary.mean_ci.high,
            "minimum": summary.minimum,
            "maximum": summary.maximum,
            "paired": paired,
            "paired_se": paired_se,
            "unpaired_se": unpaired_se,
            "mean_difference": mean_difference,
            "variant_count": len(variants),
            "metric": metric,
            "unit": raw["metric_units"][name][metric],
            "source_digest": raw["outcome_digest"],
        }
        contexts.append(
            PublicContext("research-" + raw["outcome_digest"][:12], "research", 0, 0, facts)
        )
    return tuple(contexts)


def maker_contexts(observation, *, source, event, hard_limit, tick_size="0.01"):
    """Input is MakerObservation, the same public object supplied to Phase 4 policies."""

    def money(value):
        return str(Fraction(value) * Fraction(tick_size)) if value is not None else None

    account = observation.account
    common = {
        "position": account.inventory,
        "limit": hard_limit,
        "reference": money(observation.reference_ticks),
    }
    bid, ask = observation.best_bid, observation.best_ask
    return (
        PublicContext(
            source,
            "book",
            event,
            observation.time_us,
            common
            | {
                "bid": money(bid),
                "ask": money(ask),
                "spread": money(ask - bid) if bid is not None and ask is not None else None,
            },
        ),
        PublicContext(
            source,
            "quotes",
            event,
            observation.time_us,
            common
            | {
                "bids": [
                    money(q.price_ticks) for q in observation.quotes if q.side.value == "buy"
                ],
                "asks": [
                    money(q.price_ticks) for q in observation.quotes if q.side.value == "sell"
                ],
            },
        ),
        PublicContext(
            source,
            "position",
            event,
            observation.time_us,
            common
            | {
                "realised": money(account.realised_pnl_ticks),
                "unrealised": money(account.unrealised_pnl_ticks),
                "pnl": money(account.total_pnl_ticks),
                "drawdown": None,
            },
        ),
    )
