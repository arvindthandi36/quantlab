# Limit order books: from instructions to transactions

## Intuition

A **bid** is a standing offer to buy at a particular price. An **ask** is a standing
offer to sell. The order book stores unfilled offers. Its **depth** is the actual
quantity available at each price; liquidity here means the ability to trade
against these quantities.

A limit order specifies the worst acceptable price: a maximum for a buyer or a
minimum for a seller. It may execute immediately, wait, or execute partly and
leave a remainder waiting. A market order requests immediate available liquidity;
it does not promise either a particular price or unlimited execution.

QuantLab first uses the most favourable available price, then the earliest arrival
at that price. The price of an execution is the resting order's limit. These
conventions have an exchange analogue in [Coinbase's matching-engine documentation](https://docs.cdp.coinbase.com/exchange/concepts/matching-engine).
QuantLab implements only the subset explicitly listed in its assumptions; that
source is not evidence that QuantLab reproduces the exchange as a whole.

## Mathematics

Let τ be tick size in currency per unit, and k a positive integer. An order price is:

\[
p = k\tau.
\]

With τ = £0.01, £100.02 is exactly 10,002 ticks. Binary floating-point prices can
make supposedly equal decimal values differ; integer comparison avoids that issue.

Let b be the highest resting bid and a the lowest resting ask. When both exist:

\[
\text{spread}=a-b,\qquad m=\frac{a+b}{2}.
\]

Here m is the mid-price, a summary of two quotes. It is not a latent fair value or
a guaranteed executable price. A bid at £100.00 and ask at £100.01 give mid £100.005,
which lies between valid order ticks. When a side is empty these summaries are
undefined; QuantLab returns `None`, never a fake zero or a stale last trade.

For incoming remaining size Q and maker remaining size R:

\[
f=\min(Q,R),\qquad Q'=Q-f,\qquad R'=R-f.
\]

f is executed size. A buy limit at L accepts a maker price p when p ≤ L; a sell
limit accepts p ≥ L. Choosing the best price first means later levels cannot
become eligible after the best remaining level fails the bound.

For execution prices pᵢ and quantities fᵢ, the volume-weighted average price is:

\[
\text{VWAP}=\frac{\sum_i p_i f_i}{\sum_i f_i}.
\]

The report retains this exactly as a rational tick value. No fills means a zero
denominator and no VWAP; the API returns `None` rather than dividing by zero.

For each incoming instruction, at submission:

\[
Q_{\text{requested}}=Q_{\text{executed}}+Q_{\text{resting}}+Q_{\text{cancelled}}.
\]

For a whole session starting with an empty book:

\[
Q_{\text{all accepted}}=2V+Q_{\text{currently resting}}+Q_{\text{all cancelled}}.
\]

V is traded volume, counted once. The factor 2 appears because executing one unit
uses one buy-order unit **and** one sell-order unit. All cancellations include
explicit cancellations plus unmet market remainders. These are conservation laws
for order instructions, not a cash/asset or P&L ledger.

### Stronger two-sided execution checks

For every match the engine measures the incoming remainder and resting remainder
before and after execution. Depending on the incoming side, these changes are
assigned to the buyer and seller: **buyer filled = seller filled = recorded quantity**.

Across one submission, independently accumulated buyer/seller changes must each
equal the sum of quantities in the emitted trades. The incoming total reduction
and increase in cumulative volume must also match that sum. These checks remain
active under Python's `-O` flag. Failure raises an error and prevents further
trading on that book; no quantity is repaired or fabricated.

`ExecutionReport.buyer_filled_quantity` and `seller_filled_quantity` expose these
measured totals. Tests additionally observe actual maker remainders, track
per-order ledgers, and deliberately corrupt accounting to test the guards.

### Aggregated visible depth

The ladder shows **Price | Total Quantity | Order Count**. Total quantity sums the
remaining sizes at that price; order count counts still-active instructions. A
partial fill changes size but removes the order only at zero remainder.
`--expand-orders` shows FIFO detail. The ask ladder displays descending above
descending bids, bringing the best quotes together; snapshots and matching
still use best-price-first order on both sides.

## Where it appears in QuantLab

- `PriceGrid` enforces the tick equation without implicit rounding.
- `OrderBook._eligible` enforces the limit bound; `_match` implements the minimum
  remaining size, resting-price execution and priority.
- `BookSnapshot` and `OrderBook` expose spread and rational mid-price.
- `ExecutionReport` exposes executed size and exact VWAP.
- Generated tests independently account for every submitted order after every action.

Run `venv/bin/quantlab-demo`. The worked scenario first fills 3 units from A and
2 from B at £100.02 even though the buyer permits £100.05. A worse £100.04 ask
arrived earlier than both, but price priority keeps it behind them. Later a sell
market order executes 6 at £99.98 and 2 at £99.97, illustrating a depth sweep.
The final buy requests more than available sell liquidity and reports the shortage.

## Assumptions

All orders are displayed; one instrument and one serial caller; no latency or
hidden orders. A partially filled order keeps its original priority. There are
no fees, accounts or trading strategies yet. See [ASSUMPTIONS.md](../../ASSUMPTIONS.md).

## Failure cases

Low depth can force a market order through worse prices and still leave it
partially unfilled. A passive limit can remain unfilled indefinitely. A midpoint
can be unavailable or not itself a valid order price. FIFO is a choice of market
design, not a universal rule across venues or products.

Economically, a spread represents a difference between immediately buying and
selling prices. It is not guaranteed revenue: two passive quotes need not both
fill, inventory can remain, subsequent prices can move and costs may apply.
Those risks motivate later phases; none is estimated by this matching demo.

## Interview questions

1. Why can a buy limit execute below its stated limit?
2. Why should a later, better-priced ask beat an older, worse-priced ask?
3. Why can mid-price be valid as a statistic but invalid as an order price?
4. Why does session order-unit conservation count executed volume twice?
5. What does a passing matching-engine test suite fail to establish about profitability?
