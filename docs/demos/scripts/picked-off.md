# Getting picked off

SYNTHETIC

## SETUP

A stale attractive quote can be selected by better-informed flow.

{"scenario": "controlled synthetic information experiment", "seed": 140042}

Initial hedge branch: full. All result numbers below originate in the existing Python engines.

## The next public market update

### WHAT USER DOES

Advance to the next public event

### WHAT QUANTLAB SHOWS

The public tape records an execution at a resting quote. A participant's identity or private motive cannot be inferred from this fill alone.

```json
{
  "time_us": 14236,
  "best_bid": "100.04000",
  "best_ask": "100.05000",
  "last_price": "100.05000",
  "account": {
    "cash": "10100.04900",
    "position": -1,
    "average_entry": "100.05000",
    "realised": "-0.00100",
    "unrealised": "0.00000",
    "total_pnl": "-0.00100",
    "fees": "0.00100",
    "exposure": "-100.05000",
    "position_limit": 50,
    "drawdown": "0.00100",
    "max_drawdown": "0.00100",
    "buy_capacity": 51,
    "sell_capacity": 47
  },
  "orders": [
    {
      "order_id": "user-1",
      "time_us": 0,
      "side": "sell",
      "type": "limit",
      "price": "100.05000",
      "original": 3,
      "filled": 1,
      "remaining": 2,
      "cancelled": 0,
      "status": "partial · resting",
      "vwap": "100.05000",
      "vwap_exact_ticks": "10005",
      "fills": [
        {
          "order_id": "user-1",
          "trade_id": 1,
          "time_us": 14236,
          "side": "sell",
          "quantity": 1,
          "role": "provider",
          "price": "100.05000",
          "fee": "0.00100"
        }
      ]
    }
  ],
  "markouts": [
    {
      "trade_id": 1,
      "role": "provider",
      "horizon": 1,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 1,
      "role": "provider",
      "horizon": 5,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 1,
      "role": "provider",
      "horizon": 20,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    }
  ]
}
```

### KEY EXPLANATION

A signed comparison between an execution price and a later public reference.

Only markouts already present at this public point are available. Positive favours your side; negative opposes it. A pending horizon is not zero and does not reveal a later price.

### MATHS

M = s (R_h − P)

### REAL-FINANCE USE

Liquidity provision and execution-quality review; public outcomes alone do not identify private information.

Capture states: picked-off-before-fill, picked-off-after-event

## The next public market update

### WHAT USER DOES

Advance to the next public event

### WHAT QUANTLAB SHOWS

The public tape records an execution at a resting quote. A participant's identity or private motive cannot be inferred from this fill alone.

```json
{
  "time_us": 263578,
  "best_bid": "100.04000",
  "best_ask": "100.05000",
  "last_price": "100.05000",
  "account": {
    "cash": "10200.09800",
    "position": -2,
    "average_entry": "100.05000",
    "realised": "-0.00200",
    "unrealised": "0.00000",
    "total_pnl": "-0.00200",
    "fees": "0.00200",
    "exposure": "-200.10000",
    "position_limit": 50,
    "drawdown": "0.00200",
    "max_drawdown": "0.00200",
    "buy_capacity": 52,
    "sell_capacity": 47
  },
  "orders": [
    {
      "order_id": "user-1",
      "time_us": 0,
      "side": "sell",
      "type": "limit",
      "price": "100.05000",
      "original": 3,
      "filled": 2,
      "remaining": 1,
      "cancelled": 0,
      "status": "partial · resting",
      "vwap": "100.05000",
      "vwap_exact_ticks": "10005",
      "fills": [
        {
          "order_id": "user-1",
          "trade_id": 1,
          "time_us": 14236,
          "side": "sell",
          "quantity": 1,
          "role": "provider",
          "price": "100.05000",
          "fee": "0.00100"
        },
        {
          "order_id": "user-1",
          "trade_id": 2,
          "time_us": 263578,
          "side": "sell",
          "quantity": 1,
          "role": "provider",
          "price": "100.05000",
          "fee": "0.00100"
        }
      ]
    }
  ],
  "markouts": [
    {
      "trade_id": 1,
      "role": "provider",
      "horizon": 1,
      "status": "matured",
      "observed_time_us": 263578,
      "value": "0.00500"
    },
    {
      "trade_id": 1,
      "role": "provider",
      "horizon": 5,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 1,
      "role": "provider",
      "horizon": 20,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 2,
      "role": "provider",
      "horizon": 1,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 2,
      "role": "provider",
      "horizon": 5,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 2,
      "role": "provider",
      "horizon": 20,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    }
  ]
}
```

### KEY EXPLANATION

A signed comparison between an execution price and a later public reference.

Only markouts already present at this public point are available. Positive favours your side; negative opposes it. A pending horizon is not zero and does not reveal a later price.

