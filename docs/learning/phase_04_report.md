# Phase 4 review — Market Making Lab

> Historical phase record. Current core conventions and release status are in the root README, ASSUMPTIONS and Phase 11 release report. Test counts and runtime labels below describe this phase.


Owner: **Arvind Thandi**. QuantLab 0.4.0. Verified 10 September 2026.
Phase 4 is implemented. **Phase 5 has not started and requires Arvind's review.**

## BUILD REPORT

The existing market now accepts a fixed, inventory-aware or manually controlled
liquidity provider. It posts real limit orders into the established FIFO book,
receives actual fills and maintains exact cash, inventory and FIFO accounting.
The [accounting/strategy contract](../maths/phase_04_accounting.md) was documented
before implementation. No parameters were tuned to make the demo profitable.

The fixed policy uses two ticks on either side of a public reference. The
inventory-aware policy moves its centre by −kq, with a stronger adjustment beyond
the soft limit. Both share passive-order protection, soft size restrictions and
hard outstanding-order reservations. Defaults: size 2/side, k=0.5 ticks/unit,
soft limit 4, hard limit 8, refresh every simulated second. Quotes cancel before
replacement; fresh orders lose queue priority. Exhausted sides await the next
refresh. At session end, quotes cancel and any inventory remains marked.

The public marking/quoting reference uses the external midpoint, excluding our
own orders. If it is unavailable, use last transaction, then the public opening
reference. Every observation states its source. Normal strategies/manual views
receive no latent value, signal, counterparty type, private arrival time or seed.
Private debug is separate. Markout horizons for the lab count public exchange
events, preserving the 1/5/20 lengths without leaking the internal private clock.

The CLI supports observation, prediction, hints/retries, manual quotes, interval
results and delayed explanation. A small paired comparison runner prepares a
repeatable strategy interface without implementing the full Phase 5 research engine.

## TEST REPORT

**372 passed, 0 failed, 0 skipped. All 248 existing cases are preserved, with 124 additions.**

| Added test file | Cases | Principal protections |
| --- | ---: | --- |
| `tests/unit/test_maker_accounting.py` | 29 | Signed buys/sells, cash, FIFO partial closing and crossing zero, short/long gains and losses, exact fees, P&L identities, corrupted state and optimisation-safe guards |
| `tests/unit/test_maker_quotes.py` | 36 | Fixed prices, skew direction, exact outward rounding, soft restrictions, independent hard-side reservations, passive adjustments and invalid controls |
| `tests/unit/test_maker_analytics.py` | 20 | Public markout signs/maturity/coverage, no cash mutation, time-weighted inventory, drawdown, misleading profit, tight quotes with adverse outcomes and volume-weighted summaries |
| `tests/integration/test_maker_lab.py` | 29 | Complete runs, common environments, historical prefixes, privacy, hard-limit extremes, stale quote prevention, cancellation/replacement, replay and corrupt journals |
| `tests/integration/test_maker_manual.py` | 10 | Manual interaction, hint/retry/result/explanation order, interruption, CLI validation and saved replay |

The suite still includes 10 statistical cases and the existing Hypothesis test
configured for 200 generated mixed-operation examples. Those examples count as
one pytest case. Tests use hand-calculated accounts and real matching on declared
order paths. A tight-quote fixture fills more but finishes adversely; a separate
fixture identifies profit dominated by carrying inventory through a reference rise.

Ruff lint/format checks and dependency consistency pass. Installed command-line
entry points, fresh seed regeneration and saved action/account replay were exercised.
The manual teaching loop was also run with scripted test answers; these are not
Arvind's answers or evidence of mastery. Environment: Python 3.14.0 on macOS,
pytest 9.1.1, Hypothesis 6.168.0, Ruff 0.16.6. Other Python versions are unverified.

## ONE SHORT MARKET-MAKING DEMO

From the repository root:

```bash
venv/bin/quantlab-maker-demo --strategy inventory --seed 42 --duration 5 --debug
venv/bin/quantlab-maker-demo --debug --replay docs/learning/phase_04_session.json
venv/bin/quantlab-maker-demo --manual --teach
```

The third command is normal public manual mode. Enter four values such as
`2 3 1 2`: bid distance 2 ticks, ask distance 3 ticks, bid size 1, ask size 2.
Blank repeats the requested settings; a zero size withdraws that side; `q` stops
without claiming a completed result. Limits and passive-price adjustments still
apply. Add `--debug` explicitly for a separate observer panel. Custom exact maker
parameters are available through `MakerConfig`; the terminal keeps its controls small.

