import json
import threading
from http.client import HTTPConnection

import pytest

from quantlab.trading.replay import dumps, loads
from quantlab.trading.server import Controller, TradingServer


@pytest.fixture
def service(tmp_path):
    server = TradingServer(("127.0.0.1", 0), Controller(tmp_path / "sessions"))
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    yield server
    server.shutdown()
    server.server_close()
    worker.join()


def request(server, method="GET", path="/api/state", body=None, headers=None):
    connection = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    connection.request(method, path, body=body, headers=headers or {})
    response = connection.getresponse()
    result = response.status, dict(response.getheaders()), response.read()
    connection.close()
    return result


def command(server, kind, **payload):
    status, _, data = request(
        server,
        "POST",
        "/api/command",
        json.dumps({"kind": kind, "payload": payload}),
        {"Content-Type": "application/json", "X-QuantLab-Token": server.controller.token},
    )
    return status, json.loads(data)


@pytest.mark.parametrize(
    "path,mime",
    [("/", "text/html"), ("/app.js", "text/javascript"), ("/style.css", "text/css")],
)
def test_bundled_assets_are_served_locally(service, path, mime):
    status, headers, data = request(service, path=path)
    assert status == 200 and headers["Content-Type"].startswith(mime) and data
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
    assert headers["Cache-Control"] == "no-store"


def test_http_order_cancel_report_export_and_auto_saved_replay(service):
    status, body = command(service, "order", side="buy", order_type="market", quantity=6)
    assert status == 200 and body["state"]["account"]["position"] == 6
    assert body["state"]["orders"][0]["vwap_exact_ticks"] == "30005/3"
    command(service, "order", side="buy", order_type="limit", quantity=5, price="99.98")
    status, result = command(service, "cancel", order_id="user-2")
    assert status == 200 and result["result"]["cancelled"] == ["user-2"]
    assert request(service, path="/api/journal")[0] == 400
    command(service, "end")
    status, headers, data = request(service, path="/api/journal")
    assert status == 200 and "attachment" in headers["Content-Disposition"]
    verified = loads(data)
    assert verified.account.inventory == 6 and verified.status == "ended"
    saved = list(service.controller.save_directory.glob("*.json"))
    assert len(saved) == 1 and loads(saved[0].read_text()).evidence == verified.evidence


@pytest.mark.parametrize(
    "extra",
    [
        {},
        {"X-QuantLab-Token": "wrong"},
        {"Origin": "https://untrusted.example"},
        {"Host": "untrusted.example"},
    ],
)
def test_mutation_rejects_missing_token_cross_origin_and_bad_host(service, extra):
    headers = {"Content-Type": "application/json"}
    if "Origin" in extra or "Host" in extra:
        headers["X-QuantLab-Token"] = service.controller.token
    status, _, _ = request(service, "POST", "/api/command", '{"kind":"start"}', headers | extra)
    assert status == 403 and service.controller.session.status == "paused"


def test_no_paths_or_raw_observer_state_in_http(service):
    assert request(service, path="/../pyproject.toml")[0] == 404
    assert request(service, path="/api/debug")[0] == 404
    assert request(service, headers={"Host": "untrusted.example"})[0] == 403
    status, _, data = request(service)
    assert status == 200
    text = data.decode()
    assert "latent_ticks" not in text and "informed_arrival" not in text


def test_http_rejects_bad_json_without_changing_exchange(service):
    before = service.controller.session.book.snapshot()
    status, _, _ = request(
        service,
        "POST",
        "/api/command",
        "{bad",
        {"Content-Type": "application/json", "X-QuantLab-Token": service.controller.token},
    )
    assert status == 400
    assert service.controller.session.book.snapshot() == before


def test_server_clock_command_not_exposed_and_unknown_cancel_honest(service):
    assert command(service, "advance", delta_us=1)[0] == 400
    status, result = command(service, "cancel", order_id="no-such-order")
    assert status == 200 and result["result"]["ok"] is False


def test_browser_upload_preserves_original_numeric_representations(service):
    command(service, "step_interval", delta_us=2_000_000)
    command(service, "end")
    original = dumps(service.controller.session)
    assert "10000.0" in original
    status, result = command(service, "load_replay", journal_text=original)
    assert status == 200 and result["result"]["ok"]
    assert result["state"]["replay"]
