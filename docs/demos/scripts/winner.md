# Winner’s curse / multiple testing

SYNTHETIC STATISTICAL CONTROL

## SETUP

Best-of-many backtests can disappoint on untouched data.

{"development_runs": 40, "evaluation_runs": 400, "root": 140042, "variants": 50}

Initial hedge branch: full. All result numbers below originate in the existing Python engines.

## Test the registered alternatives

### WHAT USER DOES

Run 50 equal-skill variants on development seeds

### WHAT QUANTLAB SHOWS

Compare the recorded result with the inputs available before the action.

```json
{
  "selected_variant": {
    "configuration": {
      "mean": 0.0,
      "sd": 1.0,
      "variant_id": "32"
    },
    "name": "variant-32"
  },
  "selection_rule": "highest development mean; original order breaks ties",
  "development": {
    "available": 40,
    "maximum": 1.9102290468961276,
    "mean": 0.27750574177195075,
    "mean_ci": {
      "confidence": 0.95,
      "high": 0.6032139260803003,
      "low": -0.048202442536398826,
      "method": "Student t mean"
    },
    "median": 0.3791783509748689,
    "minimum": -1.9177146466882369,
    "missing": 0,
    "p05": -1.5858431992633302,
    "p25": -0.27314224428716427,
    "p75": 0.9278693030694374,
    "p95": 1.8341732425912372,
    "requested": 40,
    "standard_deviation": 1.0184252124428184,
    "standard_error": 0.161027164893008,
    "variance": 1.0371899133391997
  }
}
```

### KEY EXPLANATION

Selecting the best noisy result tends to select some favourable noise.

Equal-skill Gaussian statistical control; synthetic payoff units, NOT trading P&L. Winner locked before evaluation.

### MATHS

This concept is a mechanism or interpretation, not a standalone formula.

### REAL-FINANCE USE

Strategy evaluation and model validation; untouched evaluation data and prespecified comparisons matter.

Capture states: winner-before-test

## Keep the winner fixed

### WHAT USER DOES

Evaluate the locked winner on untouched evaluation seeds

### WHAT QUANTLAB SHOWS

All 50 means remain visible. Compare the locked winner’s development and evaluation results. Selection favours lucky estimates; deterioration is expected across repetitions, not guaranteed on every path.

```json
{
  "selected_variant": {
    "configuration": {
      "mean": 0.0,
      "sd": 1.0,
      "variant_id": "32"
    },
    "name": "variant-32"
  },
  "development_outcome_digest": "a31afcb5e96da7202e35ac8578fd80a67e53e1726a96e9ef6d729924de9c12bb",
  "selection_rule": "highest development mean; original order breaks ties",
  "evaluation_runs": 400,
  "known_true_mean": 0.0,
  "development": {
    "available": 40,
    "maximum": 1.9102290468961276,
    "mean": 0.27750574177195075,
    "mean_ci": {
      "confidence": 0.95,
      "high": 0.6032139260803003,
      "low": -0.048202442536398826,
      "method": "Student t mean"
    },
    "median": 0.3791783509748689,
    "minimum": -1.9177146466882369,
    "missing": 0,
    "p05": -1.5858431992633302,
    "p25": -0.27314224428716427,
    "p75": 0.9278693030694374,
    "p95": 1.8341732425912372,
    "requested": 40,
    "standard_deviation": 1.0184252124428184,
    "standard_error": 0.161027164893008,
    "variance": 1.0371899133391997
  },
  "evaluation": {
    "available": 400,
    "maximum": 2.6333376571730183,
    "mean": 0.047892190682125406,
    "mean_ci": {
      "confidence": 0.95,
      "high": 0.14141979066345267,
      "low": -0.04563540929920185,
      "method": "Student t mean"
    },
    "median": 0.043918386222982886,
    "minimum": -2.0874018364118996,
    "missing": 0,
    "p05": -1.5219108732744395,
    "p25": -0.6304448825565667,
    "p75": 0.7228527819662256,
    "p95": 1.5643286529870712,
    "requested": 400,
    "standard_deviation": 0.951485847674921,
    "standard_error": 0.047574292383746046,
    "variance": 0.9053253183256628
  },
  "observed_deterioration": 0.22961355108982534,
  "interpretation": "Selection optimism is expected over repetitions, not guaranteed in each sample. No root seeds were searched to force deterioration.",
  "limitations": "Gaussian payoffs have known equal true skill; these are not simulated executions. One demo is not a performance study."
}
```

### KEY EXPLANATION

Selecting the best noisy result tends to select some favourable noise.

Equal-skill Gaussian statistical control; synthetic payoff units, NOT trading P&L. Selection optimism is expected over repetitions, not guaranteed in each sample. No root seeds were searched to force deterioration.

### MATHS

This concept is a mechanism or interpretation, not a standalone formula.

### REAL-FINANCE USE

Strategy evaluation and model validation; untouched evaluation data and prespecified comparisons matter.

Capture states: winner-after-test

## LIMITATIONS

- Equal-skill Gaussian statistical control; synthetic payoff units, NOT trading P&L.
- Gaussian payoffs have known equal true skill; these are not simulated executions. One demo is not a performance study.
- Selection optimism is expected over repetitions, not guaranteed in each sample. No root seeds were searched to force deterioration.

## HOW QUANTLAB DIFFERS FROM PRODUCTION

Educational single-machine models omit real venue latency, operational controls and much market complexity. A replay fingerprint verifies reproducibility; it does not validate a real-world investment conclusion.

## EVIDENCE

{"adapter": "winner", "engine_result_digest": "2808ad131b1d87a69e39152cbfc47bbccfa884fc78d67dfdff1cfd5e52a44e0a", "journal_digest": null, "note": "Derived from the existing engines; configuration chosen before outcomes."}
