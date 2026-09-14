import json
import subprocess
import sys
import sysconfig
from pathlib import Path

from quantlab.demo import run_demo


def test_demo_reproduces_complete_results_and_quantity_ledger():
    first = run_demo()
    assert first == run_demo()
    assert (
        first.submitted_quantity,
        first.traded_volume,
        first.resting_quantity,
        first.cancelled_quantity,
    ) == (42, 18, 2, 4)
    assert first.after_aggressive_order.asks[0].quantity == 2
    assert first.final_book.best_bid == 9997
    assert first.final_book.best_ask is None
    assert first.final_book.mid_price_ticks is first.final_book.spread_ticks is None
    assert first.reports[-1].cancelled_quantity == 2


def test_module_entrypoint_describes_actual_execution_and_missing_liquidity():
    result = subprocess.run(
        [sys.executable, "-m", "quantlab.demo"], capture_output=True, text=True, check=True
    )
    assert "Trade 1: 3 at £100.02 | maker=A" in result.stdout
    assert "Trade 2: 2 at £100.02 | maker=B" in result.stdout
    assert "executed 5; cancelled 2" in result.stdout
    assert "unavailable (one or both sides are empty)" in result.stdout
    assert "Conservation PASS: 42" in result.stdout
    assert result.stderr == ""


def test_installed_console_script_json_is_reproducible(tmp_path):
    entrypoint = Path(sysconfig.get_path("scripts")) / "quantlab-demo"
    first = subprocess.check_output([str(entrypoint), "--json"], text=True, cwd=tmp_path)
    second = subprocess.check_output(
        [sys.executable, "-m", "quantlab.demo", "--json"], text=True, cwd=tmp_path
    )
    assert first == second
    data = json.loads(first)
    assert data["tick_size"] == "0.01"
    assert data["rng_seed"] is None
    assert data["result"]["traded_volume"] == 18
    assert data["result"]["reports"][5]["trades"][0]["aggressor_side"] == "buy"
