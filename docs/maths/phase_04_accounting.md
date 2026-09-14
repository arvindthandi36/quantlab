# Phase 4 contract — defined before implementation

Owner: **Arvind Thandi**. Scope: Market Making Lab only. No Phase 5 research engine.

## Information, reference and execution

The lab reuses the existing background market and matching engine. Normal strategy
inputs contain public prices, the maker's own inventory/account/quotes and public
fills/markouts. They contain no latent value, signal, counterparty type, private
event count or root seed. Observer journals/debug may disclose these separately.

The observable marking/quoting reference R is the exact midpoint of the best
external bid/ask, excluding this maker's own orders. If either side is missing,
use the last actual transaction, else the configured public opening reference.
Every observation labels its reference source. Excluding own quotes avoids directly
moving the valuation benchmark by skewing one's own quotes. Last-trade fallback
can still be influenced by one's executions; the reference is not true value.

Decisions occur at t=0, then fixed refresh intervals strictly before the horizon.
Background events at the same time occur first, in their existing order. Cancel
old maker orders before replacing them. New IDs lose old FIFO priority. Maker
orders are passive: round bids down/asks up to integer ticks, then move an order
outward if necessary to avoid crossing an external quote. Report adjustments.
Never fabricate a fill. Nonpositive proposed sides are disabled with a reason.
Zero requested size withdraws that side. Cancel remaining maker quotes at the
horizon, without liquidating inventory or inventing an exit price.

## Strategies and limits

Fixed strategy: centre = R; symmetric distances default to 2 ticks; size 2/side.
It ignores inventory when choosing its centre. A common safety layer applies to
both strategies and manual instructions, so comparisons share the same limits.

Inventory-aware strategy, with signed inventory q (positive long, negative short):

    excess = max(0, |q| - soft_limit) / (hard_limit - soft_limit)
    centre = R - k q (1 + excess)
    bid = floor(centre - bid_distance)
    ask = ceil(centre + ask_distance)

Default k = 0.5 ticks/unit, soft limit 4 units, hard limit 8 units. Below the soft
limit this is the simple R-kq rule; beyond it the shift grows faster. Long inventory
lowers both quotes: a less attractive bid discourages more purchases; a cheaper
ask encourages sales. Short inventory reverses those incentives. This is a simple
rule, not an optimal-control solution or a volatility-aware strategy.

Beyond the soft limit, multiply the requested exposure-increasing side's size by
(hard_limit - |q|)/(hard_limit - soft_limit), rounding size down. Reducing exposure
is not soft-throttled. The fixed centre still ignores inventory; this shared risk
overlay does not. Requested sizes are also capped independently:

    resting buy quantity <= hard_limit - q
    resting sell quantity <= hard_limit + q

Never offset bid reservations against asks that might not fill. Partial fills
preserve these bounds: a buy increases q while reducing remaining bid quantity
by exactly the same amount. Selling has the mirrored effect. Check exposure after
every maker fill and quote replacement. Limits cannot be changed mid-session in
this phase. They do not model margin, funding or limits imposed by other venues.

## Exact account convention

All monetary accounting is in tick-unit amounts using exact rational arithmetic;
multiply by tick size for currency. Inventory and order size are signed/unsigned
whole units. Start with zero inventory and configured cash C0 (default 1,000,000
tick-units, or £10,000 at a penny tick). Shorts and borrowing are permitted subject
to the symmetric inventory cap; no funding charges or collateral model exists.

For a maker fill, signed size dq is positive for a buy and negative for a sell.
Execution price P is integer ticks; fee f defaults to 0.1 tick per executed unit.
No fee is charged for quotes, cancellations or unfilled quantity.

    execution_cash_change = -dq P
    q_new = q_old + dq
    cash = C0 + sum(execution_cash_change) - cumulative_fees
    marked_value = cash + q R
    total_PnL = marked_value - C0

