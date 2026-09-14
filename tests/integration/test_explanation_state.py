"""Ground explanations in actual core sessions, including replay/privacy attacks."""

import copy
import hashlib
import json
from pathlib import Path

import pytest

from quantlab.explainability.evidence import ground
from quantlab.explainability.examples import EXAMPLES, example
from quantlab.explainability.registry import DEPTHS
from quantlab.options.session import replay_options
from quantlab.risk.analytics import RiskSettings
from quantlab.risk.session import replay_risk
from quantlab.statarb.session import replay as replay_statarb
from quantlab.trading.replay import replay
from quantlab.trading.server import Controller


@pytest.fixture
def c():
    return Controller()


def buy(c, quantity=6):
    return c.command(
        {
            "kind": "order",
            "payload": {"side": "buy", "quantity": quantity, "order_type": "market"},
        }
    )


def initialise(c):
    c.options_lab.state()
    c.risk_lab.session.settings = RiskSettings(paths=100, sample_size=80)
    c.risk_lab.state()
    c.statarb_lab.session.command("step", count=80)
    return c


def test_pending_leg_keeps_signed_intention_separate_from_actual_position(c):
    lab = c.statarb_lab
    lab.session.command("step", count=80)
    lab.session.command("pair", action="long")
    public = lab.state()
    x = c.explanations.explain("leg_risk", lab="statarb")
    assert x["current"]["inputs"]["pending_leg"] == public["pending"]
    assert x["current"]["inputs"]["pending_leg"][0]["quantity"] < 0
    assert "Pending hedge intentions are not positions" in x["current"]["note"]


def test_confidence_interval_explanation_retains_both_reported_endpoints():
    facts = {"ci_low": -1.5, "ci_high": 2.8, "se": 0.9, "unit": "GBP"}
    x = ground("confidence_intervals", {"facts": facts}, "research")
    assert x["value"] == {"ci_low": -1.5, "ci_high": 2.8}
    assert x["unit"] == "GBP"
    assert ground("confidence_intervals", {"facts": {}}, "research")["value"] is None


@pytest.mark.parametrize("depth", DEPTHS)
def test_actual_vwap_exact_trace_and_depth_never_changes_value(c, depth):
    buy(c)
    x = c.explanations.explain("vwap", depth=depth)
    assert x["current"]["value"] == "100.01667"
    assert x["current"]["inputs"]["exact_vwap_gbp"] == "6001/60"
    assert [(f["price"], f["quantity"]) for f in x["current"]["rows"]] == [
        ("100.01000", 2),
        ("100.02000", 4),
    ]
    assert x["depth"] == depth


def test_pnl_change_uses_actual_components_and_does_not_double_count_fees(c):
    c.explanations.observe("trading", c.state())
    buy(c)
    x = c.explanations.explain("pnl")
    assert x["current"]["value"] == "-0.07600"
    assert x["change"]["before"] == "0.00000"
    deltas = {r["input"]: r.get("difference") for r in x["change"]["inputs"]}
    assert deltas["realised"] == -0.006
    assert deltas["unrealised"] == -0.07
    assert deltas["total_pnl"] == pytest.approx(deltas["realised"] + deltas["unrealised"])
    assert "must not be subtracted twice" in x["current"]["note"]
    assert "causal percentages" in x["change"]["label"]


@pytest.mark.parametrize(
    "key", ["delta", "gamma", "vega", "theta", "rho", "implied_volatility", "option_pricing"]
)
def test_option_explanation_matches_selected_quote_and_changed_inputs(c, key):
    lab = c.options_lab
    c.explanations.observe("options", lab.state())
    lab.session.command("step", count=1)
    current = lab.state()
    x = c.explanations.explain(key, lab="options")
    expected = (
        current["selected"]["greeks"].get(key)
        if key in ("delta", "gamma", "vega", "theta", "rho")
        else current["selected"]["iv"]["volatility"]
        if key == "implied_volatility"
        else current["selected"]["model_value"]
    )
    assert x["current"]["value"] == expected
    assert x["current"]["inputs"]["spot"] == current["spot"]
    assert any(r["input"] == "time_years" for r in x["change"]["inputs"])


