"""Registry contracts protect broken navigation, pedagogy and information labels."""

import copy

import pytest

from quantlab.explainability.registry import (
    ASSUMPTIONS,
    CHAINS,
    CONCEPTS,
    DEPTHS,
    FORMULAS,
    LAB_CONCEPTS,
    PREREQUISITES,
    graph,
    resolve,
    search,
)


@pytest.mark.parametrize("key", tuple(CONCEPTS))
def test_registry_concept_is_complete_and_links_resolve(key):
    c = CONCEPTS[key].public()
    assert c["id"] == key and c["name"] and c["definition"] and c["matters"]
    assert c["depths"] == list(DEPTHS)
    for relation in ("related", "prerequisites", "affected_by", "affects"):
        assert all(x in CONCEPTS and x != key for x in c[relation])
    assert all(a in ASSUMPTIONS for a in c["assumptions"])
    assert c["uses"] and c["limitation"] and c["interview"]
    assert c["locations"]
    if c["maths"]["equation"]:
        assert c["maths"]["variables"]
        assert all(symbol and meaning for symbol, meaning in c["maths"]["variables"].items())
    assert "obviously" not in str(c).lower()
    assert "trivially" not in str(c).lower()


def test_prerequisites_are_acyclic_but_dependencies_are_typed_not_causal_proof():
    visited = set()

    def visit(key, path):
        assert key not in path
        if key in visited:
            return
        for parent in PREREQUISITES.get(key, ()):
            visit(parent, path | {key})
        visited.add(key)

    for key in CONCEPTS:
        visit(key, set())
    assert visited == CONCEPTS.keys()
    for i, chain in enumerate(CHAINS):
        g = graph(i)
        assert [n["id"] for n in g["nodes"]] == list(chain)
        assert all("not real-world causation" in e["relation"] for e in g["edges"])


def test_each_lab_has_learning_coverage_and_required_domains_exist():
    for lab, ids in LAB_CONCEPTS.items():
        assert 10 <= len(ids) <= 20
        assert len(ids) == len(set(ids))
        assert all(lab in {x["lab"] for x in CONCEPTS[k].public()["locations"]} for k in ids)
    assert len({c.domain for c in CONCEPTS.values()}) == 12


@pytest.mark.parametrize(
    "query,expected",
    [
        ("VWAP", "vwap"),
        ("Why did VaR rise?", "var"),
        ("gamma", "gamma"),
        ("look-ahead bias", "lookahead_bias"),
        ("what does correlation affect?", "correlation"),
        ("P&L", "pnl_attribution"),
        ("beta", "regression_beta"),
        ("IV", "implied_volatility"),
    ],
)
def test_search_matches_questions_and_aliases(query, expected):
    assert search(query)[0]["id"] == expected


def test_search_bounds_and_detached_registry():
    assert search("unrecognisableword") == []
    with pytest.raises(ValueError):
        search("x" * 201)
    with pytest.raises(ValueError):
        search(lab="missing")
    with pytest.raises(ValueError):
        resolve("../secret")
    with pytest.raises(ValueError):
        graph(-1)
    a = copy.deepcopy(CONCEPTS["vwap"].public())
    a["related"].clear()
    assert CONCEPTS["vwap"].public()["related"]


def test_mathematical_high_risk_units_and_soft_inventory_regime_are_explicit():
    assert "excess" in FORMULAS["quote_skew"][0]
    assert "hard" in FORMULAS["quote_skew"][1]
    assert "per 1.0" in FORMULAS["vega"][1]["ν"]
    assert "already includes" in FORMULAS["pnl_attribution"][1]["fees"]
    assert "excluded" in FORMULAS["z_score"][1]["t"]
