"""Verify a local Git clone, ordinary installation, CLI and installed HTTP assets.

Run from the source root with --wheelhouse pointing to downloaded dependency wheels.
The actual project Git index and remotes are never modified.
"""

import argparse
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

from scripts.release_source import export


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheelhouse", type=Path, required=True)
    args = parser.parse_args()
    project = Path.cwd()
    temp = Path(tempfile.mkdtemp(prefix="quantlab-product-release-"))
    source, clone = temp / "source", temp / "clone"
    export(project, source)
    env = os.environ.copy()
    for key in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV"):
        env.pop(key, None)
    log = temp / "install.log"

    def run(command, cwd=clone):
        result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
        with log.open("a") as f:
            f.write(result.stdout + result.stderr)
        result.check_returncode()
        return result.stdout.strip()

    run(["git", "init", "-q", "-b", "codex/release-check", str(source)], temp)
    run(["git", "add", "."], source)
    run(
        [
            "git",
            "-c",
            "user.name=Release verification",
            "-c",
            "user.email=verification@example.invalid",
            "commit",
            "-qm",
            "Local release verification snapshot",
        ],
        source,
    )
    commit = run(["git", "rev-parse", "HEAD"], source)
    run(["git", "clone", "--no-local", str(source), str(clone)], temp)
    run([sys.executable, "-m", "venv", ".venv"])
    python = str(clone / ".venv/bin/python")
    pip = [
        python,
        "-m",
        "pip",
        "--isolated",
        "install",
        "--no-cache-dir",
        "--no-index",
        "--find-links",
        str(args.wheelhouse.resolve()),
    ]
    run([*pip, "--upgrade", "pip", "setuptools", "wheel"])
    run([*pip, "."])  # Documented ordinary package installation first.
    run([python, "-m", "pip", "check"])
    version = run([str(clone / ".venv/bin/quantlab"), "--version"], temp)
    installed = json.loads(
        run(
            [
                python,
                "-c",
                "import json,quantlab,importlib.metadata as m; from pathlib import Path; "
                'assert "site-packages" in str(Path(quantlab.__file__)); '
                'd=m.distribution("quantlab"); '
                'assert any(str(p).endswith("LICENSE") for p in d.files); '
                'print(json.dumps({"version":d.version,"author":d.metadata["Author"],'
                '"mit":d.metadata["License"].startswith("MIT License"),'
                '"site_packages":True}))',
            ],
            temp,
        )
    )
    run([*pip, ".[dev]"])
    tests = run([python, "-m", "pytest", "-q", "--durations=10"])
    passed = re.search(r"(\d+) passed in ([0-9.]+)s", tests)
    assert passed and int(passed[1]) == 1933, tests[-2000:]
    (project / "docs/release/phase_15/clean_tests.txt").write_text(tests + "\n")
    run([python, "-m", "ruff", "check", "."])
    core = json.loads(run([python, "-m", "tests.core_workflows"]))
    assert core == json.loads((project / "docs/release/phase_15/core_before.json").read_text())
    # Choose an available user port for the documented CLI.
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server_log = temp / "server.log"
    with server_log.open("w") as output:
        server = subprocess.Popen(
            [
                str(clone / ".venv/bin/quantlab"),
                "serve",
                "--port",
                str(port),
                "--learning-path",
                str(temp / "learning.json"),
            ],
            cwd=temp,
            env={**env, "PYTHONUNBUFFERED": "1"},
            stdout=output,
            stderr=subprocess.STDOUT,
        )
        try:
            base = None
            for _ in range(100):
                match = re.search(r"http://127\.0\.0\.1:(\d+)/home", server_log.read_text())
                if match:
                    base = "http://127.0.0.1:" + match[1]
                    break
                assert server.poll() is None, server_log.read_text()
                time.sleep(0.1)
            assert base
            routes = [
                "/home",
                "/",
                "/options",
                "/risk",
                "/statarb",
                "/research",
                "/learning",
                "/explain",
                "/demos",
                "/environments",
                "/how-it-works",
                "/limitations",
                "/showcase",
                "/defence",
                "/product.css",
                "/product.js",
            ]
            verified = []
            for route in routes:
                with urllib.request.urlopen(base + route, timeout=10) as response:
                    body = response.read()
                    assert response.status == 200 and body
                    verified.append(route)
        finally:
            server.terminate()
            server.wait(timeout=10)
    files = {
        str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in source.rglob("*")
        if p.is_file() and ".git" not in p.parts
    }
    result = {
        "status": "passed",
        "source_kind": "Fresh clone of temporary local Git snapshot; no remote publication",
        "snapshot_commit": commit,
        "source_file_count": len(files),
        "source_manifest_sha256": hashlib.sha256(
            json.dumps(files, sort_keys=True).encode()
        ).hexdigest(),
        "python": sys.version.split()[0],
        "platform": sys.platform,
        "installation": "Non-editable pip install .; then .[dev]; isolated virtual environment",
        "dependency_source": (
            "Downloaded registry wheels via --no-index; no environment packages inherited"
        ),
        "pip_check": "passed",
        "metadata": installed,
        "cli_version": version,
        "tests_passed": int(passed[1]),
        "tests_seconds": float(passed[2]),
        "ruff": "passed",
        "core_fingerprint_equal": True,
        "installed_routes_http_200": verified,
        "remote_clone_tested": False,
        "windows_linux_or_other_python_tested": False,
        "original_git_index_modified": False,
        "evidence_note": (
            "Snapshot contains pending final reports; "
            "only documentation/evidence is finalised after this run."
        ),
    }
    (project / "docs/release/phase_15/clean_install.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    Path("/private/tmp/quantlab-phase15-clean-location.json").write_text(
        json.dumps({"root": str(temp), "clone": str(clone), "log": str(log)})
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
