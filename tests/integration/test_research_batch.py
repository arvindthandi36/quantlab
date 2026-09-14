from dataclasses import asdict
from fractions import Fraction

import pytest

from quantlab.market.config import SimulationConfig
from quantlab.market.simulation import MarketEnvironment
from quantlab.market_making.analytics import diagnostics, lab_markouts, summarise_markouts
from quantlab.market_making.config import MakerConfig
from quantlab.market_making.lab import MarketMakingLab
from quantlab.research.adapters.maker import MakerAccumulator, MakerAdapter, maker_configuration
from quantlab.research.codec import plain
from quantlab.research.seeds import SeedPlan


@pytest.mark.parametrize("seed", [0, 1, 3, 42, 99])
@pytest.mark.parametrize("strategy", ["fixed", "inventory"])
def test_batch_matches_full_and_independent_offline_diagnostics(seed, strategy):
    adapter = MakerAdapter()
    config = maker_configuration(strategy=strategy, duration_us=12_000_000)
    batch = adapter.run(seed, config)
    full = adapter.run(seed, config, full=True)
    assert batch == full and batch.journal is None and full.journal is not None
    account = full.journal.final_account
    d = diagnostics(full.journal.records)
    expected = {
        "net_pnl": float(account.total_pnl_ticks / 100),
        "realised_pnl": float(account.realised_pnl_ticks / 100),
        "maximum_drawdown": float(d.maximum_drawdown_ticks / 100),
        "average_absolute_inventory": float(d.average_absolute_inventory),
        "average_inventory": float(d.average_inventory),
        "maximum_absolute_inventory": d.maximum_absolute_inventory,
        "rms_inventory": d.rms_inventory,
        "turnover": d.turnover_ticks / 100,
        "fill_rate": float(d.fill_rate) if d.fill_rate is not None else None,
        "average_quoted_spread": float(d.average_quoted_spread_ticks / 100)
        if d.average_quoted_spread_ticks is not None
        else None,
        "average_effective_spread": float(d.average_effective_spread_ticks / 100)
        if d.average_effective_spread_ticks is not None
        else None,
        "two_sided_quote_time_fraction": float(d.two_sided_quote_time_fraction),
        "buy_fills": d.buy_fills,
        "sell_fills": d.sell_fills,
        "buy_units": d.buy_units,
        "sell_units": d.sell_units,
    }
    for key, value in expected.items():
        assert batch.metrics[key] == value
    marks = summarise_markouts(lab_markouts(full.journal.records), horizons=(1, 5, 20))
    for mark in marks:
        assert batch.coverage["markouts"][str(mark.horizon_events)] == plain(
            {k: v for k, v in asdict(mark).items() if k != "horizon_events"}
        )
        assert batch.metrics[f"markout_{mark.horizon_events}"] == (
            float(mark.mean_ticks / 100) if mark.mean_ticks is not None else None
        )
    assert batch.metrics["net_pnl"] == pytest.approx(
        batch.metrics["execution_edge"]
        + batch.metrics["inventory_movement"]
        - batch.metrics["fees"]
    )
    assert set(batch.metrics) == set(adapter.metric_units(config))


def test_lightweight_mode_retains_no_full_record_history():
    sink = MakerAccumulator((1, 5, 20))
    lab = MarketMakingLab(
        SimulationConfig(duration_us=5_000_000),
        MakerConfig(),
        retain_records=False,
        record_sink=sink,
    )
    lab.run_to_completion()
    assert lab._records == [] and lab._environment._records == []
    assert sink.ended and sink.events > 0
    with pytest.raises(RuntimeError, match="lightweight"):
        lab.result()
    with pytest.raises(RuntimeError, match="lightweight"):
        lab.observer_records()


def test_lightweight_event_cap_still_fails_loudly():
    config = SimulationConfig(max_events=1, duration_us=10_000_000)
    lab = MarketMakingLab(config, MakerConfig(), retain_records=False)
    with pytest.raises(RuntimeError, match="event budget"):
        lab.run_to_completion()


def test_unrelated_signal_draw_does_not_change_arrivals_or_latent(monkeypatch):
    original = MarketEnvironment.__init__
    config = maker_configuration(duration_us=10_000_000)
    first = MakerAdapter().run(42, config, full=True)

    def with_draw(self, *args, **kwargs):
        original(self, *args, **kwargs)
        self._signal_rng.random()

    monkeypatch.setattr(MarketEnvironment, "__init__", with_draw)
    second = MakerAdapter().run(42, config, full=True)

    def weather(result):
        return [
            (r.market.event.time_us, r.market.event.kind, r.market.latent_after_ticks)
            for r in result.journal.records
            if r.market
        ]

    assert weather(first) == weather(second)
    assert first.environment_fingerprint != second.environment_fingerprint


def test_no_normal_batch_metric_or_coverage_contains_private_values():
    result = MakerAdapter().run(42, maker_configuration())
    keys = str((result.metrics.keys(), result.coverage.keys()))
    assert all(name not in keys for name in ("latent", "signal", "informed", "counterparty"))


def test_crn_paired_weather_matches_but_outcomes_may_differ():
    seed = SeedPlan(9, "development", 1).seeds()[0]
    a = MakerAdapter().run(seed, maker_configuration(strategy="fixed"))
    b = MakerAdapter().run(seed, maker_configuration(strategy="inventory"))
    assert a.environment_fingerprint == b.environment_fingerprint
    assert a.trajectory_fingerprint != b.trajectory_fingerprint


def test_custom_horizons_and_exact_fees_remain_consistent():
    c = maker_configuration(duration_us=5_000_000, fee_ticks=Fraction(1, 3))
    c["market"]["markout_horizons_events"] = [2, 3]
    batch = MakerAdapter().run(42, c)
    assert set(batch.coverage["markouts"]) == {"2", "3"}
    assert batch == MakerAdapter().run(42, c, full=True)
