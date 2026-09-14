"""Catalogue real, manually verified native-browser captures; never generate UI pixels."""

import hashlib
import json
from pathlib import Path

from PIL import Image

STATES = {
    "home": ("/home", "Static overview"),
    "home-mobile": ("/home", "Phone 390 × 844"),
    "trading-desk": ("/", "Seed 42; paused; BUY 6 MARKET; position 6"),
    "order-vwap": ("/demos", "order-after-multifill; Quick showcase; Recording mode"),
    "synthetic-prices": ("/demos", "synthetic-after-event; public evidence only"),
    "options-lab": ("/options", "Fresh default day-0 chain; no option position"),
    "delta-hedge": ("/demos", "delta-after-hedge; full branch; stock -51"),
    "risk-lab": ("/demos", "var-vs-es-tail; actual calculation"),
    "stress-test": (
        "/risk#stress",
        "Six-unit stock position; default custom stress full repriced",
    ),
    "statarb-lab": ("/statarb#model", "Default seed; 120 observed rows; past-only fit"),
    "correlation-residual": ("/demos", "correlation-vs-residual; actual controlled paths"),
    "research-distribution": ("/demos", "winner-before-test; 50 development scores"),
    "explain-mode": ("/demos", "order-after-multifill → Explain VWAP; selected demo context"),
    "guided-demo": ("/demos", "order-before-submit; public input checkpoint"),
    "learning-dashboard": ("/learning", "Temporary QA profile; zero graded answers"),
}


def run():
    root = Path("docs/assets/readme")
    rows = []
    for name, (route, state) in STATES.items():
        path = root / (name + ".jpg")
        with Image.open(path) as im:
            width, height = im.size
            assert im.format == "JPEG", path
        rows.append(
            {
                "file": path.name,
                "route": route,
                "state": state,
                "width": width,
                "height": height,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    manifest = {
        "capture_method": "Direct native tab screenshots of the actual local application",
        "generated_mockups": False,
        "pixel_edits": False,
        "discarded_method": "Full-page stitching produced padding/repeated strips; replaced",
        "captures": rows,
    }
    (root / "captures.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