def test_portfolio_delta_affordance_is_not_per_unit_delta(c):
    lab = c.options_lab
    lab.session.command(
        "option_order",
        contract_id=lab.selected,
        side="buy",
        quantity=2,
        quote_revision=lab.session.quote_revision,
    )
    x = c.explanations.explain("delta", lab="options", selector="portfolio")
    assert x["current"]["value"] == lab.state()["greeks"]["delta"]
    assert x["current"]["value"] != lab.state()["selected"]["greeks"]["delta"]


@pytest.mark.parametrize("method", ["monte_carlo", "historical", "parametric"])
def test_var_has_actual_holdings_settings_and_correct_method(c, method):
    buy(c, 3)
    initialise(c)
    x = c.explanations.explain("var", lab="risk", selector=method)
    r = c.risk_lab.state()["report"][method]
    assert x["current"]["value"] == (r if method == "parametric" else r["full"])["var"]
    assert x["current"]["inputs"]["holdings"][0]["quantity"] == 3
    assert x["current"]["inputs"]["settings"]["confidence"] == 0.95
    assert "risk" in x["concept"]["assumptions"]


def test_zscore_uses_current_residual_and_past_normalisation(c):
    s = c.statarb_lab.session
    s.command("step", count=80)
    c.explanations.observe("statarb", s.state())
    s.command("step", count=1)
    out = c.explanations.explain("z_score", lab="statarb")
    sig = s.state()["signal"]
    assert out["current"]["value"] == sig["z"]
    inputs = out["current"]["inputs"]
    assert (
        inputs["spread"] == sig["spread"]
        and inputs["mean"] == sig["mean"]
        and inputs["sd"] == sig["sd"]
    )
    assert inputs["normalization_end"] == 81 and inputs["fit"]["end"] <= 81
    assert {"spread", "mean", "sd"} <= {r["input"] for r in out["change"]["inputs"]}


def test_missing_history_and_unfilled_vwap_are_unavailable_not_zero(c):
    assert c.explanations.explain("vwap")["current"]["value"] is None
    c.statarb_lab.state()
    assert c.explanations.explain("z_score", lab="statarb")["current"]["value"] is None


def test_future_rows_appended_to_a_historical_state_never_enter_explanation(c):
    c.statarb_lab.session.command("step", count=80)
    s = c.statarb_lab.state()
    before = ground("z_score", s, "statarb")
    s["history"].extend([[99999, 88888], [123456, 654321]])
    assert ground("z_score", s, "statarb") == before


def test_selected_order_and_portfolio_greek_comparisons_use_matching_units(c):
    buy(c, 1)
    c.explanations.observe("trading", c.state())
    buy(c, 2)
    x = c.explanations.explain("vwap", selector="user-1")
    assert x["change"]["before"] == x["change"]["after"] == "100.01000"
    lab = c.options_lab
    lab.session.command(
        "option_order",
        contract_id=lab.selected,
        side="buy",
        quantity=2,
        quote_revision=lab.session.quote_revision,
    )
    prior = lab.state()["greeks"]["delta"]
    c.explanations.observe("options", lab.state())
    lab.session.command("step", count=1)
    x = c.explanations.explain("delta", lab="options", selector="portfolio")
    assert x["change"]["before"] == prior


def test_normal_explanations_ignore_injected_private_and_future_fields(c):
    buy(c)
    s = c.state()
    clean = ground("vwap", s, "trading")
    s["latent_value"] = "PRIVATE_SENTINEL"
    s["future_events"] = ["FUTURE_SENTINEL"]
    s["orders"][-1]["fills"][-1]["counterparty_type"] = "PRIVATE_SENTINEL"
    assert ground("vwap", s, "trading") == clean
    assert "SENTINEL" not in json.dumps(c.explanations.explain("vwap"))


def test_reading_does_not_change_learning_or_financial_state(c):
    buy(c)
    before = copy.deepcopy(c.learning.tutor.progress.data)
    state = copy.deepcopy(c.session.public_snapshot())
    evidence = copy.deepcopy(c.session.evidence)
    for depth in DEPTHS:
        c.explanations.explain("vwap", depth=depth)
    assert before == c.learning.tutor.progress.data
    assert state == c.session.public_snapshot() and evidence == c.session.evidence


