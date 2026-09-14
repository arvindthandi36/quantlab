> Archived register. The root ASSUMPTIONS.md is authoritative for the current release.

# Assumptions and limitations

These are **Phase 0–5 conventions**, not claims about every exchange. Changing an
economic convention requires a documented decision and corresponding test updates.

| Area | Current convention | Consequence |
| --- | --- | --- |
| Instrument | One separate book per instrument; no instrument registry | Callers must not mix instruments or price grids |
| Prices | Strictly positive integer ticks; exact decimal conversion through `PriceGrid` | Negative-price products are out of scope; off-grid instructions are rejected, never rounded |
| Tick size | Configurable `Decimal`; demo uses GBP 0.01 | The engine never interprets a float as currency or infers a tick grid |
| Quantity | Positive whole units; Python integers | No fractional lots, minimum notionals or exchange size caps |
| Order priority | Better price first; FIFO at equal price | No pro-rata allocation, hidden/reserve quantity or special participant priority |
| Execution price | Resting order's limit | A crossing limit can receive price improvement; its own limit is a bound |
| Limit remainder | Rests at its limit until filled or cancelled | No exchange-level post-only flag; lab quotes are made passive before submission |
| Market remainder | Consume eligible displayed liquidity and cancel unmet size | No fabricated fills, borrowing from future orders, auction routing or price protection collar |
| Cancellation | Return active remainder, else `None`; never alter previous trades | Repeated/unknown cancellation is an explicit no-op |
| IDs | Nonempty strings, unique for book lifetime | An ID remains used after fill, cancellation or an unfilled market order |
| Time | Market events use elapsed integer microseconds and scheduling-order ties; book priority uses submission sequence | Atomic decision/submission/matching; no latency or exchange calendar |
| Concurrency | One synchronous caller | No thread safety, persistence transaction or crash recovery guarantee |
| Depth | Only actual, displayed resting instructions | No external liquidity, fake depth or independent price chart |
| Quotes | Spread and mid require both sides | Missing quotes are `None`, displayed with a reason; mid may be half a tick |
| Output | Detached immutable result objects; mutable remainders remain private | A report describes submission-time state, not an order's later status |
| Volume | Executed units counted once per match | Global order-unit accounting subtracts two units per executed unit |
| Ownership | Maker-owned IDs map to one maker account; background orders have no funding ledgers | No general participant registry, margin or clearing system; passive maker replacement avoids own crossing |
| Costs and P&L | Exact maker FIFO account and per-unit fees; informed cost allowance is separate | Maker marked P&L is defined; gross markouts remain diagnostics rather than cash flows |
| Market behaviour | Noise-limit and liquidity-market flow remains uninformed; optional informed arrivals see noisy current measurements | No calibrated equilibrium, guaranteed price discovery or perfect signals |
| RNG | SHA-256-derived named `random.Random` streams | Stable naming separates draw streams; it does not prove financial realism or statistical independence |
| Reproduction | Same instructions reproduce matching; RNG work also records runtime/tool versions | No promise of identical future distribution draws across all Python versions |

## Numerical contract

`PriceGrid.to_ticks` accepts strings or `Decimal`, rejects floats, nonfinite values
and off-grid prices, and uses exact rational arithmetic to avoid ambient decimal
rounding. `to_price` also avoids context rounding; nonterminating rational prices
raise an error. A VWAP such as one third of a tick is therefore retained as a
`Fraction`; a future display layer must explicitly choose and label display rounding.
Returned observation classes are value containers, not accepted order commands.

## Three principal red-team findings

1. **Simplified beliefs and flow.** Random limits and external execution needs
   provide background flow. Informed decisions use a subjective Gaussian belief
   and imperfect current measurements. This cannot establish efficient price
   discovery, realistic spreads or alpha.
2. **Limited economic ledger.** Maker cash, inventory, FIFO P&L and fees reconcile;
   background agents have no funding ledger. Public marking uses a stated fallback
   reference that may reflect the maker's own fills. This is not a full clearing system.
3. **Transparent but limited storage.** New/deleted price levels involve shifting a
   Python list; all used IDs remain in memory. This is not a low-latency or unbounded
   production exchange. Profile real experiments before redesigning it.

