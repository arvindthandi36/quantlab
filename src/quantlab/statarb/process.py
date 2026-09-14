"""Sequential exogenous processes; private generating parameters never agent inputs."""

import math
from dataclasses import asdict, dataclass

import numpy as np

from quantlab.risk.monte_carlo import factor_matrix


@dataclass(frozen=True)
class Asset:
    identifier: str
    initial: float = 100
    volatility: float = 0.25  # GBP increment SD; common-factor mode uses return conversion.
    loading: float = 1

    def __post_init__(self):
        if (
            not isinstance(self.identifier, str)
            or not self.identifier
            or len(self.identifier) > 40
        ):
            raise ValueError("Asset needs a short identifier")
        if not all(math.isfinite(x) for x in (self.initial, self.volatility, self.loading)):
            raise ValueError("Finite asset parameters required")
        if self.initial <= 1 or not 0 <= self.volatility <= 10:
            raise ValueError("Invalid initial price/volatility")


@dataclass(frozen=True)
class Link:
    x: int = 0
    y: int = 1
    alpha: float = 0
    beta: float = 1
    phi: float = 0.92
    sigma: float = 0.16
    mean: float = 0
    break_at: int | None = None
    break_kind: str = "none"

    def __post_init__(self):
        if type(self.x) is not int or type(self.y) is not int or not 0 <= self.x < self.y:
            raise ValueError("Links must be acyclic in asset index order: x < y")
        if not all(
            math.isfinite(x) for x in (self.alpha, self.beta, self.phi, self.sigma, self.mean)
        ):
            raise ValueError("Finite link parameters required")
        if not 0 <= self.phi <= 1 or not 0 < self.sigma <= 10 or not 0.05 <= self.beta <= 5:
            raise ValueError("Invalid relationship parameters")
        if self.break_at is not None and (type(self.break_at) is not int or self.break_at < 1):
            raise ValueError("Break time must be a positive observation index")
        if self.break_kind not in ("none", "beta", "mean", "volatility", "decouple", "drift"):
            raise ValueError("Unknown relationship break")


class Process:
    def __init__(
        self, *, seed=10042, assets=None, correlation=0, common_factor=False, links=()
    ):
        if type(seed) is not int or not 0 <= seed < 2**1024:
            raise ValueError("Seed must be an integer in [0,2^1024)")
        self.assets = tuple(assets or (Asset("SA-X"), Asset("SA-Y")))
        self.links = tuple(sorted(links, key=lambda p: p.y))
        n = len(self.assets)
        if not 2 <= n <= 30 or len({a.identifier for a in self.assets}) != n:
            raise ValueError("Use 2–30 unique assets")
        if len({p.y for p in self.links}) != len(self.links) or any(
            p.y >= n for p in self.links
        ):
            raise ValueError("Each linked asset has one valid parent")
        if type(common_factor) is not bool or not math.isfinite(correlation):
            raise ValueError("Invalid process flags")
        if not -1 / (n - 1) <= correlation <= 1:
            raise ValueError("Equicorrelation outside the valid PSD range")
        corr = np.full((n, n), correlation)
        np.fill_diagonal(corr, 1)
        vol = np.array([a.volatility for a in self.assets])
        self.factor, self.factor_info = factor_matrix(corr * np.outer(vol, vol))
        self.config = dict(
            seed=seed,
            assets=[asdict(a) for a in self.assets],
            correlation=correlation,
            common_factor=common_factor,
            links=[asdict(p) for p in self.links],
        )
        self.rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence([seed, 1010])))
        self.common_factor = common_factor
        self.prices = np.array([a.initial for a in self.assets], dtype=float)
        self.spreads = {p.y: p.mean for p in self.links}
        self.t = 0
        self.evidence = []
        for p in self.links:
            self.prices[p.y] = p.alpha + p.beta * self.prices[p.x] + self.spreads[p.y]
        self._positive()

    def _positive(self):
        if not np.isfinite(self.prices).all() or (self.prices <= 0.05).any():
            raise ValueError(
                "Synthetic arithmetic process reached nonpositive executable prices; run failed"
            )

    def step(self):
        self.t += 1
        z = self.rng.standard_normal(len(self.assets) + 1)
        common = float(z[-1] * 0.002)
        if self.common_factor:
            returns = np.array(
                [
                    a.loading * common + a.volatility / a.initial * z[i]
                    for i, a in enumerate(self.assets)
                ]
            )
            self.prices = self.prices * (1 + returns)
        else:
            self.prices += self.factor @ z[:-1]
        for p in self.links:
            active = p.break_at is not None and self.t >= p.break_at
            kind = p.break_kind if active else "none"
            phi = 1 if kind in ("decouple", "drift") else p.phi
            mu = p.mean + (2 if kind == "mean" else 0)
            sigma = p.sigma * (4 if kind == "volatility" else 1)
            self.spreads[p.y] = mu + phi * (self.spreads[p.y] - mu) + sigma * z[p.y]
            if kind == "drift":
                self.spreads[p.y] += 0.06
            beta = p.beta + (0.15 if kind == "beta" else 0)
            self.prices[p.y] = p.alpha + beta * self.prices[p.x] + self.spreads[p.y]
        self._positive()
        self.evidence.append(
            dict(
                t=self.t,
                innovations=z.tolist(),
                common_factor_return=common,
                latent=self.prices.tolist(),
                residuals=dict(self.spreads),
            )
        )
        return np.round(self.prices, 2).tolist()

    @classmethod
    def from_config(cls, config):
        return cls(
            **(
                config
                | {
                    "assets": [Asset(**a) for a in config["assets"]],
                    "links": [Link(**p) for p in config["links"]],
                }
            )
        )


def scenario(name="stable", *, seed=10042, steps=240):
    if name == "common_factor":
        return Process(
            seed=seed,
            common_factor=True,
            assets=(
                Asset("SA-X", volatility=0.08, loading=1),
                Asset("SA-Y", volatility=0.12, loading=1.5),
            ),
        )
    if name in ("independent", "positive", "negative"):
        return Process(
            seed=seed, correlation={"independent": 0, "positive": 0.9, "negative": -0.9}[name]
        )
    if name == "noncointegrated":
        return Process(seed=seed, links=(Link(phi=1, sigma=0.08),))
    if name == "stable":
        return Process(seed=seed, links=(Link(),))
    if name in ("beta", "mean", "volatility", "decouple", "drift"):
        return Process(seed=seed, links=(Link(break_at=steps // 2, break_kind=name),))
    raise ValueError("Unknown synthetic scenario")
