import json
from dataclasses import FrozenInstanceError

import pytest

from quantlab.environments.data import FIELDS, compatible, load_csv
from quantlab.environments.fixtures import fixture_inputs, fixtures
from tests.markets.helpers import bars, change_rows


def test_dataset_immutable_prefix_and_provenance():
    d = bars()
    assert len(d.prefix(1)) == 2 and set(d.prefix(1)[0]) == set(FIELDS)
    assert not d.provenance(1)["dataset_fingerprint"]
    assert d.provenance(4, ended=True)["dataset_fingerprint"] == d.fingerprint
    with pytest.raises(FrozenInstanceError):
        d.fingerprint = "changed"
    m = d.meta
    m["source"] = "changed"
    assert d.meta["source"] != "changed"


@pytest.mark.parametrize(
    "field,value",
    [
        ("open", "0"),
        ("open", "-1"),
        ("high", "99"),
        ("low", "101"),
        ("close", "200"),
        ("close", "nan"),
        ("open", "inf"),
        ("volume", "-1"),
        ("volume", "0.5"),
        ("volume", "1000000001"),
        ("open", "100.001"),
        ("close", ""),
        ("timestamp", ""),
        ("timestamp", "2020-01-02T09:30:00"),
        ("timestamp", "2020-01-02T09:30:00+01:00"),
        ("timestamp", "bad"),
    ],
)
def test_reject_invalid_bar(field, value):
    d = bars()
    text = change_rows(d, lambda rows: rows[0].update({field: value}))
    with pytest.raises(ValueError):
        load_csv(text, d.meta)


@pytest.mark.parametrize(
    "field,value",
    [
        ("instrument", ""),
        ("source", ""),
        ("licence", ""),
        ("timezone", "GMT+banana"),
        ("frequency_seconds", True),
        ("frequency_seconds", 0),
        ("frequency_seconds", 1.1),
        ("currency", "USD"),
        ("price_basis", "close_adjusted"),
        ("corporate_actions", "unknown"),
        ("transformations", ""),
        ("tick_size", "0"),
        ("tick_size", "nan"),
        ("tick_size", "0.00123"),
        ("data_kind", "official"),
        ("price_basis", "adjusted"),
        ("corporate_actions", "all_ohlc_adjusted"),
        ("instrument", "X" * 41),
    ],
)
def test_reject_bad_or_inconsistent_metadata(field, value):
    d = bars()
    with pytest.raises(ValueError):
        load_csv(d.csv_text, d.meta | {field: value})


@pytest.mark.parametrize(
    "operation", ["duplicate", "backward", "missing", "extra", "frequency"]
)
def test_reject_structure_and_order(operation):
    d = bars()

    def mutate(rows):
        if operation == "duplicate":
            rows[1]["timestamp"] = rows[0]["timestamp"]
        if operation == "backward":
            rows.reverse()
        if operation == "missing":
            rows[1]["close"] = ""
        if operation == "extra":
            rows[0]["depth"] = "5"
        if operation == "frequency":
            rows[1]["timestamp"] = "2020-01-02T09:31:01+00:00"

    with pytest.raises(ValueError):
        load_csv(change_rows(d, mutate), d.meta)


def test_timezone_dst_offsets_preserve_real_instant_order():
    d = bars()
    text = (
        "timestamp,open,high,low,close,volume\n"
        "2020-10-25T01:59:00+01:00,100,100,100,100,1\n"
        "2020-10-25T01:00:00+00:00,100,100,100,100,1\n"
    )
    loaded = load_csv(text, d.meta | {"timezone": "Europe/London"})
    assert loaded.bars[1].time_us - loaded.bars[0].time_us == 60_000_000


def test_consistently_adjusted_and_gap_allowed_but_never_filled_forward():
    d = bars(price_basis="adjusted", corporate_actions="all_ohlc_adjusted")
    text = change_rows(d, lambda rows: rows.pop(1))
    assert len(load_csv(text, d.meta).bars) == 4


@pytest.mark.parametrize(
    "what", ["text", "source", "licence", "basis", "timezone", "transformations"]
)
def test_full_content_and_metadata_fingerprint(what):
    d = bars()
    meta = d.meta
    text = d.csv_text
    if what == "text":
        text += "\n"
    elif what == "basis":
        meta.update(price_basis="adjusted", corporate_actions="all_ohlc_adjusted")
    elif what == "timezone":
        meta["timezone"] = "Europe/London"
    else:
        meta[what] += " amended"
    assert load_csv(text, meta).fingerprint != d.fingerprint
    assert load_csv(d.csv_text, d.meta).fingerprint == d.fingerprint


@pytest.mark.parametrize(
    "change",
    ["instrument", "timezone", "frequency_seconds", "price_basis", "data_kind", "timestamps"],
)
def test_pair_compatibility(change):
    x, y = fixtures()
    if change == "timestamps":
        y = load_csv(change_rows(y, lambda rows: rows.pop()), y.meta)
    elif change == "price_basis":
        y = load_csv(
            y.csv_text,
            y.meta | {"price_basis": "adjusted", "corporate_actions": "all_ohlc_adjusted"},
        )
    else:
        value = {
            "instrument": x.meta["instrument"],
            "timezone": "Europe/London",
            "frequency_seconds": 30,
            "data_kind": "recorded",
        }[change]
        y = load_csv(y.csv_text, y.meta | {change: value})
    with pytest.raises(ValueError):
        compatible([x, y])


def test_fixture_provenance_and_loader_budgets():
    v = fixture_inputs(2)[0]
    assert v["metadata"]["data_kind"] == "artificial_fixture"
    assert "NOT historical" in v["metadata"]["source"]
    d = bars()
    for text in ("", "x" * 2_000_001, "timestamp,open,high,low,close,volume\n"):
        with pytest.raises(ValueError):
            load_csv(text, d.meta)
    for meta in ({}, d.meta | {"extra": "x"}):
        with pytest.raises(ValueError):
            load_csv(d.csv_text, meta)
    assert "latent" not in json.dumps(d.provenance(0))