### MATHS

M = s (R_h − P)

### REAL-FINANCE USE

Liquidity provision and execution-quality review; public outcomes alone do not identify private information.

Capture states: 

## The next public market update

### WHAT USER DOES

Advance to the next public event

### WHAT QUANTLAB SHOWS

The public tape records an execution at a resting quote. A participant's identity or private motive cannot be inferred from this fill alone.

```json
{
  "time_us": 281753,
  "best_bid": "100.04000",
  "best_ask": "100.06000",
  "last_price": "100.05000",
  "account": {
    "cash": "10300.14700",
    "position": -3,
    "average_entry": "100.05000",
    "realised": "-0.00300",
    "unrealised": "0.00000",
    "total_pnl": "-0.00300",
    "fees": "0.00300",
    "exposure": "-300.15000",
    "position_limit": 50,
    "drawdown": "0.00300",
    "max_drawdown": "0.00300",
    "buy_capacity": 53,
    "sell_capacity": 47
  },
  "orders": [
    {
      "order_id": "user-1",
      "time_us": 0,
      "side": "sell",
      "type": "limit",
      "price": "100.05000",
      "original": 3,
      "filled": 3,
      "remaining": 0,
      "cancelled": 0,
      "status": "filled",
      "vwap": "100.05000",
      "vwap_exact_ticks": "10005",
      "fills": [
        {
          "order_id": "user-1",
          "trade_id": 1,
          "time_us": 14236,
          "side": "sell",
          "quantity": 1,
          "role": "provider",
          "price": "100.05000",
          "fee": "0.00100"
        },
        {
          "order_id": "user-1",
          "trade_id": 2,
          "time_us": 263578,
          "side": "sell",
          "quantity": 1,
          "role": "provider",
          "price": "100.05000",
          "fee": "0.00100"
        },
        {
          "order_id": "user-1",
          "trade_id": 3,
          "time_us": 281753,
          "side": "sell",
          "quantity": 1,
          "role": "provider",
          "price": "100.05000",
          "fee": "0.00100"
        }
      ]
    }
  ],
  "markouts": [
    {
      "trade_id": 1,
      "role": "provider",
      "horizon": 1,
      "status": "matured",
      "observed_time_us": 263578,
      "value": "0.00500"
    },
    {
      "trade_id": 1,
      "role": "provider",
      "horizon": 5,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 1,
      "role": "provider",
      "horizon": 20,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 2,
      "role": "provider",
      "horizon": 1,
      "status": "matured",
      "observed_time_us": 281753,
      "value": "0.00000"
    },
    {
      "trade_id": 2,
      "role": "provider",
      "horizon": 5,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 2,
      "role": "provider",
      "horizon": 20,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 3,
      "role": "provider",
      "horizon": 1,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 3,
      "role": "provider",
      "horizon": 5,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 3,
      "role": "provider",
      "horizon": 20,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    }
  ]
}
```

### KEY EXPLANATION

A signed comparison between an execution price and a later public reference.

Only markouts already present at this public point are available. Positive favours your side; negative opposes it. A pending horizon is not zero and does not reveal a later price.

### MATHS

M = s (R_h − P)

### REAL-FINANCE USE

Liquidity provision and execution-quality review; public outcomes alone do not identify private information.

Capture states: 

## The next public market update

### WHAT USER DOES

Advance to the next public event

### WHAT QUANTLAB SHOWS

The public tape records an execution at a resting quote. A participant's identity or private motive cannot be inferred from this fill alone.

```json
{
  "time_us": 816519,
  "best_bid": "100.04000",
  "best_ask": "100.06000",
  "last_price": "100.04000",
  "account": {
    "cash": "10300.14700",
    "position": -3,
    "average_entry": "100.05000",
    "realised": "-0.00300",
    "unrealised": "0.00000",
    "total_pnl": "-0.00300",
    "fees": "0.00300",
    "exposure": "-300.15000",
    "position_limit": 50,
    "drawdown": "0.00300",
    "max_drawdown": "0.00300",
    "buy_capacity": 53,
    "sell_capacity": 47
  },
  "orders": [
    {
      "order_id": "user-1",
      "time_us": 0,
      "side": "sell",
      "type": "limit",
      "price": "100.05000",
      "original": 3,
      "filled": 3,
      "remaining": 0,
      "cancelled": 0,
      "status": "filled",
      "vwap": "100.05000",
      "vwap_exact_ticks": "10005",
      "fills": [
        {
          "order_id": "user-1",
          "trade_id": 1,
          "time_us": 14236,
          "side": "sell",
          "quantity": 1,
          "role": "provider",
          "price": "100.05000",
          "fee": "0.00100"
        },
        {
          "order_id": "user-1",
          "trade_id": 2,
          "time_us": 263578,
          "side": "sell",
          "quantity": 1,
          "role": "provider",
          "price": "100.05000",
          "fee": "0.00100"
        },
        {
          "order_id": "user-1",
          "trade_id": 3,
          "time_us": 281753,
          "side": "sell",
          "quantity": 1,
          "role": "provider",
          "price": "100.05000",
          "fee": "0.00100"
        }
      ]
    }
  ],
  "markouts": [
    {
      "trade_id": 1,
      "role": "provider",
      "horizon": 1,
      "status": "matured",
      "observed_time_us": 263578,
      "value": "0.00500"
    },
    {
      "trade_id": 1,
      "role": "provider",
      "horizon": 5,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 1,
      "role": "provider",
      "horizon": 20,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 2,
      "role": "provider",
      "horizon": 1,
      "status": "matured",
      "observed_time_us": 281753,
      "value": "0.00000"
    },
    {
      "trade_id": 2,
      "role": "provider",
      "horizon": 5,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 2,
      "role": "provider",
      "horizon": 20,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 3,
      "role": "provider",
      "horizon": 1,
      "status": "matured",
      "observed_time_us": 816519,
      "value": "0.00000"
    },
    {
      "trade_id": 3,
      "role": "provider",
      "horizon": 5,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 3,
      "role": "provider",
      "horizon": 20,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    }
  ]
}
```

