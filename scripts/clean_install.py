"""Create a private release-candidate Git source, clone it, install, and test.

The original worktree and its Git index are never changed. No remote is invented.
Usage: python -m scripts.clean_install
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run(args, cwd, log):
    environment = os.environ.copy()
    for key in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV"):
        environment.pop(key, None)
    with log.open("a") as output:
        subprocess.run(
            args, cwd=cwd, env=environment, stdout=output, stderr=subprocess.STDOUT, check=True
        )


def main():
    project = Path.cwd()
    root = Path(tempfile.mkdtemp(prefix="quantlab-core-release-"))
    source = root / "source"
    clone = root / "clone"
    source.mkdir()
    included = [
        "src",
        "tests",
        "scripts",
        "docs",
        "pyproject.toml",
        "README.md",
        "ASSUMPTIONS.md",
        "CHANGELOG.md",
        "ROADMAP.md",
        "requirements-dev.lock",
        "requirements-research.lock",
        ".gitignore",
    ]
    for name in included:
        src = project / name
        dest = source / name
        if src.is_dir():
            shutil.copytree(
                src,
                dest,
                ignore=shutil.ignore_patterns(
                    "__pycache__",
                    "*.pyc",
                    ".pytest_cache",
                    ".hypothesis",
                    ".ruff_cache",
                    "*.egg-info",
                ),
            )
        else:
            shutil.copy2(src, dest)
    manifest = {
        str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in source.rglob("*")
        if p.is_file()
    }
    log = root / "clean-install.log"
    run(["git", "init", "-q", str(source)], root, log)
    run(["git", "add", "."], source, log)
    run(
        [
            "git",
            "-c",
            "user.name=QuantLab release validation",
            "-c",
            "user.email=validation@example.invalid",
            "commit",
            "-qm",
            "Core release candidate",
        ],
        source,
        log,
    )
    run(["git", "clone", "--no-local", str(source), str(clone)], root, log)
    run([sys.executable, "-m", "venv", "venv"], clone, log)
    python = str(clone / "venv/bin/python")
    run(
        [
            python,
            "-m",
            "pip",
            "--isolated",
            "install",
            "--no-cache-dir",
            "--upgrade",
            "pip>=26.2.1,<27",
        ],
        clone,
        log,
    )
    run([python, "-m", "pip", "--isolated", "install", "--no-cache-dir", ".[dev]"], clone, log)
    run([python, "-m", "pip", "check"], clone, log)
    run([python, "-m", "pytest", "-q", "--durations=10"], clone, log)
    run([str(clone / "venv/bin/quantlab"), "--version"], clone, log)
    # An ordinary installed package, not the original checkout or an editable path.
    run(
        [
            python,
            "-c",
            "import quantlab; from pathlib import Path; "
            'assert "site-packages" in str(Path(quantlab.__file__)); '
            "print(quantlab.__version__)",
        ],
        clone,
        log,
    )
    result = {
        "temporary_root": str(root),
        "clone": str(clone),
        "status": "tests_complete",
        "source_kind": "temporary local Git release snapshot; original has no commits",
        "manifest": manifest,
        "installation": "non-editable .[dev], no-cache, isolated pip",
        "python": sys.version.split()[0],
    }
    # Temporary locations are operational evidence, not published release documentation.
    Path("/private/tmp/quantlab-phase11-clean-location.json").write_text(
        json.dumps(result, indent=2)
    )
    print(json.dumps({"root": str(root), "status": "tests_complete"}), flush=True)


if __name__ == "__main__":
    main()
