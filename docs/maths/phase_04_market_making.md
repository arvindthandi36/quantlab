# Phase 4 lesson — quoting, inventory and honest P&L

Owner: **Arvind Thandi**. Read alongside the [exact contract](phase_04_accounting.md).
Every example below is teaching arithmetic unless explicitly identified as the
recorded seed-42 run. The baseline policy is deliberately simple and unoptimised.

## Intuition: a shop with changing stock value

A maker offers to buy at a bid and sell at an ask. The difference is its quoted
spread. Both orders are genuine offers in the existing book. Nobody promises that
both will fill, that they will fill in a convenient order, or that value will stay
unchanged while the maker waits.

Inventory is the number of units currently held: +3 means long three; −3 means
short three. Buying adds to inventory; selling subtracts. A short position benefits
from a falling reference and suffers from a rising one, before costs and other trades.

## Quote centre and inventory sign

At reference £100, a fixed two-tick half-spread gives £99.98 bid and £100.02 ask.
The half-spread is the distance on one side; the whole quoted spread is four ticks.

The basic inventory-aware centre is R − kq. R is public reference, q inventory,
and k the price shift per inventory unit. At q=+4 and k=£0.005 per unit, centre is
£99.98; before safety adjustments, bid £99.96 and ask £100.00. Lowering the bid makes
another purchase less competitive. Lowering the ask makes a sale more attractive.
For q=−4 the centre rises to £100.02, encouraging purchases and discouraging sales.

This changes willingness to trade; it cannot force a counterparty to appear. The
maker stays passive, so a proposed crossing order is moved outward. Tick rounding
is also deliberate: floor a bid, ceil an ask. With centre £100.025 and two-penny
distances, the bid becomes £100.00 and ask £100.05, not off-grid half-penny orders.

Beyond the soft limit, both the centre adjustment and the size restriction become
stronger. At q=+5, soft=4 and hard=8, excess is (5−4)/(8−4)=1/4. The inventory-aware
shift is −0.5×5×1.25 = −3.125 ticks. A requested two-unit bid is scaled by 3/4 and
rounded down to one unit. Its ask size is not soft-throttled.

At the hard limit, the exposure-increasing side is disabled. At q=+7 and hard=8,
no more than one additional resting buy unit is permitted, even if sell orders
are also present. Those sells might never execute. Hard capacity counts outstanding
orders as well as current holdings.

## Cash is not profit

Buying two units at £99 costs £198 and leaves two assets in the account. A £198
cash decrease is not automatically a loss: the assets have a marked value too.
Selling short produces cash but creates an obligation represented by negative inventory.

With initial cash C0, current cash C, inventory q and public reference R:

    marked value = C + qR
    total P&L = C + qR − C0       (starting inventory is zero)

No one claims that the full position could be liquidated at R. It is a stated
valuation benchmark, not a guaranteed exit quote.

## Realised and unrealised P&L

FIFO means first in, first out. Suppose you buy two at £99, buy one at £101, then
sell two at £103. The sale closes the oldest two purchases: gross realised trading
P&L is 2×(103−99)=£8. One unit bought at £101 remains. Mark it at £102 and unrealised
P&L is £1. Before fees, total P&L is £9.

The ledger subtracts all paid fees immediately from net realised P&L, including
fees on still-open lots. Thus net realised plus unrealised equals total marked P&L.
Gross realised trading P&L is also shown, so the fee convention is visible.
Other lot conventions can change realised versus unrealised allocation while
leaving total marked P&L unchanged under the same execution/fee/reference facts.

## Spread capture, carrying inventory and markouts

For a signed fill dq at price P, the execution-edge proxy is dq(R_before−P).
Buying below the public reference gives positive edge; selling above it does too.
This is called a spread-capture proxy, because R may differ from the full-book midpoint.
It is not another cash receipt to add to realised P&L.

