# Trade a progressively revealed path

Open Trading → **Choose your market environment** → **Set up historical replay**.
Import a CSV and describe its source, rights, adjustment basis, timezone, frequency and
transformations. Select one instrument or two exactly aligned series. Choose volume
participation, adverse slippage and fee, then start. The initial account sees only bar zero.

For a ready local mechanics demonstration, choose **Load artificial test fixture**.
This deliberately does not claim to be a real historical session. A five-bar fixture and
metadata are also in [sample](sample/artificial_fixture.csv); see [provenance](DATA_PROVENANCE.md).

Use Buy/Sell, Market/Limit, size and Cancel. The account table shows cash, realised gross,
unrealised, fees and net P&L. The chart uses the first selected instrument; the account
section lists current closes for both. Risk and the paired signal use both when applicable.

Play advances model observations, Pause stops advancement, Step observation reveals one
bar, and Step time reveals up to one minute on the browser button. The API accepts explicit
seconds. A gap can mean a time step reveals nothing. Speed is 1–10 observations per second;
one request reveals at most 200 observations. Playback timing is presentation, not market RNG.

End before switching away from a session that contains actions. Export its journal if you
want to keep it. Imports and active environment sessions are held in local server memory;
closing the process discards them unless you saved the original CSV, metadata and journal.

Load a journal only with the exact original imported data and provenance. Verification
reruns every instruction and state fingerprint. Frames are **read-only** and can move
backwards. Neither their account nor their learner question can use a later frame.
**Start a new session at the beginning** makes a new account, not a rewind of the same
live account. Prior human knowledge cannot be erased; a repeat is not a blind trial.

Historical options are unavailable because OHLCV contains no option chain. Past-return
VaR/ES revalues current holdings using at most 250 revealed returns, through the existing
risk engine. It needs two returns to compute, but such a small sample is extremely noisy.
Its horizon is **one observed interval**, not an assumed trading day. Gaps can mix interval
lengths, a limitation the user must assess. No future volatility estimate enters live risk.

With two compatible series, the existing causal model reports regression, residual and
z-score. Default fit uses 20 past observations; normalisation uses 12 past residuals. The
current point is compared with past fitted/normalised values; no full-sample backward fit.
After ending, **Run separate historical threshold study** registers fixed/rolling/walk-forward
training/evaluation boundaries through Phase 5. This is POST-SESSION FULL-DATA ANALYSIS;
its one recorded path does not create independent Monte Carlo evidence. Fixed one-unit
legs are deliberately not described as beta-neutral portfolio construction.

Post-session summary supplies largest position/drawdown/trade, costliest paper execution,
largest revealed price moves and instructions. Safe pre/post public replay hooks support
later teaching work. Phase 14's annotated guided replay is not implemented here.