## Evidence boundary

The tests cover the declared simplified contract. The reference matcher is a
separate algorithm, not an external certification, and generated tests are not a
proof over all possible inputs. Observer JSON records configuration, versions,
events, latent values, instructions, reports, book snapshots and private informed
audits when enabled. Replay recomputes informed decisions from saved measurements,
resubmits instructions and verifies their consequences without RNG draws. It
checks mechanical consistency, not authenticity or the probability of the saved
random choices. Regeneration from a seed also depends on implementation/runtime.

## Phase 2 baseline market conventions

- The market starts empty, with separate configured public opening reference and
  hidden initial value. Both default to 10,000 ticks; that equality is initial
  configuration, not a continuing signal to traders.
- Latent value follows a zero-drift arithmetic Gaussian walk at regular updates,
  held between them. Sigma is ticks per square-root second. Nonpositive/nonfinite
  results abort the run; no reflection, clipping or replacement occurs.
- Noise and liquidity sources represent aggregate populations, not named accounts.
  Each arrival has a fresh fair buy/sell direction and uniformly sampled whole size.
  Noise limits use public midpoint (rounded half-up), else last trade, else opening
  reference, plus a uniformly drawn signed tick offset. Limits may cross. Invalid
  nonpositive sampled limits are skipped with a recorded reason, never clamped.
- Liquidity needs submit market orders. Unmet quantity is cancelled and the need
  is not retried. No inventory, cash constraint or economic optimisation exists.
- Independent exponential gaps are rounded **up** to at least one microsecond.
  This is a discretised Poisson approximation; at extreme arrival rates clock
  resolution materially distorts the intended rate. Default rates are 1 and 0.6/s.
- Three baseline event kinds: latent update, noise arrival, liquidity arrival.
  Phase 3 adds informed arrival. Each trader arrival includes its decision,
  submission and resulting fills atomically.
- No autonomous expiry/cancellation policy is added; unmatched limits rest for the
  session. Matching-engine cancellations remain independently supported/tested.
- Only `--debug` prints latent values. Saved journals are observer/research data
  and contain latent state. Trader APIs receive no latent fields or future events.
- Every event records a full immutable book snapshot. This is intentionally easy
  to inspect but memory-heavy for long runs. `max_events` raises on exhaustion;
  a failed simulation cannot be resumed as a successful session.
- `09:30` is a presentation origin, not a real timestamp or trading-hours claim.
  Events at the horizon are included; no fictitious latent update is added at a
  horizon between the configured update times.

## Phase 3 information and markout conventions

- Signal Y = current latent X + independent Gaussian error. Positive error standard
  deviation η defaults to 2 ticks. The informed trader receives Y, time and η,
  never X, actual error, future shocks or observer records. It has no signal memory.
- The prior uses the existing public reference and fixed uncertainty τ = 8 ticks.
  This Gaussian prior is subjective, reset per arrival and not calibrated to the
  evolving book. Its conditional-mean formula is valid under that assumed model.
- One unit is bought/sold at the observed opposing quote only when estimated
  executable edge strictly exceeds cost + minimum edge + uncertainty buffer.
  Defaults are 0.25 + 0.25 + 0.5 × posterior standard deviation, in ticks/unit.
  The allowance is not a booked fee; the buffer is not comprehensive risk management.
- The informed rate defaults to zero, preserving Phase 2. `--informed` enables 1/s.
  Arrival and signal streams are separate from each other and the original streams.
  Latent updates are not conditioned on fills. Information measures current value;
  subsequent latent increments retain zero conditional mean.
- Markout sign belongs to the resting provider: +1 for buying, −1 for selling.
  Markouts use d × (later reference − execution price), gross per unit, not P&L.
  Decomposition uses the reference just before the whole incoming order, including
  when that order creates multiple executions.
- Horizons are 1, 5 and 20 subsequent processed events, excluding the trade event.
  Equal-time events count separately. A maturity event may be a private hold or
  latent update, so the analysis is observer-only even for midpoint references.
- Midpoint and latent references remain separately labelled. Pending horizons
  contain no future values/times. Missing future midpoints stay unavailable, with
  no last-trade, latent or end-of-run substitution. Missing initial midpoint
  prevents spread decomposition but not a markout with a valid future midpoint.
