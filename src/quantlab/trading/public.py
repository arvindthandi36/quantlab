"""Presentation-only sanitisation; retain full local destinations inside controllers."""

import copy
from pathlib import Path


def research_view(job):
    result = copy.deepcopy(job)
    if result.get("path"):
        result["path"] = Path(result["path"]).name
    return result
