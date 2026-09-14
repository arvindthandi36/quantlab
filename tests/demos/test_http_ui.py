import json
from pathlib import Path

import pytest

from tests.integration.test_trading_http import request
from tests.integration.test_trading_http import service as http_service


@pytest.fixture
def service(tmp_path):
    yield from http_service.__wrapped__(tmp_path)


def send(service, kind, **p):
    code, _, body = request(
        service,
        "POST",
        "/api/demos",
        json.dumps({"kind": kind, "payload": p}),
        {"Content-Type": "application/json", "X-QuantLab-Token": service.controller.token},
    )
    return code, json.loads(body)


@pytest.mark.parametrize(
    "path,mime",
    [("/demos", "text/html"), ("/demos.js", "text/javascript"), ("/demos.css", "text/css")],
)
def test_demo_assets_same_local_security_and_cache_contract(service, path, mime):
    code, headers, body = request(service, path=path)
    assert code == 200 and headers["Content-Type"].startswith(mime) and body
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
    assert headers["Cache-Control"] == "no-store"


def test_demo_page_has_own_source_label_not_personal_environment_banner(service):
    _, _, body = request(service, path="/demos")
    text = body.decode()
    assert "/markets.js" not in text and "/explain.js" in text and "/demos.js" in text
    assert 'href="/demos"' in text
    _, _, body = request(service, path="/")
    assert "/markets.js" in body.decode()


def test_demo_commands_require_session_token(service):
    status, _, _ = request(
        service, "POST", "/api/demos", '{"kind":"next"}', {"Content-Type": "application/json"}
    )
    assert status == 403


def test_http_lifecycle_explain_script_and_path_preserve_personal_account(service):
    _, _, before = request(service, path="/api/state")
    code, v = send(service, "start", id="order", mode="learn")
    assert code == 200
    assert v["active"]["phase"] == "PREDICT"
    code, d = send(service, "explain", concept="vwap")
    assert code == 200 and d["demo_context"]
    code, _, _ = request(service, path="/api/demos/script.md")
    assert code == 400
    code, v = send(service, "next")
    assert v["active"]["point"]["core"]["orders"][0]["vwap"] == "100.02300"
    send(service, "next")
    code, headers, body = request(service, path="/api/demos/script.md")
    assert (
        code == 200
        and headers["Content-Type"].startswith("text/markdown")
        and b"100.02300" in body
    )
    code, _, body = request(service, path="/api/demos/path.json")
    assert code == 200
    assert json.loads(body)["digest"]
    _, _, after = request(service, path="/api/state")
    assert after == before


def test_global_teach_entry_is_available_only_after_session_end(service):
    _, _, body = request(service, path="/api/demos/availability")
    assert not json.loads(body)["available_sessions"]
    service.controller.command({"kind": "end"})
    _, _, body = request(service, path="/api/demos/availability")
    assert json.loads(body)["available_sessions"][0]["id"] == "trading"
    code, v = send(service, "teach_current", lab="trading")
    assert code == 200 and v["active"]["spec"]["id"] == "your-session"


def test_recording_controls_do_not_mutate_financial_state_and_keep_required_labels(service):
    _, v = send(service, "start", id="historical")
    before = v["active"]["point"]
    code, v = send(service, "recording", enabled=True, large_text=True)
    assert code == 200 and v["recording"] and v["large_text"] and v["active"]["point"] == before
    assert "SIMULATED HISTORICAL EXECUTION" in v["active"]["point"]["environment"]["badge"]
    assert v["active"]["limitations"]


def test_ui_only_renders_python_financial_data_and_is_responsive():
    js = Path("src/quantlab/trading/static/demos.js").read_text()
    css = Path("src/quantlab/trading/static/demos.css").read_text()
    assert "Math.random" not in js and "eval(" not in js
    for forbidden in (
        "function blackScholes",
        "function calculateVwap",
        "function computeVar",
        "norm.cdf",
        "Math.log(",
    ):
        assert forbidden not in js
    assert "@media(max-width:480px)" in css and "grid-template-columns:1fr" in css
    assert "data-required-badge" in js and "data-required-limitations" in js
    assert ".demo-recording .demo-limitations" not in css
    assert "quantlab-demo-explain" in js
    assert "Enter showcase capture" in js and "No video is recorded." in js
