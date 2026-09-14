import json
from dataclasses import asdict, replace

import pytest

from quantlab import LimitOrder, MarketOrder, Side
from quantlab.market.config import SimulationConfig
from quantlab.market.events import EventKind
from quantlab.market_making.analytics import diagnostics, lab_markouts, public_frames
from quantlab.market_making.comparison import compare_strategies, exogenous_signature
from quantlab.market_making.config import MakerConfig, Strategy
from quantlab.market_making.journal import encode, load_lab, replay_lab, save_lab
from quantlab.market_making.lab import MarketMakingLab, run_lab
from quantlab.market_making.quotes import QuoteRequest
from quantlab.market_making.views import render_lab, render_observation
from quantlab.randomness import RandomStreams
from tests.lab_helpers import finish_manual, scripted_lab


@pytest.mark.parametrize("strategy", [Strategy.FIXED, Strategy.INVENTORY])
def test_seeded_lab_reproduction_replay_and_exact_accounting(strategy, tmp_path, monkeypatch):
    market = SimulationConfig(informed_rate_per_second=1, duration_us=12_000_000)
    maker = MakerConfig(strategy=strategy)
    result = run_lab(market, maker)
    assert result == run_lab(market, maker)
    assert len(result.fills) > 0
    for record in result.records:
        a = record.account
        assert a.marked_value_ticks == a.cash_ticks + a.inventory * a.reference_ticks
        assert a.total_pnl_ticks == a.realised_pnl_ticks + a.unrealised_pnl_ticks
        assert (
            a.total_pnl_ticks
            == a.spread_capture_ticks + a.inventory_movement_ticks - a.fees_ticks
        )
        if record.market and record.market.report:
            report = record.market.report
            assert (
                report.buyer_filled_quantity
                == report.seller_filled_quantity
                == report.executed_quantity
            )
    path = tmp_path / "lab.json"
    save_lab(result, path)

    def forbid(*args):
        raise AssertionError("replay sampled new randomness")

    monkeypatch.setattr(RandomStreams, "create", forbid)
    assert load_lab(path) == replay_lab(result) == result
    assert lab_markouts(load_lab(path).records) == lab_markouts(result.records)


def test_longer_horizon_cannot_change_earlier_decisions_or_fills():
    market = SimulationConfig(informed_rate_per_second=1)
    short = run_lab(market, MakerConfig(strategy=Strategy.INVENTORY))
    long = run_lab(replace(market, duration_us=10_000_000), short.maker_config)
    expected = tuple(r for r in short.records if r.kind != "end")
    prefix = tuple(
        r
        for r in long.records
        if r.time_us < market.duration_us
        or (r.time_us == market.duration_us and r.kind == "market")
    )
    assert expected == prefix


@pytest.mark.parametrize("side", list(Side))
def test_worst_case_one_sided_flow_cannot_exceed_reserved_capacity(side):
    maker = MakerConfig(strategy=Strategy.MANUAL, refresh_us=2)
    lab = scripted_lab(
        [(1, MarketOrder("need", side, 100)), (3, MarketOrder("reverse", side.opposite, 100))],
        maker=maker,
    )
    result = finish_manual(lab, QuoteRequest(bid_size=100, ask_size=100))
    assert result.final_account.maximum_absolute_inventory == 8
    assert all(abs(r.account.inventory) <= 8 for r in result.records)
    assert [f.quantity for f in result.fills] == [8, 16]
    assert result.final_account.inventory == (8 if side is Side.BUY else -8)
    assert replay_lab(result) == result  # Manual instructions are replayed too.


def test_partial_resting_quotes_are_cancelled_before_replacement_and_never_fill_later():
    lab = scripted_lab(
        [(1, MarketOrder("one", Side.SELL, 1)), (3, MarketOrder("later", Side.SELL, 10))]
    )
    result = finish_manual(lab, QuoteRequest(bid_size=3, ask_size=3))
    first_quote = next(r for r in result.records if r.kind == "quote")
    old_bid = first_quote.placed[0].order_id
    replacement = next(r for r in result.records if r.kind == "quote" and r.time_us == 2)
    assert (
        next(o for o in replacement.cancelled if o.order_id == old_bid).remaining_quantity == 2
    )
    later = next(r for r in result.records if r.market and r.time_us == 3)
    assert all(t.maker_order_id != old_bid for t in later.market.report.trades)
    assert all(o.order_id != old_bid for level in later.book_after.bids for o in level.orders)
    assert len({o.order_id for r in result.records for o in r.placed}) == sum(
        len(r.placed) for r in result.records
    )


