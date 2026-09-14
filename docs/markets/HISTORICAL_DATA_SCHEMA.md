# Local historical data schema

Phase 13 supports **GBP OHLCV CSV only**, with one file per instrument. This deliberately
small adapter accepts neither quotes nor depth. A future genuine quote/trade adapter can
implement the environment contract without pretending bars contain exchange queues.

Exact UTF-8 header, in this order:

```csv
timestamp,open,high,low,close,volume
2020-01-02T09:30:00+00:00,100,100.20,99.80,100,20
2020-01-02T09:31:00+00:00,100.05,100.20,99.80,100.05,20
```

These example rows are **artificial**, not market history. Timestamp means the **end /
availability time** of the complete bar. Convert provider start-labelled bars to their
actual availability time before importing, and record this transformation. Otherwise
showing an entire bar at its start would be look-ahead.

Required metadata (JSON through the Python/API adapter; labelled fields in the browser):

```json
{
  "instrument": "MY-INSTRUMENT",
  "source": "Your actual provider and export description",
  "licence": "Your actual rights / local-use restriction",
  "timezone": "Europe/London",
  "frequency_seconds": 60,
  "currency": "GBP",
  "price_basis": "raw",
  "corporate_actions": "none_in_session",
  "transformations": "None, or an explicit account of each transformation",
  "tick_size": "0.01",
  "data_kind": "recorded"
}
```

Use `artificial_fixture` for generated test data. The fixture button and supplied metadata
file already do this. Do not relabel the fixture as `recorded` in the real-data import form.

Timestamps require an explicit UTC offset consistent with the declared IANA timezone.
Ordering is by actual UTC instant: the repeated autumn local hour is allowed when its
offsets distinguish the instants. Duplicate/reversed instants fail. Intervals must be
whole multiples of the declared frequency. Gaps are allowed, not interpolated or filled.
Daily data across changing offsets needs a consistent availability convention (for example
UTC) that satisfies this contract; the loader does not silently adjust a dataset.

All prices must be positive, finite, on the declared tick grid, and satisfy
`low <= min(open,close) <= max(open,close) <= high`. Volume is non-negative **whole
instrument units**, not currency turnover. Zero volume is valid and yields no fills.
No missing values, extra columns, fractional volume or malformed records are repaired.
Budgets: 2 MB, 5,000 bars/file, eight imported files, one or two active instruments.

For two instruments, timestamps must align exactly and currency, timezone, frequency,
adjustment basis and data kind must match. There is no interpolation or forward fill.
Python entry point: `quantlab.environments.data.load_csv(text, metadata)`.

Raw inputs require `none_in_session`. Adjusted inputs require `all_ohlc_adjusted`.
These are source declarations: the application can reject inconsistent declarations and
invalid OHLC ranges, but cannot prove a vendor adjusted every field. No split/dividend
processing is implemented. Choose a controlled session or provide a consistently adjusted
series with compatible volume and tick units; an unexplained discontinuity is unacceptable.
