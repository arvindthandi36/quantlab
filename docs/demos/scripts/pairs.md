# Correlation vs cointegration

SYNTHETIC

## SETUP

It affects diversification and is useful for diagnosing relationships.

{"seeds": [101001, 101002, 101003], "source": "Phase 10 independent completed teaching cases"}

Initial hedge branch: full. All result numbers below originate in the existing Python engines.

## Similar pictures can hide different relationships

### WHAT USER DOES

Inspect regression residuals and past-window z-scores

### WHAT QUANTLAB SHOWS

Compare the recorded result with the inputs available before the action.

```json
{
  "noncointegrated": {
    "fit": {
      "alpha": 12.587112833366163,
      "beta": 0.8791338453364587,
      "r_squared": 0.8596406295184116,
      "alpha_se": 2.8259131377520506,
      "beta_se": 0.02826107617652104,
      "n": 160,
      "start": 0,
      "end": 160,
      "warnings": [
        "Conventional SE assumes IID homoskedastic errors; no price-series inference",
        "Large residual: outlier sensitivity; inspect observations"
      ]
    },
    "correlation": 0.9808050114480267,
    "return_correlation": 0.9515077168146974,
    "diagnostics": {
      "mean": 1.2221531728358725,
      "sd": 0.8256658155593133,
      "autocorrelation": 0.9956381204322672,
      "phi": 0.9990312504778855,
      "half_life": 715.1604904155807,
      "first_mean": 0.5274552492754003,
      "second_mean": 1.9111097912429524,
      "first_sd": 0.2640693488588608,
      "second_sd": 0.5771261776291995,
      "histogram": {
        "counts": [
          10,
          12,
          29,
          26,
          24,
          22,
          18,
          8
        ],
        "edges": [
          -0.06269815143942026,
          0.11216774782637717,
          0.2870336470921746,
          0.46189954635797204,
          0.6367654456237695,
          0.8116313448895669,
          0.9864972441553643,
          1.1613631434211618
        ]
      },
      "label": "Descriptive AR(1), not ADF, not a unit-root or cointegration test",
      "warning": "Half-life is conditional on 0 < fitted phi < 1, not a convergence deadline"
    },
    "training_rows": 160,
    "label": "Completed teaching dataset: fit first 160 rows; subsequent z uses only past residuals"
  },
  "stable": {
    "fit": {
      "alpha": 10.62841652290777,
      "beta": 0.8949928310141556,
      "r_squared": 0.728222317811431,
      "alpha_se": 4.349466886962537,
      "beta_se": 0.04349766218132402,
      "n": 160,
      "start": 0,
      "end": 160,
      "warnings": [
        "Conventional SE assumes IID homoskedastic errors; no price-series inference"
      ]
    },
    "correlation": 0.9828403377348357,
    "return_correlation": 0.8277388222332116,
    "diagnostics": {
      "mean": 0.3385073653119813,
      "sd": 0.390888060103609,
      "autocorrelation": 0.9273055652048963,
      "phi": 0.9216823908730761,
      "half_life": 8.499180159121932,
      "first_mean": 0.11379933276534947,
      "second_mean": 0.5613583066805418,
      "first_sd": 0.34251333911449516,
      "second_sd": 0.297790354685339,
      "histogram": {
        "counts": [
          3,
          4,
          10,
          17,
          16,
          13,
          21,
          28
        ],
        "edges": [
          -0.6735479754566001,
          -0.5429868126907547,
          -0.41242564992490927,
          -0.28186448715906387,
          -0.15130332439321847,
          -0.02074216162737308,
          0.10981900113847232,
          0.2403801639043177
        ]
      },
      "label": "Descriptive AR(1), not ADF, not a unit-root or cointegration test",
      "warning": "Half-life is conditional on 0 < fitted phi < 1, not a convergence deadline"
    },
    "training_rows": 160,
    "label": "Completed teaching dataset: fit first 160 rows; subsequent z uses only past residuals"
  }
}
```

### KEY EXPLANATION

The difference between Y and the fitted value predicted from X.

Completed independent teaching datasets, not forecasts for your live session

### MATHS

e_t = Y_t − (α + βX_t)

### REAL-FINANCE USE

Econometric relationship modelling, factor models and pairs research; regression alone is not a trading edge.

Capture states: correlation-vs-residual

## Challenge the stable relationship

### WHAT USER DOES

Apply the existing decoupling scenario and recalculate residuals

### WHAT QUANTLAB SHOWS

Compare the recorded result with the inputs available before the action.

```json
{
  "decoupled": {
    "fit": {
      "alpha": 10.62841652290777,
      "beta": 0.8949928310141556,
      "r_squared": 0.728222317811431,
      "alpha_se": 4.349466886962537,
      "beta_se": 0.04349766218132402,
      "n": 160,
      "start": 0,
      "end": 160,
      "warnings": [
        "Conventional SE assumes IID homoskedastic errors; no price-series inference"
      ]
    },
    "correlation": 0.9453114168332526,
    "return_correlation": 0.830797662301518,
    "diagnostics": {
      "mean": 1.4261007263078311,
      "sd": 1.5024059669552117,
      "autocorrelation": 0.9953026274680458,
      "phi": 0.9989210287592357,
      "half_life": 642.0682444238167,
      "first_mean": 0.16488266609868182,
      "second_mean": 2.6768954967631857,
      "first_sd": 0.4233516705029383,
      "second_sd": 1.0809802717737669,
      "histogram": {
        "counts": [
          7,
          39,
          22,
          26,
          20,
          22,
          10,
          4
        ],
        "edges": [
          -0.6735479754566001,
          -0.3702242947682901,
          -0.06690061407998016,
          0.2364230666083298,
          0.5397467472966397,
          0.8430704279849497,
          1.1463941086732596,
          1.4497177893615696
        ]
      },
      "label": "Descriptive AR(1), not ADF, not a unit-root or cointegration test",
      "warning": "Half-life is conditional on 0 < fitted phi < 1, not a convergence deadline"
    },
    "training_rows": 160,
    "label": "Completed teaching dataset: fit first 160 rows; subsequent z uses only past residuals"
  }
}
```

### KEY EXPLANATION

An answer can be internally correct while its assumptions misrepresent the world.

Existing QuantLab calculation; assumptions apply.

### MATHS

This concept is a mechanism or interpretation, not a standalone formula.

### REAL-FINANCE USE

Strategy evaluation and model validation; untouched evaluation data and prespecified comparisons matter.

Capture states: 

## LIMITATIONS

- Existing controlled teaching calculation, not a forecast or a production risk model.
- Known synthetic process labels support a model claim, not an empirical cointegration test. Exact observed correlations are shown, not replaced with 0.98.

## HOW QUANTLAB DIFFERS FROM PRODUCTION

Educational single-machine models omit real venue latency, operational controls and much market complexity. A replay fingerprint verifies reproducibility; it does not validate a real-world investment conclusion.

## EVIDENCE

{"adapter": "pairs", "engine_result_digest": "129dc1be401367429c6264e0ee384f6d4c9a219b3d2b61133247e653d4c1ecdc", "journal_digest": null, "note": "Derived from the existing engines; configuration chosen before outcomes."}
