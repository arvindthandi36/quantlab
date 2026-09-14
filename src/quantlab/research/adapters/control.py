"""Known-equal-skill statistical control; these payoffs are NOT trading-engine P&L."""

import math

from quantlab.randomness import RandomStreams
from quantlab.research.codec import digest
from quantlab.research.models import SimulationOutcome


class GaussianControl:
    name = "gaussian-equal-skill-control-v1"

    def validate(self, configuration):
        if set(configuration) != {"variant_id", "mean", "sd"}:
            raise ValueError("control requires variant_id, mean and sd")
        if not isinstance(configuration["variant_id"], str) or not configuration["variant_id"]:
            raise ValueError("control variant id must be nonempty")
        for key in ("mean", "sd"):
            if type(configuration[key]) not in (int, float) or not math.isfinite(
                configuration[key]
            ):
                raise ValueError("control parameters must be finite")
        if configuration["sd"] <= 0:
            raise ValueError("control sd must be positive")

    def environment_key(self, configuration):
        return {"weather": "standard-normal-v1"}

    def run(self, seed, configuration, *, full=False):
        self.validate(configuration)
        streams = RandomStreams(seed)
        weather = streams.create("control.weather").gauss(0, 1)
        idiosyncratic = streams.create("control.variant:" + configuration["variant_id"]).gauss(
            0, 1
        )
        payoff = configuration["mean"] + configuration["sd"] * (
            0.5 * weather + math.sqrt(0.75) * idiosyncratic
        )
        evidence = {"weather": weather, "variant_noise": idiosyncratic, "payoff": payoff}
        return SimulationOutcome(
            {"net_pnl": payoff},
            digest(weather),
            digest(evidence),
            journal=evidence if full else None,
        )

    def metric_units(self, configuration):
        return {"net_pnl": "synthetic payoff units; not trade P&L"}
