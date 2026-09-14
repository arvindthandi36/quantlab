# Controlled scenario markets

Each entry selects or changes **existing validated engine inputs**. No preset hard-codes
profits, losses or a transaction price. Stock prices still emerge from simulated agent
orders in the matching engine; option quotes use the existing finite synthetic dealer.
The paired engine uses its existing observed-factor process and venues.

| Scenario | Actual mechanism | Engine |
|---|---|---|
| Normal | Existing baseline noise/liquidity/informed arrivals; latent sigma 2 ticks/√second | Stock |
| High volatility | Latent sigma 8 ticks/√second | Stock |
| Low liquidity | One-unit opening levels, maker disabled, reduced noise arrivals | Stock |
| Toxic / informed flow | Informed arrival rate 4/second; signal SD 1 tick | Stock |
| Reduce opening inventory | Existing endowed long position of eight units | Stock |
| Trending | Existing drifting residual from observation 1, persistence one | Paired |
| Mean reverting | Stable AR(1) relationship residual | Paired |
| Volatility shock | Existing residual sigma multiplied by four at midpoint | Paired |
| Liquidity shock | Existing venue liquidity command reduces both best levels to two units at midpoint | Paired |
| Correlation breakdown | Existing covariance factor rebuilt from +0.9 to −0.8 at midpoint; current prices and RNG retained | Paired |
| Relationship breakdown | Existing decoupling break makes residual persistence one | Paired |
| Option volatility shock | Existing `set_iv` changes base quote volatility from 20% to 40% at midpoint | Options |

Mean reversion/trend describes a **relationship residual**, not guaranteed reversion/rising
levels of every stock. Correlation is instantaneous factor correlation, not a promise that
a short realised sample exhibits that exact number. The option shock changes quote IV,
not the underlying process volatility or its future realised price path.

A seed, duration and configuration reproduce the scenario exactly. Defaults: seed 42,
60 seconds for stock scenarios or 60 model observations for paired/options scenarios.
Allowed duration: 20–120. The paired engine retains its causal warmup; with 20/12 windows,
orders require 32 observations. A 20-observation paired run can demonstrate prices/shocks
but cannot trade with that model. The default 60 permits trading after warmup. Its tickets
explain this limitation rather than supplying future-fitted coefficients.

Manual stock orders/two-sided quotes use the original stock engine. Pair/individual-leg
orders use the original paired engine after warmup. Options and hedges use existing quotes,
contract multipliers, accounts and stock books. Each scenario has its own ended journal;
no existing synthetic lab account is silently carried into another engine.

Known setup displays the configured mechanism. Hidden setup displays **Scenario Session**
and **SCENARIO — HIDDEN**. The backend chooses the entry and seed privately. End, then
explicitly reveal to compare visible evidence with configuration. The reveal describes
what the controlled model did, never forecasts the real market.

Objectives are evaluated independently from profit: finish within £1 maximum drawdown;
flatten endowed inventory; record observable liquidity deterioration; or keep absolute
portfolio delta within ten units. Hidden mode uses the generic drawdown objective to avoid
naming its regime. Delta tracks executions as well as steps. Early ending fails duration
completion. A losing round trip can meet a drawdown objective; positive final P&L cannot
erase an earlier breach. Liquidity acknowledgement is self-reported, not graded proof of inference.

The comparison button runs the same fixed maker configuration across Normal, High volatility
and Toxic flow using Phase 5 registration, outcomes and distribution summaries. The initial
comparison is deliberately limited to these three stock presets. Each scenario/replicate
uses an independently derived stream; **unpaired**, not identical-path paired evidence.
It reports P&L, inventory, drawdown, markouts, fills and missing coverage from the core metrics.
Environment metadata is included in every registration and run. Mislabelling a scenario's
parameters is rejected. Historical and scenario outcomes are not silently pooled.
