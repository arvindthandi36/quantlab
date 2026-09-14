"""Reproduce Phase 12 demonstrations and bounded explanation timings locally."""

import copy
import json
import statistics
import sys
import tempfile
import time
import tracemalloc
from pathlib import Path

from quantlab.explainability.examples import example
from quantlab.research.adapters.maker import MakerAdapter, maker_configuration
from quantlab.research.engine import execute
from quantlab.research.models import ExperimentSpec, Variant
from quantlab.research.seeds import SeedPlan
from quantlab.risk.analytics import RiskSettings
from quantlab.trading.replay import journal
from quantlab.trading.server import Controller
from quantlab.tutor.adapters import research_contexts


def main():
    output = Path(sys.argv[1] if len(sys.argv) > 1 else "docs/explainability/evidence")
    output.mkdir(parents=True, exist_ok=True)
    c = Controller()
    e = c.explanations
    e.observe("trading", c.state())
    c.command({"kind": "order", "payload": dict(side="buy", quantity=6, order_type="market")})
    demo = {"vwap": e.explain("vwap"), "pnl_change": e.explain("pnl")}
    demo["what_if_order_size"] = e.what_if("order_size", inputs={"quantity": 20})
    o = c.options_lab
    o.session.command(
        "option_order",
        contract_id=o.selected,
        side="buy",
        quantity=1,
        quote_revision=o.session.quote_revision,
    )
    demo["delta"] = e.explain("delta", lab="options")
    demo["what_if_volatility"] = e.what_if(
        "volatility", lab="options", inputs={"volatility": 0.3}
    )
    e.observe("options", o.state())
    o.session.command("step", count=1)
    demo["delta_change"] = e.explain("delta", lab="options")
    r = c.risk_lab
    r.session.settings = RiskSettings(paths=1000, sample_size=100)
    demo["var_before"] = e.explain("var", lab="risk")
    r.session.execute("options", "stock_order", side="buy", quantity=5, order_type="market")
    demo["var_change"] = e.explain("var", lab="risk")
    demo["what_if_correlation"] = e.what_if(
        "correlation", lab="risk", inputs={"correlation": 0.9}
    )
    s = c.statarb_lab
    s.session.command("step", count=80)
    demo["z_score"] = e.explain("z_score", lab="statarb")
    s.session.command("step", count=1)
    demo["z_change"] = e.explain("z_score", lab="statarb")
    demo["what_if_entry"] = e.what_if("entry_threshold", lab="statarb", inputs={"entry": 2.5})
    demo["engineering"] = e.explain("integer_ticks")
    learner = copy.deepcopy(c.learning.tutor.progress.data)
    e.explain("vwap")
    e.what_if("inventory", inputs={"inventory": 20})
    demo["reading_preserves_learning"] = learner == c.learning.tutor.progress.data
    demo["quiz"] = e.quiz("vwap")
    with tempfile.TemporaryDirectory() as directory:
        config = maker_configuration(duration_us=2_000_000)
        spec = ExperimentSpec(
            "How uncertain is the mean?",
            "Independent runs show sampling variability.",
            SeedPlan(121042, "development", 4),
            (Variant("fixed", config),),
            MakerAdapter().name,
            bootstrap_resamples=40,
        )
        study = Path(directory) / "study"
        execute(spec, MakerAdapter(), study)
        c.learning.tutor.study(research_contexts(study), "standard_error")
        demo["research"] = e.explain("standard_error", lab="research")
    p = Controller()
    p.command({"kind": "order", "payload": dict(side="buy", quantity=6, order_type="market")})
    try:
        p.explanations.explain("vwap", mode="observer", reveal=True)
    except ValueError as error:
        demo["live_observer_rejected"] = str(error)
    p.command({"kind": "step_event"})
    p.command({"kind": "end"})
    demo["post_session"] = p.explanations.explain("markouts", mode="post_session")
    observer = p.explanations.explain("markouts", mode="observer", reveal=True)
    demo["observer"] = {k: observer[k] for k in ("mode", "label", "quiz_allowed")}
    demo["observer"]["record_count"] = observer["observer"]["total_records"]
    p.command({"kind": "load_replay", "payload": journal(p.session)})
    demo["replay_initial"] = p.explanations.explain("vwap")
    p.command({"kind": "replay_step", "payload": {"index": 1}})
    demo["replay_trade"] = p.explanations.explain("vwap")
    demo["replay_hook"] = p.explanations.replay_hook("trading")
    demo["example_standard_error"] = example("se")
    (output / "demo.json").write_text(json.dumps(demo, indent=2, allow_nan=False) + "\n")
    timings = {}
    cases = [
        ("trading", "vwap"),
        ("trading", "pnl"),
        ("options", "delta"),
        ("risk", "var"),
        ("statarb", "z_score"),
    ]
    for lab, key in cases:
        e.explain(key, lab=lab)
        times = []
        for _ in range(30):
            start = time.perf_counter()
            e.explain(key, lab=lab)
            times.append((time.perf_counter() - start) * 1000)
        timings[lab + "_" + key] = dict(
            n=30, median_ms=statistics.median(times), p95_ms=sorted(times)[28]
        )
    for kind, lab, inputs in [
        ("volatility", "options", {"volatility": 0.3}),
        ("correlation", "risk", {"correlation": 0.9}),
        ("order_size", "trading", {"quantity": 20}),
        ("inventory", "trading", {"inventory": 20}),
        ("entry_threshold", "statarb", {"entry": 2.5}),
    ]:
        times = []
        for _ in range(10):
            start = time.perf_counter()
            e.what_if(kind, lab=lab, inputs=inputs)
            times.append((time.perf_counter() - start) * 1000)
        timings["what_if_" + kind] = dict(
            n=10, median_ms=statistics.median(times), max_ms=max(times)
        )
    tracemalloc.start()
    for _ in range(20):
        e.explain("var", lab="risk")
    retained, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    perf = dict(
        timings=timings,
        retained_explanation_cache_bytes=len(json.dumps(e.observed).encode()),
        traced_retained_bytes=retained,
        traced_peak_bytes=peak,
        workload=(
            "Warm core reports; 1,000 risk paths already computed. "
            "Times are local Python response construction, not browser rendering "
            "or universal guarantees. Explain does not launch a new experiment."
        ),
        memory_scope=(
            "Twenty repeated risk explanations; tracemalloc Python allocations, "
            "not whole-process RSS."
        ),
    )
    (output / "performance.json").write_text(json.dumps(perf, indent=2) + "\n")
    print(
        json.dumps(
            {
                "vwap": demo["vwap"]["current"]["value"],
                "pnl": demo["pnl_change"]["current"]["value"],
                "var_before": demo["var_before"]["current"]["value"],
                "var_after": demo["var_change"]["current"]["value"],
                "z": demo["z_score"]["current"]["value"],
                "benchmarks": timings,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
