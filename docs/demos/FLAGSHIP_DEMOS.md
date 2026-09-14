# The eight flagship demonstrations

All are genuine engine/calculation paths. Root 140042 was fixed before viewing outputs; the
existing Phase 10/13 example seeds remain unchanged. Full evidence and measured timings are in
[evidence/demo-report.json](evidence/demo-report.json).

| Demo | Source of financial truth | Teaching question | Script |
|---|---|---|---|
| Order execution | TradingSession → FIFO → exact account | Will every unit fill at the best ask? | [Order](scripts/order.md) |
| Getting picked off | Noisy informed engine + subsequent markouts | Does a fill prove a good trade or an informed counterparty? | [Picked off](scripts/picked-off.md) |
| Delta hedging | OptionsSession + real stock hedge book | Which signed stock units offset aggregate delta? | [Hedge](scripts/delta-hedge.md) |
| VaR vs ES | Existing empirical tail example | Does equal VaR imply equal tail severity? | [Tails](scripts/tails.md) |
| Correlation vs cointegration | Phase 10 completed cases + decoupling | Does high price correlation establish a stable residual? | [Pairs](scripts/pairs.md) |
| Winner's curse | Phase 5 equal-skill selection control | Does the largest development mean prove skill? | [Selection](scripts/winner.md) |
| Synthetic price formation | Latent process → agents → FIFO executions | Must an unseen model value equal the next transaction? | [Formation](scripts/synthetic-prices.md) |
| Historical evidence | Phase 13 fixture and next-close paper execution | Does OHLCV prove where you would have filled? | [Historical](scripts/historical.md) |

The order result is **3 @ £100.01, 4 @ £100.02, 3 @ £100.04**. Actual VWAP is **£100.023**;
fees £0.01, ending cash £8,999.76, position +10. The remaining ask is 5 units at £100.04.

The controlled stale seller trades at **£100.05**. The first informed signal is about **£100.19717**;
the model estimate is **£100.18851**, and estimated buy edge **13.85114 ticks** exceeds a
**1.47014-tick** hurdle. These are observer-only facts. At the five-event horizon the latent
reference is about **£100.20610**, giving the seller a **−£0.15610 per-unit latent markout**.
The public-midpoint markout at that horizon is **£0.00**. Both are shown: neither is relabelled
as the other, and neither is a realised profit/loss measure.

The call creates delta **51.14358**. A genuine 51-stock-unit sale leaves **0.14358**. The seeded
market moves to **£99.73**; aggregate delta becomes **−1.78995**. Buying 2 stock units leaves
**0.21005**. The subsequent 30% IV input leaves positive vega and changes delta again.

The two 95% VaRs are **10**; ES is **12 versus 48**. The existing pair correlations are
**0.980805 versus 0.982840**, not rounded into a fabricated identical statistic. Known process
construction and residual behaviour differ; a separate decoupling scenario challenges stability.

All **50** selection-control variants have true expected payoff zero. The development winner is
**variant-32**: observed mean **0.277506**, untouched evaluation mean **0.047892**. The outcome
is less dramatic than a forced negative result and is retained exactly. The winner is locked by
the original Phase 5 selection function before evaluation exists. Payoff units are not trade P&L.

The historical-style fixture starts at £100. The paper BUY 3 waits; the next fixture close is
**£99.63**, and the execution rule fills at **£99.64**, with **£0.003** fees. This is artificial
input plus simulated execution, not a claim about a historical exchange fill.
