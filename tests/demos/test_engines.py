"Phase 14 acceptance tests: genuine engine paths, all catalogue entries and reproducibility."

import copy
import json
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

import pytest

from quantlab.demos import SEED
from quantlab.demos.builders import build
from quantlab.demos.projections import journey
from quantlab.demos.registry import FLAGSHIPS, REGISTRY, catalogue
from quantlab.demos.replays import verified
from quantlab.explainability.registry import CONCEPTS
from quantlab.research.codec import digest
from quantlab.trading.server import Controller


def test_catalogue_covers_every_requested_domain_topic_and_unique_id():
    rows = catalogue()
    assert len(rows) == len({r["id"] for r in rows}) == 58
    assert set(r["domain"] for r in rows) == {
        "Trading",
        "Market Making",
        "Research",
        "Options",
        "Risk",
        "Stat Arb",
        "Markets",
        "Engineering",
    }
    assert sum(r["flagship"] for r in rows) == 8
    for r in rows:
        assert 2 <= r["duration_minutes"] <= 8
        assert r["title"] and r["description"] and r["difficulty"] and r["environment"]
        assert set(r["concepts"]) <= CONCEPTS.keys()
        assert set(r["prerequisites"]) <= CONCEPTS.keys()
        assert r["id"] not in r["prerequisites"] or r["id"] in CONCEPTS


@pytest.mark.parametrize("key", list(REGISTRY))
def test_every_demo_has_actual_evidence_explain_links_and_valid_checkpoints(key):
    h = Controller().demos
    h.start(key)
    assert h.evidence.moments and h.evidence.limitations
    while not h.completed:
        v = h.state()["active"]
        assert v["point"]["environment"]["badge"]
        assert v["explanation"]["concept"]["id"] in CONCEPTS
        if h.moment.question:
            assert h.moment.question.validate(h.moment.question.expected)
            assert v["question"]["question"]["concept"]
        assert v["explanation"]["demo_context"]
        assert v["explanation"]["quiz_allowed"] is False
        h.command({"kind": "next"})
    assert h.evidence.verification["engine_result_digest"] == digest(
        [m.after for m in h.evidence.moments]
    )
    assert "LIMITATIONS" in h.export()


@pytest.mark.parametrize("key", FLAGSHIPS)
def test_restart_rebuilds_identical_book_positions_parameters_and_outputs(key):
    h = Controller().demos
    h.start(key)
    original = copy.deepcopy(h.evidence)
    for _ in range(2):
        h.command({"kind": "next"})
    h.command({"kind": "restart"})
    assert h.index == 0 and not h.revealed
    assert h.evidence.configuration == original.configuration
    assert [m.before for m in h.evidence.moments] == [m.before for m in original.moments]
    assert [m.after for m in h.evidence.moments] == [m.after for m in original.moments]
    assert h.evidence.journal == original.journal


def test_order_exact_fifo_fills_vwap_fees_cash_and_position():
    e = build("order")
    a = e.moments[0].after["core"]
    o = a["orders"][0]
    assert [(f["quantity"], f["price"]) for f in o["fills"]] == [
        (3, "100.01000"),
        (4, "100.02000"),
        (3, "100.04000"),
    ]
    assert o["vwap"] == "100.02300"
    assert Fraction(a["account"]["fees"]) == Fraction("0.01")
    assert Fraction(a["account"]["cash"]) == Fraction("8999.76")
    assert a["account"]["position"] == 10
    assert a["asks"][0]["quantity"] == 5
    frames, _, _, _ = verified(e.journal)
    assert frames[-1]["core"] == e.journal["final_public"]


def test_market_order_unfilled_remainder_and_exact_account_replay():
    e = build("partial")
    o = e.moments[0].after["core"]["orders"][0]
    assert (o["original"], o["filled"], o["remaining"], o["cancelled"]) == (20, 15, 0, 5)
    verified(e.journal)


def test_queue_keeps_individual_fifo_and_cancel_does_not_trade():
    e = build("queue")
    a = e.moments[0].after["core"]
    level = a["bids"][0]
    assert (level["quantity"], level["order_count"]) == (12, 2)
    assert [r["yours"] for r in level["queue"]] == [False, True]
    assert e.moments[1].after["core"]["orders"][0]["cancelled"] == 2
    assert not e.moments[1].after["core"]["trades"]


def test_picked_off_uses_noisy_decisions_actual_owned_provider_fills_and_mature_markouts():
    e = build("picked-off")
    trades = e.moments[-1].after["core"]["trades"]
    assert trades and all(t["role"] == "provider" for t in trades)
    events = e.private["events"]
    assert any(r["informed"] and r["executions"] for r in events)
    for r in events:
        if r["informed"]:
            decision = r["informed"]["decision"]
            assert r["informed"]["signal"]["noise_sd_ticks"] > 0
            assert 0 < decision["signal_weight"] < 1
            if decision["order"]:
                assert (
                    max(
                        x
                        for x in (decision["buy_edge_ticks"], decision["sell_edge_ticks"])
                        if x is not None
                    )
                    > decision["threshold_ticks"]
                )
    negative = [
        m
        for m in e.private["markouts"]
        if m["reference"] == "observer_latent"
        and m["provider_markout_ticks"] is not None
        and m["provider_markout_ticks"] < 0
    ]
    assert negative and all(m["status"] == "available" for m in negative)
    verified(e.journal)