The actual five-second inventory-aware run has 21 observer records, 15 public
exchange events and three maker execution records, totalling four units.
Scheduling begins at the same empty market and seed 42 used in earlier phases.

| Time after 09:30 | Actual maker event | Explanation |
| --- | --- | --- |
| 0.000s | Bid 2 at £99.98; ask 2 at £100.02 | Zero inventory; centre is the £100 public opening reference. |
| 1.000s | Replace at the same prices | Scheduled refresh cancels old orders first and loses their FIFO priority. |
| 2.000s | Bid £99.99; ask £100.03, two units each | Reference is now last transaction £100.01. |
| 2.451686s | Sell 2 at £100.03; inventory −2 | A liquidity buy consumes the real resting ask. Its third requested unit cannot fill. Cash rises but a short position is created. |
| 3.000s | Bid £100.02; ask £100.06 | Reference £100.03 plus a one-tick centre shift: q=−2, so −0.5q=+1 tick. The maker is more willing to buy back stock. |
| 3.656763s | Buy 1 at £100.02; inventory −1 | Earlier external orders at the same bid fill first. The remainder reaches the maker, respecting FIFO. |
| 4.000s | Bid £100.00; ask £100.05 | Reference £100.02 plus half-tick shift gives £100.025 centre. Distances are rounded outward to valid prices. |
| 4.485043s | Buy 1 at £100.00; inventory 0 | The resting bid fills; the remaining short lot closes. Normal view does not identify the counterparty type. |
| 5.000s | Cancel remaining quotes | No forced liquidation is needed here because inventory is already zero. |

Recorded evidence: [debug trace](phase_04_demo.txt), [observer journal](phase_04_session.json),
[scripted manual smoke test](phase_04_manual_smoke.txt). The journal and a fresh
run reproduce the exchange actions, account states and derived markouts exactly.

Maker-only cash arithmetic:

    +2 × £100.03 − £100.02 − £100.00 = +£0.04 execution cash
    4 executed units × £0.001 fee/unit = £0.004 fees
    final cash = £10,000 + £0.04 − £0.004 = £10,000.036

Final inventory is zero; gross realised trading P&L £0.040, net realised £0.036,
unrealised £0, total marked P&L **£0.036**. These small amounts reflect a one-unit
teaching instrument and tiny horizon, not a scaling claim.

Other actual diagnostics: maximum absolute inventory 2; time-weighted average
inventory −0.648; average absolute inventory 0.648; RMS inventory 1.063; executed
units / posted units 4/20=20%; average own quoted spread £0.0422 over 89.0% of the
horizon; average effective spread £0.0175 across all four units; turnover £400.08;
maximum observed marked-P&L drawdown £0.002.

## DUMMY EXPLANATION

You are running a small shop for the asset. Your bid says what you will pay; your
ask says what you will accept. You can end up with too much stock, or owe stock
after selling short. Inventory-aware quoting changes those offers to encourage
trades that move you back towards flat.

In the demo, the maker sells first, becoming short two units. It then raises its
quote centre to make buying back more attractive. Two later purchases close the
short. The account records the money, the position and fees independently; the
analysis separately asks whether those executions looked good against later prices.

## P&L EXPLANATION

All accounting uses exact rational tick-unit amounts. Fractional fees never get
rounded out of the ledger; display rounding does not change results.

| Quantity | Meaning |
| --- | --- |
| Execution cash | Money received from sales minus money paid for purchases, before fees |
| Realised trading P&L | Gross gains/losses on FIFO lots that have been closed |
| Net realised P&L | Gross realised trading P&L minus all fees paid so far |
| Unrealised P&L | Difference between the reference and entry prices of remaining lots, with position signs |
| Total marked P&L | Cash plus marked inventory, less initial cash |
| Spread-capture proxy | Signed execution edge against the stated pre-order public marking reference |
| Markout | A later reference comparison; it is never an account cash flow |

Three identities reconcile after every relevant change:

    cash = initial cash + execution cash − fees
    total P&L = cash + inventory × reference − initial cash
    total P&L = net realised P&L + unrealised P&L

An additional path attribution reconciles:

    total P&L = execution-edge proxy + inventory/reference movement − fees

For this demo, £0.036 = £0.060 − £0.020 − £0.004. This is another explanation of
the same P&L, not another amount to add to it. The additive identity is exact for
the specified reference path/order of operations. Its economic meaning remains
model-dependent. Full-book midpoint effective spread is separately diagnostic.