- Public projections exclude private reasons, source labels, seeds, signals,
  configuration and non-actions. Public snapshot timestamps reflect public updates
  or declared completion only. Ordinary agent observations stay public-only.
- Full sessions/journals and direct `step()`/`now_us` access belong to the observer.
  These are Python interface boundaries, not isolation against hostile plugins.
- Negative marks are compatible with informed selection but do not prove its cause.
  Independent price shocks, quote depletion and neutral flow can also produce them.
  The controlled statistical tests establish the specified synthetic mechanisms,
  not a causal estimate for this entire market or real-market strategy performance.

## Conservation and displayed depth

Measured buyer and seller remainder reductions reconcile to each trade quantity,
then to the full submission's recorded volume. These guards remain active under
Python `-O`. Failure disables subsequent submits/cancels on that book. No repairs
are attempted; diagnostic observations can be inspected before discarding it.

Depth aggregates remaining quantity and active order count by price. Optional FIFO
expansion exposes individual instructions. Only the ask display is reversed to
form a descending ladder; underlying snapshots/matching remain best-first.

## Phase 4 maker conventions

- Reference is external midpoint excluding maker-owned orders; otherwise last
  transaction, otherwise public opening. Exact half ticks are retained for
  valuation. Own executions can influence the fallback; R is not latent truth.
- Initial inventory is zero; initial cash defaults to £10,000 at the demo tick.
  Shorts and borrowing are permitted within a symmetric unit cap. No funding,
  margin, borrow interest, dividends or portfolio-wide limits are modelled.
- Fees default to 0.1 tick per maker-executed unit, expensed immediately. Orders,
  cancellations and unmet quantity have no fees. Fractional tick-unit accounting
  is exact; display values are rounded to four currency decimals.
- FIFO determines gross realised trading P&L; net realised subtracts all paid
  fees, including opening fees. Remaining signed lots determine unrealised P&L.
  Both reconcile to cash plus marked inventory less initial cash.
- Additive execution edge plus inventory/reference movement minus fees uses one
  documented reference path and order of operations. This is an arithmetic identity,
  not a unique causal attribution. Effective spread and markouts are separate diagnostics.
- The fixed centre ignores inventory, while both policies and manual instructions
  share risk controls. Inventory-aware k defaults to 0.5 ticks/unit; soft=4, hard=8.
  Positive inventory lowers the centre; soft excess strengthens shift and throttles
  increasing-side size. Reserve hard capacity independently for both resting sides.
- Refresh is every simulated second, starting at zero and excluding the terminal
  instant. Background events at equal time go first. Cancel before replace; new
  IDs lose priority. Exhausted sides wait for refresh. No cancellation race exists.
- Bid prices round down and asks up; crossing proposals move outward. Invalid
  nonpositive sides are disabled with a reason. The account is never permitted
  to repair an inventory breach by clipping an actual fill.
- Horizon completion cancels maker quotes without forced liquidation. End inventory
  retains its public reference mark and may not be executable at that price.
- Normal lab markouts count public exchange events; hidden holds/latent updates do
  not advance that clock. Phase 3 internal-event analytics retain their old convention.
  Missing/pending marks are never substituted; means report quantity coverage.
- Fill rate means executed units / posted units, including replacements. It is
  sensitive to refresh frequency. Inventory and quoted spread use time weights;
  effective spread/markouts use volume weights; drawdown uses public event-end P&L.
- The maker policy does not estimate volatility or implement Avellaneda–Stoikov
  optimal quoting. Reservation-price theory is taught as motivation only.
- Common exogenous draws do not imply identical subsequent order prices or fills.
  The 20 paired runs are modest validation, not a full research engine or proof
  of policy superiority. All seeds and the unfavourable inventory-aware result are retained.

## Phase 5 research conventions

- QuantLab is a synthetic quantitative research environment. Synthetic performance
  is not evidence of real-world alpha. Monte Carlo precision is conditional on the
  chosen market, execution, reference and strategy assumptions.
