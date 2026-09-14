"""Artificial import demonstrations; never represented as real recorded market data."""

from datetime import UTC, datetime, timedelta

from quantlab.environments.data import load_csv
from quantlab.statarb.process import Link, Process


def fixture_inputs(rows=100):
    process = Process(seed=131042, links=(Link(),))
    prices = [process.prices.tolist()] + [process.step() for _ in range(rows - 1)]
    output = []
    for j, instrument in enumerate(("FIXTURE-X", "FIXTURE-Y")):
        csv = ["timestamp,open,high,low,close,volume"]
        for i, row in enumerate(prices):
            close = round(row[j], 2)
            opening = round(prices[max(0, i - 1)][j], 2)
            timestamp = (
                datetime(2020, 1, 2, 9, 30, tzinfo=UTC) + timedelta(minutes=i)
            ).isoformat()
            csv.append(
                f"{timestamp},{opening:.2f},{max(opening, close) + 0.02:.2f},"
                f"{min(opening, close) - 0.02:.2f},{close:.2f},{100 + i % 5 * 10}"
            )
        meta = dict(
            instrument=instrument,
            source="QuantLab generated test fixture; NOT historical market data",
            licence="Original artificial test data; no third-party market observations",
            timezone="UTC",
            frequency_seconds=60,
            currency="GBP",
            price_basis="raw",
            corporate_actions="none_in_session",
            transformations=(
                "Artificial OHLC ranges constructed around a seeded synthetic close path"
            ),
            tick_size="0.01",
            data_kind="artificial_fixture",
        )
        output.append({"csv_text": "\n".join(csv) + "\n", "metadata": meta})
    return output


def fixtures(rows=100):
    return tuple(load_csv(v["csv_text"], v["metadata"]) for v in fixture_inputs(rows))
