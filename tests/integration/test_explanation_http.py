"""Real HTTP contracts, tokens, responses and mutation isolation."""

import copy
import json

import pytest

from tests.integration.test_trading_http import command, request
from tests.integration.test_trading_http import service as http_service


@pytest.fixture
def service(tmp_path):
    yield from http_service.__wrapped__(tmp_path)


def explain(service, action="explain", **payload):
    status, _, body = request(
        service,
        "POST",
        "/api/explanations",
        json.dumps({"kind": action, "payload": payload}),
        {"Content-Type": "application/json", "X-QuantLab-Token": service.controller.token},
    )
    return status, json.loads(body)


def test_http_trace_matches_browser_display_value_and_keeps_original_outcome(service):
    command(service, "order", side="buy", quantity=6, order_type="market")
    status, x = explain(service, concept="vwap")
    assert (
        status == 200
        and x["current"]["value"] == service.controller.state()["orders"][-1]["vwap"]
    )
    assert len(x["current"]["rows"]) == 2
    assert "private" not in x["current"]["inputs"]
    assert explain(service, concept="pnl")[1]["change"]["available"]


def test_http_what_if_and_reading_never_award_mastery_or_make_trades(service):
    c = service.controller
    before = copy.deepcopy(c.learning.tutor.progress.data)
    state = c.session.public_snapshot()
    assert (
        explain(service, "what_if", kind="order_size", lab="trading", inputs={"quantity": 20})[
            0
        ]
        == 200
    )
    assert explain(service, concept="spread")[0] == 200
    assert c.session.public_snapshot() == state and before == c.learning.tutor.progress.data


@pytest.mark.parametrize(
    "path", ["/", "/options", "/risk", "/statarb", "/research", "/learning", "/explain"]
)
def test_shared_explanation_assets_and_local_only_navigation(service, path):
    status, _, body = request(service, path=path)
    assert status == 200 and b"/explain.js" in body and b"/explain.css" in body
    assert b'href="/explain"' in body


def test_search_registry_and_malicious_payloads(service):
    status, _, body = request(
        service, path="/api/explanations/search?q=Why%20did%20VaR%20rise%3F"
    )
    assert status == 200 and json.loads(body)["results"][0]["id"] == "var"
    status, _, body = request(service, path="/api/explanations")
    assert status == 200 and len(json.loads(body)["concepts"]) >= 70
    for payload in (
        {"concept": "../private"},
        {"concept": "var", "lab": "missing"},
        {"concept": "vwap", "source": "historical"},
        {"concept": "vwap", "mode": "observer", "reveal": True},
        {"concept": "vwap", "private": True},
    ):
        assert explain(service, **payload)[0] == 400
    assert (
        request(
            service, "POST", "/api/explanations", "{}", {"Content-Type": "application/json"}
        )[0]
        == 403
    )


def test_actual_quote_request_includes_public_inputs_and_not_automatic_skew(service):
    command(service, "new", mode="manual_maker")
    status, _ = command(
        service,
        "quotes",
        bid_distance="2",
        ask_distance="3",
        bid_size=2,
        ask_size=3,
        shift="-1",
    )
    assert status == 200
    status, x = explain(service, concept="quote_skew", lab="maker")
    assert status == 200
    assert (
        x["current"]["inputs"]["last_actual_manual_quote_request"]["request"]["shift"] == "-1"
    )
    assert x["current"]["inputs"]["own_resting_orders"]


def test_explanation_retention_failure_cannot_turn_executed_trade_into_failed_response(
    service, monkeypatch
):
    def fail(*args, **kwargs):
        raise ValueError("projection unavailable")

    monkeypatch.setattr(service.controller.explanations, "observe", fail)
    status, r = command(service, "order", side="buy", quantity=1, order_type="market")
    assert status == 200 and r["result"]["ok"]
    assert service.controller.session.account.inventory == 1