- One complete session is one statistical observation. For policy differences,
  one matched session pair is one observation. Individual fills within a session
  are dependent and are never counted as independent Monte Carlo evidence.
- Deterministic run seeds use root/pool/index addresses. Development/evaluation
  pools are disjoint; pairs intentionally share a seed. Named market randomness
  remains separate for latent shocks, arrivals, decisions and informed signals.
  Bootstrap draws use separate recorded seeds and NumPy PCG64.
- Strict common-random-number comparisons require identical exogenous market
  configuration and fingerprints. Different strategy actions legitimately change
  endogenous book states, fills and future public prices. Market-parameter sweeps
  share base seeds without claiming identical realised weather.
- Questions, hypotheses, counts and configurations are registered before sessions
  run. The baseline and sensitivity sweep were declared in the research contract;
  final baseline parameters were not changed in response to development results.
  All requested rows remain visible, including no-fill and losing sessions.
- Failed runs remain in the log and mark an experiment incomplete; survivor-only
  inference is disabled. Interruptions leave partial evidence and do not claim a
  completed result. There is no automatic replacement seed or resumable scheduler.
- Statistics use finite floating-point summaries; execution accounting remains
  exact. Sample variance uses n−1, SE=s/sqrt(n), quantiles interpolate at (n−1)p.
  Mean t intervals are exact for independent normal observations and approximate
  otherwise; their validity is conditional on finite variance and adequate samples.
- Percentile bootstrap intervals use 2,000 resamples for the principal experiments.
  Resample whole sessions or paired differences. A bootstrap cannot restore unseen
  tails, fix a misspecified market or undo data snooping. Degenerate/insufficient
  t tests are explicitly undefined rather than assigned misleading p-values.
- Report all metric distributions and markout coverage. A distribution of per-session
  markout means weights sessions equally; a pooled markout weights available units.
  Missing/pending midpoint marks are not zeros. Horizons remain public-event counts.
- Threshold probabilities use strict inequalities; zero P&L is neither a profit
  nor a loss. The worst-five-percent mean uses ceil(0.05n) ordered observations.
  The illustrative practical difference threshold is £0.05/session; it is not a
  real capital, risk or investment hurdle. Intervals are not simultaneous across
  exploratory sweep values/metrics; no multiple-testing correction is claimed.
- The selection-bias and significance controls are labelled Gaussian statistical
  demonstrations. Their synthetic payoffs are not exchange-generated trading P&L.
  No seed search or retuning is used to force their observed results.
- Evaluation access is recorded before execution, including failed attempts.
  Repeated overlap warns that seeds are no longer fresh. A local file registry
  cannot prevent deliberate bypass, a different registry or off-platform peeking.
  Train/test separation does not remove model bias or guarantee external validity.
- Lightweight mode drops retained event/book histories but preserves all matching,
  accounting and conservation checks. Internal book/account evidence still grows
  with duration. No parallel worker executor has been added. Profiling reports
  actual local runtime and Python-traced memory, not unmeasured speed claims.
- Exact extreme regeneration requires the recorded simulator/Python versions and
  matching outcome/trajectory fingerprints before saving and replaying a full lab
  journal. Record hashes detect accidents; they are not authentication signatures.
- The generic engine has no market-making dependency. Later directional, options
  and portfolio adapters can use the same research interface and existing market
  infrastructure. Phase 6 manual trading remains unimplemented pending review.


## Phase 6 — manual trading conventions

- The browser submits commands; the existing Python OrderBook alone matches orders.
  Manual and automated-maker accounts are separate; all actual fills use the same
  exact FIFO ledger. The matching engine's conservation checks are unchanged.
- Opening scenario inventory is endowed at the opening public reference. Starting
  equity = cash0 + q0 × reference0; no opening trade, fee or turnover is fabricated.
  Remaining-lot average entry differs from cumulative per-order VWAP. Fees are
  expensed immediately in realised P&L; unrealised is gross remaining-lot valuation.
- Risk reserves every outstanding buy/sell independently. Opposite sides cannot
  net reservations. Market orders reserve their full requested size conservatively.
  Own-crossing orders reject; replacement is explicit cancellation plus new priority.
