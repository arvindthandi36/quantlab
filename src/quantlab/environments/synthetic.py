"""A thin environment facade over the approved synthetic application."""


class SyntheticEnvironment:
    engine = "trading"

    def __init__(self, controller):
        self.controller = controller

    @property
    def status(self):
        return self.controller.state()["status"]

    @property
    def actions(self):
        return self.controller.session.actions

    def public(self):
        return {
            "environment": {
                "type": "SYNTHETIC",
                "badge": "SYNTHETIC",
                "hidden": False,
                "id": "synthetic-session",
                "source": "QuantLab seeded agent simulation",
                "hidden_model_state": True,
                "counterparty_simulation": True,
                "future_stored": False,
                "execution_model": "Approved price-time FIFO book",
                "truth": "Artificial agent orders and model values; actual simulated matches.",
            },
            "core": self.controller.state(),
        }

    def command(self, kind, **payload):
        return self.controller.command({"kind": kind, "payload": payload})

    def journal(self):
        return self.controller.environments.journal()
