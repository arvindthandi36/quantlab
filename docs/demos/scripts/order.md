# How an order becomes a trade

SYNTHETIC

## SETUP

It prioritises immediacy over a chosen price; large sizes may sweep levels.

{"branch": "full", "scenario": "predeclared finite book", "seed": 140042}

Initial hedge branch: full. All result numbers below originate in the existing Python engines.

## A buy order meets finite depth

### WHAT USER DOES

Submit BUY 10 MARKET

### WHAT QUANTLAB SHOWS

Each fill is priced at the resting seller's quote. The order's executed VWAP weights those actual prices by units; fees are booked separately.

```json
{
  "time_us": 0,
  "best_bid": "99.99000",
  "best_ask": "100.04000",
  "last_price": "100.04000",
  "account": {
    "cash": "8999.76000",
    "position": 10,
    "average_entry": "100.02300",
    "realised": "-0.01000",
    "unrealised": "-0.08000",
    "total_pnl": "-0.09000",
    "fees": "0.01000",
    "exposure": "1000.15000",
    "position_limit": 50,
    "drawdown": "0.09000",
    "max_drawdown": "0.09000",
    "buy_capacity": 40,
    "sell_capacity": 60
  },
  "orders": [
    {
      "order_id": "user-1",
      "time_us": 0,
      "side": "buy",
      "type": "market",
      "price": null,
      "original": 10,
      "filled": 10,
      "remaining": 0,
      "cancelled": 0,
      "status": "filled",
      "vwap": "100.02300",
      "vwap_exact_ticks": "100023/10",
      "fills": [
        {
          "order_id": "user-1",
          "trade_id": 1,
          "time_us": 0,
          "side": "buy",
          "quantity": 3,
          "role": "aggressor",
          "price": "100.01000",
          "fee": "0.00300"
        },
        {
          "order_id": "user-1",
          "trade_id": 2,
          "time_us": 0,
          "side": "buy",
          "quantity": 4,
          "role": "aggressor",
          "price": "100.02000",
          "fee": "0.00400"
        },
        {
          "order_id": "user-1",
          "trade_id": 3,
          "time_us": 0,
          "side": "buy",
          "quantity": 3,
          "role": "aggressor",
          "price": "100.04000",
          "fee": "0.00300"
        }
      ]
    }
  ],
  "markouts": [
    {
      "trade_id": 1,
      "role": "aggressor",
      "horizon": 1,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 1,
      "role": "aggressor",
      "horizon": 5,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 1,
      "role": "aggressor",
      "horizon": 20,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 2,
      "role": "aggressor",
      "horizon": 1,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 2,
      "role": "aggressor",
      "horizon": 5,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 2,
      "role": "aggressor",
      "horizon": 20,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 3,
      "role": "aggressor",
      "horizon": 1,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 3,
      "role": "aggressor",
      "horizon": 5,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 3,
      "role": "aggressor",
      "horizon": 20,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    }
  ]
}
```

### KEY EXPLANATION

An average execution price that gives larger fills more weight.

Calculated from these recorded fills using the same execution calculation as the order book. Larger fills receive more weight. Display is rounded to five decimal places; the exact fraction is retained.

### MATHS

VWAP = Σᵢ(Pᵢ Qᵢ) / ΣᵢQᵢ

### REAL-FINANCE USE

Order handling, execution analysis and transaction-cost analysis; live venues have additional fees, latency and order types.

Capture states: order-before-submit, order-after-multifill

## LIMITATIONS

- One synthetic venue with immediate order arrival, finite depth and no communication latency.
- P&L uses a public mark. Marked gains do not establish decision quality or guarantee liquidation.

## HOW QUANTLAB DIFFERS FROM PRODUCTION

Educational single-machine models omit real venue latency, operational controls and much market complexity. A replay fingerprint verifies reproducibility; it does not validate a real-world investment conclusion.

## EVIDENCE

{"adapter": "order", "engine_result_digest": "5e0d6b07621450060501f661b9898474e8f90de16bd5e41a2dbb78bc19dc44bf", "journal_digest": "2cbe8ce021aa2beecd572515f30c0dfe29f3bd4e47e2df6dd6130704875df997", "note": "Derived from the existing engines; configuration chosen before outcomes."}