- Manual marking excludes own orders: external midpoint, then actual last trade,
  then opening public reference. This can be endogenous/stale and is not an exit
  quote. Background agents observe real manual executions without extra random draws.
- Public stepping skips private events internally. Pausing freezes automatic time;
  explicit steps remain allowed. Matching one submitted order is atomic. Background
  ties precede automated quote refresh; ending finishes ties at current time, then
  cancels live user/maker orders. It never advances to later timestamps or closes
  positions automatically. The simulation may run slower than wall time under load.
- Public markouts use own-side sign × (future full-book midpoint − execution), at
  1/5/20 subsequent public actions, with missing/pending explicit. Provider/aggressor
  roles are separate; own actions/end cancellations can influence marks. Marks are
  neither extra P&L nor causal proof of information asymmetry.
- Public data is explicitly allowlisted, including anonymised FIFO queues. Hidden
  background records/signals/latent values are only in post-session observer exports.
  A user who chooses a reproducible seed can inspect local code; this information
  boundary is pedagogical, not isolation from a hostile local operator.
- Single shared loopback session, fixed 250 ms timer increments, no browser financial
  rules or third-party scripts. Responses carry revisions. Ended sessions auto-save
  under runs/manual; active sessions remain in memory. Maximum live setup is 300
  seconds and 5,000 commands. Original journal text preserves numeric representations
  through browser import; checksums detect corruption but do not authenticate logs.
- Five uncalibrated scenarios alter actual model/depth/position parameters. A higher
  latent volatility need not imply a larger realised price change in every run.
  No latency, margin/borrow/capital model, options or advanced agents are added.

See [Phase 6 contract](phase_06.md),
[lesson](../maths/phase_06_trading.md) and [review](../learning/phase_06_report.md).


## Phase 7 — learning conventions

- The tutor sees detached, allowlisted public facts. The original exchange/account
  modules remain the financial source of truth. Tutor commands, scores, dates and
  option ordering do not enter market RNG streams or replay actions.
- Correct implementation is not proof of realistic markets, sound human decisions
  or real-world skill. P&L never awards mastery. A negative provider mark neither
  identifies an informed trader nor adds a second loss to the account.
- Practice categories use documented recent answer credits and heuristic thresholds.
  They are not calibrated competence probabilities. Viewing is not credit; absent
  assessment is not failure. Structured options test recognition, not eloquence.
- Misconceptions cite selected claims. Repeated means separate incorrect question
  instances; it does not diagnose a permanent belief. Arithmetic mistakes do not
  justify inventing a conceptual explanation for the learner.
- Review uses UTC calendar days, independently of simulated time. Automatic prompts
  have a configurable public-event gap. No application feature requires a quiz pass.
- Progress uses atomic local JSON replacement and one writer per profile. Multiple
  browser tabs share one active question. Recent history/completion keys are bounded;
  counters persist. Local file editing can alter scores; this is not an exam system.
- Live trading remains in memory; learning persists independently. Forensics is an
  explicitly requested ended-session view, never fed back to learning inputs/exports.
  The boundary is pedagogical, not protection against a hostile local code reader.
- The research tutor recomputes verified complete-session summaries and retains units.
  Observed extremes are not hard loss bounds. Pairing can help or hurt precision.
  Old evaluation data is not new out-of-sample evidence.
- Tutor I/O and human thinking can slow wall-clock operation. Independence tests
  compare the same ordered market actions/ticks, not differently timed human actions.
- Numerical examples exist where meaningful; qualitative concepts progress to
  reasoning instead of artificial arithmetic. Timing/voice/free-text interviewing,
  psychometric calibration and cross-version curriculum migrations remain limitations.
- The optional future language-layer protocol has no implementation, keys or network
  calls. Phase 8 activates derivative pricing and the relevant calculus/numerical
  lessons; linear algebra, optimisation and later risk methods remain deferred.

See [Phase 7 teaching contract](phase_07.md).

## Phase 8 — derivatives conventions

- European calls/puts on one synthetic stock. Cash settlement uses fixed strike,
  whole contracts and multiplier, once at the recorded expiry reference.
  Expiry is exact ACT/365 model time, independent of wall-clock time.