def test_post_session_and_explicit_observer_are_separate(c):
    for mode in ("observer", "post_session"):
        with pytest.raises(ValueError, match="ended"):
            c.explanations.explain("markouts", mode=mode, reveal=True)
    c.command({"kind": "step_event"})
    c.command({"kind": "end"})
    with pytest.raises(ValueError, match="Explicit"):
        c.explanations.explain("markouts", mode="observer")
    public = c.explanations.explain("markouts", mode="post_session")
    private = c.explanations.explain("markouts", mode="observer", reveal=True)
    assert "observer" not in public
    assert private["quiz_allowed"] is False and "observer_only" in private["observer"]
    assert "latent_before_ticks" in json.dumps(
        private
    ) and "latent_before_ticks" not in json.dumps(public)


def test_replay_uses_selected_point_and_predecessor_even_after_future_view(c):
    buy(c)
    c.command({"kind": "step_event"})
    c.command({"kind": "end"})
    verified = replay(
        json.loads(
            json.dumps(
                __import__("quantlab.trading.replay", fromlist=["journal"]).journal(c.session)
            )
        ),
        capture_frames=True,
    )
    c.frames = verified.frames
    c.replay_session = verified
    c.frame_index = len(c.frames) - 1
    c.explanations.explain("vwap")
    c.frame_index = 0
    early = c.explanations.explain("vwap")
    assert early["current"]["value"] is None and not early["change"]["available"]
    before = copy.deepcopy(early)
    c.frames[-1]["account"]["total_pnl"] = "999999.00000"
    assert c.explanations.explain("vwap") == before
    with pytest.raises(ValueError):
        c.explanations.explain("vwap", mode="post_session")
    hook = c.explanations.replay_hook("trading")
    assert hook["pre"] is None and hook["post"]["vwap"]["value"] is None


@pytest.mark.parametrize("lab", ["options", "risk", "statarb"])
def test_all_lab_replays_cannot_explain_later_state(c, lab):
    obj = getattr(c, lab + "_lab")
    if lab == "options":
        obj.session.command("step", count=2)
        obj.session.command("end")
        verified = replay_options(obj.session.journal(), capture_frames=True)
        frames = verified.frames
        key = "delta"
    elif lab == "risk":
        obj.session.execute("desk", "order", side="buy", quantity=1, order_type="market")
        obj.session.execute("risk", "end")
        verified, frames = replay_risk(obj.session.journal(), frames=True)
        key = "var"
    else:
        obj.session.command("step", count=82)
        obj.session.command("end")
        verified, frames = replay_statarb(obj.session.journal(), frames=True)
        key = "z_score"
    obj.session = verified
    obj.frames = frames
    obj.frame_index = len(frames) - 1
    c.explanations.explain(key, lab=lab)
    obj.frame_index = 0
    first = c.explanations.explain(key, lab=lab)
    assert first["current"] == ground(key, frames[0], lab)
    assert not first["change"]["available"]
    frames[-1]["FUTURE_SENTINEL"] = "private"
    assert c.explanations.explain(key, lab=lab) == first


def test_explanation_quiz_uses_actual_fills_without_awarding_mastery(c):
    buy(c)
    attempts = sum(
        v.get("attempts", 0) for v in c.learning.tutor.progress.data["concepts"].values()
    )
    v = c.explanations.quiz("vwap")
    assert v["current"]["question"]["concept"] == "vwap"
    assert c.learning.tutor.active["context"]["facts"]["filled"] == 6
    assert (
        sum(r.get("attempts", 0) for r in c.learning.tutor.progress.data["concepts"].values())
        == attempts
    )


@pytest.mark.parametrize("id", tuple(EXAMPLES))
def test_guided_examples_are_independent_and_engine_backed(id, c):
    before = c.session.public_snapshot()
    progress = copy.deepcopy(c.learning.tutor.progress.data)
    a = example(id)
    b = example(id)
    assert a == b and a["label"] == "INDEPENDENT GUIDED EXAMPLE — NOT YOUR SESSION"
    assert c.session.public_snapshot() == before and c.learning.tutor.progress.data == progress


def test_original_tests_and_financial_modules_remain_byte_identical():
    root = Path(__file__).resolve().parents[2]
    manifest = json.loads(
        (root / "docs/explainability/evidence/baseline_manifest.json").read_text()
    )
    adapters = {"src/quantlab/trading/server.py", "src/quantlab/trading/navigation.py"}
    for path, expected in manifest.items():
        if path not in adapters:
            assert hashlib.sha256((root / path).read_bytes()).hexdigest() == expected, path
