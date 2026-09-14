"""Local concurrent requests and public information boundaries across shared accounts."""

import json
from concurrent.futures import ThreadPoolExecutor

import pytest

from quantlab.trading.server import Controller
from tests.integration.test_trading_http import command, request
from tests.integration.test_trading_http import service as http_service


@pytest.fixture
def service(tmp_path):
    yield from http_service.__wrapped__(tmp_path)


def test_duplicate_submission_serializes_as_two_orders_and_cancel_refresh_is_safe(service):
    def submit(_):
        return command(service, "order", side="buy", quantity=2, order_type="market")

    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(submit, range(2)))
    assert all(status == 200 and body["result"]["ok"] for status, body in results)
    assert service.controller.session.account.inventory == 4
    assert len(service.controller.session.orders) == 2
    _, r = command(service, "order", side="buy", quantity=1, order_type="limit", price="90")
    oid = r["result"]["order_id"]
    with ThreadPoolExecutor(2) as pool:
        cancel = pool.submit(command, service, "cancel", order_id=oid)
        refresh = pool.submit(request, service, path="/api/state")
        assert cancel.result()[0] == 200 and refresh.result()[0] == 200
    service.controller.session.check_invariants()
    assert not service.controller.session.orders[oid].remaining


def test_end_twice_replay_twice_and_private_evidence_gated(service):
    command(service, "order", side="buy", quantity=1, order_type="market")
    with ThreadPoolExecutor(2) as pool:
        list(pool.map(lambda _: command(service, "end"), range(2)))
    service.controller.session.check_invariants()
    _, _, raw = request(service, path="/api/journal")
    for _ in range(2):
        status, result = command(service, "load_replay", journal_text=raw.decode())
        assert status == 200 and result["state"]["replay"]
        assert result["state"]["time_us"] == 0
    assert "latent" not in json.dumps(result["state"])
    assert request(service, path="/api/journal")[0] == 400
    with pytest.raises(ValueError, match="ended"):
        service.controller.tutor_command({"kind": "observer", "payload": {"reveal": True}})


def test_shared_options_reads_during_risk_mutation_reconcile(service):
    c = service.controller
    assert c.risk_lab.session is not None

    def trade(_):
        body = {
            "kind": "stock_order",
            "payload": {"side": "buy", "quantity": 1, "order_type": "market"},
        }
        return request(
            service,
            "POST",
            "/api/options",
            json.dumps(body),
            {"Content-Type": "application/json", "X-QuantLab-Token": c.token},
        )

    with ThreadPoolExecutor(4) as pool:
        futures = [
            pool.submit(trade, i) if i % 2 else pool.submit(request, service, path="/api/risk")
            for i in range(8)
        ]
        assert all(f.result()[0] == 200 for f in futures)
    assert c.options_lab.session.stock.account.inventory == 4
    c.options_lab.session.stock.check_invariants()


@pytest.mark.parametrize(
    "path", ["/", "/research", "/options", "/risk", "/statarb", "/learning"]
)
def test_every_lab_has_same_keyboard_navigation(service, path):
    status, _, body = request(service, path=path)
    assert status == 200
    for item in (
        b'aria-label="QuantLab labs"',
        b"Skip to content",
        b'href="/statarb"',
        b'href="/research"',
        b'href="/options"',
        b'id="main-content"',
    ):
        assert item in body


def test_duplicate_keys_rejected_before_mutation(service):
    status, _, _ = request(
        service,
        "POST",
        "/api/command",
        '{"kind":"end","kind":"start"}',
        {"Content-Type": "application/json", "X-QuantLab-Token": service.controller.token},
    )
    assert status == 400 and service.controller.session.status == "paused"


def test_learning_and_public_reads_do_not_change_market_draws():
    a, b = Controller(), Controller()
    b.learning.tutor.progress.data["settings"]["enabled"] = False
    for _ in range(8):
        for _ in range(3):
            a.state()
            a.learning.state()
        a.command({"kind": "step_event"})
        b.command({"kind": "step_event"})
    assert a.session.evidence == b.session.evidence
    assert a.session.public_snapshot() == b.session.public_snapshot()


def test_public_labs_and_tutor_reject_private_state_and_do_not_retain_path(tmp_path):
    c = Controller(tmp_path)
    states = [
        c.state(),
        c.options_lab.state(),
        c.risk_lab.state(),
        c.statarb_lab.state(),
        c.learning.state(),
    ]
    forbidden = {
        "latent_before_ticks",
        "latent_after_ticks",
        "informed_signal",
        "signal_error",
        "innovations",
        "_rng",
        "market_config",
        "process_config",
        "future_prices",
    }

    def walk(value):
        if isinstance(value, dict):
            assert not forbidden.intersection(value)
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    for state in states:
        walk(state)
    c.saved_path = str(tmp_path / "private-user-name" / "session.json")
    assert c.state()["saved_path"] == "session.json"