While q units are held and reference changes by ΔR, the inventory valuation changes
by qΔR. Three long units carried through a £2 rise contribute £6. This can create
a profitable result even if every execution occurred exactly at the reference.

By processing reference changes and executions in the documented order, we obtain:

    total P&L = execution-edge proxy + inventory/reference movement − fees

This is a second view of the same P&L. Never add it to realised plus unrealised.
It is mathematically exact for the chosen reference path, but the interpretation
depends on that reference. Last-trade fallback can be influenced by our own trades.

A markout asks a different question: how does a fill look against a later reference?
For a resting buyer it is later reference minus purchase price; for a resting seller
it is sale price minus later reference. A seller at £100.05 with later midpoint
£100.08 has a −£0.03 per-unit provider markout. That is adverse. It does not mean
£0.03 was withdrawn from cash or that a closing trade happened.

Informed takers can select quotes favourable to themselves. Tight quotes can fill
frequently and still have poor markouts. Our constructed test has a tight maker
buy at 99 ticks, followed by midpoint 96: −3 ticks. A wider maker gets no fill on
that declared path. There is no universal rule that wider quotes are better either.

## Reading risk and fill diagnostics

Average inventory weights each holding by how long it lasted. Holding +2 for one
second and 0 for three gives average +0.5. Average absolute inventory ignores sign;
otherwise long and short periods could cancel and conceal exposure. RMS inventory
is the square root of average squared inventory, giving greater weight to large
positions. Maximum absolute inventory records the largest actual position.

Drawdown measures a fall from an earlier P&L peak. A path 0 → 5 → 2 has drawdown 3,
although final P&L is positive. We measure public event-end marked P&L, not unseen
intramatch extrema or a hypothetical liquidation value.

Our fill rate is executed maker units divided by posted maker units. Replacing
quotes increases the denominator, so it is not a universal fill probability.
Turnover sums the absolute notional value of all own executions. Effective spread
is twice the provider's signed edge against the pre-order full-book midpoint,
volume weighted over fills with a valid midpoint. It is a diagnostic, not P&L.

Markout averages are also volume weighted. One unit with +12 ticks and three with
−2 ticks average (12−6)/4=+1.5 ticks per unit. Missing or pending marks are excluded,
and their quantities are reported. An average with low coverage may be misleading.

## Common random numbers and the small comparison

Compare two drivers on the same set of roads and weather conditions. Differences
then contain less unrelated environmental variation. Here each paired seed gives
both policies the same arrivals, latent shocks and noisy measurements. They can
still choose different quotes, changing the public book and subsequent decisions.

The 20-pair comparison is a mean across the predeclared seeds, not an optimiser
or a claim of statistical superiority. Inventory-aware quoting holds less inventory
on average in this sample but has worse mean P&L and larger drawdown. Inventory
size is only one part of risk: its sign, timing, trading prices, costs and chosen
valuation reference also matter. No settings were retuned to reverse that result.

## Reservation-price intuition, after the simple rule

A reservation price expresses a personal valuation given existing inventory. An
illustrative model is r = S − qγσ²(T−t): S is reference, q inventory, γ risk aversion,
σ absolute price volatility per square-root time, and T−t remaining time. Positive
q lowers r because another purchase adds exposure to an already long position.
Greater uncertainty or risk aversion strengthens that adjustment. See equation 8
of [Avellaneda–Stoikov](https://math.nyu.edu/inmemoriam/avellaneda/HighFrequencyTrading.pdf).

This equation is explanatory only. Our policy uses configured k, not a fitted γ,
volatility estimator or this model's optimal quotes. Its Brownian-price and utility
assumptions do not automatically describe our endogenous book and noisy-information market.

## Arvind check

1. You are long several units. Which way should the quote centre generally move
   to discourage more buying and encourage selling?
2. Buy one at £100, still hold it at reference £102, no fees. Is the £2 realised
   or unrealised?
3. A maker has many fills and negative provider markouts. Is high fill rate enough
   to call that successful market making? Why?
