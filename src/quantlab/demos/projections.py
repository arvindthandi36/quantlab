"""Public evidence only. No reference to simulator internals is allowed in this module."""

import copy

from quantlab.environments.explanation import explain as environment_explain
from quantlab.explainability import SCHEMA
from quantlab.explainability.evidence import result
from quantlab.explainability.registry import ASSUMPTIONS, CHAINS, CONCEPTS, DEPTHS, graph

SYNTHETIC_TRUTH = (
    "Orders execute in a synthetic model. Prices and marks are not "
    "promises of real-world fills."
)


def point(core, engine="trading", **extra):
    return {
        "engine": engine,
        "status": core.get("status", "active"),
        "revision": core.get("revision", 0),
        "index": core.get("step", core.get("time_us", core.get("t", 0))),
        "environment": {
            "type": "SYNTHETIC",
            "badge": "SYNTHETIC · SIMULATED EXECUTION",
            "hidden": False,
            "truth": SYNTHETIC_TRUTH,
        },
        "core": copy.deepcopy(core),
        **copy.deepcopy(extra),
    }


def calculation(
    values,
    *,
    label="CALCULATION",
    note="Existing QuantLab calculation; assumptions apply.",
    charts=(),
):
    return {
        "engine": "calculation",
        "status": "active",
        "index": 0,
        "environment": {
            "type": "SYNTHETIC",
            "badge": "SYNTHETIC · " + label,
            "truth": note,
            "hidden": False,
        },
        "calculation": copy.deepcopy(values),
        "charts": copy.deepcopy(charts),
        "note": note,
    }


def explain(snapshot, concept, *, previous=None, depth="beginner", selector=None):
    if concept not in CONCEPTS or depth not in DEPTHS:
        raise ValueError("Choose a registered concept and supported explanation depth")
    if snapshot["engine"] != "calculation":
        dto = environment_explain(
            snapshot,
            concept,
            previous=previous,
            depth=depth,
            selector=selector
            or ("portfolio" if snapshot["engine"] in ("options", "risk") else None),
        )
    else:
        meta = CONCEPTS[concept].public()
        dto = dict(
            schema=SCHEMA,
            concept=meta,
            current=result(
                snapshot["calculation"], inputs=snapshot["calculation"], note=snapshot["note"]
            ),
            depth=depth,
            mode="live",
            label=snapshot["environment"]["badge"],
            environment=snapshot["environment"],
            source={"environment": "synthetic", "point": {"index": snapshot["index"]}},
            change={
                "available": False,
                "before": None,
                "after": snapshot["calculation"],
                "inputs": [],
            },
            dependency_trace=[],
            assumptions=[ASSUMPTIONS[a] for a in meta["assumptions"]],
            selectors=[],
            evidence_labels=[{"type": "CALCULATION", "text": snapshot["note"]}],
        )
    dto["label"] = "SELECTED DEMO / REPLAY POINT · " + snapshot["environment"]["badge"]
    dto["quiz_allowed"] = False  # Explicit demo checkpoints own grading, never the live tutor.
    dto["demo_context"] = True
    return dto


def journey(ids):
    # Use the Phase 12 graph, including intermediate nodes where required.
    edges = [e for i in range(len(CHAINS)) for e in graph(i)["edges"]]
    selected = set(ids)
    return {
        "steps": [{"id": c, "name": CONCEPTS[c].name} for c in ids],
        "edges": [e for e in edges if e["source"] in selected and e["target"] in selected],
        ("note"): (
            "Lesson order follows this demonstration. Arrows from the concept "
            "graph show registered dependencies; they do not prove causation."
        ),
    }


def labelled(snapshot):
    """Add a demo execution label without altering the Phase 13 public contract."""
    s = copy.deepcopy(snapshot)
    if s["engine"] == "historical":
        s["environment"]["badge"] += " · SIMULATED HISTORICAL EXECUTION"
    return s
