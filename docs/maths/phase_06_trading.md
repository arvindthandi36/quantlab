# Phase 6 — trading from first principles

You already understand that a buyer first trades with the cheapest eligible seller,
and that earlier orders at the same price go first. This desk lets you make those
decisions yourself. Beginner mode explains the terms; Quant mode shows extra
diagnostics. Both use exactly the same exchange.

## Bids, asks, spread and the book

A **bid** is someone's offer to buy. An **ask** is someone's offer to sell. The best
bid is the highest buying offer; the best ask is the lowest selling offer. The
**spread** is ask minus bid. With £99.99 bid and £100.01 ask it is £0.02.
The **mid** is their average, £100.00. It is a useful summary, not an offer you can
necessarily trade against. The live price chart plots actual trades instead.

The **order book** holds waiting orders. A level showing £99.98, 10 units, 2 orders
means two separate orders together offer to buy 10 units at that price. Expand
that level to inspect the queue. Aggregation changes the view, not time priority.

## Market and limit orders; liquidity

A **market buy** requests immediate execution against available asks. A market sell
takes bids. You choose quantity and accept the available prices. The book can run
out: in this simulator the unfilled market remainder cancels; it does not wait,
invent a counterparty or acquire a made-up price.

A **limit buy** sets your highest acceptable price; a limit sell sets your lowest.
If it can trade, it receives resting-order prices, including better prices than
your limit. Any unfilled quantity rests in the book. A limit is a price boundary,
not a promise of execution. A marketable limit can be partly an aggressor and later
partly a provider when its remainder is filled.

**Liquidity** here means actual units available to trade at visible prices. A deep
book can absorb more quantity near the top price. A thin book may force you to
accept worse prices or leave some of your order unfilled. Our Thin liquidity
scenario begins with one unit at each of three asks; buying six initially fills
three and cancels three. A rising chart is not a guarantee of accessible liquidity.

## Queue priority and partial fills

Price takes priority first. Within one price, earlier orders have priority. A buy
of five at £99.98 joins behind the five opening units already there. A later sell
of seven reaching that level fills those earlier five, then two of yours. You now
have a **partial fill**: two filled, three still waiting. Cancelling removes the
three; it cannot undo the two trades. Cancelling and re-entering gives a new queue
position. Refreshing manual two-sided quotes also loses old priority.

## VWAP: an average that respects quantity

An ordinary average gives every listed price equal weight. **Volume-weighted
average price (VWAP)** gives every executed unit equal weight:

\[
\mathrm{VWAP}=\frac{\sum_i p_i n_i}{\sum_i n_i}.
\]

Here p_i is one execution price and n_i is the number of units in that execution.
The summation sign means “add these terms”. For two units at £100.01 and four at
£100.02, total purchase value is £200.02 + £400.08 = £600.10. Divide by six:
**VWAP = £100.016666…**, displayed £100.01667. It is closer to the second price
because more units traded there. It is not £100.00 mid and not the unweighted
average of the two distinct prices. Fees are reported separately.

An order's VWAP includes later passive executions too. Internally it is an exact
fraction; display rounding does not alter cash or P&L. No fills means no VWAP.
**Average entry** instead averages the cost of the units you still hold. It can
differ from an earlier order's VWAP once some units are closed using FIFO.

## Position, cash, shorts and risk reservations

Position q counts units. Buying adds units; selling subtracts. Positive q is **long**;
negative q is **short**. Starting at +1 and selling three leaves −2. The first unit
closes the long; the other two open a short. Selling increases cash, but that cash
does not by itself mean profit: the short position is an obligation valued against
the same public reference.

With a limit H=20, every possible fill must keep position between −20 and +20.
Outstanding orders reserve capacity:

\[
q+\text{all resting buys}+\text{new buy}\le H,
\qquad
q-\text{all resting sells}-\text{new sell}\ge-H.
\]

At q=6 with five units already bid, you can submit at most nine more buy units.
Opposite orders cannot cancel this risk on paper: one side might fill while the
other never does. Market orders conservatively reserve their full requested size.
Own-crossing orders are rejected to avoid self-trades. This is a small position
control, not a full margin, borrowing or portfolio risk system.

## Realised, unrealised and total P&L

P&L means profit and loss. The account closes the oldest opposite lots first
(FIFO). **Gross realised P&L** records price gains/losses on closed units. Fees are
expensed immediately, so displayed **realised P&L = gross realised − all fees so
far**, including fees on positions still open. **Unrealised P&L** values remaining
lots at today's public reference:

\[
\mathrm{unrealised}=\sum_j q_j(R-p_j),
\qquad
\mathrm{net}=\mathrm{realised}+\mathrm{unrealised}.
\]

