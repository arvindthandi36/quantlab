# Phase 8 — Options & Derivatives Lab contract

> Historical phase record. Current core conventions and release status are in the root README, ASSUMPTIONS and Phase 11 release report. Test counts and runtime labels below describe this phase.


Defined before implementation, 11 September 2026. Phase 7 is approved; only Phase 8
is authorised. Preserve the existing 747 test cases. Phase 9 is not started.

## Instruments, units and time

European calls and puts on one synthetic GBP stock. Contracts specify underlying,
strike in GBP per underlying unit, expiry as an exact year fraction from simulation
origin, and a positive integer multiplier. Quantity is signed whole contracts.
Premium and model value are GBP per underlying unit; contract cash value multiplies
by the multiplier and number of contracts. Volatility and continuously compounded
rates are annual decimals: 20% is 0.20. UI percentage inputs convert explicitly.
Time uses ACT/365, with 365 calendar days per model year, independently of wall time.
At expiry options cash-settle once at the then-observed underlying reference.

## Mathematical pricing and validation

Black–Scholes–Merton supports a constant continuous dividend yield consistently in
pricing, Greeks and risk-neutral Monte Carlo. The live trading lab initially uses
zero dividends; it must reject nonzero yields rather than omit dividend cash flows.
The theoretical assumptions are European exercise, lognormal stock dynamics,
constant rate/volatility/yield, no arbitrage, frictionless continuous replication.
Synthetic execution adds spreads, finite depth, whole shares, fees and discrete
hedging; the pricing assumptions are not claims about the real world.

Delta is dV/dS; gamma is d²V/dS². Vega is dV/dsigma per **1.00 absolute annual
volatility unit**; the interface also labels the derived per-percentage-point value
(divide by 100). Theta is calendar-time decay, −dV/dT, in GBP per model year;
daily display divides by 365. Rho is dV/dr per 1.00 absolute annual rate unit.
Contract and position Greeks multiply by multiplier and signed contract count.
Undefined derivatives at payoff kinks must be labelled, not fabricated.

IV checks discounted lower/upper feasibility bounds before solving. Safeguarded
Newton steps use vega; an explicit bracketed fallback handles bad guesses and tiny
derivatives. Return method, iterations, price residual and convergence status.
Unidentifiable boundary prices or exhausted iteration budgets cannot become
plausible-looking successful IVs. Numerical finite differences independently
validate analytic Greeks. Benchmark values and primary-source references accompany
the tests and mathematics lesson.

## Tradeable market and underlying execution

Options use an explicitly labelled finite dealer-quote mechanism, not an option
limit order book. A documented modest log-moneyness smile/skew supplies theoretical
values; quote spreads and price precision create tradeable bid/ask prices. Each
quote has a revision and remaining size; stale submissions reject. Orders execute
only available size at the proper side; an unfilled remainder cancels.

The stock is traded through `TradingSession.command('order', ...)`, the existing
Phase 6 risk/order/accounting flow and actual Phase 1 FIFO matching engine.
A derivatives venue adapter refreshes external resting liquidity around the newly
observed synthetic stock price. Refreshes, executions and cancellations are recorded
and quantity conservation remains mandatory. Stock limits/resting orders, if used,
remain real exchange orders. No hedge directly edits a stock position.

Underlying steps use causal seeded geometric-Brownian innovations. Each step
represents a configured fraction of model days, not a second of real time. The
pricing Monte Carlo uses risk-neutral drift r−q; hedging scenarios specify their
physical drift separately. Both models disclose tick/depth/discrete-time limitations.
The public state never contains future innovations or a precomputed future path.

## Accounts, hedges and reports

Option FIFO lots retain entry premiums; selling an option credits cash and opens
a liability, not instant realised profit. Closing or cash settlement realises
lot-based gross P&L. Open lots are marked at the current synthetic quote midpoint.
Stock uses the existing exact FIFO account. All monetary cash/fee ledgers use exact
decimal/fraction representations after explicit model-to-quote rounding.

Additive portfolio identity:

`total net P&L = option realised gross + option unrealised gross
                 + stock realised gross + stock unrealised gross
                 + cash financing − option fees − stock fees`.