### KEY EXPLANATION

A signed comparison between an execution price and a later public reference.

Only markouts already present at this public point are available. Positive favours your side; negative opposes it. A pending horizon is not zero and does not reveal a later price.

### MATHS

M = s (R_h − P)

### REAL-FINANCE USE

Liquidity provision and execution-quality review; public outcomes alone do not identify private information.

Capture states: 

## The next public market update

### WHAT USER DOES

Advance to the next public event

### WHAT QUANTLAB SHOWS

The public tape records an execution at a resting quote. A participant's identity or private motive cannot be inferred from this fill alone.

```json
{
  "time_us": 1207278,
  "best_bid": "100.04000",
  "best_ask": "100.06000",
  "last_price": "100.06000",
  "account": {
    "cash": "10300.14700",
    "position": -3,
    "average_entry": "100.05000",
    "realised": "-0.00300",
    "unrealised": "0.00000",
    "total_pnl": "-0.00300",
    "fees": "0.00300",
    "exposure": "-300.15000",
    "position_limit": 50,
    "drawdown": "0.00300",
    "max_drawdown": "0.00300",
    "buy_capacity": 53,
    "sell_capacity": 47
  },
  "orders": [
    {
      "order_id": "user-1",
      "time_us": 0,
      "side": "sell",
      "type": "limit",
      "price": "100.05000",
      "original": 3,
      "filled": 3,
      "remaining": 0,
      "cancelled": 0,
      "status": "filled",
      "vwap": "100.05000",
      "vwap_exact_ticks": "10005",
      "fills": [
        {
          "order_id": "user-1",
          "trade_id": 1,
          "time_us": 14236,
          "side": "sell",
          "quantity": 1,
          "role": "provider",
          "price": "100.05000",
          "fee": "0.00100"
        },
        {
          "order_id": "user-1",
          "trade_id": 2,
          "time_us": 263578,
          "side": "sell",
          "quantity": 1,
          "role": "provider",
          "price": "100.05000",
          "fee": "0.00100"
        },
        {
          "order_id": "user-1",
          "trade_id": 3,
          "time_us": 281753,
          "side": "sell",
          "quantity": 1,
          "role": "provider",
          "price": "100.05000",
          "fee": "0.00100"
        }
      ]
    }
  ],
  "markouts": [
    {
      "trade_id": 1,
      "role": "provider",
      "horizon": 1,
      "status": "matured",
      "observed_time_us": 263578,
      "value": "0.00500"
    },
    {
      "trade_id": 1,
      "role": "provider",
      "horizon": 5,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 1,
      "role": "provider",
      "horizon": 20,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 2,
      "role": "provider",
      "horizon": 1,
      "status": "matured",
      "observed_time_us": 281753,
      "value": "0.00000"
    },
    {
      "trade_id": 2,
      "role": "provider",
      "horizon": 5,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 2,
      "role": "provider",
      "horizon": 20,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 3,
      "role": "provider",
      "horizon": 1,
      "status": "matured",
      "observed_time_us": 816519,
      "value": "0.00000"
    },
    {
      "trade_id": 3,
      "role": "provider",
      "horizon": 5,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 3,
      "role": "provider",
      "horizon": 20,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    }
  ]
}
```

### KEY EXPLANATION

A signed comparison between an execution price and a later public reference.

Only markouts already present at this public point are available. Positive favours your side; negative opposes it. A pending horizon is not zero and does not reveal a later price.

### MATHS

M = s (R_h − P)

### REAL-FINANCE USE

