"""Viewing counters live separately from conceptual mastery and tutor question state."""

import copy
import json
from pathlib import Path


class DemoProgress:
    def __init__(self, path=None):
        self.path = Path(path) if path else None
        self.data = {"schema": 1, "demos": {}, "exposed_questions": []}
        self.warning = None
        if self.path and self.path.exists():
            try:
                raw = json.loads(self.path.read_text())
                if (
                    set(raw) != {"schema", "demos", "exposed_questions"}
                    or raw["schema"] != 1
                    or not isinstance(raw["demos"], dict)
                    or not isinstance(raw["exposed_questions"], list)
                ):
                    raise ValueError("invalid demo progress")
                self.data = raw
            except (OSError, ValueError, TypeError):
                self.warning = (
                    "Demo progress could not be read; using in-memory counters. "
                    "Personal mastery is unchanged."
                )
                self.path = None

    def count(self, demo, kind):
        row = self.data["demos"].setdefault(
            demo, {"viewed": 0, "completed": 0, "checkpoints_attempted": 0}
        )
        row[kind] += 1
        self.save()

    def expose(self, fingerprint):
        if fingerprint not in self.data["exposed_questions"]:
            self.data["exposed_questions"].append(fingerprint)
            self.save()

    def save(self):
        if not self.path:
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.data, sort_keys=True) + "\n")
            tmp.replace(self.path)
        except OSError:
            self.warning = (
                "Demo progress could not be saved; current playback and personal "
                "accounts are unaffected."
            )

    def public(self):
        return {
            "demos": copy.deepcopy(self.data["demos"]),
            "warning": self.warning,
            ("note"): (
                "Viewed, completed and attempted are activity counters. Watching "
                "a demo is not mastery."
            ),
        }