Cash financing accrues on combined trading cash (borrowing allowed) at the specified
rate for each elapsed interval. Its ledger is separate from stock and option gross
P&L; premium, current liability and turnover are explanatory measures, not extra
additive profits. No margin/capital adequacy claim is made.

The hedge target is minus aggregate option delta, rounded to whole stock units.
Manual orders are freely chosen; automatic benchmark hedges submit ordinary stock
orders and may be partial/rejected. Report actual hedge count, turnover, costs,
residual delta, drawdown, starting/ending/max Greeks and observed realised volatility.
Ending early marks open positions; expiry settles only expired contracts. Neither
event invents a stock liquidation.

## Research, tutor and interface boundaries

The Phase 5 adapter runs the same derivatives/stock accounting and execution model.
Hedge-frequency variants share underlying innovations and configuration; volatility
scenario variants share standard-normal innovations while transforming them with
different declared volatility. Register counts and hypotheses before seeing results,
retain complete failed/losing runs, and use the existing uncertainty/paired analysis.
Profile analytical pricing, vectorised Monte Carlo and full hedge experiments.

The shared Phase 7 tutor accepts strictly projected current derivatives facts:
contract, current quotes/IV, own fills/positions/Greeks, matured results and solver
diagnostics. No future stock movement enters a question. Answer history, hints,
review and RNG separation remain shared. New topics require a relevant derivatives
context rather than being forced into old stock-only examples.

Python is the sole financial implementation. The browser renders option chains,
positions, Greeks, scenario outputs and server-generated curve data. The desk links
to the Options Lab; the Options Lab links to stock trading and shared learning.
The working surface prioritises contract selection, actual bid/ask, trade controls
and hedge exposure. Payoff/value/delta/gamma/smile/hedge-history charts explain the
same selected instrument and session, not disconnected calculators.

Replay saves configuration and actions, regenerates and verifies the complete
evidence, and exposes public frames only. Unknown fields/corruption reject. No
external data feed, LLM, API key, surface calibration or Phase 9 work is included.

## Reusable API example

    from quantlab.options.models import PricingInputs
    from quantlab.options.pricing import price, greeks
    from quantlab.options.iv import implied_volatility
    from quantlab.options.session import OptionsConfig, OptionsSession

    x = PricingInputs(spot=100, strike=100, time_years=1,
                      volatility=.20, rate=.05, dividend_yield=0)
    premium = price("call", x)             # GBP per underlying unit
    sensitivities = greeks("call", x)      # Explicit annual-decimal conventions
    inferred = implied_volatility("call", x, premium, initial=.30)

    session = OptionsSession(OptionsConfig(seed=42))
    quote = session.snapshot()["selected"]
    fill = session.command("option_order", contract_id=quote["id"],
                           side="buy", quantity=1, quote_revision=quote["revision"])
    session.command("stock_order", side="sell", quantity=51, order_type="market")
    session.command("step", count=1)
    public = session.snapshot()           # Detached, current facts only

Session commands include option_order, stock_order, cancel_stock, hedge, step,
set_auto, set_iv and end. Unsupported fields reject. A rejected stock order remains
an audited Phase 6 command with no fabricated fill. Analysis functions do not alter
market actions or consume the stock random stream. Exceptions to accounting
identities stop the session rather than repair its financial state.

Expiry references are stored once for every contract, independently of whether it
is held. Later observations cannot rewrite an expired contract's displayed payoff.
Live quotes additionally publish intrinsic, midpoint time value and moneyness.

HTTP GET /api/options returns the public application view. POST /api/options accepts
kind/payload and the same local token/origin controls as the stock desk.
GET /api/options/journal requires an ended session. Browser load_replay sends
journal_text containing the original JSON; programmatic callers may supply a
decoded journal object. Browser JSON parsing/reserialising must not rewrite
numeric representations before checksum verification. Journals include simulator
and Python versions; exact cross-version replay is explicitly unsupported.

The Phase 7 stock-only concept catalog remains a compatibility surface.
ACTIVE_CONCEPTS is the complete runtime catalog; derivative questions require
actual derivative context. Progress assessment history is retained when a replay
rewinds, while active future questions and derivative context caches are discarded.
