import math
import statistics

import pytest

from quantlab import LimitOrder, OrderBook, Side
from quantlab.agents.basic import PublicObservation
from quantlab.agents.informed import InformedTrader, PrivateSignal
from quantlab.market.processes import fundamental_step
from quantlab.market.signals import sample_signal
from quantlab.randomness import RandomStreams


@pytest.mark.parametrize("eta", [1.0, 4.0])
def test_signal_errors_have_configured_mean_and_variance(eta):
    n = 12000
    rng = RandomStreams(2026).create("signal-accuracy")
    errors = [sample_signal(10000, i, eta, rng).value_ticks - 10000 for i in range(n)]
    assert abs(statistics.mean(errors)) < 6 * eta / math.sqrt(n)
    assert abs(statistics.variance(errors) - eta**2) < 6 * eta**2 * math.sqrt(2 / (n - 1))


def test_cleaner_signals_reduce_estimation_error_under_the_stated_prior():
    n, tau = 8000, 8
    rng = RandomStreams(12).create("posterior-calibration")
    public, agent = (
        PublicObservation(9999, 10001, None, 10000),
        InformedTrader(prior_sd_ticks=tau),
    )
    errors = {1: [], 8: []}
    for i in range(n):
        truth = 10000 + tau * rng.gauss(0, 1)
        common_error = rng.gauss(0, 1)
        for eta in errors:
            signal = PrivateSignal(i, truth + eta * common_error, eta)
            estimate = agent.decide("i", public, signal, now_us=i).estimated_value_ticks
            errors[eta].append(estimate - truth)
    for eta, residuals in errors.items():
        variance = tau**2 * eta**2 / (tau**2 + eta**2)
        assert abs(statistics.mean(residuals)) < 6 * math.sqrt(variance / n)
        assert abs(statistics.variance(residuals) - variance) < 6 * variance * math.sqrt(
            2 / (n - 1)
        )
    assert statistics.mean(e * e for e in errors[1]) < statistics.mean(e * e for e in errors[8])


def test_information_quality_improves_discrimination_not_unconditionally_trade_count():
    """Clean signals encourage buying a real gap and discourage trading at fair value.

    Compare many measurements at fixed truths using common standardised errors.
    Six standard-error separation uses the paired indicator differences, so the
    shared draws are accounted for. Stronger truth also gives stronger buy flow.
    """
    n = 8000
    rng = RandomStreams(77).create("information-behaviour")
    public = PublicObservation(9999, 10001, None, 10000)
    agent = InformedTrader()
    gap_clean_vs_noisy, fair_noisy_vs_clean, strong_vs_weak = [], [], []

    def buys(decisions, truth, eta):
        order = decisions[truth, eta]
        return int(order is not None and order.side is Side.BUY)

    for i in range(n):
        error = rng.gauss(0, 1)
        decisions = {}
        for truth, eta in ((10000, 1), (10000, 8), (10008, 1), (10008, 8), (10012, 8)):
            signal = PrivateSignal(i, truth + eta * error, eta)
            decisions[truth, eta] = agent.decide("i", public, signal, now_us=i).order

        gap_clean_vs_noisy.append(buys(decisions, 10008, 1) - buys(decisions, 10008, 8))
        fair_noisy_vs_clean.append(
            int(decisions[10000, 8] is not None) - int(decisions[10000, 1] is not None)
        )
        strong_vs_weak.append(buys(decisions, 10012, 8) - buys(decisions, 10008, 8))
    for differences in (gap_clean_vs_noisy, fair_noisy_vs_clean, strong_vs_weak):
        assert statistics.mean(differences) > 6 * statistics.stdev(differences) / math.sqrt(n)


def test_informed_selection_produces_adverse_provider_markouts_without_assigned_losses():
    """Independent one-period trials under the agent's assumed Gaussian prior.

    Truth, measurement error and future shocks are sampled independently. The
    same future draw evaluates informed and random-direction counterparties.
    This verifies selection under a stated DGP, not calibration of the full market.
    """
    n, rng = 7000, RandomStreams(31).create("selection-experiment")
    public, agent = PublicObservation(9999, 10001, None, 10000), InformedTrader()
    informed, uninformed = [], []
    for i in range(n):
        truth = 10000 + 8 * rng.gauss(0, 1)
        signal = sample_signal(truth, i, 2, rng)
        decision = agent.decide("i", public, signal, now_us=i)
        # Future is drawn only after the decision has been made.
        future = fundamental_step(truth, 1, 1000000, rng)
        random_buy = rng.random() < 0.5
        uninformed.append((10001 - future) if random_buy else (future - 9999))
        if decision.order is not None:
            book = OrderBook()
            book.submit(LimitOrder("b", Side.BUY, 1, 9999))
            book.submit(LimitOrder("a", Side.SELL, 1, 10001))
            report = book.submit(decision.order)
            trade = report.trades[0]
            provider_direction = -1 if trade.aggressor_side is Side.BUY else 1
            informed.append(provider_direction * (future - trade.price_ticks))
    assert len(informed) > n // 4
    assert (
        statistics.mean(informed) + 6 * statistics.stdev(informed) / math.sqrt(len(informed))
        < 0
    )
    assert statistics.mean(uninformed) - 6 * statistics.stdev(uninformed) / math.sqrt(n) > 0
    assert any(m > 0 for m in informed)  # Some informed trades are wrong; no guaranteed wins.
