"""Exact FIFO account and independent value/attribution reconciliation, in tick-units."""

from collections import deque
from dataclasses import dataclass
from fractions import Fraction

from quantlab.domain import Side, positive_integer
from quantlab.market_making.config import exact


class AccountingError(AssertionError):
    """An accounting identity failed; the account must not continue trading."""


@dataclass(frozen=True, slots=True)
class MakerFill:
    """Public own-execution facts. No counterparty type, latent value or signal."""

    trade_id: int
    time_us: int
    public_event_number: int
    side: Side
    quantity: int
    price_ticks: int
    fee_ticks: Fraction
    reference_before_ticks: Fraction
    midpoint_before_ticks: Fraction | None

    def __post_init__(self) -> None:
        for name in ("trade_id", "public_event_number", "quantity", "price_ticks"):
            positive_integer(getattr(self, name), name)
        if type(self.time_us) is not int or self.time_us < 0:
            raise ValueError("fill time must be nonnegative integer microseconds")
        if not isinstance(self.side, Side):
            raise TypeError("fill side must be Side")
        object.__setattr__(self, "fee_ticks", exact(self.fee_ticks, "fill fee"))
        object.__setattr__(
            self,
            "reference_before_ticks",
            exact(self.reference_before_ticks, "fill reference", positive=True),
        )
        if self.midpoint_before_ticks is not None:
            object.__setattr__(
                self,
                "midpoint_before_ticks",
                exact(self.midpoint_before_ticks, "fill midpoint", positive=True),
            )

    @property
    def signed_quantity(self) -> int:
        return self.quantity if self.side is Side.BUY else -self.quantity


@dataclass(frozen=True, slots=True)
class Lot:
    signed_quantity: int
    entry_price_ticks: int | Fraction


@dataclass(frozen=True, slots=True)
class AccountSnapshot:
    inventory: int
    execution_cash_ticks: Fraction
    cash_ticks: Fraction
    fees_ticks: Fraction
    reference_ticks: Fraction
    marked_value_ticks: Fraction
    realised_trading_pnl_ticks: Fraction
    realised_pnl_ticks: Fraction
    unrealised_pnl_ticks: Fraction
    total_pnl_ticks: Fraction
    spread_capture_ticks: Fraction
    inventory_movement_ticks: Fraction
    maximum_absolute_inventory: int


