# Real screenshot and capture plan

Use the release preview with a disposable learning profile. Screenshots must be real UI captures,
not generated mockups. Preserve simulation/source labels and avoid private user journals.
Desktop QA uses 1440 × 1000; laptop 1100 × 1000; tablet 820 × 1000; phone 390 × 844.
Use the native tab screenshot API for readable viewport captures. Native output is JPEG; the files keep the correct `.jpg` extension. The order result uses a 1200-pixel-tall capture; trading/options captures are 1234 pixels tall as returned by the browser. The full-page stitching API produced padding/duplicate strips and is not used for final assets.

| # | Image / subject | Actual route or deterministic state | What must remain visible |
|---:|---|---|---|
| 1 | `home.jpg` | `/home` | Product identity and simulation wording |
| 2 | `trading-desk.jpg` | `/`, seed 42, paused after BUY 6 MARKET | Order ticket, public book, source badge |
| 3 | `order-vwap.jpg` | order · `order-after-multifill` | Actual 3/4/3 fills and £100.023 VWAP |
| 4 | `synthetic-prices.jpg` | synthetic-prices, public result | Distinct public execution evidence; no unauthorised private signal |
| 5 | `options-lab.jpg` | `/options`, fresh finite quote chain | Multiplier, model inputs, Greek units |
| 6 | `delta-hedge.jpg` | delta-hedge · `delta-after-hedge`, full | Stock −51 and residual delta |
| 7 | `risk-lab.jpg` | tails · `var-vs-es-tail` | VaR 10/10, ES 12/48 and assumptions |
| 8 | `stress-test.jpg` | `/risk#stress`, actual detached full repricing | Hypothetical stress, not a ledger debit |
| 9 | `statarb-lab.jpg` | `/statarb#model`, 120 revealed observations | Fit window, residual and units |
| 10 | `correlation-residual.jpg` | pairs · `correlation-vs-residual` | Both correlations and actual residual paths |
| 11 | `research-distribution.jpg` | winner · `winner-before-test` | All development variants, no evaluation result before reveal |
| 12 | `explain-mode.jpg` | order after fill → Explain this moment | Demo context, actual fills and VWAP |
| 13 | `guided-demo.jpg` | order · `order-before-submit` | Predict before reveal, public information only |
| 14 | `learning-dashboard.jpg` | `/learning`, empty QA profile | No fabricated mastery |

`home-mobile.jpg` is additional responsive evidence. The machine-readable
[capture manifest](../assets/readme/captures.json) records files actually produced, dimensions,
source route/state and SHA-256 hashes. A planned row is not a claim that an image exists.

## Named capture procedure

Open a flagship, expand **Named capture states & script export**, choose the name, and explicitly
enter showcase capture. If required choose the full hedge branch first. Record the branch with
the shot. A capture disables mastery; it does not grant private observer permission.
For a public synthetic shot, leave observer material unrevealed. For a teaching video that needs
private evidence, end/review the demo, explicitly reveal, and keep the observer label in the shot.

Before recording: restart, verify the state, keep limitations, and check actual script values.
No seed search, edited profits, synthetic image generation or external screen recorder is used.
