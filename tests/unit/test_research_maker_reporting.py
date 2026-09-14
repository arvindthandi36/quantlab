from fractions import Fraction

import pytest

from quantlab.research.adapters.maker_reporting import markout_coverage


def test_coverage_aggregation_keeps_missing_and_uses_executed_units():
    record = {
        "status": "complete",
        "spec": {
            "variants": [{"name": "a", "configuration": {"market": {"tick_size": "0.01"}}}]
        },
        "runs": [
            {
                "variant": "a",
                "run_index": 0,
                "coverage": {
                    "markouts": {
                        "1": {
                            "available_units": 2,
                            "missing_units": 1,
                            "pending_units": 0,
                            "weighted_sum_ticks": "4/1",
                        }
                    }
                },
            },
            {
                "variant": "a",
                "run_index": 1,
                "coverage": {
                    "markouts": {
                        "1": {
                            "available_units": 1,
                            "missing_units": 0,
                            "pending_units": 2,
                            "weighted_sum_ticks": "-1/1",
                        }
                    }
                },
            },
        ],
    }
    group = markout_coverage(record)["a"]["1"]
    assert group == {
        "available_units": 3,
        "missing_units": 1,
        "pending_units": 2,
        "weighted_sum": Fraction(3, 100),
        "pooled_mean": pytest.approx(0.01),
    }


def test_all_unavailable_coverage_is_not_zero_markout():
    record = {
        "status": "complete",
        "spec": {
            "variants": [{"name": "a", "configuration": {"market": {"tick_size": "0.01"}}}]
        },
        "runs": [
            {
                "variant": "a",
                "run_index": 0,
                "coverage": {
                    "markouts": {
                        "1": {
                            "available_units": 0,
                            "missing_units": 3,
                            "pending_units": 1,
                            "weighted_sum_ticks": "0/1",
                        }
                    }
                },
            }
        ],
    }
    assert markout_coverage(record)["a"]["1"]["pooled_mean"] is None
