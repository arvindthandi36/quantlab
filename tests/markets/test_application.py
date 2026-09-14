import copy
import json
from hashlib import sha256
from pathlib import Path

import pytest

from quantlab.environments.application import research_summary
from quantlab.environments.contract import MarketEnvironment
from quantlab.environments.fixtures import fixtures
from quantlab.environments.research import (
    HistoricalPairAdapter,
    ScenarioAdapter,
    compare_scenarios,
    historical_study,
    scenario_configuration,
)
from quantlab.research.codec import digest
from quantlab.trading.server import Controller
from tests.integration.test_trading_http import request
from tests.integration.test_trading_http import service as http_service


@pytest.fixture
def service(tmp_path):
    yield from http_service.__wrapped__(tmp_path)


def send(service, kind, path="/api/environments", **payload):
    code, _, body = request(
        service,
        "POST",
        path,
        json.dumps({"kind": kind, "payload": payload}),
        {"Content-Type": "application/json", "X-QuantLab-Token": service.controller.token},
    )
    return code, json.loads(body)


def test_synthetic_contract_original_direct_workflow_fingerprint():
    c = Controller()
    e = c.environments.synthetic
    assert isinstance(e, MarketEnvironment)
    from quantlab.trading.scenarios import select_scenario
    from quantlab.trading.session import TradingSession

    original = TradingSession(select_scenario())
    for kind, p in [
        ("order", {"side": "buy", "quantity": 6, "order_type": "market"}),
        ("step_interval", {"delta_us": 1_000_000}),
        ("end", {}),
    ]:
        e.command(kind, **p)
        original.command(kind, **p)
    assert digest(original.public_snapshot()) == digest(c.session.public_snapshot())
    assert e.journal()["environment"] == "SYNTHETIC"


def test_existing_1507_test_sources_and_financial_core_byte_identical():
    manifest = json.loads(Path("docs/markets/evidence/phase12_manifest.json").read_text())
    allowed = {
        "src/quantlab/trading/server.py",
        "src/quantlab/trading/navigation.py",
        "src/quantlab/trading/static/explain.js",
        "src/quantlab/explainability/service.py",
        "src/quantlab/explainability/registry.py",
    }
    # Manifest is frozen before Phase 13; check every pre-existing test and financial module.
    files = manifest.get("files", manifest)
    for name, h in files.items():
        if name not in allowed:
            assert sha256(Path(name).read_bytes()).hexdigest() == h, name


def test_hub_controls_replay_restart_and_rejected_switch_preserve_session():
    c = Controller()
    h = c.environments
    h.command({"kind": "fixture"})
    h.choose("HISTORICAL", dataset_ids=["dataset-1"])
    h.command({"kind": "speed", "payload": {"observations_per_second": 4}})
    h.command({"kind": "play"})
    h.tick()
    assert h.state()["index"] == 1
    h.command({"kind": "pause"})
    h.tick()
    assert h.state()["index"] == 1
    assert not h.catalogue()["playing"] and h.catalogue()["speed"] == 4
    with pytest.raises(ValueError):
        h.choose("SYNTHETIC")
    h.act("order", instrument="FIXTURE-X", side="buy", quantity=3)
    h.act("step")
    h.act("end")
    original = digest(h.state())
    j = h.journal()
    h.load_replay(j)
    assert h.state()["index"] == 0 and h.state()["replay"]
    with pytest.raises(ValueError):
        h.act("order", instrument="FIXTURE-X", side="buy", quantity=3)
    h.command({"kind": "replay_frame", "payload": {"index": len(h.frames) - 1}})
    assert (
        h.hook()["post"]["status"] == "ended" and h.hook()["pre"]["index"] <= h.state()["index"]
    )
    out = h.command({"kind": "restart"})
    assert "knowledge" in out["result"]["message"]
    assert h.state()["account"]["positions"] == [] and h.state()["index"] == 0
    assert digest(h.state()) != original
    h.choose("SYNTHETIC")
    assert h.active is None


@pytest.mark.parametrize(
    "kind", ["pause", "restart", "load_replay", "replay_frame", "quiz", "answer", "what_if"]
)
def test_control_unknown_fields_rejected(kind):
    c = Controller()
    with pytest.raises(ValueError):
        c.environments.command({"kind": kind, "payload": {"future": True}})


def test_bad_synthetic_replay_does_not_discard_active_environment():
    h = Controller().environments
    h.choose("SCENARIO", scenario="normal", steps=20)
    before = h.active
    with pytest.raises((ValueError, KeyError, TypeError)):
        h.load_replay(
            {
                "environment": "SYNTHETIC",
                "schema": "quantlab-environment-v1",
                "quantlab_version": "1.0.0",
                "journal": {},
            }
        )
    assert h.active is before


