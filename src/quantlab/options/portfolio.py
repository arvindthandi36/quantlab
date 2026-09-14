"""Exact option cash flows and FIFO lots. Premium is cash, not immediate profit."""

from collections import deque
from dataclasses import dataclass
from fractions import Fraction

from quantlab.domain import positive_integer
from quantlab.options.models import exact
from quantlab.portfolio.accounting import AccountingError


@dataclass(frozen=True)
class OptionLot:
    quantity: int
    premium: Fraction


class OptionPortfolio:
    def __init__(self):
        self.contracts = {}
        self.lots = {}
        self.realised = {}
        self.cash = Fraction(0)
        self.fees = Fraction(0)
        self.ledger = []
        self._ids = set()
        self.settled = set()

    def quantity(self, contract_id):
        return sum(lot.quantity for lot in self.lots.get(contract_id, ()))

    def apply(
        self, contract, signed_contracts, premium, fee, execution_id, *, settlement=False
    ):
        if type(signed_contracts) is not int or signed_contracts == 0:
            raise ValueError("option fill must have nonzero signed whole contracts")
        positive_integer(abs(signed_contracts), "filled contracts")
        premium, fee = exact(premium), exact(fee)
        if min(premium, fee) < 0 or execution_id in self._ids:
            raise ValueError("negative premium/fee or duplicate execution")
        key = contract.id
        if key in self.settled:
            raise ValueError("settled option cannot trade again")
        if settlement and (signed_contracts != -self.quantity(key) or fee):
            raise ValueError(
                "cash settlement must close the entire position without trade fees"
            )
        self.contracts[key] = contract
        lots = self.lots.setdefault(key, deque())
        self.realised.setdefault(key, Fraction(0))
        remaining = signed_contracts
        while lots and remaining * lots[0].quantity < 0:
            old = lots.popleft()
            size = min(abs(remaining), abs(old.quantity))
            sign = 1 if old.quantity > 0 else -1
            self.realised[key] += sign * size * contract.multiplier * (premium - old.premium)
            remaining += sign * size
            residual = old.quantity - sign * size
            if residual:
                lots.appendleft(OptionLot(residual, old.premium))
        if remaining:
            lots.append(OptionLot(remaining, premium))
        cash_flow = -signed_contracts * contract.multiplier * premium
        self.cash += cash_flow - fee
        self.fees += fee
        self._ids.add(execution_id)
        self.ledger.append(
            {
                "id": execution_id,
                "contract_id": key,
                "quantity": signed_contracts,
                "premium": premium,
                "multiplier": contract.multiplier,
                "fee": fee,
                "cash_flow": cash_flow,
                "kind": "settlement" if settlement else "trade",
            }
        )
        if settlement:
            self.settled.add(key)
        self.check(
            {
                k: premium if k == key else (ls[-1].premium if ls else 0)
                for k, ls in self.lots.items()
            }
        )

    def snapshot(self, marks):
        values = []
        for key, contract in self.contracts.items():
            qty = self.quantity(key)
            mark = exact(marks[key]) if qty else Fraction(0)
            unrealised = sum(
                (
                    lot.quantity * contract.multiplier * (mark - lot.premium)
                    for lot in self.lots[key]
                ),
                Fraction(0),
            )
            values.append(
                {
                    "contract": contract,
                    "quantity": qty,
                    "mark": mark,
                    "value": qty * contract.multiplier * mark,
                    "realised_gross": self.realised[key],
                    "unrealised": unrealised,
                    "settled": key in self.settled,
                }
            )
        realised = sum(self.realised.values(), Fraction(0))
        unrealised = sum((x["unrealised"] for x in values), Fraction(0))
        value = sum((x["value"] for x in values), Fraction(0))
        return {
            "positions": values,
            "cash": self.cash,
            "fees": self.fees,
            "marked_value": value,
            "realised_gross": realised,
            "unrealised": unrealised,
            "net_pnl": realised + unrealised - self.fees,
        }

    def check(self, marks):
        for row in self.ledger:
            contract = self.contracts[row["contract_id"]]
            if (
                row["multiplier"] != contract.multiplier
                or row["cash_flow"] != -row["quantity"] * contract.multiplier * row["premium"]
            ):
                raise AccountingError("option premium, quantity and multiplier disagree")
        independent_cash = sum((r["cash_flow"] - r["fee"] for r in self.ledger), Fraction(0))
        independent_fees = sum((r["fee"] for r in self.ledger), Fraction(0))
        if independent_cash != self.cash or independent_fees != self.fees:
            raise AccountingError("option cash/fee ledger does not reconcile")
        for key in self.contracts:
            ledger_qty = sum(r["quantity"] for r in self.ledger if r["contract_id"] == key)
            if ledger_qty != self.quantity(key):
                raise AccountingError("option FIFO and execution quantities disagree")
            if self.lots[key] and any(
                lot.quantity * self.lots[key][0].quantity <= 0 for lot in self.lots[key]
            ):
                raise AccountingError("option FIFO retains opposing lots")
        s = self.snapshot(marks)
        if s["cash"] + s["marked_value"] != s["net_pnl"]:
            raise AccountingError("option equity and realised/unrealised P&L disagree")
