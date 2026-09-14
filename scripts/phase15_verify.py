"""Verify approved fingerprints and audit release source without revealing secret values."""

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from quantlab.demos.builders import build
from quantlab.demos.registry import FLAGSHIPS
from quantlab.research.codec import digest
from scripts.release_source import source_files

BASE = Path("docs/release/phase_15")


def run():
    old = json.loads((BASE / "baseline_manifest.json").read_text())
    changed = [
        p for p, h in old.items() if hashlib.sha256(Path(p).read_bytes()).hexdigest() != h
    ]
    allowed = {
        "src/quantlab/trading/navigation.py",
        "src/quantlab/trading/server.py",
        "src/quantlab/trading/static/demos.js",
    }
    assert set(changed) <= allowed, changed
    prior = json.loads(Path("docs/demos/evidence/demo-report.json").read_text())
    results = {}
    for key in FLAGSHIPS:
        a = prior["flagships"][key]["verification"]["engine_result_digest"]
        b = build(key).verification["engine_result_digest"]
        assert a == b, key
        results[key] = {"before": a, "after": b, "identical": True}
    before = json.loads((BASE / "core_before.json").read_text())
    after = json.loads((BASE / "core_after.json").read_text())
    assert before == after

    def ids(p):
        return {s for s in p.read_text().splitlines() if "::" in s}

    baseline_ids = ids(BASE / "baseline_tests.txt")
    final_ids = ids(BASE / "final_tests.txt")
    assert not baseline_ids - final_ids
    report = {
        "baseline_test_count": len(baseline_ids),
        "final_test_count": len(final_ids),
        "new_tests": len(final_ids - baseline_ids),
        "missing_baseline_tests": [],
        "changed_existing_source_files": changed,
        "financial_files_changed": [],
        "old_test_files_changed": [],
        "core_fingerprint": digest(after),
        "core_before_after_identical": True,
        "flagships": results,
    }
    (BASE / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def source_audit():
    root = Path.cwd()
    files = list(source_files(root))
    # Heuristics: report location/category only, never candidate secret values.
    patterns = {
        "private-key-block": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        "aws-access-key": r"\bAKIA[0-9A-Z]{16}\b",
        "github-token": r"\bgh[pousr]_[A-Za-z0-9]{30,}\b",
        "api-key-pattern": r"\bsk-[A-Za-z0-9_-]{24,}\b",
        "credential-in-url": r"https?://[^\s/:]+:[^\s/@]+@",
        "absolute-user-path": r"/(?:Users|home)/[A-Za-z0-9_.-]+/",
    }
    findings = []
    broken = []
    for path in files:
        if path.suffix.lower() in {".png", ".jpg", ".gif", ".pdf", ".woff", ".zip"}:
            continue
        try:
            text = path.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        # This scanner's patterns are documentation, not actual credentials.
        if path.name != "phase15_verify.py":
            for category, pattern in patterns.items():
                for match in re.finditer(pattern, text):
                    findings.append(
                        {
                            "file": str(path.relative_to(root)),
                            "line": text[: match.start()].count("\n") + 1,
                            "category": category,
                        }
                    )
        if path.suffix == ".md":
            for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
                parts = urlsplit(target)
                if parts.scheme or not parts.path:
                    continue
                if parts.path.startswith("/"):
                    continue  # application routes in historical audit docs
                dest = path.parent / unquote(parts.path)
                if not dest.exists():
                    broken.append({"file": str(path.relative_to(root)), "target": target})
    out = {
        "source_file_count": len(files),
        "secret_and_absolute_path_findings": findings,
        "broken_document_file_links": broken,
        "excluded_user_runs": True,
        "scope": (
            "Release export allowlist; text-pattern scan, "
            "not a formal security audit or credential validity test."
        ),
    }
    (BASE / "source_audit.json").write_text(json.dumps(out, indent=2) + "\n")
    return out


if __name__ == "__main__":
    print(json.dumps({"verification": run(), "audit": source_audit()}, indent=2))