Liquidity provision and execution-quality review; public outcomes alone do not identify private information.

Capture states: 

## The next public market update

### WHAT USER DOES

Advance to the next public event

### WHAT QUANTLAB SHOWS

The public tape records an execution at a resting quote. A participant's identity or private motive cannot be inferred from this fill alone.

```json
{
  "time_us": 4973931,
  "best_bid": "100.04000",
  "best_ask": "100.06000",
  "last_price": "100.06000",
  "account": {
    "cash": "10300.14700",
    "position": -3,
    "average_entry": "100.05000",
    "realised": "-0.00300",
    "unrealised": "0.00000",
    "total_pnl": "-0.00300",
    "fees": "0.00300",
    "exposure": "-300.15000",
    "position_limit": 50,
    "drawdown": "0.00300",
    "max_drawdown": "0.00300",
    "buy_capacity": 53,
    "sell_capacity": 47
  },
  "orders": [
    {
      "order_id": "user-1",
      "time_us": 0,
      "side": "sell",
      "type": "limit",
      "price": "100.05000",
      "original": 3,
      "filled": 3,
      "remaining": 0,
      "cancelled": 0,
      "status": "filled",
      "vwap": "100.05000",
      "vwap_exact_ticks": "10005",
      "fills": [
        {
          "order_id": "user-1",
          "trade_id": 1,
          "time_us": 14236,
          "side": "sell",
          "quantity": 1,
          "role": "provider",
          "price": "100.05000",
          "fee": "0.00100"
        },
        {
          "order_id": "user-1",
          "trade_id": 2,
          "time_us": 263578,
          "side": "sell",
          "quantity": 1,
          "role": "provider",
          "price": "100.05000",
          "fee": "0.00100"
        },
        {
          "order_id": "user-1",
          "trade_id": 3,
          "time_us": 281753,
          "side": "sell",
          "quantity": 1,
          "role": "provider",
          "price": "100.05000",
          "fee": "0.00100"
        }
      ]
    }
  ],
  "markouts": [
    {
      "trade_id": 1,
      "role": "provider",
      "horizon": 1,
      "status": "matured",
      "observed_time_us": 263578,
      "value": "0.00500"
    },
    {
      "trade_id": 1,
      "role": "provider",
      "horizon": 5,
      "status": "matured",
      "observed_time_us": 1849653,
      "value": "0.00000"
    },
    {
      "trade_id": 1,
      "role": "provider",
      "horizon": 20,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 2,
      "role": "provider",
      "horizon": 1,
      "status": "matured",
      "observed_time_us": 281753,
      "value": "0.00000"
    },
    {
      "trade_id": 2,
      "role": "provider",
      "horizon": 5,
      "status": "matured",
      "observed_time_us": 1971777,
      "value": "0.00000"
    },
    {
      "trade_id": 2,
      "role": "provider",
      "horizon": 20,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    },
    {
      "trade_id": 3,
      "role": "provider",
      "horizon": 1,
      "status": "matured",
      "observed_time_us": 816519,
      "value": "0.00000"
    },
    {
      "trade_id": 3,
      "role": "provider",
      "horizon": 5,
      "status": "matured",
      "observed_time_us": 2244269,
      "value": "0.00000"
    },
    {
      "trade_id": 3,
      "role": "provider",
      "horizon": 20,
      "status": "pending",
      "observed_time_us": null,
      "value": null
    }
  ]
}
```

### KEY EXPLANATION

A signed comparison between an execution price and a later public reference.

Only markouts already present at this public point are available. Positive favours your side; negative opposes it. A pending horizon is not zero and does not reveal a later price.

### MATHS

M = s (R_h − P)

### REAL-FINANCE USE

Liquidity provision and execution-quality review; public outcomes alone do not identify private information.

Capture states: 

## LIMITATIONS

- One synthetic venue with immediate order arrival, finite depth and no communication latency.
- P&L uses a public mark. Marked gains do not establish decision quality or guarantee liquidation.
- The stale-quote setup deliberately starts with a model value different from public quotes. Its value and noisy signals are revealed only in explicit ended-demo hindsight.
- A negative provider markout can occur without informed trading. Observer latent and public midpoint references are different diagnostics, not realised P&L.

## HOW QUANTLAB DIFFERS FROM PRODUCTION

Educational single-machine models omit real venue latency, operational controls and much market complexity. A replay fingerprint verifies reproducibility; it does not validate a real-world investment conclusion.

## EVIDENCE

{"adapter": "picked_off", "engine_result_digest": "c71f58f4b189e79894acd37663aabead59f59d53d0c082b44fce8f5d22881f1e", "journal_digest": "235a13d28cada914f013ab459d48bf8feb30e855b148dd10407ccec3d2680e47", "note": "Derived from the existing engines; configuration chosen before outcomes."}