Each q_j is signed: negative for a short lot. If the reference rises, a long gains
and a short loses. The reference is the best midpoint after excluding your own
orders, or last trade if that external book is one-sided, then the opening price
if no trade exists. The screen names the fallback. A valuation is not a guaranteed
liquidation price; exiting may cross the spread and consume several levels.

Independently, the account checks:

\[
\mathrm{net}=\mathrm{cash}+qR-\mathrm{opening\ equity}.
\]

For an opening position q0, opening equity is cash0 + q0 R0. That position is endowed
at R0 with no fabricated trade, fee or turnover. This prevents an opening long
position from appearing as free profit. A zero opening position reduces the
formula to cash + qR − cash0.

In the saved manual demo, eight bought units cost **£800.12** and eight sold units
receive **£800.07**. All positions close: gross loss £0.05, fees £0.016, net loss
**£0.066**. Realised = net, unrealised = zero at the end. Earlier, the initial
six-unit buy has £0.006 fees and a £0.07 unrealised loss, so net is −£0.076.

## Directional exposure and drawdown

With q unchanged, a reference change ΔR changes marked P&L by q × ΔR. This is
**directional risk**. In the demo, short two units benefit when their reference
falls from £100.01 to £99.995: (−2) × (−£0.015) = +£0.03. Buying back later at
£100.01 costs more than that reference and incurs another fee. Marked gains are
not guaranteed exit gains. The model does not reward the direction you choose.

Signed notional exposure is qR, in pounds. Maximum long/short exposure is reported
in units. Average absolute position weights |q| by how long you held it, rather
than giving every button press equal weight. Average absolute notional similarly
time-weights |q|R between public changes. At zero elapsed time both averages are
undefined, not zero. These are exposure summaries, not estimates of worst-case loss.

**Drawdown** is the fall from your best earlier net P&L, including opening zero.
Maximum drawdown is the largest such fall at observed public states. A later
recovery does not erase the earlier drawdown. The demo's maximum is £0.076 even
though its final loss is £0.066. Private latent moves do not revalue the public
account between observations.

## Markouts: later information, not extra profit

For each own execution, record side s=+1 for a buy or −1 for a sell. After h more
public exchange actions, inspect the public midpoint M:

\[
\mathrm{markout}_h=s(M_{t+h}-P_{\mathrm{execution}}).
\]

A positive result means the later midpoint favoured your side of that execution.
A negative result means it moved against that side, relative to your execution
price. A resting seller filled before the midpoint rises has a negative markout.
That is consistent with adverse selection, but one observation does not prove the
counterparty was informed. Counterparty identity stays hidden.

Provider means your resting order supplied liquidity; aggressor means your order
took it. An aggressor markout is a later execution-price diagnostic, not evidence
that you provided liquidity. It is neither FIFO realised P&L nor an extra sum to
add to P&L. Fees and your later trades are separate. Horizons are 1, 5 and 20 public
actions, not seconds: private events and read/pause commands do not count. Your
own cancellations/quotes can count and can influence the midpoint. A missing
two-sided midpoint is missing data; an unfinished horizon remains pending.

## Quant mode, honestly labelled

Depth imbalance = (bid units − ask units)/(bid units + ask units), using at most
five visible levels on each side. It ranges from −1 to +1 when defined. Positive
means more displayed buying quantity in that window, not a forecast of a rise.

The most recent return is ln(P_new/P_old), using successive real executions.
“ln” is the natural logarithm: it turns a multiplicative price ratio into an
additive return. A ratio of one gives zero; above one gives positive; below one
negative. Returns are not annualised and may share a timestamp across fills.

The displayed realised volatility is √sum(r²), over up to 20 such trade returns.
Squaring prevents up/down movements from cancelling; the square root restores
return units. It is a measure of movement over that trade window, not a forecast,
calendar-time volatility estimate or standard error. The observation count is
shown. No prior execution means no return/volatility value.

Order flow reports buy-aggressor and sell-aggressor executed quantity for the last
20 executions; flow imbalance uses the same difference-over-total formula. It
does not pretend to identify informed traders or count unexecuted intentions.

## Practise in the app

Load `docs/learning/phase_06/manual-session.json` to inspect verified public replay
frames. In a new paused Normal session, repeat its early actions. Then change your
orders and watch a different endogenous outcome. The scenario and random source
are fixed by the seed, but agents react to the changed book; trades need not stay
identical after you change your actions.

The optional checkpoint supplies an observed book, asks a prediction and gives a
hint/retry. It explains your actual result after you trade, without giving future
prices. A good decision can lose money and a poor one can profit. Record the
information and reasoning you had at submission, then examine outcomes separately.

Three questions for Arvind (answers deliberately not recorded):

1. You buy two units at £100.01 and four at £100.02. Why is VWAP nearer £100.02?
2. Your limit buy has filled two of five units. What does cancelling it remove?
3. You are short two units. What happens to marked P&L if the reference rises £0.03?