Immediately after the first sale, cash has increased but total P&L is −£0.002:
the short is marked at that same sale price and only fees have reduced wealth.
This guards against treating sale proceeds as profit.

## INVENTORY EXPLANATION

Positive inventory is long; negative inventory is short. A buy adds units and a
sell subtracts them. Below the soft limit, centre = R−kq. Long inventory lowers
the centre; short inventory raises it. Tests check both directions and exact prices.

Soft restrictions gradually reduce exposure-increasing quote size and strengthen
the inventory-aware shift. Hard limits reserve capacity for resting orders:
bid quantity ≤ H−q and ask quantity ≤ H+q. The maker never relies on the opposite
side filling first. Cancellations remove old reservations before replacement.

The fixed policy ignores inventory in its centre choice but shares the same safety
layer. That is essential for a fair comparison and prevents a supposedly simple
benchmark from bypassing hard limits. Limits restrict units, not cash funding or
portfolio risk across instruments.

## ADVERSE-SELECTION EXPLANATION

The demo's available one-event midpoint markouts average **−£0.005 per unit**:
three units available, one missing. At five events, the average is +£0.025 but
only two units are available; one is missing and one pending. All four units have
pending 20-event marks. Coverage is part of the result, not a footnote to suppress.

**Observer debug only:** one of the three maker execution records is against an
informed trader (33.3% by execution count). That last buy closes a profitable short,
yet its next-public-event latent markout is about −2.786 ticks per unit. There is
no contradiction: realised P&L uses the old entry price; markout compares this
execution with a later reference. Subtracting that markout from P&L would double count
an unrelated diagnostic rather than implement a cash transaction.

Positive total P&L therefore does not automatically certify good liquidity provision.
Negative marks can arise from information, unrelated shocks, or quote changes.
The lab reports evidence and decomposition without declaring a winner.

## FIXED VS INVENTORY-AWARE COMPARISON

Predeclared **20 paired seeds, 0–19; 30 simulated seconds per run**. Both policies
share spreads, sizes, limits, fees and all exogenous market randomness. Every pair
checks identical event kinds/times, latent shocks and noisy signals. Different
quotes can change subsequent public prices, decisions and fills.

| Metric | Fixed | Inventory-aware |
| --- | ---: | ---: |
| Mean total P&L | £0.1738 | −£0.1188 |
| Mean time-average absolute inventory | 2.731 | 1.763 |
| Mean RMS inventory | 3.147 | 2.170 |
| Mean maximum absolute inventory | 5.150 | 4.600 |
| Mean maximum drawdown | £0.1948 | £0.3608 |
| Mean execution-edge proxy | £0.3788 | £0.3798 |
| Mean inventory/reference movement | −£0.1850 | −£0.4758 |
| Mean fees | £0.0200 | £0.0228 |
| Pooled 1-event midpoint markout/unit | £0.0055 (277/400 units) | £0.0022 (359/456 units) |
| Pooled 5-event midpoint markout/unit | £0.0066 (342/400 units) | £0.0001 (414/456 units) |
| Pooled 20-event midpoint markout/unit | £0.0102 (288/400 units) | −£0.0058 (339/456 units) |

Amounts are displayed rounded; exact per-run fractions are retained in the
[comparison JSON](phase_04_comparison.json). [Captured table](phase_04_comparison.txt).
Reproduce with `venv/bin/quantlab-maker-demo --compare --runs 20 --duration 30`.

The inventory-aware strategy holds less inventory on average here, but makes less
money and has greater observed P&L drawdown. Its timing, execution prices and
reference valuation path matter as well as position size. Similar initial execution
edge does not imply similar P&L. Do not infer either policy is universally superior
from these 20 short synthetic pairs; no parameters were retuned after seeing them.

## MATHS LESSON

The [first-principles lesson](../maths/phase_04_market_making.md) covers signed
inventory, FIFO, cash versus profit, valuation, exact price rounding, soft/hard
capacity, spread diagnostics, weighted averages, drawdown and common random numbers.

The reservation-price intuition is introduced only after the working simple rule:
`r = S − q γ σ² (T−t)`. S is observable reference, q signed inventory, γ aversion to
risk, σ absolute price volatility and T−t remaining horizon. A long position makes
another purchase add unwanted exposure, so the inventory adjustment lowers the
reservation price. This theory is explanatory; the core policy still uses fixed k.

## FILES CHANGED

