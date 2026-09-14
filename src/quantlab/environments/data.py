"""Strict local OHLCV import. Storage knows the future; public prefixes do not."""

import csv
import io
import math
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from fractions import Fraction
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from quantlab.domain import PriceGrid
from quantlab.research.codec import digest

MAX_ROWS = 5000
MAX_BYTES = 2_000_000
FIELDS = ("timestamp", "open", "high", "low", "close", "volume")
META = {
    "instrument",
    "source",
    "licence",
    "timezone",
    "frequency_seconds",
    "currency",
    "price_basis",
    "corporate_actions",
    "transformations",
    "tick_size",
    "data_kind",
}


def integer(value, name, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name} must be a whole number from {low} to {high}")
    return value


def amount(value, name, low=0, high=1_000_000_000):
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError(f"{name} must be a finite number")
    if len(str(value)) > 60:
        raise ValueError(f"{name} is too long")
    try:
        f = float(value)
        if not math.isfinite(f) or not low <= f <= high:
            raise ValueError()
        return Fraction(str(value))
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError(f"{name} must be finite and between {low} and {high}") from exc


@dataclass(frozen=True)
class Bar:
    timestamp: str
    time_us: int
    open: int
    high: int
    low: int
    close: int
    volume: int

    def public(self, tick):
        return (
            {"timestamp": self.timestamp}
            | {k: float(getattr(self, k) * tick) for k in ("open", "high", "low", "close")}
            | {"volume": self.volume}
        )


@dataclass(frozen=True)
class Dataset:
    metadata: tuple
    bars: tuple[Bar, ...]
    fingerprint: str
    csv_text: str

    @property
    def meta(self):
        return dict(self.metadata)

    @property
    def tick(self):
        return Fraction(self.meta["tick_size"])

    def prefix(self, index):
        integer(index, "Observation", 0, len(self.bars) - 1)
        return tuple(b.public(self.tick) for b in self.bars[: index + 1])

    def provenance(self, index, *, ended=False):
        # No full-content digest, future extrema, future row count or future date on live views.
        return self.meta | {
            "available_fields": list(FIELDS),
            "revealed_from": self.bars[0].timestamp,
            "revealed_through": self.bars[index].timestamp,
            "revealed_observations": index + 1,
            "source_claim": (
                "User-supplied provenance; not independently certified exchange data"
            ),
            "dataset_fingerprint": self.fingerprint if ended else None,
            "date_range": [self.bars[0].timestamp, self.bars[-1].timestamp] if ended else None,
        }


def load_csv(text, metadata):
    if not isinstance(text, str) or not 1 <= len(text.encode()) <= MAX_BYTES:
        raise ValueError("CSV must be text, at most 2 MB")
    if not isinstance(metadata, dict) or set(metadata) != META:
        raise ValueError("Supply every documented provenance field, with no unknown fields")
    m = dict(metadata)
    for key in META - {"frequency_seconds"}:
        if not isinstance(m[key], str) or not m[key].strip() or len(m[key]) > 400:
            raise ValueError(f"Provenance {key} needs nonempty text of at most 400 characters")
    if len(m["instrument"]) > 40:
        raise ValueError("Instrument identifier is limited to 40 characters")
    integer(m["frequency_seconds"], "Frequency in seconds", 1, 86400)
    if m["currency"] != "GBP":
        raise ValueError(
            "Phase 13 paper accounts require GBP inputs; no silent currency conversion"
        )
    if m["price_basis"] not in ("raw", "adjusted"):
        raise ValueError("Price basis must be raw or adjusted for ALL OHLC columns")
    if m["corporate_actions"] not in ("none_in_session", "all_ohlc_adjusted"):
        raise ValueError(
            "Use a session with no corporate actions or all OHLC adjusted consistently"
        )
    if (m["price_basis"] == "adjusted") != (m["corporate_actions"] == "all_ohlc_adjusted"):
        raise ValueError("Adjustment basis and corporate-action policy disagree")
    if m["data_kind"] not in ("recorded", "artificial_fixture"):
        raise ValueError("Data kind must be recorded or artificial_fixture")
    if not amount(m["tick_size"], "Tick size", 0.000001, 1):
        raise ValueError("Positive tick required")
    grid = PriceGrid(Decimal(m["tick_size"]))
    try:
        zone = ZoneInfo(m["timezone"])
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError("Timezone must be an IANA name, such as Europe/London or UTC") from exc
    reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff")), strict=True)
    if reader.fieldnames != list(FIELDS):
        raise ValueError(
            "CSV columns must be timestamp,open,high,low,close,volume; "
            "quotes/depth are unsupported"
        )
    bars = []
    epoch = datetime(1970, 1, 1, tzinfo=UTC)
    try:
        for line, row in enumerate(reader, 2):
            if len(bars) >= MAX_ROWS:
                raise ValueError("CSV exceeds the 5,000-observation budget")
            if set(row) != set(FIELDS) or any(v is None or not v.strip() for v in row.values()):
                raise ValueError(f"CSV row {line}: missing or extra values")
            try:
                dt = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
                if dt.tzinfo is None or dt.utcoffset() != dt.astimezone(zone).utcoffset():
                    raise ValueError()
                elapsed = dt.astimezone(UTC) - epoch
                us = (elapsed.days * 86400 + elapsed.seconds) * 1_000_000 + elapsed.microseconds
                if us < 0:
                    raise ValueError()
            except ValueError as exc:
                raise ValueError(
                    f"CSV row {line}: timestamp needs an explicit offset "
                    "matching the declared timezone"
                ) from exc
            if bars and us <= bars[-1].time_us:
                raise ValueError(
                    f"CSV row {line}: timestamps must increase; duplicates are rejected"
                )
            if bars and (us - bars[-1].time_us) % (m["frequency_seconds"] * 1_000_000):
                raise ValueError(f"CSV row {line}: interval disagrees with declared frequency")
            prices = {}
            for k in ("open", "high", "low", "close"):
                amount(row[k], f"Row {line} {k}", 0.000001)
                prices[k] = grid.to_ticks(row[k])
            if (
                not prices["low"]
                <= min(prices["open"], prices["close"])
                <= max(prices["open"], prices["close"])
                <= prices["high"]
            ):
                raise ValueError(f"CSV row {line}: OHLC range is inconsistent")
            volume = amount(row["volume"], f"Row {line} volume", 0, 1_000_000_000)
            if volume.denominator != 1:
                raise ValueError(f"CSV row {line}: volume must be whole instrument units")
            bars.append(Bar(dt.astimezone(zone).isoformat(), us, **prices, volume=int(volume)))
    except csv.Error as exc:
        raise ValueError("Malformed CSV quoting or field structure") from exc
    if len(bars) < 2:
        raise ValueError("At least two observations are required")
    canonical = {"metadata": m, "csv": text}
    return Dataset(tuple(sorted(m.items())), tuple(bars), digest(canonical), text)


def compatible(datasets):
    if not 1 <= len(datasets) <= 2:
        raise ValueError("Use one instrument, or two synchronised compatible instruments")
    if len({d.meta["instrument"] for d in datasets}) != len(datasets):
        raise ValueError("Pair instruments must have distinct identifiers")
    first = datasets[0]
    for d in datasets[1:]:
        for key in ("currency", "frequency_seconds", "timezone", "price_basis", "data_kind"):
            if d.meta[key] != first.meta[key]:
                raise ValueError(f"Pair datasets disagree on {key}")
        if [b.time_us for b in d.bars] != [b.time_us for b in first.bars]:
            raise ValueError(
                "Pair timestamps must match exactly; no forward-fill or interpolation"
            )
