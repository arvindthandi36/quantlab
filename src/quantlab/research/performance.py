"""Measure full versus lightweight sessions before making speed claims."""

import cProfile
import gc
import io
import pstats
import time
import tracemalloc

from quantlab.research.engine import versions


def profile_adapter(adapter, configuration, *, seeds=(0, 1, 2, 3, 4)) -> dict:
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("profiling requires distinct seeds")
    result = {
        "versions": versions(),
        "seeds": list(seeds),
        "configuration": configuration,
        "note": "Sequential local measurements, not a benchmark across machines. "
        "tracemalloc peak excludes native allocation not tracked by Python.",
    }
    fingerprints = {}
    for full in (True, False):
        name = "full" if full else "lightweight"
        start = time.perf_counter()
        fingerprints[name] = []
        for seed in seeds:
            outcome = adapter.run(seed, configuration, full=full)
            fingerprints[name].append((outcome.metrics, outcome.trajectory_fingerprint))
        elapsed = time.perf_counter() - start
        del outcome
        gc.collect()
        tracemalloc.start()
        outcome = adapter.run(seeds[0], configuration, full=full)
        retained, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        del outcome
        profiler = cProfile.Profile()
        profiler.runcall(adapter.run, seeds[0], configuration, full=full)
        output = io.StringIO()
        pstats.Stats(profiler, stream=output).strip_dirs().sort_stats("cumulative").print_stats(
            15
        )
        result[name] = {
            "elapsed_seconds": elapsed,
            "sessions_per_second": len(seeds) / elapsed,
            "retained_traced_bytes": retained,
            "peak_traced_bytes": peak,
            "profile_top15": output.getvalue(),
        }
    if fingerprints["full"] != fingerprints["lightweight"]:
        raise ValueError("logging mode altered outcomes during profiling")
    result["identical_outcomes_verified"] = True
    return result