- Premium is GBP per underlying unit. Fills use six decimals; bid rounds down and
  ask up within discounted bounds. Midpoint may have seven decimals. Monetary ledgers
  are exact fractions after declared rounding; theoretical pricing is floating-point.
- Volatility/rate/yield inputs are annual decimals. UI percentages convert explicitly.
  Vega/rho are per 1.00; labelled percentage-point outputs divide by 100. Calendar
  theta is per year; daily display divides by 365 and is a local approximation.
- Black–Scholes–Merton assumes European exercise, no arbitrage, lognormal stock,
  constant volatility/rate/yield and continuous frictionless replication. Live trading
  requires zero dividends; analytical/MC APIs correctly support continuous yields.
- Default dealer volatility is base × (1 − .15 log(K/S) + .25 log(K/S)²), clipped
  to [.001,3]. This is neither calibrated nor guaranteed arbitrage-free across strikes.
  Partial Greeks hold volatility fixed even when the live smile moves.
- Options use finite immediate-or-cancel dealer quotes; depth replenishes on refresh,
  stale revisions reject. No option limit book, dealer risk account, margin,
  assignment, borrow charge or funding spread is modelled.
- Stock innovations are causal geometric Brownian steps with declared physical drift
  and volatility, rounded to penny ticks. External orders refresh around each
  observation; user limits retain real FIFO priority. User trades do not impact
  the future exogenous process. This model is deliberately uncalibrated.
- Stock hedges use the existing full exchange and risk/accounting path. Finite depth,
  reservations and self-cross prevention may prevent completion. Hedge rounding is
  nearest whole unit with ties to even; no invisible stock adjustments occur.
- Option and stock FIFO gross P&L plus funding minus explicit fees equals marked
  equity exactly. Premium and current asset/liability values are not extra profits.
  Spreads enter fill prices; marked value is not a guaranteed liquidation price.
- Combined cash earns/pays the same compounded rate each interval, rounded to eight
  decimals. Borrowing is unlimited within position limits. Defaults are zero rate
  and zero physical drift; this is not a realistic capital model.
- Gross hedging error means option gross P&L + stock gross P&L + financing before
  explicit fees, with spreads already included. RMS delta samples exposure entering
  model intervals, understating within-step/gap risk. Drawdown uses recorded marks.
- RV is close-to-close quadratic variation, not demeaned sample volatility. Drift,
  tick rounding and observation frequency matter. Process input, realised volatility
  and synthetic price-implied volatility are distinct.
- Research hypotheses use registered development seeds. Frequency variants share
  paths; volatility variants share normal shocks transformed differently. Entire
  sessions are observations. Development inspection is never called evaluation.
- MC uses risk-neutral drift r−q, IID terminal normals and an independent PCG64
  stream. Student-t mean intervals approximate sampling uncertainty only. Zero
  sampled variation under stochastic inputs warns about unresolved rare tails.
- IV checks feasibility, uses safeguarded Newton/bisection, and gives no reliable IV
  at expiry, saturated bounds, numerical ambiguity or iteration exhaustion.
  Numerical precision is not economic quote precision.
- Public/tutor inputs contain current facts. Market seed/future shocks are absent.
  Ended exports recreate paths, so this boundary is pedagogical isolation, not security
  against a local operator who knows a seed or a replay's ending.
- Active questions and derivative context caches clear on rewind/new sessions.
  Learning history remains past evidence; it is not a forecast. Demo answers are
  separate from Arvind's profile. Phase 9 remains unstarted.

See the [Phase 8 lesson](../maths/phase_08_options.md) and
[architecture](phase_08.md).


## Phase 9 — portfolio risk

Risk consumes existing accounts. Marked exposure excludes cash; equity includes it.
Realised/unrealised trading P&L, fees and funding remain ledger-derived. Initial
capital is separate. Risk-session drawdown starts at attachment. Distinct stocks
retain underlying identities; aggregate raw delta units are not a perfect hedge
across different stocks.

Loss is negative hypothetical P&L. Empirical VaR uses the inverse CDF and ES uses
exact worst-tail mass with fractional boundary weighting. Normal risk is explicitly
linear/delta-normal; its IID moment time scaling is not applied to nonlinear option
P&L. Historical blocks and MC compound daily simple returns and reprice options.
The default sample is synthetic and independently seeded, not the future market.
A horizon crossing a live expiry is unavailable, never silently extrapolated.

