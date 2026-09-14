# Delta hedging

SYNTHETIC

## SETUP

It supports quotes, Greeks and risk revaluation.

{"initial_hedge": "full", "options": {"curvature": 0.25, "dividend_yield": 0.0, "expiries_days": [30.0, 60.0], "implied_volatility": 0.2, "multiplier": 100, "option_fee": 0.05, "option_half_spread": 0.015, "physical_drift": 0.0, "process_volatility": 0.2, "quote_size": 20, "rate": 0.0, "seed": 140042, "skew": -0.15, "spot": 100.0, "step_days": 1.0, "steps": 10, "stock_depth": 1000, "stock_fee": 0.001, "stock_spread_ticks": 1, "strikes": [90.0, 95.0, 100.0, 105.0, 110.0]}, "seed": 140042}

Initial hedge branch: full. All result numbers below originate in the existing Python engines.

## Own one call contract

### WHAT USER DOES

Buy one at-the-money call, multiplier 100

### WHAT QUANTLAB SHOWS

Compare the recorded result with the inputs available before the action.

```json
{
  "step": 0,
  "spot": 100.0,
  "selected": {
    "id": "QL-STOCK:call:100:6/73:x100",
    "underlying": "QL-STOCK",
    "type": "call",
    "strike": 100.0,
    "expiry_years": "6/73",
    "expiry_days": 30.0,
    "remaining_years": 0.0821917808219178,
    "remaining_days": 30.0,
    "multiplier": 100,
    "settlement": "European cash settlement",
    "revision": 2,
    "model_value": 2.2871506280449694,
    "volatility_input": 0.2,
    "bid": 2.27215,
    "ask": 2.302151,
    "midpoint": 2.2871505,
    "intrinsic": 0.0,
    "time_value": 2.2871505,
    "moneyness": "ATM",
    "bid_size": 20,
    "ask_size": 19,
    "iv": {
      "volatility": 0.19999998880003317,
      "converged": true,
      "status": "converged",
      "method": "Newton",
      "iterations": 2,
      "residual": -4.440892098500626e-15,
      "bracket": [
        0.0,
        0.2
      ],
      "newton_steps": 1,
      "bisection_steps": 0
    },
    "greeks": {
      "delta": 0.5114357531402248,
      "gamma": 0.06954844076977439,
      "vega": 11.432620400510856,
      "theta": -13.909688153954876,
      "rho": 4.015596549532399,
      "status": "analytic; volatility held fixed",
      "vega_per_vol_point": 0.11432620400510857,
      "theta_per_day": -0.038108734668369525,
      "rho_per_rate_point": 0.040155965495323985
    },
    "contract_greeks": {
      "delta": 51.143575314022485,
      "gamma": 6.954844076977438,
      "vega": 1143.2620400510857,
      "theta": -1390.9688153954876,
      "rho": 401.5596549532399,
      "status": "analytic; volatility held fixed",
      "vega_per_vol_point": 11.432620400510856,
      "theta_per_day": -3.810873466836952,
      "rho_per_rate_point": 4.015596549532399
    },
    "mechanism": "Finite synthetic dealer quote; IOC remainder cancels"
  },
  "greeks": {
    "delta": 51.143575314022485,
    "gamma": 6.954844076977438,
    "vega": 1143.2620400510857,
    "theta": -1390.9688153954876,
    "rho": 401.5596549532399,
    "option_delta": 51.143575314022485
  },
  "accounts": {
    "cash": -230.2651,
    "option_cash": -230.2651,
    "stock_cash": 0.0,
    "option_value": 228.71505,
    "stock_value": 0.0,
    "option_realised_gross": 0.0,
    "option_unrealised": -1.50005,
    "option_gross_pnl": -1.50005,
    "hedge_gross_pnl": 0.0,
    "stock_realised_gross": 0.0,
    "stock_unrealised": 0.0,
    "option_fees": 0.05,
    "stock_fees": 0.0,
    "fees": 0.05,
    "financing": 0.0,
    "total_pnl": -1.55005,
    "net_pnl": -1.55005,
    "residual_delta": 51.143575314022485,
    "gross_hedging_error": -1.50005,
    "rms_delta": 51.143575314022485,
    "absolute_residual_delta": 51.143575314022485,
    "max_absolute_delta": 51.143575314022485,
    "max_absolute_gamma": 6.954844076977438,
    "max_absolute_vega": 1143.2620400510857,
    "drawdown": 1.55005,
    "turnover": 0,
    "hedges": 0,
    "realised_volatility": null
  },
  "hedges": []
}
```

