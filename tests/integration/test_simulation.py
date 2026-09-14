import random
from dataclasses import replace

import pytest

from quantlab.market.config import SimulationConfig
from quantlab.market.events import EventKind
from quantlab.market.simulation import MarketSimulation, run_simulation


def test_seed_reproduces_events_tape_and_state_without_global_rng_mutation():
    before = random.getstate()
    first = run_simulation()
    assert first == run_simulation()
    assert first.events != run_simulation(SimulationConfig(seed=43)).events
    assert random.getstate() == before
    assert first.end_time_us == first.config.duration_us


def test_stepping_and_running_agree_and_complete_horizon_is_inclusive():
    sim = MarketSimulation(SimulationConfig())
    observed = []
    while (record := sim.step()) is not None:
        assert record.event.time_us == sim.now_us
        observed.append(record)
    result = sim.run()
    assert tuple(observed) == result.events
    assert result == run_simulation()
    assert sim.step() is None
    assert result.events[-1].event.time_us == 5000000


def test_empty_short_horizon_has_no_fabricated_events_or_liquidity():
    config = SimulationConfig(
        duration_us=1, noise_rate_per_second=0, liquidity_rate_per_second=0
    )
    result = run_simulation(config)
    assert result.events == result.tape == ()
    assert result.final_book.bids == result.final_book.asks == ()
    assert result.end_time_us == 1


def test_latent_updates_never_create_quotes_or_transactions():
    config = SimulationConfig(noise_rate_per_second=0, liquidity_rate_per_second=0)
    result = run_simulation(config)
    assert len(result.events) == 5
    assert all(r.order is r.report is None for r in result.events)
    assert (
        result.tape == () and result.final_book.best_bid is result.final_book.best_ask is None
    )


def test_liquidity_only_flow_reports_unfilled_orders_on_empty_book():
    result = run_simulation(
        SimulationConfig(noise_rate_per_second=0, liquidity_rate_per_second=5)
    )
    reports = [r.report for r in result.events if r.report is not None]
    assert reports
    assert all(r.cancelled_quantity == r.requested_quantity for r in reports)
    assert all(r.executed_quantity == 0 for r in reports)
    assert result.tape == ()


def test_changing_hidden_values_does_not_change_orders_or_trades():
    config = SimulationConfig()
    alternate = replace(config, initial_latent_ticks=20000, latent_sigma_ticks=20)
    first, second = run_simulation(config), run_simulation(alternate)
    assert [r.order for r in first.events] == [r.order for r in second.events]
    assert [r.report for r in first.events] == [r.report for r in second.events]
    assert first.tape == second.tape
    assert first.events[-1].latent_after_ticks != second.events[-1].latent_after_ticks


def test_decision_draw_changes_do_not_shift_arrival_or_latent_streams():
    config = SimulationConfig(duration_us=20000000)
    alternate = replace(config, noise_max_quantity=31, noise_price_radius_ticks=12)
    first, second = run_simulation(config), run_simulation(alternate)
    assert [r.event for r in first.events] == [r.event for r in second.events]
    assert [r.latent_after_ticks for r in first.events] == [
        r.latent_after_ticks for r in second.events
    ]


def test_tape_and_full_session_accounting_come_only_from_executions():
    result = run_simulation(SimulationConfig(duration_us=20000000))
    expected = [
        (r.event.time_us, t) for r in result.events if r.report for t in r.report.trades
    ]
    assert [(t.time_us, t.trade) for t in result.tape] == expected
    assert expected
    reports = [r.report for r in result.events if r.report]
    volume = sum(t.trade.quantity for t in result.tape)
    resting = sum(p.quantity for p in result.final_book.bids + result.final_book.asks)
    assert sum(r.requested_quantity for r in reports) == (
        2 * volume + resting + sum(r.cancelled_quantity for r in reports)
    )
    assert sum(r.buyer_filled_quantity for r in reports) == volume
    assert sum(r.seller_filled_quantity for r in reports) == volume
    assert all(r.order is None for r in result.events if r.event.kind is EventKind.LATENT)


def test_event_budget_exhaustion_is_a_failure_not_silent_partial_success():
    with pytest.raises(RuntimeError, match="budget exceeded"):
        run_simulation(SimulationConfig(max_events=1))


def test_equal_time_sources_use_initial_scheduling_order(monkeypatch):
    monkeypatch.setattr("quantlab.market.simulation.exponential_wait_us", lambda *_: 1000000)
    result = run_simulation(SimulationConfig(duration_us=1000000))
    assert [r.event.kind for r in result.events] == [
        EventKind.LATENT,
        EventKind.NOISE,
        EventKind.LIQUIDITY,
    ]


def test_failed_latent_event_cannot_be_skipped_by_resuming_the_simulation(monkeypatch):
    sim = MarketSimulation(
        SimulationConfig(noise_rate_per_second=0, liquidity_rate_per_second=0)
    )

    def fail(*args):
        raise ValueError("latent model failed")

    monkeypatch.setattr("quantlab.market.simulation.fundamental_step", fail)
    with pytest.raises(ValueError, match="latent model failed"):
        sim.step()
    with pytest.raises(RuntimeError, match="previously failed"):
        sim.run()
