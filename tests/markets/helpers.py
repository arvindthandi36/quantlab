import csv
import io
from datetime import UTC, datetime, timedelta

from quantlab.environments.data import load_csv
from quantlab.environments.fixtures import fixture_inputs


def bars(closes=(100, 101, 99, 102, 100), volume=100, **metadata):
    meta = fixture_inputs(2)[0]["metadata"] | metadata
    rows = ["timestamp,open,high,low,close,volume"]
    for i, c in enumerate(closes):
        t = (datetime(2020, 1, 2, 9, 30, tzinfo=UTC) + timedelta(minutes=i)).isoformat()
        v = volume[i] if isinstance(volume, list) else volume
        rows.append(f"{t},{c},{c + 10},{c - 10},{c},{v}")
    return load_csv("\n".join(rows) + "\n", meta)


def change_rows(d, fn):
    rows = list(csv.DictReader(io.StringIO(d.csv_text)))
    fn(rows)
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=rows[0].keys(), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return out.getvalue()


def mutated_future(d, t, variant=0):
    def mutate(rows):
        for i, r in enumerate(rows):
            if i > t:
                price = 200 + (i + variant * 3) % 17
                # Every stored future OHLCV and timestamp changes; past is identical.
                r.update(
                    open=str(price),
                    high=str(price + 8),
                    low=str(price - 7),
                    close=str(price + 2),
                    volume=str((i + 1) * 11),
                )
                r["timestamp"] = (
                    datetime.fromisoformat(r["timestamp"]) + timedelta(days=20 + variant)
                ).isoformat()

    return load_csv(change_rows(d, mutate), d.meta)