### KEY EXPLANATION

A model estimates the value of a payoff that depends on a future underlying price.

Selected-contract values are per underlying unit. Contract and portfolio sensitivities retain multipliers and signed quantities. Changes in displayed inputs are observed contributors, not an additive causal attribution.

### MATHS

This concept is a mechanism or interpretation, not a standalone formula.

### REAL-FINANCE USE

Option hedging, derivatives market making and portfolio risk; production pricing can use surfaces and richer models.

Capture states: 

## Choose your initial hedge

### WHAT USER DOES

Execute the full hedge choice through the stock book

### WHAT QUANTLAB SHOWS

Read actual stock fills, fees and resulting aggregate delta. The partial and unhedged choices deliberately retain more delta.

```json
{
  "step": 0,
  "spot": 100.0,
  "selected": {
    "id": "QL-STOCK:call:100:6/73:x100",
    "underlying": "QL-STOCK",
    "type": "call",
    "strike": 100.0,
    "expiry_years": "6/73",
    "expiry_days": 30.0,
    "remaining_years": 0.0821917808219178,
    "remaining_days": 30.0,
    "multiplier": 100,
    "settlement": "European cash settlement",
    "revision": 2,
    "model_value": 2.2871506280449694,
    "volatility_input": 0.2,
    "bid": 2.27215,
    "ask": 2.302151,
    "midpoint": 2.2871505,
    "intrinsic": 0.0,
    "time_value": 2.2871505,
    "moneyness": "ATM",
    "bid_size": 20,
    "ask_size": 19,
    "iv": {
      "volatility": 0.19999998880003317,
      "converged": true,
      "status": "converged",
      "method": "Newton",
      "iterations": 2,
      "residual": -4.440892098500626e-15,
      "bracket": [
        0.0,
        0.2
      ],
      "newton_steps": 1,
      "bisection_steps": 0
    },
    "greeks": {
      "delta": 0.5114357531402248,
      "gamma": 0.06954844076977439,
      "vega": 11.432620400510856,
      "theta": -13.909688153954876,
      "rho": 4.015596549532399,
      "status": "analytic; volatility held fixed",
      "vega_per_vol_point": 0.11432620400510857,
      "theta_per_day": -0.038108734668369525,
      "rho_per_rate_point": 0.040155965495323985
    },
    "contract_greeks": {
      "delta": 51.143575314022485,
      "gamma": 6.954844076977438,
      "vega": 1143.2620400510857,
      "theta": -1390.9688153954876,
      "rho": 401.5596549532399,
      "status": "analytic; volatility held fixed",
      "vega_per_vol_point": 11.432620400510856,
      "theta_per_day": -3.810873466836952,
      "rho_per_rate_point": 4.015596549532399
    },
    "mechanism": "Finite synthetic dealer quote; IOC remainder cancels"
  },
  "greeks": {
    "delta": 0.1435753140224847,
    "gamma": 6.954844076977438,
    "vega": 1143.2620400510857,
    "theta": -1390.9688153954876,
    "rho": 401.5596549532399,
    "option_delta": 51.143575314022485
  },
  "accounts": {
    "cash": 4869.1739,
    "option_cash": -230.2651,
    "stock_cash": 5099.439,
    "option_value": 228.71505,
    "stock_value": -5100.0,
    "option_realised_gross": 0.0,
    "option_unrealised": -1.50005,
    "option_gross_pnl": -1.50005,
    "hedge_gross_pnl": -0.51,
    "stock_realised_gross": 0.0,
    "stock_unrealised": -0.51,
    "option_fees": 0.05,
    "stock_fees": 0.051,
    "fees": 0.101,
    "financing": 0.0,
    "total_pnl": -2.11105,
    "net_pnl": -2.11105,
    "residual_delta": 0.1435753140224847,
    "gross_hedging_error": -2.01005,
    "rms_delta": 0.1435753140224847,
    "absolute_residual_delta": 0.1435753140224847,
    "max_absolute_delta": 51.143575314022485,
    "max_absolute_gamma": 6.954844076977438,
    "max_absolute_vega": 1143.2620400510857,
    "drawdown": 2.11105,
    "turnover": 51,
    "hedges": 1,
    "realised_volatility": null
  },
  "hedges": [
    {
      "step": 0,
      "side": "sell",
      "quantity": 51,
      "benchmark": true,
      "order_id": "user-1"
    }
  ]
}
```

