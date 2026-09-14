import json

import pytest

from tests.integration.test_trading_http import request
from tests.integration.test_trading_http import service as http_service


@pytest.fixture
def service(tmp_path):
    yield from http_service.__wrapped__(tmp_path)


def command(server, kind, **payload):
    status, _, body = request(
        server,
        "POST",
        "/api/statarb",
        json.dumps(dict(kind=kind, payload=payload)),
        {"Content-Type": "application/json", "X-QuantLab-Token": server.controller.token},
    )
    return status, json.loads(body)


@pytest.mark.parametrize(
    "path,mime",
    [
        ("/statarb", "text/html"),
        ("/statarb.js", "text/javascript"),
        ("/statarb.css", "text/css"),
        ("/api/statarb", "application/json"),
    ],
)
def test_surfaces(service, path, mime):
    status, headers, body = request(service, path=path)
    assert status == 200 and headers["Content-Type"].startswith(mime) and body


@pytest.mark.parametrize(
    "headers", [{}, {"X-QuantLab-Token": "wrong"}, {"Origin": "https://elsewhere.example"}]
)
def test_mutations_require_token_and_same_origin(service, headers):
    assert request(service, "POST", "/api/statarb", '{"kind":"end"}', headers)[0] == 403
    assert service.controller._statarb_lab is None


def test_http_acceptance_flow_and_replay(service):
    assert command(service, "step", count=80)[0] == 200
    assert command(service, "liquidity", instrument="SA-X", depth=0)[1]["result"]["ok"]
    _, r = command(service, "pair", action="long")
    assert len(r["state"]["pending"]) == 1
    _, r = command(service, "next_leg")
    assert r["state"]["markets"][0]["position"] == 0
    assert r["state"]["markets"][1]["position"] > 0
    assert request(service, path="/api/statarb/journal")[0] == 400
    command(service, "end")
    status, _, raw = request(service, path="/api/statarb/journal")
    assert status == 200
    _, r = command(service, "load_replay", journal_text=raw.decode())
    assert r["state"]["replay"]
    assert command(service, "pair", action="short")[0] == 400
    command(service, "replay_frame", index=r["state"]["frame_count"] - 1)
    assert request(service, path="/api/statarb/journal")[0] == 200


@pytest.mark.parametrize(
    "raw", ["[]", '{"kind":"wait","secret":1}', '{"kind":"new","payload":NaN}']
)
def test_invalid_envelope(service, raw):
    status, _, _ = request(
        service,
        "POST",
        "/api/statarb",
        raw,
        {"Content-Type": "application/json", "X-QuantLab-Token": service.controller.token},
    )
    assert status == 400


def test_new_does_not_discard_active_history(service):
    command(service, "step", count=80)
    assert command(service, "new")[0] == 400
    command(service, "end")
    _, r = command(service, "new", scenario_name="drift", rules={"mode": "walk_forward"})
    assert r["state"]["t"] == 0 and not r["state"]["fills"]
