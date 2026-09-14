import json
import subprocess
import sys
import sysconfig
from dataclasses import replace
from pathlib import Path

import pytest

from quantlab.market.config import SimulationConfig
from quantlab.market.journal import load_session, save_session, session_json
from quantlab.market.replay import replay_session
from quantlab.market.simulation import run_simulation
from quantlab.market.timeline import render_timeline
from quantlab.randomness import RandomStreams


def test_saved_journal_roundtrips_and_replays_without_random_draws(tmp_path, monkeypatch):
    session = run_simulation()
    path = tmp_path / "session.json"
    save_session(session, path)

    def forbidden(*args):
        raise AssertionError("replay must not create a random stream")

    monkeypatch.setattr(RandomStreams, "create", forbidden)
    loaded = load_session(path)
    assert loaded == session
    assert replay_session(loaded) == session.final_book
    assert session_json(loaded) == path.read_text()
    assert render_timeline(loaded, debug=True) == render_timeline(session, debug=True)


@pytest.mark.parametrize(
    "corruption", ["trade", "snapshot", "clock", "latent", "missing_latent", "end"]
)
def test_replay_rejects_inconsistent_evidence(corruption):
    session = run_simulation()
    events = list(session.events)
    index = next(i for i, r in enumerate(events) if r.report and r.report.trades)
    record = events[index]
    if corruption == "trade":
        wrong = replace(record.report.trades[0], quantity=999)
        events[index] = replace(record, report=replace(record.report, trades=(wrong,)))
    elif corruption == "snapshot":
        events[0] = replace(events[0], book_after=replace(events[0].book_after, bids=()))
    elif corruption == "clock":
        events[0], events[1] = events[1], events[0]
    elif corruption == "latent":
        events[index] = replace(record, latent_after_ticks=record.latent_after_ticks + 1)
    elif corruption == "missing_latent":
        events.pop()  # Final scheduled value update is mandatory at the horizon.
    else:
        session = replace(session, end_time_us=1)
    with pytest.raises(ValueError):
        replay_session(replace(session, events=tuple(events)))


@pytest.mark.parametrize(
    "corruption", ["schema", "float_quantity", "bool_quantity", "nan", "metadata"]
)
def test_loader_rejects_invalid_types_nonfinite_values_and_unsupported_versions(
    tmp_path, corruption
):
    payload = json.loads(session_json(run_simulation()))
    if corruption == "schema":
        payload["schema_version"] = 99
    elif corruption in ("float_quantity", "bool_quantity"):
        events = payload["session"]["events"]
        trade = next(
            r["report"]["trades"][0] for r in events if r["report"] and r["report"]["trades"]
        )
        trade["quantity"] = 1.0 if corruption == "float_quantity" else True
    elif corruption == "nan":
        payload["session"]["events"][0]["latent_after_ticks"] = float("nan")
    else:
        payload["session"]["python_version"] = ""
    path = tmp_path / "corrupt.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="invalid session journal"):
        load_session(path)


def test_public_view_hides_latent_values_debug_exposes_them_and_output_is_bounded():
    session = run_simulation()
    public = render_timeline(session)
    debug = render_timeline(session, debug=True)
    assert "LATENT" not in public and "LATENT" in debug
    assert "observer only" in debug
    assert "further visible events omitted" in render_timeline(session, limit=1)
    assert "Price | Total Quantity | Order Count" in public
    assert "FIFO oldest first" not in public
    assert "FIFO oldest first" in render_timeline(session, expand_orders=True)
    with pytest.raises(ValueError):
        render_timeline(session, limit=0)


def test_cli_saved_run_matches_verified_replay_and_new_console_entrypoint(tmp_path):
    path = tmp_path / "session.json"
    entrypoint = Path(sysconfig.get_path("scripts")) / "quantlab-market-demo"
    result = subprocess.run(
        [str(entrypoint), "--debug", "--save", str(path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    replay = subprocess.run(
        [sys.executable, "-m", "quantlab.market_demo", "--debug", "--replay", str(path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Replay verified" in replay.stdout
    assert render_timeline(load_session(path), debug=True) in result.stdout
    assert render_timeline(load_session(path), debug=True) in replay.stdout
    assert result.stderr == replay.stderr == ""


@pytest.mark.parametrize(
    "args",
    [
        ["--duration", "0"],
        ["--seed", "-1"],
        ["--limit", "0"],
        ["--replay", "missing.json", "--seed", "1"],
    ],
)
def test_cli_reports_invalid_inputs_as_failure(args):
    result = subprocess.run(
        [sys.executable, "-m", "quantlab.market_demo", *args], capture_output=True, text=True
    )
    assert result.returncode == 2
    assert "failed" in result.stderr or "do not supply" in result.stderr


def test_empty_session_also_replays(tmp_path):
    config = SimulationConfig(
        duration_us=1, noise_rate_per_second=0, liquidity_rate_per_second=0
    )
    session = run_simulation(config)
    path = tmp_path / "empty.json"
    save_session(session, path)
    assert load_session(path) == session
