import copy
import json

import pytest

from quantlab.environments.explanation import explain, what_if
from quantlab.environments.fixtures import fixtures
from quantlab.environments.historical import HistoricalSession
from quantlab.environments.learning import EnvironmentTutor
from quantlab.research.codec import digest
from quantlab.trading.server import Controller
from tests.markets.helpers import bars, mutated_future


def run_to(datasets, t):
    s = HistoricalSession(datasets)
    s.command("order", instrument=s.instruments[0], side="buy", quantity=7)
    s.command("step", count=t - 1)
    s.command(
        "order",
        instrument=s.instruments[0],
        side="sell",
        quantity=2,
        order_type="limit",
        price="99",
    )
    s.command("step")
    s.command(
        "order",
        instrument=s.instruments[0],
        side="buy",
        quantity=1,
        order_type="limit",
        price="1",
    )
    return s


@pytest.mark.parametrize("t", [3, 15, 32, 50])
@pytest.mark.parametrize("pair", [False, True])
@pytest.mark.parametrize("variant", [0, 1, 2])
def test_all_future_records_mutated_every_public_surface_identical(t, pair, variant):
    ds = fixtures(80)[: 2 if pair else 1]
    altered = tuple(mutated_future(d, t, variant) for d in ds)
    assert all(a.fingerprint != b.fingerprint for a, b in zip(ds, altered, strict=True))
    a, b = run_to(ds, t), run_to(altered, t)
    sa, sb = a.public(), b.public()
    assert digest(sa) == digest(sb)  # chart, prices, orders, account, signal and VaR
    assert a.actions == b.actions
    if pair and t >= 32:
        assert sa["signal"]["available"]
    assert sa["risk"]["available"]
    for concept in (
        "current_price",
        "vwap",
        "var",
        "expected_shortfall",
        "z_score",
        "regression",
        "pnl",
    ):
        assert explain(sa, concept) == explain(sb, concept)
    assert what_if(sa, "position_risk", {"quantity": 9}) == what_if(
        sb, "position_risk", {"quantity": 9}
    )
    ca, cb = Controller(), Controller()
    qa, qb = EnvironmentTutor(ca.learning), EnvironmentTutor(cb.learning)
    assert qa.ask(sa) == qb.ask(sb)
    assert qa.ask(sa, "vwap") == qb.ask(sb, "vwap")
    # The tape and public decisions remain identical even when subsequent marks diverge.
    assert [f["index"] for f in sa["fills"]] == [f["index"] for f in sb["fills"]]
    assert all(len(v) == t + 1 for v in sa["observations"].values())
    assert "fingerprint" not in json.dumps(sa["environment"])
    assert not sa["provenance"][0]["dataset_fingerprint"]


def test_chart_payload_bounded_and_whatif_uses_same_250_return_window():
    s = HistoricalSession(fixtures(350))
    s.command("step", count=200)
    s.command("step", count=120)
    p = s.public()
    assert all(len(v) == 300 for v in p["observations"].values())
    assert p["risk"]["lookback_returns"] == 250
    h = what_if(p, "position_risk", {"quantity": 0})
    assert h["result"]["after"]["var"] == p["risk"]["var"] == 0
    assert len(p["path"]) <= 300


@pytest.mark.parametrize(
    "concept",
    [
        "bid",
        "ask",
        "spread",
        "depth",
        "queue_priority",
        "delta",
        "gamma",
        "vega",
        "implied_volatility",
        "option_pricing",
        "markouts",
        "covariance",
        "portfolio_variance",
        "stress_testing",
    ],
)
def test_bars_do_not_invent_quotes_options_or_uncomputed_risk(concept):
    p = HistoricalSession([bars()]).public()
    out = explain(p, concept)
    assert out["current"]["value"] is None
    assert not p["capabilities"]["options"] and not p["capabilities"]["quotes"]


def test_recorded_explanation_observes_does_not_invent_latent_cause():
    s = HistoricalSession([bars(data_kind="recorded", source="User supplied demo provenance")])
    old = s.public()
    s.command("step")
    x = explain(s.public(), "current_price", previous=old)
    assert x["source"]["environment"] == "historical"
    assert "does not establish why" in x["current"]["note"]
    assert "latent" not in json.dumps(x).lower()
    assert x["change"]["available"]
    assert x["current"]["value"][0]["close"] == 101


def test_risk_whatif_does_not_mutate_accounts_rng_journals_or_learning():
    c = Controller()
    h = c.environments
    h.command({"kind": "fixture"})
    h.choose("HISTORICAL", dataset_ids=["dataset-1"])
    h.act("step", count=5)
    before = (
        copy.deepcopy(h.state()),
        copy.deepcopy(h.active.actions),
        copy.deepcopy(c.learning.tutor.progress.data),
    )
    x = c.explanations.what_if("position_risk", inputs={"quantity": 10})
    assert x["result"]["after"]["var"] > 0
    assert (h.state(), h.active.actions, c.learning.tutor.progress.data) == before
    with pytest.raises(ValueError):
        h.explain("current_price", source="synthetic")
    with pytest.raises(ValueError):
        h.explain("current_price", mode="observer", reveal=True)


def test_tutor_existing_grader_only_explicit_answer_and_stale_guard():
    c = Controller()
    h = c.environments
    h.command({"kind": "fixture"})
    h.choose("HISTORICAL", dataset_ids=["dataset-1"])
    h.act("order", instrument="FIXTURE-X", side="buy", quantity=5)
    h.act("step")
    q = h.tutor.ask(h.state(), "vwap")["current"]
    assert q["question"]["answer_type"] == "number" and "expected" not in q["question"]
    correct = str(h.active.orders[-1]["vwap"])
    out = h.tutor.answer(h.state(), q["id"], correct)
    assert out["current"]["closed"] and "Correct" in out["current"]["feedback"]
    with pytest.raises(ValueError):
        h.tutor.answer(h.state(), q["id"], correct)
    q = h.tutor.ask(h.state())["current"]
    h.act("step")
    with pytest.raises(ValueError, match="context changed"):
        h.tutor.answer(h.state(), q["id"], "supported")


def test_public_returned_dicts_do_not_alias_live_state():
    s = HistoricalSession([bars()])
    s.command("order", instrument=s.instruments[0], side="buy", quantity=1)
    s.command("step")
    s.command("end")
    before = digest(s.public())
    p = s.public()
    p["last_result"]["message"] = "edited"
    p["summary"]["worst_execution"]["price"] = 1
    p["orders"][0]["fills"][0]["price"] = 2
    assert digest(s.public()) == before
    from quantlab.environments.scenarios import ScenarioSession

    a = ScenarioSession("normal")
    before = digest(a.public())
    p = a.public()
    p["last_result"]["message"] = "edited"
    p["core"]["account"]["position"] = 999
    assert digest(a.public()) == before