### KEY EXPLANATION

A stock position is used to offset an option portfolio's current first-order stock sensitivity.

Selected-contract values are per underlying unit. Contract and portfolio sensitivities retain multipliers and signed quantities. Changes in displayed inputs are observed contributors, not an additive causal attribution.

### MATHS

This concept is a mechanism or interpretation, not a standalone formula.

### REAL-FINANCE USE

Option hedging, derivatives market making and portfolio risk; production pricing can use surfaces and richer models.

Capture states: delta-before-hedge, delta-after-hedge

## Move the underlying market

### WHAT USER DOES

Advance one model day

### WHAT QUANTLAB SHOWS

Gamma describes delta's sensitivity to spot; time and volatility inputs can also change delta. Use the actual before/after model values.

```json
{
  "step": 1,
  "spot": 99.73,
  "selected": {
    "id": "QL-STOCK:call:100:6/73:x100",
    "underlying": "QL-STOCK",
    "type": "call",
    "strike": 100.0,
    "expiry_years": "6/73",
    "expiry_days": 30.0,
    "remaining_years": 0.07945205479452055,
    "remaining_days": 29.0,
    "multiplier": 100,
    "settlement": "European cash settlement",
    "revision": 3,
    "model_value": 2.112358940965514,
    "volatility_input": 0.19991925593936233,
    "bid": 2.097358,
    "ask": 2.127359,
    "midpoint": 2.1123585,
    "intrinsic": 0.0,
    "time_value": 2.1123585,
    "moneyness": "OTM",
    "bid_size": 20,
    "ask_size": 20,
    "iv": {
      "volatility": 0.19991921661140993,
      "converged": true,
      "status": "converged",
      "method": "Newton",
      "iterations": 3,
      "residual": -8.881784197001252e-16,
      "bracket": [
        0.0,
        0.19991921663598936
      ],
      "newton_steps": 2,
      "bisection_steps": 0
    },
    "greeks": {
      "delta": 0.4921005446208538,
      "gamma": 0.07097279410761076,
      "vega": 11.212521826674699,
      "theta": -14.106614527402114,
      "rho": 3.7314521173920405,
      "status": "analytic; volatility held fixed",
      "vega_per_vol_point": 0.11212521826674698,
      "theta_per_day": -0.03864825897918387,
      "rho_per_rate_point": 0.0373145211739204
    },
    "contract_greeks": {
      "delta": 49.21005446208538,
      "gamma": 7.097279410761076,
      "vega": 1121.25218266747,
      "theta": -1410.6614527402114,
      "rho": 373.14521173920406,
      "status": "analytic; volatility held fixed",
      "vega_per_vol_point": 11.212521826674699,
      "theta_per_day": -3.8648258979183874,
      "rho_per_rate_point": 3.7314521173920405
    },
    "mechanism": "Finite synthetic dealer quote; IOC remainder cancels"
  },
  "greeks": {
    "delta": -1.789945537914619,
    "gamma": 7.097279410761076,
    "vega": 1121.25218266747,
    "theta": -1410.6614527402114,
    "rho": 373.14521173920406,
    "option_delta": 49.21005446208538
  },
  "accounts": {
    "cash": 4869.1739,
    "option_cash": -230.2651,
    "stock_cash": 5099.439,
    "option_value": 211.23585,
    "stock_value": -5086.23,
    "option_realised_gross": 0.0,
    "option_unrealised": -18.97925,
    "option_gross_pnl": -18.97925,
    "hedge_gross_pnl": 13.26,
    "stock_realised_gross": 0.0,
    "stock_unrealised": 13.26,
    "option_fees": 0.05,
    "stock_fees": 0.051,
    "fees": 0.101,
    "financing": 0.0,
    "total_pnl": -5.82025,
    "net_pnl": -5.82025,
    "residual_delta": -1.789945537914619,
    "gross_hedging_error": -5.719250000000001,
    "rms_delta": 0.1435753140224847,
    "absolute_residual_delta": 1.789945537914619,
    "max_absolute_delta": 51.143575314022485,
    "max_absolute_gamma": 7.097279410761076,
    "max_absolute_vega": 1143.2620400510857,
    "drawdown": 5.82025,
    "turnover": 51,
    "hedges": 1,
    "realised_volatility": 0.05165319080059299
  },
  "hedges": [
    {
      "step": 0,
      "side": "sell",
      "quantity": 51,
      "benchmark": true,
      "order_id": "user-1"
    }
  ]
}
```

