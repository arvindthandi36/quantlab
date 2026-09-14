"""IID risk-neutral terminal sampling, with the existing Phase 5 uncertainty tools."""

import math
from dataclasses import asdict

import numpy as np

from quantlab.options.models import OptionType
from quantlab.options.pricing import price
from quantlab.randomness import RandomStreams
from quantlab.research.statistics import mean_interval


def terminal_payoffs(kind, inputs, *, paths, seed):
    if type(paths) is not int or not 2 <= paths <= 2_000_000:
        raise ValueError("Monte Carlo paths must be an integer in 2–2,000,000")
    stream_seed = RandomStreams(seed).create("options.pricing.terminal-v1").getrandbits(128)
    rng = np.random.Generator(np.random.PCG64(stream_seed))
    z = rng.standard_normal(paths)
    t, sigma = inputs.time_years, inputs.volatility
    terminal = inputs.spot * np.exp(
        (inputs.rate - inputs.dividend_yield - 0.5 * sigma * sigma) * t
        + sigma * math.sqrt(t) * z
    )
    sign = 1 if OptionType(kind) == OptionType.CALL else -1
    payoffs = math.exp(-inputs.rate * t) * np.maximum(sign * (terminal - inputs.strike), 0)
    if not np.isfinite(payoffs).all():
        raise ArithmeticError("Monte Carlo payoffs overflowed; no estimate returned")
    return payoffs


def monte_carlo_price(kind, inputs, *, paths=100_000, seed=42):
    values = terminal_payoffs(kind, inputs, paths=paths, seed=seed)
    estimate = float(np.mean(values))
    se = float(np.std(values, ddof=1) / math.sqrt(paths))
    analytic = price(kind, inputs)
    return {
        "estimate": estimate,
        "standard_error": se,
        "confidence_interval": asdict(mean_interval(values)),
        "paths": paths,
        "analytic": analytic,
        "error": estimate - analytic,
        "standard_errors_from_analytic": (estimate - analytic) / se if se else None,
        "seed": seed,
        "measure": "risk-neutral; drift = rate − continuous dividend yield",
        "sampling": "IID terminal normals; PCG64, named independent pricing stream",
        "unit": "GBP per underlying unit",
        "inputs": asdict(inputs),
        "warnings": (
            ["No sampled payoff variation: the interval cannot resolve unsampled rare tails."]
            if se == 0 and inputs.volatility > 0 and inputs.time_years > 0
            else []
        ),
    }
