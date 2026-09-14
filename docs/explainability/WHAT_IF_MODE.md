# What-if mode

Open an explanation in Trading, Options, Risk or Stat Arb. The amber **Hypothetical
analysis** section takes explicit inputs and returns separately labelled results.
It does not submit a trading command or save a research experiment.

| Experiment | Actual evidence source | Approved calculation | Bound / interpretation |
|---|---|---|---|
| Order size | Frozen public price levels and FIFO quantities | Fresh `OrderBook`, `MarketOrder`, exact `execution.vwap` | 1–10,000 requested units, at most 10,000 resting orders; visible liquidity only |
| Option volatility/spot/rate/time | Selected contract's current public inputs | `PricingInputs`, `price`, `greeks` | Volatility 0–3, rate −1 to 1, no time beyond expiry; UI starts with volatility |
| Portfolio effect of an IV change | Existing consolidated public holdings | Detached `Position`/`Portfolio`, model pricing and `linear_risk` | All option IV inputs replaced; live stock marks and covariance fixed; no new MC |
| Correlation | Actual public holdings and current report | `RiskSettings.covariance`, `linear_risk` | Three-factor common correlation −0.5 to 1; configured daily volatility held fixed |
| Inventory | Current public reference and displayed limits | `MakerAccount`, `quote_request`, `plan_quotes` | Whole inventory within the displayed limit; sensitivity 0–10 ticks/unit; half spread 0.01–100 ticks |
| Entry threshold | Selected published synthetic session prefix | `CausalModel.at`, `Rules`, `decision` | At most 2,001 rows; independent flat-position qualification at each point |

The option and correlation risk comparisons explicitly use the same **delta-normal
approximation on both sides**. They must not be compared as though their new value
were the live Monte Carlo VaR. The IV portfolio hypothesis replaces quoted option
marks with model prices, so its full trace discloses the model/quote-basis change.
Any custom covariance override is replaced in the common-correlation hypothesis.

The frozen-book analysis includes all displayed orders, including displayed own
orders. It is a matching/liquidity experiment: live self-trade rules, reserved capacity,
fees, risk limits and later market reactions are not part of its scope. It does not say
what definitely would have happened had the user really submitted that order.

Inventory analysis applies the existing automatic inventory policy to the snapshot.
Manual live quotes still use the user's explicit shift. The inventory rule increases
skew beyond its soft limit, rounds bids down/asks up and applies passive-price and
position-capacity checks. The sandbox does not invent a second simpler quoting rule.

The threshold scan is not a backtest. It does not simulate holding periods or fills,
select an optimal threshold, read a holdout or modify registered evaluation results.
It shows which already-published signals would qualify under each entry rule while
flat. Stops and unavailable-history states still apply.

No financial session, RNG object, learning service or research writer is passed into
the calculation functions. Tests compare all live state and action histories before
and after, then compare future real market/option events with an untouched control.
Invalid inputs fail explicitly. The hypothetical response is neither replay evidence
nor a new starting configuration; starting a real session remains an explicit existing
lab action.
