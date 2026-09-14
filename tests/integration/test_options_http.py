import json

import pytest

from tests.integration.test_trading_http import request
from tests.integration.test_trading_http import service as http_service


@pytest.fixture
def service(tmp_path):
    yield from http_service.__wrapped__(tmp_path)


def command(server, kind, **payload):
    status, _, data = request(
        server,
        "POST",
        "/api/options",
        json.dumps({"kind": kind, "payload": payload}),
        {"Content-Type": "application/json", "X-QuantLab-Token": server.controller.token},
    )
    return status, json.loads(data)


@pytest.mark.parametrize(
    "path,mime",
    [
        ("/options", "text/html"),
        ("/options.js", "text/javascript"),
        ("/options.css", "text/css"),
        ("/api/options", "application/json"),
    ],
)
def test_options_surfaces_share_secure_local_server(service, path, mime):
    status, headers, raw = request(service, path=path)
    assert status == 200 and headers["Content-Type"].startswith(mime) and raw
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]


@pytest.mark.parametrize(
    "headers", [{}, {"X-QuantLab-Token": "wrong"}, {"Origin": "https://elsewhere.example"}]
)
def test_options_mutations_require_same_origin_and_token(service, headers):
    status, _, _ = request(service, "POST", "/api/options", '{"kind":"hedge"}', headers)
    assert status == 403 and not service.controller.options_lab.session.actions


def test_manual_option_and_real_stock_hedge_http_then_replay(service, tmp_path):
    service.controller.options_lab.directory = tmp_path / "options"
    q = service.controller.options_lab.state()["selected"]
    status, data = command(
        service,
        "option_order",
        contract_id=q["id"],
        side="buy",
        quantity=1,
        quote_revision=q["revision"],
    )
    assert status == 200
    assert data["result"]["premium"] == q["ask"]
    assert data["state"]["accounts"]["option_cash"] == pytest.approx(-100 * q["ask"] - 0.05)
    assert request(service, path="/api/options/journal")[0] == 400
    assert command(service, "stock_order", side="sell", quantity=51)[0] == 200
    assert service.controller.options_lab.session.stock.book.traded_volume == 51
    assert command(service, "step", count=1)[0] == 200
    assert command(service, "hedge")[0] == 200
    command(service, "end")
    status, _, raw = request(service, path="/api/options/journal")
    assert status == 200
    status, data = command(service, "load_replay", journal=json.loads(raw))
    assert status == 200 and data["state"]["step"] == 0
    assert command(service, "hedge")[0] == 400


def test_invalid_option_analysis_does_not_mutate_financial_state(service):
    s = service.controller.options_lab.session
    before = s.snapshot()
    assert command(service, "iv", market_price=101)[0] == 400
    assert command(service, "shock", volatility_change=-20)[0] == 400
    assert command(service, "mc", paths=1)[0] == 400
    assert s.snapshot() == before


def test_browser_replay_upload_preserves_original_numeric_json(service, tmp_path):
    service.controller.options_lab.directory = tmp_path / "options"
    command(service, "new", spot=100.0, step_days=1.0)
    command(service, "step", count=1)
    command(service, "end")
    status, _, raw = request(service, path="/api/options/journal")
    assert status == 200
    # A browser JSON.parse/stringify turns 100.0 into 100 and breaks the checksum.
    # Upload the original text as a string so its numerical representations survive.
    text = raw.decode()
    assert "100.0" in text
    status, data = command(service, "load_replay", journal_text=text)
    assert status == 200 and data["state"]["frame_index"] == 0
    assert data["state"]["step"] == 0
    assert command(service, "replay_frame", index=data["state"]["frame_count"] - 1)[0] == 200
    assert service.controller.options_lab.journal() == json.loads(text)
