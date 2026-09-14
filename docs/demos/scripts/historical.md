# Historical replay: what is real and what is simulated

SIMULATED HISTORICAL EXECUTION · ARTIFICIAL FIXTURE

## SETUP

It separates real data from simulated fills and prevents decisions using unseen bars.

{"fixture": "Phase 13 fixture_inputs; 100 bars"}

Initial hedge branch: full. All result numbers below originate in the existing Python engines.

## An observation and a paper order

### WHAT USER DOES

Submit a BUY 3 MARKET instruction for FIXTURE-X

### WHAT QUANTLAB SHOWS

Compare the recorded result with the inputs available before the action.

```json
{
  "index": 0,
  "timestamp": "2020-01-02T09:30:00+00:00",
  "account": {
    "positions": [],
    "cash": 10000.0,
    "market_value": 0,
    "equity": 10000.0,
    "initial_capital": 10000.0,
    "realised_gross": 0.0,
    "unrealised": 0.0,
    "fees": 0.0,
    "financing": 0,
    "pnl": 0.0,
    "drawdown": 0.0,
    "long": 0,
    "short": 0,
    "gross": 0,
    "net": 0,
    "delta_gbp": 0,
    "gross_delta_gbp": 0,
    "factors": {},
    "greeks": {
      "delta": 0,
      "gamma": 0,
      "vega": 0,
      "theta": 0,
      "rho": 0
    },
    "largest_position_share": 0,
    "largest_delta_share": 0,
    "hhi": 0,
    "max_position": 0,
    "source": "Simulated account over revealed imported observations"
  },
  "orders": [
    {
      "order_id": "paper-1",
      "instrument": "FIXTURE-X",
      "side": "buy",
      "type": "market",
      "price": null,
      "original": 3,
      "filled": 0,
      "remaining": 3,
      "cancelled": 0,
      "submitted_index": 0,
      "status": "waiting for next observation",
      "vwap": null,
      "fills": []
    }
  ],
  "fills": [],
  "risk": {
    "available": false,
    "var": null,
    "es": null,
    "reason": "Need at least two revealed returns",
    "label": "LIVE REPLAY RISK ESTIMATE"
  }
}
```

### KEY EXPLANATION

Recorded observations are revealed progressively while paper orders follow an explicit execution rule.

These are artificial test bars, not real market history. The same time-causal replay rules apply.

### MATHS

This concept is a mechanism or interpretation, not a standalone formula.

### REAL-FINANCE USE

Auditable trading and research software, incident reproduction and model governance.

Capture states: historical-before-order

## Reveal the next observation

### WHAT USER DOES

Advance one bar; apply the documented paper execution rule

### WHAT QUANTLAB SHOWS

The next recorded fixture close is an input. The paper fill adds configured slippage, uses a volume cap and books fees. No real historical fill or hidden cause is established.