Scenario option P&L is a model change with current quote/model basis frozen. IV is
sticky strike; ordinary return VaR holds IV fixed. Stress can change IV and rates.
The 100-bp liquidity haircut is a scenario assumption, not an exchange-impact model.
Scenarios never alter realised accounts. Full BSM repricing is not a real price forecast.

Covariance must be finite, symmetric and PSD. No automatic statistical regularisation;
roundoff-level handling is reported. Cholesky handles positive definite matrices;
an explicit eigenfactor handles singular PSD cases. Correlation of zero-variance
series is unavailable. Heavy tails use covariance-matched multivariate t(5).

Order limits use actual-fill previews and current-mark reservations for outstanding
orders. Hard limits prohibit new or worsening breaches; reductions remain possible.
Market movements can create subsequent breaches. VaR limits explicitly use the
nonnegative delta-normal approximation and cannot capture every option tail risk.
Optimisation has explicit budget/weight/cash constraints, synthetic expected returns
and independent feasibility checks; weights are never executed automatically.


## Phase 10 — stat-arb model and execution assumptions

- **No real alpha claim.** Gaussian additive or common-factor synthetic processes are
  teaching assumptions. Fixed asset universes omit real survivorship/corporate-action issues.
- Cointegration claims are by generating construction, not significance tests. The AR(1)
  diagnostic is **not ADF**; fitted persistence/half-life cannot certify stationarity.
- Exact arithmetic-process paths are unbounded. Nonpositive executable prices fail visibly;
  no clipping, silent retries or seed replacement repairs them. Published prices round to pennies.
- Ordinary agents see published price history only. No future rows, process innovations,
  true relationship coefficients, break timestamps or market seed enter public snapshots.
- At t, fitting ends before t and residual normalization excludes t. All normalizing residuals
  use one available model vintage. New fits never rewrite an open trade's entry hedge.
- Conventional OLS SEs require IID/homoskedastic errors; price residuals often violate this.
  Constant/tiny-variance predictors are rejected; no claimed valid time-series p-values.
- Unit-hedge estimates outside [0.05,5] block entry. Zero-trade outcomes remain in reports.
  Whole-unit rounding and price scales prevent automatic exact neutrality.
- Sequential actual Phase 6/1 fills, two finite external depth levels and fees determine positions.
  External liquidity is exogenously refreshed; no endogenous impact or queue competition.
  A close order can fail, and sample-end residual inventory remains marked and disclosed.
- No borrow availability, short fees, margin financing or liquidation engine. Return denominator
  is explicit user-supplied research capital; position notional is not an economic leverage limit.
- Gross/leg safeguards preflight orders; z/loss/time guards request actual systematic exits.
  The existing Risk Lab's limits cover its original venues; Stat Arb limits have separate scope.
- Stat-arb covariance uses up to 80 observed returns, one observation horizon, zero mean and
  normal tails. X-return proxy loading is estimated, not a hidden true common-factor loading.
- Consolidated Risk Lab view reads the actual additional ledgers. Cross-lab covariance is set
  to zero and one stat-arb observation mapped to one risk day for illustration; this is not a
  calibrated joint forecast. Replays never silently mix a past frame with a future live pair.
- Attribution: spread movement plus remaining unit-hedge directional movement, less signed
  execution shortfall and fees, must reconcile to ledgers. Temporary directional P&L is a subset.
- Selection ranks training outcomes only. Generalisation/mining scored intervals have equal
  length; the selected specification is refitted on past data at deployment, so differences
  combine selection optimism, sampling and model re-estimation effects.
- Final research parameters/seeds were registered before outcomes. Reinspection is reuse,
  not a new holdout. Results/intervals are conditional on the synthetic process; candidates
  share assets and are not independent significance tests. No p-values are claimed for mining.
- One-step future oracle is an isolated **INVALID** teaching demonstration, never a live policy.
- Phase 10 retains runtime version 0.9.0 in archived evidence; its separate stat-arb schema and
  adapter identify this unreleased feature increment. Old records are not relabelled.
