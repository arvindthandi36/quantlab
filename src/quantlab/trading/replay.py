"""Versioned manual actions + existing background journal evidence, verified end to end."""

import platform

from quantlab import __version__
from quantlab.jsonio import loads as strict_loads
from quantlab.market.journal import _record
from quantlab.market.replay import ReplayMarketEnvironment
from quantlab.research.codec import canonical, digest, plain
from quantlab.trading.scenarios import scenario_from_dict
from quantlab.trading.session import TradingSession


def journal(session):
    if session.status != "ended":
        raise ValueError("End the session before exporting privileged replay evidence")
    payload = plain(
        {
            "schema": 1,
            "version": __version__,
            "python": platform.python_version(),
            "scenario": session.scenario,
            "mode": session.mode,
            "end_time_us": session.now_us,
            "actions": session.actions,
            "evidence": session.evidence,
            "final_public": session.public_snapshot(),
        }
    )
    return {**payload, "sha256": digest(payload)}


def replay(payload, *, regenerate_seed=False, capture_frames=False):
    """Rebuild real exchange/account transitions; saved public states are only comparisons.

    The checksum detects accidents, not forgery. Seed regeneration is version-bound;
    recorded-event verification does not draw random numbers.
    """
    if not isinstance(payload, dict) or payload.get("schema") != 1:
        raise ValueError("Unsupported trading journal")
    body = {k: v for k, v in payload.items() if k != "sha256"}
    if payload.get("sha256") != digest(body):
        raise ValueError("Journal checksum mismatch")
    if len(payload["actions"]) > 20_000 or len(payload["evidence"]) > 40_000:
        raise ValueError("Journal exceeds replay budget")
    scenario = scenario_from_dict(payload["scenario"])
    if scenario.market.max_events > 20_000 or scenario.market.duration_us > 300_000_000:
        raise ValueError("Journal exceeds local replay horizon")
    factory = None
    if regenerate_seed:
        if payload["version"] != __version__ or payload["python"] != platform.python_version():
            raise ValueError(
                "Seed regeneration requires the recorded simulator and Python versions"
            )
    else:
        records = tuple(
            _record(e["market"]) for e in payload["evidence"] if e["kind"] == "market"
        )
        factory = lambda c, b: ReplayMarketEnvironment(  # noqa: E731
            c, b, records, end_time_us=payload["end_time_us"]
        )
    session = TradingSession(
        scenario, payload["mode"], environment_factory=factory, capture_frames=capture_frames
    )
    if capture_frames:
        session.frames.append(session.public_snapshot())
    for action in payload["actions"]:
        if session.now_us != action["at_us"]:
            raise ValueError("Action timestamp mismatch")
        result = session.command(action["kind"], **action["payload"])
        if result != action["result"]:
            raise ValueError("Action result mismatch")
    if session.status != "ended" or session.now_us != payload["end_time_us"]:
        raise ValueError("Journal is not a complete ended session")
    if not regenerate_seed:
        session.environment.finish()
    if session.evidence != payload["evidence"]:
        raise ValueError("Exchange/account evidence mismatch")
    if session.public_snapshot() != payload["final_public"]:
        raise ValueError("Final public state mismatch")
    return session


def loads(data, **kwargs):
    return replay(strict_loads(data), **kwargs)


def dumps(session):
    return canonical(journal(session)) + "\n"
