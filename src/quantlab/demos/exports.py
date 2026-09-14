"""Deterministic Markdown recording outlines: central explanations, actual evidence."""

import json

from quantlab.demos.projections import explain


def trim(v):
    if isinstance(v, dict):
        return {
            k: trim(x)
            for k, x in v.items()
            if k not in ("prices", "returns", "residual", "z", "all_development_means")
        }
    if isinstance(v, (list, tuple)):
        return [trim(x) for x in v[:8]]
    return v


def compact(snapshot):
    c = snapshot.get("core", snapshot)
    if snapshot["engine"] == "calculation":
        values = c["calculation"]
        # Keep a readable script; the complete state remains available in the viewer.
        return trim(values)

    keys = {
        "trading": (
            "time_us",
            "best_bid",
            "best_ask",
            "last_price",
            "account",
            "orders",
            "markouts",
        ),
        "options": ("step", "spot", "selected", "greeks", "accounts", "hedges"),
        "historical": ("index", "timestamp", "account", "orders", "fills", "risk"),
        "statarb": ("t", "signal", "portfolio", "pending", "last_result"),
        "risk": ("portfolio", "report", "last_result"),
    }.get(snapshot["engine"], ())
    return {k: c[k] for k in keys if k in c}


def script(e, branch="full"):
    lines = [
        "# " + e.spec.title,
        "",
        e.spec.environment,
        "",
        "## SETUP",
        "",
        e.spec.description,
        "",
        json.dumps(e.configuration, sort_keys=True, ensure_ascii=False),
        "",
        "Initial hedge branch: "
        + branch
        + ". All result numbers below originate in the existing Python engines.",
        "",
    ]
    for m in e.moments:
        dto = explain(
            m.after,
            m.concept,
            previous=m.before if m.before["engine"] == m.after["engine"] else None,
        )
        c = dto["concept"]
        lines += [
            "## " + m.title,
            "",
            "### WHAT USER DOES",
            "",
            m.action,
            "",
            "### WHAT QUANTLAB SHOWS",
            "",
            m.result_note,
            "",
            "```json",
            json.dumps(compact(m.after), indent=2, ensure_ascii=False),
            "```",
            "",
            "### KEY EXPLANATION",
            "",
            c["definition"],
            "",
            dto["current"]["note"],
            "",
            "### MATHS",
            "",
            c["maths"]["equation"]
            or "This concept is a mechanism or interpretation, not a standalone formula.",
            "",
            "### REAL-FINANCE USE",
            "",
            c["uses"],
            "",
            "Capture states: " + ", ".join(x for x in (m.capture_before, m.capture_after) if x),
            "",
        ]
    lines += (
        ["## LIMITATIONS", ""]
        + ["- " + x for x in e.limitations]
        + [
            "",
            "## HOW QUANTLAB DIFFERS FROM PRODUCTION",
            "",
            (
                "Educational single-machine models omit real venue latency, "
                "operational controls and much market complexity. A replay "
                "fingerprint verifies reproducibility; it does not validate a "
                "real-world investment conclusion."
            ),
            "",
            "## EVIDENCE",
            "",
            json.dumps(e.verification, sort_keys=True),
            "",
        ]
    )
    return "\n".join(lines)