### KEY EXPLANATION

Gamma measures how quickly delta changes as the stock price moves.

Selected-contract values are per underlying unit. Contract and portfolio sensitivities retain multipliers and signed quantities. Changes in displayed inputs are observed contributors, not an additive causal attribution.

### MATHS

Γ = ∂²V/∂S² = ∂Δ/∂S

### REAL-FINANCE USE

Option hedging, derivatives market making and portfolio risk; production pricing can use surfaces and richer models.

Capture states: 

## Review the new exposure

### WHAT USER DOES

Re-hedge to the nearest whole stock unit

### WHAT QUANTLAB SHOWS

Compare the recorded result with the inputs available before the action.

```json
{
  "step": 1,
  "spot": 99.73,
  "selected": {
    "id": "QL-STOCK:call:100:6/73:x100",
    "underlying": "QL-STOCK",
    "type": "call",
    "strike": 100.0,
    "expiry_years": "6/73",
    "expiry_days": 30.0,
    "remaining_years": 0.07945205479452055,
    "remaining_days": 29.0,
    "multiplier": 100,
    "settlement": "European cash settlement",
    "revision": 3,
    "model_value": 2.112358940965514,
    "volatility_input": 0.19991925593936233,
    "bid": 2.097358,
    "ask": 2.127359,
    "midpoint": 2.1123585,
    "intrinsic": 0.0,
    "time_value": 2.1123585,
    "moneyness": "OTM",
    "bid_size": 20,
    "ask_size": 20,
    "iv": {
      "volatility": 0.19991921661140993,
      "converged": true,
      "status": "converged",
      "method": "Newton",
      "iterations": 3,
      "residual": -8.881784197001252e-16,
      "bracket": [
        0.0,
        0.19991921663598936
      ],
      "newton_steps": 2,
      "bisection_steps": 0
    },
    "greeks": {
      "delta": 0.4921005446208538,
      "gamma": 0.07097279410761076,
      "vega": 11.212521826674699,
      "theta": -14.106614527402114,
      "rho": 3.7314521173920405,
      "status": "analytic; volatility held fixed",
      "vega_per_vol_point": 0.11212521826674698,
      "theta_per_day": -0.03864825897918387,
      "rho_per_rate_point": 0.0373145211739204
    },
    "contract_greeks": {
      "delta": 49.21005446208538,
      "gamma": 7.097279410761076,
      "vega": 1121.25218266747,
      "theta": -1410.6614527402114,
      "rho": 373.14521173920406,
      "status": "analytic; volatility held fixed",
      "vega_per_vol_point": 11.212521826674699,
      "theta_per_day": -3.8648258979183874,
      "rho_per_rate_point": 3.7314521173920405
    },
    "mechanism": "Finite synthetic dealer quote; IOC remainder cancels"
  },
  "greeks": {
    "delta": 0.21005446208538103,
    "gamma": 7.097279410761076,
    "vega": 1121.25218266747,
    "theta": -1410.6614527402114,
    "rho": 373.14521173920406,
    "option_delta": 49.21005446208538
  },
  "accounts": {
    "cash": 4669.6919,
    "option_cash": -230.2651,
    "stock_cash": 4899.957,
    "option_value": 211.23585,
    "stock_value": -4886.77,
    "option_realised_gross": 0.0,
    "option_unrealised": -18.97925,
    "option_gross_pnl": -18.97925,
    "hedge_gross_pnl": 13.24,
    "stock_realised_gross": 0.5,
    "stock_unrealised": 12.74,
    "option_fees": 0.05,
    "stock_fees": 0.053,
    "fees": 0.103,
    "financing": 0.0,
    "total_pnl": -5.84225,
    "net_pnl": -5.84225,
    "residual_delta": 0.21005446208538103,
    "gross_hedging_error": -5.73925,
    "rms_delta": 0.1435753140224847,
    "absolute_residual_delta": 0.21005446208538103,
    "max_absolute_delta": 51.143575314022485,
    "max_absolute_gamma": 7.097279410761076,
    "max_absolute_vega": 1143.2620400510857,
    "drawdown": 5.84225,
    "turnover": 53,
    "hedges": 2,
    "realised_volatility": 0.05165319080059299
  },
  "hedges": [
    {
      "step": 0,
      "side": "sell",
      "quantity": 51,
      "benchmark": true,
      "order_id": "user-1"
    },
    {
      "step": 1,
      "side": "buy",
      "quantity": 2,
      "benchmark": true,
      "order_id": "user-2"
    }
  ]
}
```