@pytest.mark.parametrize("branch", ["full", "partial", "none"])
def test_delta_branches_execute_real_hedges_and_replay(branch):
    e = build("delta-hedge", branch)
    before = e.moments[1].before["core"]
    after = e.moments[1].after["core"]
    assert before["positions"] and before["greeks"]["delta"] > 0
    expected = {"full": -51, "partial": -26, "none": 0}[branch]
    assert after["stock"]["account"]["position"] == expected
    assert sum(f["quantity"] for f in after["stock"]["trades"]) == abs(expected)
    assert abs(e.moments[3].after["core"]["greeks"]["delta"]) <= 0.5
    assert e.moments[4].after["core"]["greeks"]["vega"] > 0
    verified(e.journal)


def test_tail_statistics_are_the_existing_controlled_example():
    from quantlab.risk.analytics import tail_example

    data = build("tails").moments[0].after["calculation"]
    assert data == tail_example()
    assert data["mild"]["var"] == data["severe"]["var"] == 10
    assert data["mild"]["es"] == 12 and data["severe"]["es"] == 48


def test_pair_comparison_and_breakdown_come_from_phase10():
    from quantlab.statarb.examples import relationship_example, teaching_cases
    from quantlab.statarb.research import generate

    e = build("pairs")
    cases = teaching_cases()["cases"]
    assert e.moments[0].after["calculation"]["stable"] == cases["stable"]
    assert e.moments[0].after["calculation"]["noncointegrated"] == cases["noncointegrated"]
    data, _ = generate(101001, name="decouple", steps=400)
    assert e.moments[1].after["calculation"]["decoupled"] == relationship_example(data)
    assert (
        cases["stable"]["correlation"] != 0.98
    )  # display actual value, not narrative placeholder


def test_winner_is_locked_from_all_50_development_means_before_separate_evaluation():
    from quantlab.demos.build_research import selection
    from quantlab.research.seeds import SeedPlan, derived_seed

    result, proof = selection()
    means = result["all_development_means"]
    assert len(means) == 50 and proof["root"] == SEED
    assert result["selected_variant"]["name"] == max(means, key=means.get)
    assert result["known_true_mean"] == 0
    assert proof["selection_lock"]["selected_variant"] == result["selected_variant"]
    dev = set(SeedPlan(derived_seed(SEED, "selection-control"), "development", 40).seeds())
    assert not dev.intersection(proof["evaluation_seeds"])
    assert result["observed_deterioration"] == pytest.approx(
        result["development"]["mean"] - result["evaluation"]["mean"]
    )


def test_research_results_cached_and_callers_cannot_mutate_future_runs():
    from quantlab.demos.build_research import selection

    a = build("winner")
    saved = copy.deepcopy(a.moments[-1].after)
    before = selection.cache_info().misses
    a.moments[-1].after["calculation"]["development"]["mean"] = 999
    b = build("winner")
    assert b.moments[-1].after == saved
    assert selection.cache_info().misses == before


def test_historical_order_waits_for_later_observation_and_is_labelled_artificial():
    e = build("historical")
    one, two = e.moments
    assert not one.after["fills"]
    assert two.after["fills"][0]["index"] > one.after["index"]
    assert two.after["environment"]["data_kind"] == "artificial_fixture"
    assert "SIMULATED" in two.after["environment"]["badge"]
    verified(e.journal)


def test_no_preexisting_tests_or_financial_sources_changed():
    frozen = json.loads(Path("docs/demos/evidence/phase13_manifest.json").read_text())
    permitted = {
        "src/quantlab/trading/server.py",
        "src/quantlab/trading/navigation.py",
        "src/quantlab/trading/static/explain.js",
    }
    for name, h in frozen.get("files", frozen).items():
        if name not in permitted:
            assert sha256(Path(name).read_bytes()).hexdigest() == h, name


@pytest.mark.parametrize("key", FLAGSHIPS)
def test_named_capture_states_and_graph_references(key):
    h = Controller().demos
    h.start(key)
    caps = h.capture_names()
    assert caps and len({c["name"] for c in caps}) == len(caps)
    j = journey(h.evidence.spec.concepts)
    assert [s["id"] for s in j["steps"]] == list(h.evidence.spec.concepts)
    for c in caps:
        h.command({"kind": "capture", "payload": {"name": c["name"], "showcase": True}})
        assert h.index == c["index"] and h.revealed == c["result"] and h.showcase
        expected = h.moment.after if c["result"] else h.moment.before
        assert h.state()["active"]["point"] == expected


def test_observer_comparison_uses_actual_signal_quotes_and_mature_reference():
    e = build("picked-off")
    review = e.private["review"]
    signal = review["signals"][0]
    assert signal["estimated_value_GBP"] == "100.18851"
    assert signal["chosen_action"] == "buy"
    assert signal["buy_edge_ticks"] > signal["threshold_ticks"]
    marked = [r for r in review["matured_markouts"] if r["your_order"]]
    assert marked and any(Fraction(r["provider_markout_GBP_per_unit"]) < 0 for r in marked)
    assert all(r["maturity_time_us"] is not None for r in marked)
    assert (
        review["timeline"][0]["last_transaction_GBP"]
        != review["timeline"][0]["latent_value_GBP"]
    )