class MakerAccount:
    """FIFO gross realised P&L; optional endowed inventory; fees expensed immediately."""

    def __init__(
        self,
        initial_cash_ticks: Fraction,
        initial_reference_ticks: Fraction,
        *,
        hard_limit: int,
        initial_position: int = 0,
    ) -> None:
        self.initial_cash = exact(initial_cash_ticks, "initial_cash_ticks")
        self.reference = exact(
            initial_reference_ticks, "initial_reference_ticks", positive=True
        )
        positive_integer(hard_limit, "hard_limit")
        self.hard_limit = hard_limit
        if type(initial_position) is not int or abs(initial_position) > hard_limit:
            raise ValueError("initial_position must be an integer within the hard limit")
        self.initial_position = initial_position
        self.initial_position_value = initial_position * self.reference
        self.starting_equity = self.initial_cash + self.initial_position_value
        self.inventory = initial_position
        self.execution_cash = Fraction(0)
        self.fees = Fraction(0)
        self.realised = Fraction(0)
        self.capture = Fraction(0)
        self.movement = Fraction(0)
        self.maximum_inventory = abs(initial_position)
        self._lots: deque[Lot] = deque()
        if initial_position:
            self._lots.append(Lot(initial_position, self.reference))
        self._fills: list[MakerFill] = []
        self._seen: set[int] = set()
        self._failed = False

    @property
    def fills(self) -> tuple[MakerFill, ...]:
        return tuple(self._fills)

    @property
    def lots(self) -> tuple[Lot, ...]:
        return tuple(self._lots)

    def _healthy(self) -> None:
        if self._failed:
            raise AccountingError("account failed reconciliation; discard this instance")

    def mark(self, reference_ticks: Fraction) -> None:
        self._healthy()
        reference = exact(reference_ticks, "reference_ticks", positive=True)
        self.check_invariants()
        self.movement += self.inventory * (reference - self.reference)
        self.reference = reference
        self.check_invariants()

    def apply(self, fill: MakerFill) -> None:
        """Apply one actual fill once. Prevalidate before mutating; never clamp inventory."""
        self._healthy()
        for name in ("trade_id", "public_event_number", "quantity", "price_ticks"):
            positive_integer(getattr(fill, name), name)
        if type(fill.time_us) is not int or fill.time_us < 0:
            raise ValueError("fill time must be nonnegative integer microseconds")
        if not isinstance(fill.side, Side):
            raise TypeError("fill side must be Side")
        fee = exact(fill.fee_ticks, "fill fee")
        reference = exact(fill.reference_before_ticks, "fill reference", positive=True)
        if fill.trade_id in self._seen:
            raise ValueError("duplicate maker fill")
        self.check_invariants()
        if reference != self.reference:
            self._failed = True
            raise AccountingError("fill reference differs from the current account mark")
        if abs(self.inventory + fill.signed_quantity) > self.hard_limit:
            self._failed = True
            raise AccountingError("actual fill would breach the hard inventory limit")
        remaining = fill.signed_quantity
        while remaining and self._lots and remaining * self._lots[0].signed_quantity < 0:
            oldest = self._lots.popleft()
            closed = min(abs(remaining), abs(oldest.signed_quantity))
            sign = 1 if oldest.signed_quantity > 0 else -1
            self.realised += sign * closed * (fill.price_ticks - oldest.entry_price_ticks)
            residue = oldest.signed_quantity - sign * closed
            remaining += sign * closed
            if residue:
                self._lots.appendleft(Lot(residue, oldest.entry_price_ticks))
        if remaining:
            self._lots.append(Lot(remaining, fill.price_ticks))
        self.inventory += fill.signed_quantity
        self.execution_cash -= fill.signed_quantity * fill.price_ticks
        self.fees += fee
        self.capture += fill.signed_quantity * (self.reference - fill.price_ticks)
        self.maximum_inventory = max(self.maximum_inventory, abs(self.inventory))
        self._fills.append(fill)
        self._seen.add(fill.trade_id)
        self.check_invariants()

    def snapshot(self) -> AccountSnapshot:
        self.check_invariants()
        unrealised = sum(
            (
                lot.signed_quantity * (self.reference - lot.entry_price_ticks)
                for lot in self._lots
            ),
            Fraction(0),
        )
        cash = self.initial_cash + self.execution_cash - self.fees
        marked = cash + self.inventory * self.reference
        return AccountSnapshot(
            self.inventory,
            self.execution_cash,
            cash,
            self.fees,
            self.reference,
            marked,
            self.realised,
            self.realised - self.fees,
            unrealised,
            marked - self.starting_equity,
            self.capture,
            self.movement,
            self.maximum_inventory,
        )

    def check_invariants(self) -> None:
        """These explicit checks remain active under python -O."""
        self._healthy()
        q = self.initial_position + sum(fill.signed_quantity for fill in self._fills)
        execution_cash = sum(
            (-f.signed_quantity * f.price_ticks for f in self._fills), Fraction(0)
        )
        fees = sum((f.fee_ticks for f in self._fills), Fraction(0))
        capture = sum(
            (
                f.signed_quantity * (f.reference_before_ticks - f.price_ticks)
                for f in self._fills
            ),
            Fraction(0),
        )
        running_q = self.initial_position
        maximum_q = abs(running_q)
        for fill in self._fills:
            running_q += fill.signed_quantity
            maximum_q = max(maximum_q, abs(running_q))
        lots_q = sum(lot.signed_quantity for lot in self._lots)
        unrealised = sum(
            (
                lot.signed_quantity * (self.reference - lot.entry_price_ticks)
                for lot in self._lots
            ),
            Fraction(0),
        )
        total = (
            self.execution_cash
            - self.fees
            + self.inventory * self.reference
            - self.initial_position_value
        )
        checks = (
            q == self.inventory == lots_q,
            execution_cash == self.execution_cash,
            fees == self.fees,
            len(self._seen) == len(self._fills)
            and self._seen == {f.trade_id for f in self._fills},
            capture == self.capture,
            maximum_q == self.maximum_inventory,
            all(lot.signed_quantity * self.inventory > 0 for lot in self._lots),
            abs(q) <= self.hard_limit,
            total == self.realised + unrealised - self.fees,
            total == self.capture + self.movement - self.fees,
        )
        if not all(checks):
            self._failed = True
            raise AccountingError(
                "cash, fills, FIFO inventory or P&L attribution do not reconcile"
            )
