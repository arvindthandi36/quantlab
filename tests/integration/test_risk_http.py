import json

import pytest

from tests.integration.test_trading_http import request
from tests.integration.test_trading_http import service as http_service


@pytest.fixture
def service(tmp_path):
    yield from http_service.__wrapped__(tmp_path)


def command(server, kind, **p):
    status, _, raw = request(
        server,
        "POST",
        "/api/risk",
        json.dumps({"kind": kind, "payload": p}),
        {"Content-Type": "application/json", "X-QuantLab-Token": server.controller.token},
    )
    return status, json.loads(raw)


@pytest.mark.parametrize(
    "path,mime",
    [
        ("/risk", "text/html"),
        ("/risk.js", "text/javascript"),
        ("/risk.css", "text/css"),
        ("/api/risk", "application/json"),
    ],
)
def test_risk_surfaces(service, path, mime):
    status, headers, raw = request(service, path=path)
    assert status == 200 and headers["Content-Type"].startswith(mime) and raw
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]


@pytest.mark.parametrize(
    "headers", [{}, {"X-QuantLab-Token": "wrong"}, {"Origin": "https://elsewhere.example"}]
)
def test_risk_secure_mutations(service, headers):
    status, _, _ = request(service, "POST", "/api/risk", '{"kind":"end"}', headers)
    assert status == 403 and service.controller._risk_lab is None


def test_risk_http_trade_hedge_stress_and_replay(service):
    s = service.controller.risk_lab.session
    status, r = command(
        service,
        "trade",
        target="options",
        command="option_order",
        fields=dict(
            contract_id=s.options.selected,
            side="buy",
            quantity=1,
            quote_revision=s.options.quote_revision,
        ),
    )
    assert status == 200 and r["state"]["trading"]["option_fills"] == 1
    assert request(service, path="/api/risk/journal")[0] == 400
    assert command(service, "trade", target="options", command="hedge", fields={})[0] == 200
    assert command(service, "scenario", stock_return=-0.08, volatility_change=0.12)[0] == 200
    assert command(service, "end")[0] == 200
    status, _, raw = request(service, path="/api/risk/journal")
    assert status == 200
    status, r = command(service, "load_replay", journal_text=raw.decode())
    assert status == 200 and r["state"]["frame_index"] == 0
    assert command(service, "scenario", stock_return=-0.1)[0] == 400
    assert command(service, "replay_frame", index=r["state"]["frame_count"] - 1)[0] == 200


@pytest.mark.parametrize(
    "kind,p",
    [
        ("covariance", {"matrix": [[1, 2, 0], [2, 1, 0], [0, 0, 1]]}),
        ("settings", {"correlation": -1}),
        ("scenario", {"stock_return": -2}),
        ("optimise", {"max_cash": 0, "max_weight": 0.1}),
    ],
)
def test_invalid_risk_requests_are_explained_and_accounts_unchanged(service, kind, p):
    before = service.controller.risk_lab.session.portfolio().public()
    status, r = command(service, kind, **p)
    assert status == 400 and r["error"]
    assert service.controller.risk_lab.session.portfolio().public() == before
