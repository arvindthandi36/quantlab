# Phase 6 contract — manual trading

> Historical phase record. Current core conventions and release status are in the root README, ASSUMPTIONS and Phase 11 release report. Test counts and runtime labels below describe this phase.


Defined before implementation. Phase 7 is outside this change.

The local Python server owns a single session under a lock. The browser sends
commands and renders public projections. Every submitted order enters the Phase 1
OrderBook. The existing event sources, FIFO accounting and Phase 4 quote planner
are reused. No browser-side fills, accounting, random draws or financial metrics.

## Account and risk

The manual account and automated maker have separate ledgers and order ownership.
An opening scenario position q0 is endowed at the opening public reference R0:
starting equity is cash0 + q0 R0. It creates a FIFO lot but no execution, fee or
turnover. Net P&L = cash + q R - starting equity. Fees are expensed immediately.
Average entry is the quantity-weighted price of remaining FIFO lots.

For limit H, admission requires q + all outstanding buy quantity + new buy <= H,
and q - all outstanding sell quantity - new sell >= -H. Opposite orders do not
net reservations. Market orders conservatively reserve their whole requested
quantity before matching. Cancellation releases capacity only after engine success.
Orders that could cross one's own orders are rejected (conservative self-trade
prevention). Replacement is explicit cancellation followed by a new order, losing
priority. Manual two-sided quote refresh explicitly cancels all own orders first.

## Time, information and prices

A session opens paused. Wall-clock ticks advance a running session by recorded,
fixed simulation intervals; reads never advance time. Pause freezes automatic
progress. Explicit steps work while paused. Step event advances to the next
public exchange action, skipping private value updates and private no-trade
decisions internally. Matching an incoming order is one atomic exchange action.
Equal-time background events precede automated quote refreshes; user commands
follow events already processed at that clock. Ending cancels own and automated
maker orders at the current time and marks remaining inventory; no forced exit.

Public data is constructed from an allowlist: book depth, anonymised FIFO queues,
executions, own orders/account, elapsed time and already matured public markouts.
No raw background records, actor types, private clocks, signals or latent values.
Privileged journal export and debug inspection are available only after ending.
The user may choose a seed; this is an educational reproducibility tool, not a
security boundary against a user reverse-engineering the simulator locally.

Manual-account marking uses the midpoint of best quotes excluding its own orders;
if unavailable, the most recent real transaction, then opening reference. This
reference is a valuation convention, not an executable exit price. Public book
midpoint includes all quotes. Manual executions update the background agents'
last-transaction observation without drawing any randomness.

## Analytics, replay and UI

Per-order VWAP uses every actual fill, including later passive fills, exactly as a
Fraction. Display decimal rounding does not feed back into accounting. Markouts
use own-side sign times (future public midpoint - execution), at 1/5/20 subsequent
public exchange actions. Missing midpoint is reported as missing; unmatured
observations remain pending. Aggressor marks are execution diagnostics, not proof
of providing liquidity or an extra P&L component.

Replay saves configuration, ordered accepted/rejected/control actions, actual
background journal records and reconciled checkpoints. Verification re-executes
actions through the real engine and existing recorded-event replay source; a
separate seed regeneration verifies the original random path. Public playback
frames are rebuilt during verification; stored screenshots are not evidence.

The server binds loopback only, rejects cross-origin mutations, and serves bundled
assets without third-party scripts. UI commands return a revision; older responses
cannot overwrite newer views. Session errors stop automatic trading loudly.
Scenarios are deliberately uncalibrated configurations, not promised outcomes.


Implementation notes: ending first completes remaining events tied at the current
clock, then cancels orders; it never advances to a later timestamp. Live sessions
are capped at 5,000 commands; reaching the cap ends/cancels without applying the
extra requested action. The launcher auto-saves ended sessions to runs/manual;
active sessions are in memory. Browser imports send original journal text to avoid
changing JSON numeric representations before checksum verification. Save errors
are explicit and preserve the downloadable in-memory ended journal.
