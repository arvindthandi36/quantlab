"""Phase 5 adapter: complete executed hedge sessions on common Gaussian innovations."""

from quantlab.options.models import OptionType, number
from quantlab.options.session import OptionsConfig, OptionsSession
from quantlab.research.codec import digest
from quantlab.research.models import SimulationOutcome


class OptionsAdapter:
    name = "european-discrete-hedging-v1"

    def validate(self, configuration):
        if not isinstance(configuration, dict) or set(configuration) != {
            "market",
            "option_type",
            "strike",
            "expiry_days",
            "quantity",
            "hedge_frequency",
        }:
            raise ValueError(
                "Derivatives adapter requires market, contract, signed quantity and "
                "hedge frequency"
            )
        market = OptionsConfig(**configuration["market"])
        OptionType(configuration["option_type"])
        if (
            configuration["strike"] not in market.strikes
            or configuration["expiry_days"] not in market.expiries_days
        ):
            raise ValueError("Research contract must be in the configured chain")
        qty = configuration["quantity"]
        if type(qty) is not int or not 1 <= abs(qty) <= min(100, market.quote_size):
            raise ValueError(
                "Research position must fill completely within configured option depth"
            )
        if type(configuration["hedge_frequency"]) is not int or configuration[
            "hedge_frequency"
        ] not in (0, 1, 5, 20):
            raise ValueError("Supported hedge frequencies are 0,1,5,20")
        number(configuration["expiry_days"], "research expiry days", 0.01)

    def environment_key(self, configuration):
        self.validate(configuration)
        c = OptionsConfig(**configuration["market"])
        # Volatility comparisons share innovations, not identical transformed price paths.
        return {
            "weather": "options.stock.innovations-v1",
            "steps": c.steps,
            "step_days": c.step_days,
        }

    def run(self, seed, configuration, *, full=False):
        self.validate(configuration)
        config = OptionsConfig(**(configuration["market"] | {"seed": seed}))
        s = OptionsSession(config, capture=full)
        contract = next(
            c
            for c in s.contracts.values()
            if c.option_type == configuration["option_type"]
            and float(c.strike_gbp) == configuration["strike"]
            and float(c.expiry_years * 365) == configuration["expiry_days"]
        )
        qty = configuration["quantity"]
        s.command(
            "option_order",
            contract_id=contract.id,
            side="buy" if qty > 0 else "sell",
            quantity=abs(qty),
            quote_revision=s.quote_revision,
        )
        frequency = configuration["hedge_frequency"]
        if frequency:
            s.command("set_auto", frequency=frequency)
            s.command("hedge")
        s.command("step", count=config.steps)
        metrics = s.metrics()
        evidence = {
            "history": s.history,
            "option_ledger": s.portfolio.ledger,
            "stock_fills": s.stock.account.fills,
            "funding": s.funding_ledger,
            "metrics": metrics,
        }
        return SimulationOutcome(
            metrics,
            digest(s._innovations),
            digest(evidence),
            coverage={
                "complete_steps": s.step_index,
                "weather": "common standard normals; transformed prices may differ",
            },
            journal=s.journal() if full else None,
        )

    def metric_units(self, configuration):
        financial = (
            "cash",
            "option_cash",
            "stock_cash",
            "option_value",
            "stock_value",
            "option_realised_gross",
            "option_unrealised",
            "option_gross_pnl",
            "hedge_gross_pnl",
            "stock_realised_gross",
            "stock_unrealised",
            "option_fees",
            "stock_fees",
            "fees",
            "financing",
            "total_pnl",
            "net_pnl",
            "gross_hedging_error",
            "drawdown",
        )
        return {
            **dict.fromkeys(financial, "GBP"),
            **dict.fromkeys(
                (
                    "residual_delta",
                    "absolute_residual_delta",
                    "max_absolute_delta",
                    "rms_delta",
                ),
                "underlying units",
            ),
            "max_absolute_gamma": "underlying units per GBP stock move",
            "max_absolute_vega": "GBP per 1.00 absolute annual volatility",
            "turnover": "underlying units traded",
            "hedges": "executed hedge occasions",
            "realised_volatility": "annual decimal; close-to-close quadratic variation",
        }
