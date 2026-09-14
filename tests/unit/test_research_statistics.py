import math

import numpy as np
import pytest
from scipy import stats

from quantlab.research.codec import plain
from quantlab.research.statistics import (
    bootstrap,
    mean_interval,
    paired_analysis,
    paired_differences,
    quantile,
    relationship,
    sample,
    summarise,
    tail_risk,
)


def test_hand_calculated_description():
    result = summarise([1, 2, 3, 4])
    assert result.mean == result.median == 2.5
    assert result.variance == pytest.approx(5 / 3)
    assert result.standard_deviation == pytest.approx(math.sqrt(5 / 3))
    assert result.standard_error == pytest.approx(math.sqrt(5 / 3) / 2)
    assert (result.p05, result.p25, result.p75, result.p95) == pytest.approx(
        (1.15, 1.75, 3.25, 3.85)
    )
    assert (result.minimum, result.maximum) == (1, 4)


@pytest.mark.parametrize(
    "probability,expected",
    [(0, 10), (0.05, 11.5), (0.25, 17.5), (0.5, 25), (0.75, 32.5), (0.95, 38.5), (1, 40)],
)
def test_quantile_linear_interpolation(probability, expected):
    assert quantile([40, 10, 30, 20], probability) == pytest.approx(expected)


@pytest.mark.parametrize(
    "values", [[], [True, 1], [1, float("nan")], [float("inf")], ["2", 3], [[1, 2]], [None, 1]]
)
def test_statistical_inputs_reject_invalid(values):
    with pytest.raises((ValueError, TypeError)):
        sample(values)


@pytest.mark.parametrize("probability", [-0.1, 1.1, float("nan"), True])
def test_bad_quantile_probability(probability):
    with pytest.raises(ValueError):
        quantile([1, 2], probability)


def test_missing_and_insufficient_are_explicit():
    missing = summarise([None, None])
    assert missing.available == 0 and missing.missing == 2 and missing.mean is None
    one = summarise([None, 2])
    assert one.mean == 2 and one.standard_error is None and one.mean_ci is None
    assert summarise([]).requested == 0
    assert summarise([3, 3, 3]).mean_ci.low == 3


def test_t_interval_matches_hand_value_and_scipy():
    result = mean_interval([1, 2, 3, 4])
    assert result.low == pytest.approx(0.4457397432)
    assert result.high == pytest.approx(4.5542602568)
    expected = stats.t.interval(0.95, 3, loc=2.5, scale=math.sqrt(5 / 3) / 2)
    assert (result.low, result.high) == pytest.approx(expected)


@pytest.mark.parametrize("confidence", [0, 1, -1, float("nan"), True])
def test_invalid_confidence(confidence):
    with pytest.raises(ValueError):
        mean_interval([1, 2], confidence)


def test_paired_difference_and_t_test_reference():
    first = [1, 2, 5, -2, 8]
    second = [3, 1, 6, -4, 11]
    assert paired_differences(first, second).tolist() == [2, -1, 1, -2, 3]
    result = paired_analysis(first, second, seed=4, resamples=100)
    expected = stats.ttest_rel(second, first)
    assert result["t_statistic"] == pytest.approx(expected.statistic)
    assert result["p_value_two_sided"] == pytest.approx(expected.pvalue)
    assert result["proportion_positive"] == 0.6 and result["proportion_negative"] == 0.4
    assert result["summary"].mean == 0.6


def test_paired_alignment_and_degeneracy():
    with pytest.raises(ValueError):
        paired_differences([1], [1, 2])
    result = paired_analysis([1, 2, 3], [1, 2, 3], seed=1, resamples=20)
    assert result["proportion_zero"] == 1
    assert result["p_value_two_sided"] is None
    assert result["summary"].mean_ci.low == 0
    assert paired_analysis([1], [2], seed=1)["bootstrap"] is None


def test_bootstrap_determinism_and_complete_pair_unit():
    first = np.array([1000, -1000, 2000, -2000, 500, -500])
    d = np.array([1, 2, 3, 2, 1, 3])
    direct = bootstrap(d, seed=19, resamples=100, unit="complete matched session pair")
    paired = paired_analysis(first, first + d, seed=19, resamples=100)["bootstrap"]
    assert direct == paired
    assert paired == paired_analysis(first, first + d, seed=19, resamples=100)["bootstrap"]
    assert paired != paired_analysis(first, first + d, seed=20, resamples=100)["bootstrap"]
    # The huge shared weather disappears; independent-side resampling would be wrong.
    assert paired.interval.high - paired.interval.low < 2


def test_bootstrap_reusable_statistic_and_constant_sample():
    result = bootstrap([1, 2, 3, 9], seed=3, resamples=100, statistic=np.median)
    assert result.estimate == 2.5
    constant = bootstrap([7] * 5, seed=3, resamples=100)
    assert constant.interval.low == constant.interval.high == 7
    assert constant.standard_error == 0


@pytest.mark.parametrize(
    "kwargs",
    [{"seed": -1}, {"seed": True}, {"seed": 1, "resamples": 1}, {"seed": 1, "confidence": 1}],
)
def test_bootstrap_invalid_parameters(kwargs):
    with pytest.raises(ValueError):
        bootstrap([1, 2], **kwargs)


def test_covariance_correlation_missing_and_constants():
    result = relationship([1, 2, 3, None], [2, 4, 6, 100])
    assert result == {"available": 3, "missing": 1, "covariance": 2.0, "correlation": 1.0}
    assert relationship([1, 1], [2, 3])["correlation"] is None
    assert relationship([1], [2])["covariance"] is None
    with pytest.raises(ValueError):
        relationship([1, 2], [1])


def test_tail_thresholds_are_strict_and_all_losses_retained():
    result = tail_risk([-2, -1, 0, 1, 2], thresholds=(0, -1, -2))
    assert result["probability_below"] == {"0.0": 0.4, "-1.0": 0.2, "-2.0": 0}
    assert result["worst"] == -2 and result["worst_five_percent_mean"] == -2
    assert result["p05"] == pytest.approx(-1.8)
    assert plain(result) == result
