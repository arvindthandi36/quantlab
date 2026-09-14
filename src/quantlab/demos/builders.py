"""Dispatch small adapters; never change the personal lab or its random generators."""

from quantlab.demos import (
    build_calculations,
    build_environments,
    build_options,
    build_research,
    build_trading,
)
from quantlab.demos.registry import REGISTRY
from quantlab.research.codec import digest


def build(demo_id, branch="full"):
    if demo_id not in REGISTRY:
        raise ValueError("Choose a registered demo")
    if branch not in ("full", "partial", "none"):
        raise ValueError("Unknown hedge branch")
    spec = REGISTRY[demo_id]
    if spec.builder in ("order", "partial", "queue", "long_short", "skew"):
        fn = build_trading.build
    elif spec.builder in ("picked_off", "synthetic"):
        fn = build_trading.market
    elif spec.builder in ("delta", "solver", "option_inputs"):
        fn = build_options.build
    elif spec.builder in ("winner", "precision", "crn"):
        fn = build_research.build
    elif spec.builder in ("historical", "scenario", "hidden"):
        fn = build_environments.build
    else:
        fn = build_calculations.build
    evidence = fn(spec, branch)
    if not spec.flagship and evidence.moments:
        evidence.moments[0].concept = spec.concepts[0]
    evidence.verification = {
        "engine_result_digest": digest([m.after for m in evidence.moments]),
        "journal_digest": digest(evidence.journal) if evidence.journal else None,
        "adapter": spec.builder,
        "note": "Derived from the existing engines; configuration chosen before outcomes.",
    }
    return evidence