### KEY EXPLANATION

A stock position is used to offset an option portfolio's current first-order stock sensitivity.

Selected-contract values are per underlying unit. Contract and portfolio sensitivities retain multipliers and signed quantities. Changes in displayed inputs are observed contributors, not an additive causal attribution.

### MATHS

This concept is a mechanism or interpretation, not a standalone formula.

### REAL-FINANCE USE

Option hedging, derivatives market making and portfolio risk; production pricing can use surfaces and richer models.

Capture states: 

## Change the volatility assumption

### WHAT USER DOES

Raise input implied volatility to 0.30

### WHAT QUANTLAB SHOWS

Compare the recorded result with the inputs available before the action.

```json
{
  "step": 1,
  "spot": 99.73,
  "selected": {
    "id": "QL-STOCK:call:100:6/73:x100",
    "underlying": "QL-STOCK",
    "type": "call",
    "strike": 100.0,
    "expiry_years": "6/73",
    "expiry_days": 30.0,
    "remaining_years": 0.07945205479452055,
    "remaining_days": 29.0,
    "multiplier": 100,
    "settlement": "European cash settlement",
    "revision": 4,
    "model_value": 3.2333289420885407,
    "volatility_input": 0.2998788839090435,
    "bid": 3.218328,
    "ask": 3.248329,
    "midpoint": 3.2333285,
    "intrinsic": 0.0,
    "time_value": 3.2333285,
    "moneyness": "OTM",
    "bid_size": 20,
    "ask_size": 20,
    "iv": {
      "volatility": 0.29987884448629,
      "converged": true,
      "status": "converged",
      "method": "Newton",
      "iterations": 3,
      "residual": -3.269384762916161e-12,
      "bracket": [
        0.2,
        0.29989398906341147
      ],
      "newton_steps": 2,
      "bisection_steps": 0
    },
    "greeks": {
      "delta": 0.5041003986036608,
      "gamma": 0.047321974132020245,
      "vega": 11.214128057973284,
      "theta": -21.16295302075711,
      "rho": 3.737472631531458,
      "status": "analytic; volatility held fixed",
      "vega_per_vol_point": 0.11214128057973284,
      "theta_per_day": -0.05798069320755373,
      "rho_per_rate_point": 0.037374726315314584
    },
    "contract_greeks": {
      "delta": 50.41003986036608,
      "gamma": 4.732197413202025,
      "vega": 1121.4128057973285,
      "theta": -2116.2953020757113,
      "rho": 373.7472631531458,
      "status": "analytic; volatility held fixed",
      "vega_per_vol_point": 11.214128057973285,
      "theta_per_day": -5.798069320755373,
      "rho_per_rate_point": 3.737472631531458
    },
    "mechanism": "Finite synthetic dealer quote; IOC remainder cancels"
  },
  "greeks": {
    "delta": 1.4100398603660835,
    "gamma": 4.732197413202025,
    "vega": 1121.4128057973285,
    "theta": -2116.2953020757113,
    "rho": 373.7472631531458,
    "option_delta": 50.41003986036608
  },
  "accounts": {
    "cash": 4669.6919,
    "option_cash": -230.2651,
    "stock_cash": 4899.957,
    "option_value": 323.33285,
    "stock_value": -4886.77,
    "option_realised_gross": 0.0,
    "option_unrealised": 93.11775,
    "option_gross_pnl": 93.11775,
    "hedge_gross_pnl": 13.24,
    "stock_realised_gross": 0.5,
    "stock_unrealised": 12.74,
    "option_fees": 0.05,
    "stock_fees": 0.053,
    "fees": 0.103,
    "financing": 0.0,
    "total_pnl": 106.25475,
    "net_pnl": 106.25475,
    "residual_delta": 1.4100398603660835,
    "gross_hedging_error": 106.35775,
    "rms_delta": 0.1435753140224847,
    "absolute_residual_delta": 1.4100398603660835,
    "max_absolute_delta": 51.143575314022485,
    "max_absolute_gamma": 7.097279410761076,
    "max_absolute_vega": 1143.2620400510857,
    "drawdown": 5.84225,
    "turnover": 53,
    "hedges": 2,
    "realised_volatility": 0.05165319080059299
  },
  "hedges": [
    {
      "step": 0,
      "side": "sell",
      "quantity": 51,
      "benchmark": true,
      "order_id": "user-1"
    },
    {
      "step": 1,
      "side": "buy",
      "quantity": 2,
      "benchmark": true,
      "order_id": "user-2"
    }
  ]
}
```