def test_zero_manual_size_withdraws_quotes_without_moving_cash_or_inventory():
    lab = scripted_lab([])
    lab.advance_to_decision()
    lab.decide(QuoteRequest())
    before = lab.advance_to_decision().account
    record = lab.decide(QuoteRequest(bid_size=0, ask_size=0))
    assert len(record.cancelled) == 2 and record.placed == record.own_quotes == ()
    assert record.account == before
    assert finish_manual(lab, QuoteRequest(bid_size=0, ask_size=0)).fills == ()


def test_external_quotes_cannot_be_crossed_by_new_maker_orders():
    lab = scripted_lab([(1, LimitOrder("external", Side.SELL, 2, 110))])
    lab.advance_to_decision()
    lab.decide(QuoteRequest(bid_size=0, ask_size=0))
    lab.advance_to_decision()
    record = lab.decide(QuoteRequest(centre_shift_ticks=20))
    assert record.plan.bid_ticks == 109
    assert all(report.trades == () for report in record.reports)
    assert any("passive" in a for a in record.plan.adjustments)


def test_untracked_stale_owned_order_fails_and_disables_lab():
    lab = scripted_lab([])
    lab.advance_to_decision()
    lab.decide(QuoteRequest())
    lab.advance_to_decision()
    lab._book.submit(LimitOrder("rogue", Side.BUY, 1, 97))
    lab._owned.add("rogue")
    with pytest.raises(AssertionError, match="stale"):
        lab.decide(QuoteRequest())
    with pytest.raises(RuntimeError, match="discard"):
        lab.advance_to_decision()


def test_horizon_cancels_quotes_without_fake_liquidation():
    result = finish_manual(scripted_lab([(1, MarketOrder("sell", Side.SELL, 1))]))
    end = result.records[-1]
    assert end.kind == "end" and end.own_quotes == () and end.fills == ()
    assert end.account.inventory == 1
    assert len(result.fills) == 1


def test_decision_clock_is_public_and_private_steps_are_not_exposed():
    lab = MarketMakingLab(SimulationConfig(informed_rate_per_second=1), MakerConfig())
    with pytest.raises(RuntimeError, match="public decision"):
        lab.observation()
    times = []
    while (obs := lab.advance_to_decision()) is not None:
        times.append(obs.time_us)
        assert lab.advance_to_decision() == obs
        lab.decide(QuoteRequest())
        with pytest.raises(RuntimeError, match="public decision"):
            lab.observation()
    assert times == [0, 1_000_000, 2_000_000, 3_000_000, 4_000_000]


def test_public_strategy_inputs_and_outputs_do_not_contain_hidden_information():
    lab = MarketMakingLab(SimulationConfig(informed_rate_per_second=1), MakerConfig())
    while (obs := lab.advance_to_decision()) is not None:
        text = json.dumps(asdict(obs), default=encode).lower()
        text += render_observation(obs, lab_markouts(lab.observer_records())).lower()
        for hidden in (
            "latent",
            "signal",
            "seed",
            "informed",
            "noise_arrival",
            "liquidity_arrival",
        ):
            assert hidden not in text
        lab.decide(QuoteRequest())
    result = lab.result()
    public_text = render_lab(result).lower()
    public_json = json.dumps(
        [asdict(f) for f in public_frames(result.records)], default=encode
    ).lower()
    for hidden in (
        "latent",
        "signal",
        "seed",
        "informed",
        "noise_arrival",
        "liquidity_arrival",
    ):
        assert hidden not in public_text + public_json
    assert "informed traders" in render_lab(result, debug=True).lower()


def test_private_path_changes_cannot_affect_normal_maker_without_informed_flow():
    market = SimulationConfig(informed_rate_per_second=0, latent_sigma_ticks=0)
    a = run_lab(market, MakerConfig(strategy=Strategy.INVENTORY))
    b = run_lab(replace(market, latent_sigma_ticks=20), a.maker_config)
    assert public_frames(a.records) == public_frames(b.records)
    assert diagnostics(a.records) == diagnostics(b.records)
    assert lab_markouts(a.records) == lab_markouts(b.records)


