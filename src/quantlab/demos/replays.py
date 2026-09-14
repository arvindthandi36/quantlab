"""Verify saved journals with the original replay APIs before selecting any lesson."""

import copy

from quantlab.demos.projections import labelled, point
from quantlab.environments.fixtures import fixtures
from quantlab.environments.historical import replay_historical
from quantlab.environments.scenarios import replay_scenario
from quantlab.jsonio import loads
from quantlab.options.session import replay_options
from quantlab.research.codec import canonical, digest
from quantlab.risk.session import replay_risk
from quantlab.statarb.session import replay as replay_statarb
from quantlab.trading.replay import replay as replay_trading


def verified(raw, datasets=()):
    if isinstance(raw, str):
        if len(raw) > 25_000_000:
            raise ValueError("Journal exceeds the 25 MB import limit")
        raw = loads(raw)
    if not isinstance(raw, dict) or len(canonical(raw)) > 25_000_000:
        raise ValueError("Supply one compatible journal up to 25 MB")
    if raw.get("schema") == "quantlab-environment-v1" and raw.get("environment") == "SYNTHETIC":
        from quantlab import __version__

        if raw.get("quantlab_version") != __version__:
            raise ValueError("Unsupported synthetic wrapper version")
        return verified(raw["journal"], datasets)
    actions = raw.get("actions")
    if not isinstance(actions, list) or len(actions) > 20_000:
        raise ValueError("Replay action budget exceeded")
    schema = raw.get("schema")
    private = {}
    if schema == "quantlab-environment-v1":
        if raw.get("environment") == "SCENARIO":
            s, frames = replay_scenario(raw)
            private = s.reveal()
        elif raw.get("environment") == "HISTORICAL":
            # Fixture matching still requires exact provenance/fingerprint verification.
            available = list(datasets) + list(fixtures())
            selected = []
            for wanted in raw.get("datasets", []):
                match = next(
                    (d for d in available if d.fingerprint == wanted["fingerprint"]), None
                )
                if match is None:
                    raise ValueError(
                        "Import the exact original historical datasets in Markets first, "
                        "then load this journal"
                    )
                selected.append(match)
            s, frames = replay_historical(raw, selected)
            frames = [labelled(f) for f in frames]
        else:
            raise ValueError("Unknown environment journal")
    elif schema == "quantlab-options-v1":
        s = replay_options(raw, capture_frames=True)
        views = []
        for f in s.frames:
            if not views or f["revision"] > views[-1]["revision"]:
                views.append(f)
        frames = [point(f, "options") for f in views]
    elif schema == "quantlab-risk-v1":
        s, views = replay_risk(raw, frames=True)
        frames = [point(f, "risk") for f in views]
    elif schema == "quantlab-statarb-v1":
        s, views = replay_statarb(raw, frames=True)
        frames = [point(f, "statarb") for f in views]
    elif schema == 1:
        s = replay_trading(raw, capture_frames=True)
        # Use completed command boundaries, avoiding duplicate intra-command captures.
        views = []
        for f in s.frames:
            if not views or f["revision"] > views[-1]["revision"]:
                views.append(f)
        frames = [point(f) for f in views]
        rows = []
        for rec in s.evidence:
            if rec.get("market"):
                m = rec["market"]
                rows.append(
                    {
                        k: copy.deepcopy(m[k])
                        for k in (
                            "event",
                            "latent_before_ticks",
                            "latent_after_ticks",
                            "informed",
                        )
                    }
                )
        private = {
            "label": "OBSERVER ONLY · completed synthetic path; unavailable at decision time",
            "events": rows[:30],
        }
    else:
        raise ValueError("Unsupported saved journal; use a compatible ended QuantLab session")
    if len(frames) != len(actions) + 1:
        raise ValueError("Replay command-boundary frames do not align with recorded actions")
    if s.status != "ended":
        raise ValueError("Teach Me requires a completed session")
    return (
        frames,
        copy.deepcopy(actions),
        private,
        {
            "journal_digest": digest(raw),
            "verified": True,
            "source_schema": schema,
            "frames": len(frames),
            ("note"): (
                "Original version, evidence and financial reconciliation checks all passed."
            ),
        },
    )