def test_http_environment_flow_and_source_labels(service):
    assert send(service, "fixture")[0] == 200
    assert (
        send(service, "choose", environment="HISTORICAL", dataset_ids=["dataset-1"])[0] == 200
    )
    status, body = send(service, "order", instrument="FIXTURE-X", side="buy", quantity=5)
    assert status == 200 and not body["state"]["fills"]
    status, body = send(service, "step", count=4)
    assert status == 200 and body["state"]["fills"]
    status, x = send(service, "explain", path="/api/explanations", concept="vwap")
    assert status == 200 and x["current"]["value"] == body["state"]["orders"][0]["vwap"]
    assert x["environment"]["type"] == "HISTORICAL"
    assert request(service, path="/api/environments/journal")[0] == 400
    send(service, "end")
    assert request(service, path="/api/environments/journal")[0] == 200


@pytest.mark.parametrize("path", ["/", "/options", "/risk", "/statarb"])
def test_environment_routes_and_mobile_assets_are_one_shared_desk(service, path):
    send(service, "choose", environment="SCENARIO", scenario="normal")
    code, _, body = request(service, path=path)
    assert code == 200 and b"environment-desk" in body and b"/markets.js" in body
    assert b"/app.js" not in body
    css = request(service, path="/markets.css")[2]
    assert b"@media" in css


@pytest.mark.parametrize(
    "path",
    [
        "/api/state",
        "/api/options",
        "/api/risk",
        "/api/statarb",
        "/api/journal",
        "/api/options/journal",
        "/api/risk/journal",
        "/api/statarb/journal",
    ],
)
def test_external_environment_cannot_read_another_lab_as_current(service, path):
    send(service, "choose", environment="SCENARIO", hidden=True)
    assert request(service, path=path)[0] == 400


@pytest.mark.parametrize("path", ["/api/command", "/api/options", "/api/risk", "/api/statarb"])
def test_external_environment_cannot_trade_another_account(service, path):
    send(service, "choose", environment="SCENARIO", hidden=True)
    assert send(service, "step", path=path, count=1)[0] == 400


def test_new_endpoint_token_and_malformed_import(service):
    assert (
        request(
            service, "POST", "/api/environments", "{}", {"Content-Type": "application/json"}
        )[0]
        == 403
    )
    assert send(service, "import", csv_text="malformed", metadata={})[0] == 400
    assert not service.controller.environments.datasets
    assert send(service, "choose", environment="SCENARIO", hidden=True, seed=5)[0] == 400
    assert (
        send(service, "choose", environment="SCENARIO", hidden=True, scenario="normal")[0]
        == 400
    )


def test_research_environment_labels_and_identical_policy_independent_regimes(tmp_path):
    record = compare_scenarios(tmp_path / "scenario", runs=2, seconds=1)
    assert record["status"] == "complete" and len(record["runs"]) == 6
    assert not record["spec"]["paired"]
    variants = record["spec"]["variants"]
    assert len({digest(v["configuration"]["engine"]["strategy"]) for v in variants}) == 1
    assert all(r["coverage"]["environment"]["type"] == "SCENARIO" for r in record["runs"])
    assert len({r["coverage"]["actual_seed"] for r in record["runs"]}) == 6
    summary = research_summary(tmp_path / "scenario")
    assert len(summary["variants"]) == 3
    c = scenario_configuration("normal")
    c["environment"]["type"] = "HISTORICAL"
    with pytest.raises(ValueError):
        ScenarioAdapter().validate(c)


@pytest.mark.parametrize("mode", ["fixed", "rolling", "walk_forward"])
def test_historical_study_single_path_and_causal_fitting_schedule(tmp_path, mode):
    ds = fixtures()
    r = historical_study(ds, tmp_path / mode, training_end=30, evaluation_end=45, mode=mode)
    assert r["status"] == "complete" and len(r["runs"]) == 2
    assert all(x["coverage"]["independent_historical_paths"] == 1 for x in r["runs"])
    assert all(x["coverage"]["environment"]["type"] == "HISTORICAL" for x in r["runs"])
    assert len(research_summary(tmp_path / mode)["outcomes"]) == 2
    c = copy.deepcopy(r["spec"]["variants"][0]["configuration"])
    c["environment"]["type"] = "SCENARIO"
    with pytest.raises(ValueError):
        HistoricalPairAdapter(ds).validate(c)


def test_research_scenario_name_cannot_misrepresent_engine_settings():
    c = scenario_configuration("normal")
    c["engine"]["market"]["latent_sigma_ticks"] = 8
    with pytest.raises(ValueError, match="label"):
        ScenarioAdapter().validate(c)


def test_scenario_option_portfolio_delta_explanation_matches_display(service):
    send(service, "choose", environment="SCENARIO", scenario="option_volatility_shock")
    s = service.controller.environments.active
    q = s.public_core()["selected"]
    status, _ = send(
        service,
        "option_order",
        contract_id=q["id"],
        side="buy",
        quantity=1,
        quote_revision=q["revision"],
    )
    assert status == 200
    status, out = send(
        service,
        "explain",
        path="/api/explanations",
        concept="delta",
        lab="options",
        selector="portfolio",
    )
    assert status == 200 and out["current"]["value"] == s.public_core()["greeks"]["delta"]
    js = request(service, path="/markets.js")[2]
    assert b'data-env-selector="portfolio"' in js
