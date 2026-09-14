# VaR vs ES

SYNTHETIC

## SETUP

It summarises a model's loss distribution while allowing worse outcomes.

{"seed": 140042, "source": "approved teaching functions"}

Initial hedge branch: full. All result numbers below originate in the existing Python engines.

## Look beyond the threshold

### WHAT USER DOES

Reveal the severity of the loss tail

### WHAT QUANTLAB SHOWS

Compare the recorded result with the inputs available before the action.

```json
{
  "mild": {
    "var": 10.0,
    "es": 12.0,
    "confidence": 0.95,
    "n": 100,
    "tail_mass": 5.0,
    "whole_tail_observations": 5,
    "boundary_weight": 0.0,
    "worst": [
      20.0,
      10.0,
      10.0,
      10.0,
      10.0,
      10.0,
      0.0,
      0.0
    ],
    "histogram": {
      "edges": [
        0.0,
        2.0,
        4.0,
        6.0,
        8.0,
        10.0,
        12.0,
        14.0
      ],
      "counts": [
        94,
        0,
        0,
        0,
        0,
        5,
        0,
        0
      ]
    },
    "mean_loss": 0.7,
    "loss_sd": 2.9318866956210288,
    "warnings": [
      "Fewer than 20 effective tail observations; tail estimate is noisy"
    ],
    "convention": "Inverse empirical CDF VaR; ES averages exact worst 1-alpha mass with fractional boundary atom",
    "interpretation": "Model/data loss threshold, never a maximum possible loss"
  },
  "severe": {
    "var": 10.0,
    "es": 48.0,
    "confidence": 0.95,
    "n": 100,
    "tail_mass": 5.0,
    "whole_tail_observations": 5,
    "boundary_weight": 0.0,
    "worst": [
      200.0,
      10.0,
      10.0,
      10.0,
      10.0,
      10.0,
      0.0,
      0.0
    ],
    "histogram": {
      "edges": [
        0.0,
        20.0,
        40.0,
        60.0,
        80.0,
        100.0,
        120.0,
        140.0
      ],
      "counts": [
        99,
        0,
        0,
        0,
        0,
        0,
        0,
        0
      ]
    },
    "mean_loss": 2.5,
    "loss_sd": 20.06932429798716,
    "warnings": [
      "Fewer than 20 effective tail observations; tail estimate is noisy"
    ],
    "convention": "Inverse empirical CDF VaR; ES averages exact worst 1-alpha mass with fractional boundary atom",
    "interpretation": "Model/data loss threshold, never a maximum possible loss"
  }
}
```

### KEY EXPLANATION

The average loss in the worst selected fraction of outcomes.

Expected Shortfall averages the exact worst 5% mass. The sample contains only five effective tail observations; fees and returns are not being simulated here.

### MATHS

ES_α = (1/(1−α)) ∫ₐ¹ VaR_u du

### REAL-FINANCE USE

Market-risk measurement, limits and reporting contexts; this educational implementation is not a regulatory capital engine.

Capture states: var-vs-es-tail

## LIMITATIONS

- Existing controlled teaching calculation, not a forecast or a production risk model.
- These are deliberately constructed loss distributions, not sampled live portfolios.
- VaR is not a maximum loss; ES is an average within a model/data tail.

## HOW QUANTLAB DIFFERS FROM PRODUCTION

Educational single-machine models omit real venue latency, operational controls and much market complexity. A replay fingerprint verifies reproducibility; it does not validate a real-world investment conclusion.

## EVIDENCE

{"adapter": "tails", "engine_result_digest": "1eb096f62f2e35a8d708591674a1ca57f9febc69aa6508a89d5790d3b0ed0ebc", "journal_digest": null, "note": "Derived from the existing engines; configuration chosen before outcomes."}