| Files | Purpose |
| --- | --- |
| [portfolio/accounting.py](../../src/quantlab/portfolio/accounting.py), package initializer | Exact cash, FIFO lots, inventory, P&L and always-on reconciliation |
| [strategies/market_making.py](../../src/quantlab/strategies/market_making.py), package initializer | Fixed and inventory-aware public-input policies |
| [market_making/config.py](../../src/quantlab/market_making/config.py), [quotes.py](../../src/quantlab/market_making/quotes.py) | Exact controls, public observations and shared quote safety |
| [market_making/lab.py](../../src/quantlab/market_making/lab.py), `records.py`, package initializer | Scheduled/manual controller, ownership, risk reservations and full evidence |
| [market_making/analytics.py](../../src/quantlab/market_making/analytics.py), `views.py` | Public data projection, diagnostics, markouts/coverage, public and debug presentation |
| [market_making/journal.py](../../src/quantlab/market_making/journal.py) | Full quote/exchange/account save/load/replay |
| [market_making/comparison.py](../../src/quantlab/market_making/comparison.py) | Bounded paired comparison with verified common exogenous randomness |
| [tutor/market_making.py](../../src/quantlab/tutor/market_making.py), package initializer | Prediction, hint, retry and delayed explanation |
| [maker_demo.py](../../src/quantlab/maker_demo.py) | Installed automatic/manual/teaching/comparison/replay CLI |
| `market/simulation.py`, `market/replay.py` | Factored reusable background/replay sources; original Phase 2/3 API remains |
| `analytics/markouts.py` | Shared result annotations also permit exact rational public-reference marks |
| `src/quantlab/__init__.py`, `pyproject.toml` | Version 0.4.0 and maker CLI entry point |
| Five new test files above, `tests/lab_helpers.py` | Hand-calculated and end-to-end verification |
| Phase 4 contract, lesson, architecture, this report, demo/session/comparison/manual evidence | Reviewable design and actual results |
| README, roadmap, assumptions, learning log, changelog | Current scope, usage, limitations and Phase 5 review gate |

The matching-engine implementation was not rewritten. No new runtime dependency
was introduced. The repository remains uncommitted; no commit was requested.

## RED TEAM

1. **Public reference quality is imperfect.** Excluding own quotes prevents direct
   self-marking by quote skew, but last-trade fallback can reflect our own fills.
   Branch changes can move valuations. A public reference is not latent truth or
   a guaranteed liquidation price; attribution depends on this choice.
2. **Less inventory did not mean better outcomes.** The observed inventory-aware
   policy loses money on average here and has larger drawdown. Do not conceal that
   by selecting a favourable seed or optimising k after observing these results.
3. **Execution is simplified.** Quotes refresh atomically without latency or
   cancellation races. Exhausted sides wait until the next refresh. Market orders
   can reach distant quotes without realistic price sensitivity or protection collars.
   The non-informational flow and informed beliefs remain uncalibrated.
4. **The account is local to one maker.** Background traders have no funding ledgers.
   Maker shorts/borrowing are allowed without margin, borrow fees or interest.
   Quantity conservation is global; the exact monetary reconciliation covers this
   maker's executions/fees, not a complete clearing system.
5. **Diagnostics have denominators and selection effects.** Posted-unit fill rate
   depends on refresh frequency. Midpoints may be missing/non-executable. Markout
   coverage differs across policies and horizons. Public-event horizons are not
   elapsed seconds and are not Phase 3's private-event clock.
6. **No perfect liquidation or risk model.** End inventory remains marked. Drawdown
   is measured at public event ends. The simple k rule neither estimates volatility
   nor optimises utility, and inventory caps do not guarantee acceptable monetary loss.
7. **Privacy and replay have limits.** Public interfaces exclude secrets and private
   timing; observer objects/journals remain privileged Python data, not a hostile-code
   sandbox. Replay checks consistency, not authenticity or cross-version RNG identity.
8. **Small validation is not strategy research.** Twenty paired synthetic runs do
   not establish superiority, calibration or real-market alpha. Full histories and
   repeated ledger checks favour inspectability over long-run performance.

## 3-QUESTION ARVIND CHECK

1. You are long several units. Should your quote centre generally move up or down
   to discourage more buying and encourage selling?
2. You buy one at £100 and still hold it when reference is £102, with no fees.
   Is the £2 realised or unrealised?
3. A maker has many fills but negative provider markouts. Is high fill rate enough
   to call the strategy successful? Why?

Answers and Phase 4 review are pending. No mastery is inferred from running tests.