```json
{
  "index": 1,
  "timestamp": "2020-01-02T09:31:00+00:00",
  "account": {
    "positions": [
      {
        "instrument": "FIXTURE-X",
        "underlying": "FIXTURE-X",
        "quantity": 3,
        "multiplier": 1,
        "mark": 99.63,
        "spot": 99.63,
        "kind": "stock",
        "strike": 0,
        "years": 0,
        "volatility": 0,
        "rate": 0,
        "dividend": 0,
        "value": 298.89,
        "greeks": {
          "delta": 3.0,
          "gamma": 0.0,
          "vega": 0.0,
          "theta": 0.0,
          "rho": 0.0
        },
        "delta_gbp": 298.89,
        "value_share": 1.0,
        "delta_share": 1.0
      }
    ],
    "cash": 9701.077,
    "market_value": 298.89,
    "equity": 9999.966999999999,
    "initial_capital": 10000.0,
    "realised_gross": 0.0,
    "unrealised": -0.03,
    "fees": 0.003,
    "financing": 0,
    "pnl": -0.03300000000126602,
    "drawdown": 0.033,
    "long": 298.89,
    "short": 0,
    "gross": 298.89,
    "net": 298.89,
    "delta_gbp": 298.89,
    "gross_delta_gbp": 298.89,
    "factors": {
      "FIXTURE-X": {
        "spot": 99.63,
        "delta": 3.0,
        "gamma": 0.0,
        "vega": 0.0,
        "theta": 0.0,
        "rho": 0.0
      }
    },
    "greeks": {
      "delta": 3.0,
      "gamma": 0.0,
      "vega": 0.0,
      "theta": 0.0,
      "rho": 0.0
    },
    "largest_position_share": 1.0,
    "largest_delta_share": 1.0,
    "hhi": 1.0,
    "max_position": 3,
    "source": "Simulated account over revealed imported observations"
  },
  "orders": [
    {
      "order_id": "paper-1",
      "instrument": "FIXTURE-X",
      "side": "buy",
      "type": "market",
      "price": null,
      "original": 3,
      "filled": 3,
      "remaining": 0,
      "cancelled": 0,
      "submitted_index": 0,
      "status": "filled",
      "vwap": 99.64,
      "fills": [
        {
          "trade_id": 1,
          "order_id": "paper-1",
          "instrument": "FIXTURE-X",
          "side": "buy",
          "quantity": 3,
          "price": 99.64,
          "exact_price": "99.64",
          "fee": 0.003,
          "reference": 99.63,
          "timestamp": "2020-01-02T09:31:00+00:00",
          "time_us": 1577957460000000,
          "index": 1,
          "execution_model": "bar-next-close-v1",
          "evidence": "SIMULATED HISTORICAL EXECUTION"
        }
      ]
    }
  ],
  "fills": [
    {
      "trade_id": 1,
      "order_id": "paper-1",
      "instrument": "FIXTURE-X",
      "side": "buy",
      "quantity": 3,
      "price": 99.64,
      "exact_price": "99.64",
      "fee": 0.003,
      "reference": 99.63,
      "timestamp": "2020-01-02T09:31:00+00:00",
      "time_us": 1577957460000000,
      "index": 1,
      "execution_model": "bar-next-close-v1",
      "evidence": "SIMULATED HISTORICAL EXECUTION"
    }
  ],
  "risk": {
    "available": false,
    "var": null,
    "es": null,
    "reason": "Need at least two revealed returns",
    "label": "LIVE REPLAY RISK ESTIMATE"
  }
}
```

### KEY EXPLANATION

An average execution price that gives larger fills more weight.

SIMULATED EXECUTION ON HISTORICAL DATA: next revealed close, adverse tick slippage, shared volume participation and explicit fees. High/low does not trigger fills; no historical queue or observed order book is inferred.

### MATHS

VWAP = Σᵢ(Pᵢ Qᵢ) / ΣᵢQᵢ

### REAL-FINANCE USE

Order handling, execution analysis and transaction-cost analysis; live venues have additional fees, latency and order types.

Capture states: historical-after-paper-fill

## LIMITATIONS

- ARTIFICIAL TEST FIXTURE, not actual historical market data.
- SIMULATED HISTORICAL EXECUTION: next revealed close, adverse tick, shared volume cap and fees; OHLC contains no queue truth.
- Recorded movements alone do not establish why a real market moved.

## HOW QUANTLAB DIFFERS FROM PRODUCTION

Educational single-machine models omit real venue latency, operational controls and much market complexity. A replay fingerprint verifies reproducibility; it does not validate a real-world investment conclusion.

## EVIDENCE

{"adapter": "historical", "engine_result_digest": "1eae5c6da22b97e039d250d0becbefc8789e49de250ac4e4678993e9fcbd4f48", "journal_digest": "05a46fb41568c0c212f6468b669607a66d4c638df585bee1f6ad729d23d8154a", "note": "Derived from the existing engines; configuration chosen before outcomes."}