### KEY EXPLANATION

Vega measures the option value's sensitivity to the volatility input.

Selected-contract values are per underlying unit. Contract and portfolio sensitivities retain multipliers and signed quantities. Changes in displayed inputs are observed contributors, not an additive causal attribution.

### MATHS

ν = ∂V/∂σ

### REAL-FINANCE USE

Option hedging, derivatives market making and portfolio risk; production pricing can use surfaces and richer models.

Capture states: delta-after-volatility-shock

## LIMITATIONS

- European cash-settled options, fixed model assumptions and finite synthetic dealer quotes.
- Stock hedges execute against the existing FIFO book with fees. A nearest whole-unit hedge leaves residual delta.
- A hedge changes exposure; it does not remove gamma, vega, jumps, costs or model risk.

## HOW QUANTLAB DIFFERS FROM PRODUCTION

Educational single-machine models omit real venue latency, operational controls and much market complexity. A replay fingerprint verifies reproducibility; it does not validate a real-world investment conclusion.

## EVIDENCE

{"adapter": "delta", "engine_result_digest": "e620398ac73d73e5b3803324868e8a04c151549af81cbb78766c4e0ffb80decf", "journal_digest": "69ce19e3ca01932c9d515f2bee1007edd6ce0f025fc2b85592a95cb489b3b654", "note": "Derived from the existing engines; configuration chosen before outcomes."}
