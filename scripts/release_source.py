"""Export a clean local source tree without user histories or Git metadata.

The caller can initialise a temporary Git repository here to test an actual fresh clone.
This never stages, commits, tags or publishes the working project.
"""

import argparse
import shutil
from pathlib import Path

ROOT_FILES = (
    ".gitignore",
    "README.md",
    "LICENSE",
    "pyproject.toml",
    "requirements-dev.lock",
    "requirements-research.lock",
    "ASSUMPTIONS.md",
    "CHANGELOG.md",
    "LEARNING_LOG.md",
    "ROADMAP.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "FEATURE_FREEZE.md",
)
ROOT_DIRS = ("src", "tests", "scripts", "docs")
EXCLUDED = {"__pycache__", ".pytest_cache", ".ruff_cache", ".hypothesis"}


def source_files(root):
    for name in ROOT_FILES:
        if (root / name).is_file():
            yield root / name
    for name in ROOT_DIRS:
        for p in sorted((root / name).rglob("*")):
            if not p.is_file() or p.is_symlink():
                continue
            if EXCLUDED.intersection(p.parts) or any(x.endswith(".egg-info") for x in p.parts):
                continue
            if p.suffix in {".pyc", ".pyo", ".log"} or p.name == ".DS_Store":
                continue
            yield p


def export(root, destination):
    root, destination = root.resolve(), destination.resolve()
    if destination.exists() or destination.is_relative_to(root):
        raise ValueError("Choose a new destination outside the source tree")
    destination.mkdir(parents=True)
    copied = []
    for p in source_files(root):
        relative = p.relative_to(root)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
        copied.append(str(relative))
    return copied


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    copied = export(Path.cwd(), args.destination)
    print(
        f"Exported {len(copied)} source/documentation/evidence files; "
        "no user runs or Git metadata"
    )


if __name__ == "__main__":
    main()
