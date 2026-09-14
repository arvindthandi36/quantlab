import json
from dataclasses import asdict, replace

import pytest

from quantlab.analytics.markouts import analyse_markouts
from quantlab.market.config import SimulationConfig
from quantlab.market.events import EventKind
from quantlab.market.journal import load_session, save_session
from quantlab.market.public import project_public
from quantlab.market.replay import replay_session
from quantlab.market.simulation import MarketSimulation, run_simulation
from quantlab.market.timeline import render_timeline
from quantlab.randomness import RandomStreams


def test_informed_reproduction_replay_and_trade_conservation(tmp_path, monkeypatch):
    config = SimulationConfig(informed_rate_per_second=1, duration_us=12000000)
    first = run_simulation(config)
    assert first == run_simulation(config)
    assert any(r.informed and r.order for r in first.events)
    for record in first.events:
        if record.report:
            assert (
                record.report.buyer_filled_quantity
                == record.report.seller_filled_quantity
                == record.report.executed_quantity
            )
    path = tmp_path / "informed.json"
    save_session(first, path)

    def forbid(*args):
        raise AssertionError("replay sampled a new random stream")

    monkeypatch.setattr(RandomStreams, "create", forbid)
    loaded = load_session(path)
    assert loaded == first
    assert replay_session(loaded) == first.final_book
    assert analyse_markouts(loaded) == analyse_markouts(first)


def test_old_phase2_journal_still_loads_without_informed_flow():
    session = load_session("docs/learning/phase_02_session.json")
    assert session.config.informed_rate_per_second == 0
    assert all(r.informed is None for r in session.events)


def test_decisions_and_signals_in_short_run_are_exact_prefix_of_longer_run():
    config = SimulationConfig(informed_rate_per_second=1)
    short = run_simulation(config)
    long = run_simulation(replace(config, duration_us=15000000))
    prefix = tuple(r for r in long.events if r.event.time_us <= config.duration_us)
    assert short.events == prefix


def test_first_signal_cannot_read_a_future_latent_draw(monkeypatch):
    sim = MarketSimulation(SimulationConfig(informed_rate_per_second=1))

    def forbid(*args):
        raise AssertionError("future latent draw was read")

    monkeypatch.setattr(sim._latent_rng, "gauss", forbid)
    first = sim.step()
    assert first.event.kind is EventKind.INFORMED
    assert first.event.time_us < sim.config.latent_step_us
    assert first.informed.signal.time_us == first.event.time_us
    assert (
        first.informed.signal.value_ticks - first.informed.error_ticks
        == first.latent_before_ticks
    )


def test_signal_noise_changes_do_not_shift_arrivals_or_latent_shocks():
    base = SimulationConfig(informed_rate_per_second=1)
    clean = run_simulation(replace(base, signal_noise_ticks=0.5))
    noisy = run_simulation(replace(base, signal_noise_ticks=10))
    assert [r.event for r in clean.events] == [r.event for r in noisy.events]
    assert [r.latent_after_ticks for r in clean.events] == [
        r.latent_after_ticks for r in noisy.events
    ]


def test_public_projection_and_snapshot_have_no_private_fields_or_source_ids():
    sim = MarketSimulation(SimulationConfig(informed_rate_per_second=1))
    while sim.step() is not None:
        snapshot = sim.public_snapshot()
        raw = json.dumps(asdict(snapshot), default=str).lower()
        for forbidden in (
            "latent",
            "signal",
            "seed",
            "informed",
            "noise_arrival",
            "liquidity_arrival",
            "threshold",
        ):
            assert forbidden not in raw
        assert set(asdict(sim.observation())) == {
            "best_bid",
            "best_ask",
            "last_trade_ticks",
            "opening_reference_ticks",
        }
    session = sim.run()
    projected = project_public(session)
    encoded = json.dumps(asdict(projected), default=str).lower()
    text = render_timeline(session, expand_orders=True).lower()
    for forbidden in (
        "latent",
        "signal",
        "seed",
        "informed",
        "noise_arrival",
        "posterior",
        "hurdle",
        "reason",
    ):
        assert forbidden not in encoded
        assert forbidden not in text
    assert len(projected.events) == sum(r.order is not None for r in session.events)
    assert any(r.informed and r.order is None for r in session.events)
    assert "Private:" in render_timeline(session, debug=True)


def test_private_events_cannot_leak_through_public_snapshot_timing():
    sim = MarketSimulation(SimulationConfig(informed_rate_per_second=1))
    previous = sim.public_snapshot()
    hidden_events = 0
    while (record := sim.step()) is not None:
        current = sim.public_snapshot()
        if record.order is None:
            assert current == previous
            hidden_events += 1
        else:
            assert current.time_us == record.event.time_us
        previous = current
    assert hidden_events > 0
    assert sim.public_snapshot() == project_public(sim.run()).final


def test_private_diagnostics_and_seed_cannot_change_public_projection():
    session = run_simulation(SimulationConfig(informed_rate_per_second=1))
    # This intentionally altered observer log is not replayable. Projection must
    # nevertheless be a function of public facts alone, including final depth.
    records = tuple(
        replace(
            r,
            latent_before_ticks=32123.45,
            latent_after_ticks=65432.1,
            informed=None,
            reason="private sentinel",
        )
        for r in session.events
    )
    altered = replace(session, config=replace(session.config, seed=999), events=records)
    assert project_public(session) == project_public(altered)
    assert render_timeline(session) == render_timeline(altered)


@pytest.mark.parametrize(
    "corruption", ["signal_time", "signal_error", "estimate", "threshold", "action", "noise"]
)
def test_replay_rejects_private_audit_inconsistent_with_current_information(corruption):
    session = run_simulation(SimulationConfig(informed_rate_per_second=1))
    records = list(session.events)
    index = next(i for i, r in enumerate(records) if r.informed and r.order)
    record = records[index]
    audit = record.informed
    if corruption == "signal_time":
        audit = replace(audit, signal=replace(audit.signal, time_us=record.event.time_us + 1))
    elif corruption == "signal_error":
        audit = replace(audit, error_ticks=audit.error_ticks + 1)
    elif corruption == "noise":
        audit = replace(audit, signal=replace(audit.signal, noise_sd_ticks=99))
    else:
        key = {
            "estimate": "estimated_value_ticks",
            "threshold": "threshold_ticks",
            "action": "order",
        }[corruption]
        value = None if key == "order" else getattr(audit.decision, key) + 1
        audit = replace(audit, decision=replace(audit.decision, **{key: value}))
    records[index] = replace(record, informed=audit)
    with pytest.raises(ValueError):
        replay_session(replace(session, events=tuple(records)))