def test_private_diagnostics_and_extra_holds_cannot_change_public_marks_or_metrics():
    result = run_lab()
    records = []
    for r in result.records:
        if r.market is not None and r.market.order is None:
            # Hidden no-action observations can be removed without changing public evidence.
            continue
        if r.market:
            r = replace(
                r,
                market=replace(
                    r.market,
                    latent_before_ticks=12345,
                    latent_after_ticks=67890,
                    informed=None,
                    reason="private sentinel",
                ),
            )
        records.append(r)
    altered = tuple(records)
    assert public_frames(altered) == public_frames(result.records)
    assert diagnostics(altered) == diagnostics(result.records)
    assert lab_markouts(altered) == lab_markouts(result.records)


@pytest.mark.parametrize(
    "change",
    [
        "cash",
        "inventory",
        "capture",
        "public_clock",
        "request",
        "cancel",
        "signal",
        "missing_quote",
        "missing_end",
    ],
)
def test_replay_rejects_corrupted_account_actions_and_private_evidence(change):
    result = run_lab()
    records = list(result.records)
    if change in ("cash", "inventory", "capture"):
        name = {
            "cash": "cash_ticks",
            "inventory": "inventory",
            "capture": "spread_capture_ticks",
        }[change]
        records[-1] = replace(
            records[-1],
            account=replace(
                records[-1].account, **{name: getattr(records[-1].account, name) + 1}
            ),
        )
    elif change == "public_clock":
        records[-1] = replace(records[-1], public_event_number=999)
    elif change == "request":
        records[0] = replace(records[0], request=QuoteRequest(bid_size=1))
    elif change == "cancel":
        index = next(i for i, r in enumerate(records) if r.cancelled)
        records[index] = replace(records[index], cancelled=())
    elif change == "signal":
        index = next(i for i, r in enumerate(records) if r.market and r.market.informed)
        event = records[index].market
        audit = event.informed
        audit = replace(audit, signal=replace(audit.signal, time_us=event.event.time_us + 1))
        records[index] = replace(records[index], market=replace(event, informed=audit))
    elif change == "missing_quote":
        records.pop(0)
    else:
        records.pop()
    with pytest.raises((ValueError, AssertionError)):
        replay_lab(replace(result, records=tuple(records)))


@pytest.mark.parametrize("field", ["inventory", "cash_ticks", "public_event_number"])
def test_journal_rejects_boolean_numeric_corruption(field, tmp_path):
    path = tmp_path / "bad.json"
    save_lab(run_lab(), path)
    raw = json.loads(path.read_text())
    end = raw["result"]["records"][-1]
    (end if field == "public_event_number" else end["account"])[field] = True
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError):
        load_lab(path)


def test_comparison_shares_exogenous_randomness_and_is_reproducible():
    market = SimulationConfig(seed=5, duration_us=15_000_000, informed_rate_per_second=1)
    a = run_lab(market, MakerConfig())
    b = run_lab(market, MakerConfig(strategy=Strategy.INVENTORY))
    assert exogenous_signature(a) == exogenous_signature(b)
    assert [r.plan for r in a.records] != [r.plan for r in b.records]
    first = compare_strategies(seeds=(0, 1), duration_us=5_000_000)
    assert first == compare_strategies(seeds=(0, 1), duration_us=5_000_000)
    assert [(r.seed, r.strategy) for r in first] == [
        (0, Strategy.FIXED),
        (0, Strategy.INVENTORY),
        (1, Strategy.FIXED),
        (1, Strategy.INVENTORY),
    ]


def test_comparison_signature_distinguishes_event_kind_at_identical_time_and_sequence():
    result = run_lab()
    records = list(result.records)
    index = next(
        i for i, r in enumerate(records) if r.market and r.market.event.kind is EventKind.NOISE
    )
    background = records[index].market
    records[index] = replace(
        records[index],
        market=replace(background, event=replace(background.event, kind=EventKind.LIQUIDITY)),
    )
    assert exogenous_signature(result) != exogenous_signature(
        replace(result, records=tuple(records))
    )


def test_configured_markout_horizons_are_used_in_both_public_and_debug_reports():
    result = run_lab(
        SimulationConfig(informed_rate_per_second=1, markout_horizons_events=(2, 7))
    )
    for debug in (False, True):
        text = render_lab(result, debug=debug)
        assert "h2 " in text and "h7 " in text
        assert "h1 " not in text and "h5 " not in text and "h20 " not in text
