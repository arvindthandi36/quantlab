import json

import pytest

from tests.integration.test_trading_http import command, request
from tests.integration.test_trading_http import service as http_service


@pytest.fixture
def service(tmp_path):
    yield from http_service.__wrapped__(tmp_path)


def teach(server, kind, **payload):
    status, _, data = request(
        server,
        "POST",
        "/api/tutor",
        json.dumps({"kind": kind, "payload": payload}),
        {"Content-Type": "application/json", "X-QuantLab-Token": server.controller.token},
    )
    return status, json.loads(data)


@pytest.mark.parametrize(
    "path,mime",
    [
        ("/learning", "text/html"),
        ("/tutor.js", "text/javascript"),
        ("/tutor.css", "text/css"),
        ("/api/tutor", "application/json"),
        ("/api/learning", "application/json"),
        ("/api/learning/export.json", "application/json"),
        ("/api/learning/export.md", "text/markdown"),
    ],
)
def test_local_tutor_surfaces_and_exports(service, path, mime):
    status, headers, body = request(service, path=path)
    assert status == 200 and headers["Content-Type"].startswith(mime)
    assert body and "frame-ancestors 'none'" in headers["Content-Security-Policy"]


def test_actual_http_trade_answer_and_export(service):
    command(service, "order", side="buy", quantity=6, order_type="market")
    _, _, raw = request(service, path="/api/tutor")
    current = json.loads(raw)["current"]
    status, result = teach(service, "answer", question_id=current["id"], answer="mid")
    assert status == 200 and "Not yet" in result["current"]["feedback"]
    status, result = teach(service, "answer", question_id=current["id"], answer="weighted")
    assert status == 200 and "layers" in result["current"]["question"]
    _, _, raw = request(service, path="/api/learning/export.json")
    export = json.loads(raw)
    assert export["learning"]["recent"][-1]["result"] == "correct_after_hint"


@pytest.mark.parametrize(
    "extra",
    [
        {},
        {"X-QuantLab-Token": "wrong"},
        {"Origin": "https://untrusted.example"},
        {"Host": "untrusted.example"},
    ],
)
def test_learning_mutations_use_same_origin_and_token_checks(service, extra):
    headers = {"Content-Type": "application/json"}
    if "Origin" in extra or "Host" in extra:
        headers["X-QuantLab-Token"] = service.controller.token
    status, _, _ = request(service, "POST", "/api/tutor", '{"kind":"explain"}', headers | extra)
    assert status == 403
    assert not service.controller.learning.tutor.progress.data["recent"]


@pytest.mark.parametrize(
    "payload",
    [
        {"concept": "vwap", "context": {"latent_ticks": 123}},
        {"concept": "vwap", "difficulty": 4},
        {"concept": "option_pricing"},
    ],
)
def test_client_cannot_supply_private_context_or_force_future_curriculum(service, payload):
    status, result = teach(service, "quiz", **payload)
    assert status == 400 and result["error"]
    assert service.controller.session.actions == []


def test_unknown_tutor_action_does_not_reach_market(service):
    before = service.controller.state()
    status, _ = teach(service, "order", side="buy", quantity=3)
    assert status == 400 and service.controller.state() == before


def test_observer_http_is_explicit_post_session_only(service):
    assert request(service, path="/api/tutor/observer")[0] == 404
    assert teach(service, "observer", reveal=True)[0] == 400
    command(service, "step_interval", delta_us=2_000_000)
    command(service, "end")
    assert teach(service, "observer", reveal=False)[0] == 400
    status, hidden = teach(service, "observer", reveal=True)
    assert status == 200 and hidden["observer_only"]
    for path in (
        "/api/state",
        "/api/tutor",
        "/api/learning/export.json",
        "/api/learning/export.md",
    ):
        _, _, body = request(service, path=path)
        assert b"latent_after_ticks" not in body and b"signal_error_ticks" not in body


def test_research_route_uses_registry_not_arbitrary_filesystem(service):
    assert teach(service, "research", experiment="../../README.md")[0] == 400
    assert teach(service, "research", experiment="/etc/passwd")[0] == 400


def test_invalid_answer_does_not_add_mastery_evidence(service):
    command(service, "order", side="buy", quantity=6, order_type="market")
    identifier = service.controller.learning.tutor.active["id"]
    assert (
        teach(service, "answer", question_id=identifier, answer="weighted or whatever")[0]
        == 400
    )
    assert service.controller.learning.tutor.progress.data["recent"] == []
