# Bar paper execution — version bar-next-close-v1

**SIMULATED EXECUTION ON HISTORICAL DATA**. No result is an actual historical fill.
The artificial fixture runs the same rule, with its non-historical badge always visible.

1. At bar t, its full recorded OHLCV is available. Submit an instruction; it receives
   an ID but cannot execute at t.
2. At the next observed bar, reveal its close and volume. Candidate buy price is
   `close + slippage_ticks × tick_size`; candidate sell price is `close − slippage_ticks × tick_size`.
   Non-positive candidates cannot fill. The high and low never trigger an execution.
3. Each instrument has a shared budget `floor(volume × participation)`. Both sides
   draw from this same budget. Earlier submitted eligible instructions consume it first.
   This allocation rule is an assumption, not a reconstruction of historical FIFO queues.
4. Market instructions try **one** next observation. Execute up to the budget;
   cancel the unfilled remainder. Even zero volume cancels a market remainder.
5. Limit buys require candidate price at or below the limit; sells require at or above.
   Unfilled limit quantity can wait for later closes until cancellation/end. A crossed
   high/low alone does not fill a limit.
6. Fee equals executed units times the explicit fee per unit. Default: participation
   10%, one tick adverse slippage, £0.001 per executed unit. No fee on unfilled units.

`floor` means rounding **down** to a whole unit. If volume is 25 and participation is 10%,
2.5 becomes two executable units. It does not mean a real trader could have obtained them.
The fill becomes known at the later observation, not when the user submitted the order.
There is no market impact feedback into the recorded path, quoted spread, order-book depth,
queue-position estimate, or individual historical transaction tape.

The existing exact FIFO `MakerAccount` records executed cash, positions, lots, realised
and unrealised P&L and fees. A mirrored paper counterparty independently checks quantity,
execution price and execution cash. Orders, tape and both ledgers reconcile after each
fill; discrepancies poison the session and raise an error, without repair.

Net P&L = realised gross P&L + unrealised P&L − fees. The current recorded close marks
open lots. That is a valuation reference, not a promised exit price. Default starting cash
is £10,000 and the position limit is ±100 units per instrument. Pending same-side orders
reserve capacity. Borrow, cash funding, margin, dividends and financing are not modelled.
Shorting within the position limit is allowed. A cash balance is not a leverage constraint.

End cancels open instructions but does **not** fabricate liquidation. The summary ranks
execution cost against the same recorded close plus fees; no absent quote benchmark is
invented. Position/drawdown history samples revealed bars and each simulated execution.
