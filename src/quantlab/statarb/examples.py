"""Completed, separately seeded teaching datasets; never the live market's future."""

import itertools

import numpy as np

from quantlab.statarb.process import Asset, Process
from quantlab.statarb.research import generate, mining_universe
from quantlab.statarb.statistics import correlation, diagnostics, ols, zscore


def relationship_example(prices):
    a = np.asarray(prices)
    f = ols(a[:160, 0], a[:160, 1], end=160)
    residual = f.residual(a[:, 0], a[:, 1])
    returns = np.diff(a, axis=0) / a[:-1]
    z = [None] * 160
    for t in range(160, len(a)):
        z.append(zscore(float(residual[t]), residual[:t], window=40)["z"])
    return dict(
        prices=a.tolist(),
        returns=returns.tolist(),
        fit=f.public(),
        residual=residual.tolist(),
        z=z,
        correlation=correlation(*a.T),
        return_correlation=correlation(*returns.T),
        diagnostics=diagnostics(residual[160:]),
        training_rows=160,
        label=(
            "Completed teaching dataset: fit first 160 rows; subsequent z "
            "uses only past residuals"
        ),
    )


def teaching_cases():
    cases = {}
    for name in (
        "stable",
        "noncointegrated",
        "positive",
        "negative",
        "independent",
        "common_factor",
    ):
        data, _ = generate(101001, name=name, steps=400)
        cases[name] = relationship_example(data)
    null, _ = mining_universe(101002, assets=8, steps=400)
    pairs = [
        dict(pair=[i, j], correlation=correlation(null[:160, i], null[:160, j]))
        for i, j in itertools.combinations(range(8), 2)
    ]
    best = max(pairs, key=lambda x: abs(x["correlation"]))
    cases["spurious"] = relationship_example(null[:, best["pair"]]) | {
        "selection": (
            "Largest absolute training price correlation among all 28 "
            "unrelated pairs; deliberately selected, not representative"
        ),
        "all_candidates": pairs,
        "selected": best["pair"],
    }
    p = Process(
        seed=101003,
        common_factor=True,
        assets=[
            Asset("F-X", volatility=0.08, loading=1),
            Asset("F-Y", volatility=0.12, loading=1.5),
            Asset("F-Z", volatility=0.1, loading=-0.5),
        ],
    )
    prior = p.prices.copy()
    prices = p.step()
    evidence = p.evidence[-1]
    factor = evidence["common_factor_return"]
    cases["factor_step"] = dict(
        factor_return=factor,
        assets=[
            dict(
                asset=a.identifier,
                loading=a.loading,
                common=a.loading * factor,
                idiosyncratic=a.volatility / a.initial * evidence["innovations"][i],
                total_unrounded=p.prices[i] / prior[i] - 1,
                published_price=prices[i],
            )
            for i, a in enumerate(p.assets)
        ],
    )
    cases["exact_regression"] = ols([1, 2, 3, 4, 5], [5, 8, 11, 14, 17]).public()
    return dict(
        label="Completed independent teaching datasets, not forecasts for your live session",
        cases=cases,
        process_claims={
            "stable": (
                "By construction: X random walk, Y=X+s with phi=.92. Stationary "
                "residual in the ideal unbounded process."
            ),
            "noncointegrated": (
                "By construction: X random walk, Y=X+s with independent phi=1 "
                "residual. High co-movement, no stationary linear combination."
            ),
            "spurious": (
                "Independent random walks; selecting the highest sample "
                "correlation is disclosed selection bias."
            ),
        },
    )