FIFO lots determine gross realised trading P&L. Sell against oldest long lots;
buy against oldest short lots. A trade through zero closes old lots then opens
the opposite position at its execution price. Remaining lots determine unrealised
P&L. Fees are expensed immediately, including opening-position fees:

    realised_net_PnL = realised_gross_trading_PnL - cumulative_fees
    unrealised_PnL = sum(signed_open_lot_size * (R - entry_price))
    total_PnL = realised_net_PnL + unrealised_PnL

Independently reconcile fills to inventory, execution cash, fees and open lots,
and reconcile both P&L identities after mutations/marks. Fail loudly and make a
failed account/lab unusable for continued trading. Do not repair mismatches.

## Additive attribution versus diagnostics

Use one stated marking reference path for an exact arithmetic decomposition.
For a fill, record execution edge dq(R_before - P). This is called the **spread
capture proxy**: it is an edge against the observable marking reference, not
necessarily half the quoted spread or a completed round-trip profit.

For each reference change, record inventory carried across that change times
the reference change. Mark to the pre-order reference, process all fills at that
reference, then mark the resulting inventory to the post-order reference:

    total_PnL = cumulative_execution_edge + inventory_reference_movement - fees

This identity is exact under this event convention. Attribution changes if the
chosen reference or event convention changes. It is not a unique economic truth.
The report identifies positive results dominated by inventory/reference movement
without declaring them successful liquidity provision.

Separately report provider-signed markouts. For normal mode, h=1,5,20 counts
subsequent **public exchange events** (a submitted background order, a quote
replacement with actual exchange actions, or final cancellation with actions).
Private holds/latent updates do not count. The trade event is excluded. All fills
from one incoming order share its pre-order reference and horizon origin.

Public markouts use the full visible book's midpoint, not the marking fallback.
Missing midpoints stay missing; immature horizons remain pending. Private debug
may also calculate latent-reference marks at these same public-event horizons.
Phase 3's existing internal-event analytics remain available for its old sessions;
do not compare its event horizons numerically with this newly labelled clock.

Markouts are gross, per-unit diagnostics; quantity-weighted averages report their
coverage. They are never posted to the cash ledger or added to P&L attribution.
Effective spread, when the full pre-order midpoint exists, is twice the signed
provider edge against that midpoint, volume weighted. It is positive for passive
fills in this uncrossed-book model, but does not guarantee favourable later markouts.

## Diagnostics and comparison

Fill rate = maker executed units / all posted maker units, including replacement
orders. It is sensitive to refresh/cancellation frequency and is not an estimated
probability conditional on quote distance. Also report buy/sell fill counts and
units, fill count, turnover (sum of absolute executed notionals), costs, P&L and
maximum observed peak-to-trough marked-P&L drawdown. No annualised ratios.

Inventory averages, absolute averages and RMS inventory are time weighted over
the full horizon, including idle intervals. Maximum absolute inventory checks
every fill. Quoted-spread average is time weighted only over intervals with both
own quotes resting; report that coverage. Effective spread and markouts are
quantity weighted over observations where the reference is available.

Compare fixed and inventory-aware configurations with identical market seeds,
independent named exogenous streams, horizons, spreads, fees and limits. Verify
that arrival times, latent paths and private measurements agree. Strategies can
change public prices and therefore later decisions/fills; common random numbers
mean common exogenous randomness, not identical executed order flow. Predeclare
20 seeds (0 through 19) and 30-second horizons; retain all runs, without tuning
parameters or selecting favourable seeds. This is modest validation, not Phase 5.

## Manual teaching loop

Manual mode shows public book/reference, own quotes/account, recent own fills and
public midpoint markouts before each fixed decision. The user chooses bid/ask
distance and size, then advances to the next decision. Debug is separately opt-in.

At selected decisions: OBSERVE → PREDICT → DECIDE → RESULT → EXPLAIN. A wrong first
prediction gets a hint and retry; explanation is withheld until the result stage.
Questions may use clearly labelled hypothetical situations when the current state
does not demonstrate the concept. Do not award mastery merely for running a demo.
