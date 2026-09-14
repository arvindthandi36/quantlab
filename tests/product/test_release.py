"""Release integration gates: presentation must not mutate the approved engines."""

import hashlib
import json
import subprocess
import sys
import tomllib
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest

from quantlab import __version__ as core_version
from quantlab.demos.builders import build
from quantlab.demos.registry import FLAGSHIPS
from quantlab.product import VERSION
from quantlab.product.content import FEATURED
from quantlab.product.pages import PAGES
from quantlab.trading.navigation import GROUPS
from tests.integration.test_trading_http import request
from tests.integration.test_trading_http import service as http_service


@pytest.fixture
def service(tmp_path):
    yield from http_service.__wrapped__(tmp_path)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.extend(v for k, v in attrs if k == "href")


@pytest.mark.parametrize("path", PAGES)
def test_editorial_routes_share_shell_and_cannot_change_financial_state(service, path):
    c = service.controller
    before = c.session.public_snapshot()
    code, headers, raw = request(service, path=path)
    assert code == 200 and "text/html" in headers["Content-Type"]
    text = raw.decode()
    assert "QuantLab labs" in text and 'id="main-content"' in text
    assert "/product.css" in text and "/product.js" in text
    assert "1.1.0" in text and "/home" in text
    assert "/app.js" not in text and "/markets.js" not in text
    assert c.session.public_snapshot() == before
    assert c._options_lab is None and c._risk_lab is None and c._statarb_lab is None


def test_every_product_link_is_a_real_route_and_demo_links_are_registered(service):
    routes = set(PAGES) | {
        "/",
        "/demos",
        "/options",
        "/risk",
        "/statarb",
        "/research",
        "/learning",
        "/explain",
    }
    for path in PAGES:
        links = Links()
        links.feed(request(service, path=path)[2].decode())
        for href in links.links:
            parts = urlsplit(href)
            assert not parts.netloc
            assert (parts.path or path) in routes, href
    assert len({key for key, _, _ in FEATURED}) == 6
    assert all(key in FLAGSHIPS for key, _, _ in FEATURED)
    for _, entries in GROUPS:
        for _, href in entries:
            assert urlsplit(href).path in routes


def test_home_and_limits_remain_static_during_hidden_scenario(service):
    c = service.controller
    before = request(service, path="/home")[2]
    c.environments.command(
        {"kind": "choose", "payload": {"environment": "SCENARIO", "hidden": True}}
    )
    assert request(service, path="/home")[2] == before
    assert b"environment-desk" in request(service, path="/")[2]
    limits = request(service, path="/limitations")[2]
    assert b"Security / deployment" in limits and b"OHLCV" in limits
    assert b"latent_after" not in limits and b"selected_scenario" not in limits


@pytest.mark.parametrize(
    "path,mime", [("/product.css", "text/css"), ("/product.js", "text/javascript")]
)
def test_new_assets_keep_existing_local_security_contract(service, path, mime):
    code, headers, body = request(service, path=path)
    assert code == 200 and mime in headers["Content-Type"] and body
    assert request(service, path=path, headers={"Host": "attacker.example"})[0] == 403
    assert request(service, path="/../../LICENSE")[0] == 404


def test_product_version_and_mit_metadata_preserve_old_replay_contract():
    p = tomllib.loads(Path("pyproject.toml").read_text())["project"]
    assert p["version"] == VERSION == "1.1.0"
    assert core_version == "1.0.0"
    assert p["scripts"]["quantlab"] == "quantlab.product.cli:main"
    assert p["authors"] == [{"name": "Arvind Thandi"}]
    assert p["license"] == {"file": "LICENSE"}
    text = Path("LICENSE").read_text()
    assert text.startswith("MIT License\n\nCopyright (c) 2026 Arvind Thandi\n")
    assert 'THE SOFTWARE IS PROVIDED "AS IS"' in text
    result = subprocess.run(
        [sys.executable, "-m", "quantlab.product.cli", "--version"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "QuantLab 1.1.0 (financial replay core 1.0.0)" in result.stdout


def test_approved_sources_preserved_except_declared_presentation_adapters():
    allowed = {
        "src/quantlab/trading/navigation.py",
        "src/quantlab/trading/server.py",
        "src/quantlab/trading/static/demos.js",
    }
    baseline = json.loads(Path("docs/release/phase_15/baseline_manifest.json").read_text())
    for path, expected in baseline.items():
        if path not in allowed:
            assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected, path


@pytest.mark.parametrize("key", FLAGSHIPS)
def test_all_flagship_financial_results_keep_approved_fingerprints(key):
    baseline = json.loads(Path("docs/demos/evidence/demo-report.json").read_text())
    expected = baseline["flagships"][key]["verification"]["engine_result_digest"]
    assert build(key).verification["engine_result_digest"] == expected


def test_product_presentation_never_recalculates_finances_or_hides_required_recording_labels():
    js = Path("src/quantlab/trading/static/product.js").read_text()
    css = Path("src/quantlab/trading/static/product.css").read_text()
    assert "fetch(" not in js and "Math.random" not in js
    assert "prefers-reduced-motion" in css and ":focus-visible" in css
    assert ".demo-recording .ql-masthead" in css
    assert ".demo-recording .demo-limitations" not in css
    assert "data-required-badge" not in js and "data-required-limitations" not in js
    demo = Path("src/quantlab/trading/static/demos.js").read_text()
    assert "await command('start',{id:p.get('demo')" in demo
    assert "p.get('mode')||'quick'" in demo


def test_feature_freeze_and_supported_install_commands():
    text = Path("README.md").read_text()
    for command in (
        "python3 -m venv .venv",
        "python -m pip install .",
        "quantlab serve",
        "quantlab --version",
    ):
        assert command in text
    assert "/home" in text and "MIT licensed" in text
    frozen = Path("FEATURE_FREEZE.md").read_text()
    assert "planned product feature set is frozen" in frozen
    assert "not release commitments" in frozen and "1.1.0" in frozen


def test_showcase_doc_links_and_real_captures_exist():
    # Release-facing links, including source; historical audits remain separate evidence.
    import re

    paths = [
        Path("README.md"),
        *Path("docs/showcase").glob("*.md"),
        Path("docs/architecture/OVERVIEW.md"),
    ]
    for path in paths:
        for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", path.read_text()):
            parts = urlsplit(target)
            if parts.scheme or not parts.path:
                continue
            assert not parts.path.startswith("/"), (path, target)
            assert (path.parent / unquote(parts.path)).exists(), (path, target)
    manifest = json.loads(Path("docs/assets/readme/captures.json").read_text())
    assert len(manifest["captures"]) >= 14
    for row in manifest["captures"]:
        image = Path("docs/assets/readme") / row["file"]
        assert image.suffix == ".jpg"
        assert image.read_bytes().startswith(b"\xff\xd8\xff")
        assert image.read_bytes().endswith(b"\xff\xd9")
        assert hashlib.sha256(image.read_bytes()).hexdigest() == row["sha256"]
