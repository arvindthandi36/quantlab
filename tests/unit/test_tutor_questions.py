from dataclasses import replace
from fractions import Fraction

import pytest

from quantlab.trading.server import Controller
from quantlab.tutor.catalog import CONCEPTS
from quantlab.tutor.context import PublicContext, context_from_dict, trading_contexts
from quantlab.tutor.questions import question_for, relevant


@pytest.fixture
def trade():
    controller = Controller()
    controller.command(
        {"kind": "order", "payload": {"side": "buy", "order_type": "market", "quantity": 6}}
    )
    return controller.learning.tutor.contexts["vwap"]


def test_vwap_uses_actual_units_not_unweighted_price_levels(trade):
    q = question_for("vwap", trade, 2)
    assert q.answer_type == "number" and Fraction(q.expected) == Fraction(6001, 60)
    assert q.validate("100.01667")
    assert not q.validate("100.015")
    assert "2×£100.01 + 4×£100.02" in q.maths
    assert "100.01667" in q.maths
    assert "expected" not in q.public()
    assert "layers" not in q.public()
    assert set(q.public(True)["layers"]) == {"intuition", "maths", "quantlab", "interview"}


def test_option_order_is_reproducible_without_a_correct_position_shortcut(trade):
    correct_positions = set()
    for concept in CONCEPTS.values():
        if not concept.implemented:
            continue
        question = question_for(concept.id, trade)
        options = question.public()["options"]
        assert options == question.public(True)["options"]
        assert options == replace(question, options=question.options[::-1]).public()["options"]
        if question.answer_type == "choice":
            correct_positions.add([o["id"] for o in options].index(question.expected))
            assert question.validate(question.expected)
    assert len(correct_positions) > 1


@pytest.mark.parametrize(
    "answer",
    ["", "NaN", "inf", "£100.01667", "one hundred", "1/0", [], {}, True, 100.01667, "1" * 101],
)
def test_numeric_validator_rejects_nonsense(trade, answer):
    with pytest.raises(ValueError):
        question_for("vwap", trade, 2).validate(answer)


@pytest.mark.parametrize(
    "answer", ["yes absolutely", "weighted midpoint", "", None, [], {"weighted": True}, True]
)
def test_conceptual_validator_never_uses_substring_guessing(trade, answer):
    with pytest.raises(ValueError):
        question_for("vwap", trade).validate(answer)


def test_reason_sets_require_complete_correct_reasoning(trade):
    q = question_for("vwap", trade, 3)
    assert q.validate(["scope", "mechanism"])
    assert not q.validate(["mechanism"])
    assert not q.validate(["mechanism", "guarantee"])
    with pytest.raises(ValueError):
        q.validate(["mechanism", "mechanism"])
    with pytest.raises(ValueError):
        q.validate(["nonsense"])


@pytest.mark.parametrize("key", [k for k, c in CONCEPTS.items() if not c.implemented])
def test_future_material_cannot_be_quizzed(trade, key):
    with pytest.raises(ValueError, match="later phase"):
        question_for(key, trade)


def test_every_implemented_concept_has_its_own_valid_question(trade):
    for key, concept in CONCEPTS.items():
        if concept.implemented:
            q = question_for(key, trade, 1)
            assert q.validate(q.expected)
            assert q.intuition and q.maths and q.interview
            assert q.concept == key
    assert (
        question_for("variance", trade).prompt != question_for("standard_error", trade).prompt
    )
    assert "squared" in question_for("variance", trade).options[0][1]


def test_context_is_frozen_and_allowlisted(trade):
    raw = trade.public()
    raw["facts"]["fills"][0]["quantity"] = 99
    assert trade.facts["fills"][0]["quantity"] == 2
    with pytest.raises(TypeError):
        trade.facts["position"] = 99
    with pytest.raises(TypeError):
        trade.facts["fills"][0]["quantity"] = 99
    leaked = trade.public()
    leaked["facts"]["latent_ticks"] = 10001
    with pytest.raises(ValueError, match="Non-public"):
        context_from_dict(leaked)


@pytest.mark.parametrize(
    "hidden",
    [
        "informed",
        "signal",
        "counterparty_type",
        "next_event_time_us",
        "future_price",
        "future_markout",
    ],
)
def test_unknown_context_fields_fail_closed(trade, hidden):
    raw = trade.public()
    raw["facts"][hidden] = 999
    with pytest.raises(ValueError):
        context_from_dict(raw)


def test_no_hidden_counterparty_fields_in_fill_context(trade):
    raw = trade.public()
    raw["facts"]["fills"][0]["counterparty_type"] = "informed"
    with pytest.raises(ValueError, match="counterparty"):
        context_from_dict(raw)


def test_matured_marks_only_and_future_time_filtered():
    c = Controller()
    snapshot = c.state()
    base = {
        "trade_id": 1,
        "role": "provider",
        "horizon": 1,
        "status": "pending",
        "observed_time_us": None,
        "value": None,
    }
    snapshot["markouts"] = [
        base,
        base | {"status": "matured", "observed_time_us": 1, "value": "-0.1"},
    ]
    assert all(x.kind != "markout" for x in trading_contexts(snapshot, "s"))
    snapshot["time_us"] = 1
    context = trading_contexts(snapshot, "s")[-1]
    assert context.kind == "markout"
    assert ("adverse_selection", 98) in relevant(context)
    q = question_for("adverse_selection", context)
    assert "without proving" in q.intuition and q.validate("no")


def test_market_input_unknown_hidden_data_never_copied():
    c = Controller()
    snapshot = c.state()
    snapshot.update(latent_ticks=999999, informed={"signal": 11111}, next_event_time_us=123)
    contexts = trading_contexts(snapshot, "s")
    assert "999999" not in str([x.public() for x in contexts])
    assert "next_event_time_us" not in str([x.public() for x in contexts])


@pytest.mark.parametrize("position,expected", [(4, "0.2"), (-4, "-0.2"), (0, "0")])
def test_signed_exposure_calculation(position, expected):
    context = PublicContext(
        "s",
        "position",
        2,
        1,
        {
            "position": position,
            "limit": 20,
            "reference": "100",
            "realised": "0",
            "unrealised": "0",
            "pnl": "0",
            "drawdown": "0",
        },
    )
    q = question_for("exposure", context, 2)
    assert q.validate(expected)
    assert "Hypothetical, not a forecast" in q.prompt


def test_partial_fill_calculation_respects_cancelled_remainder(trade):
    raw = trade.public()
    raw["facts"].update(original=10, filled=6, remaining=0, cancelled=4)
    q = question_for("partial_fills", context_from_dict(raw), 2)
    assert q.validate("0") and not q.validate("4")


def test_predict_question_refers_only_to_the_observed_book():
    c = Controller()
    context = trading_contexts(c.state(), "s")[0]
    q = question_for("limit_orders", context, prediction=True)
    assert "£100" in q.prompt and "£100.01" in q.prompt
    assert q.validate("no")
    assert "Future changes are unknown" in q.intuition


def test_extreme_exponent_is_rejected_before_big_integer_allocation(trade):
    with pytest.raises(ValueError):
        question_for("vwap", trade, 2).validate("1e999999999")
