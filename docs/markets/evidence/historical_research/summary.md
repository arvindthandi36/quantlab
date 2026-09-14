# QuantLab synthetic research experiment

How do two prespecified entry thresholds behave on this one recorded path?

**Prediction registered before execution:** A stricter threshold changes qualification; it need not improve executed outcomes.

Status: complete. Pool: development. Sessions per variant: 1. Root seed: 131042.

Synthetic performance is not evidence of real-world alpha.

## entry-2.0

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| drawdown | GBP | 1/1 | 1.038 | 1.038 | unavailable | unavailable | 1.038 | 1.038 | 1.038 | 1.038 |
| fills | count | 1/1 | 14 | 14 | unavailable | unavailable | 14 | 14 | 14 | 14 |
| net_pnl | GBP | 1/1 | -0.524 | -0.524 | unavailable | unavailable | -0.524 | -0.524 | -0.524 | -0.524 |

Mean interval: None
Bootstrap: None
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -0.5239999999994325, 'probability_below': {'-0.25': 1.0, '-0.5': 1.0, '-1.0': 0.0, '0.0': 1.0}, 'tail_count': 1, 'worst': -0.5239999999994325, 'worst_five_percent_mean': -0.5239999999994325}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #0: -0.524; simulation seed 147165143500359106264064254969208091013421226669214277393261326133786862395060

## entry-2.5

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| drawdown | GBP | 1/1 | 0.903 | 0.903 | unavailable | unavailable | 0.903 | 0.903 | 0.903 | 0.903 |
| fills | count | 1/1 | 10 | 10 | unavailable | unavailable | 10 | 10 | 10 | 10 |
| net_pnl | GBP | 1/1 | -0.34 | -0.34 | unavailable | unavailable | -0.34 | -0.34 | -0.34 | -0.34 |

Mean interval: None
Bootstrap: None
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -0.3400000000001455, 'probability_below': {'-0.25': 1.0, '-0.5': 0.0, '-1.0': 0.0, '0.0': 1.0}, 'tail_count': 1, 'worst': -0.3400000000001455, 'worst_five_percent_mean': -0.3400000000001455}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #0: -0.34; simulation seed 147165143500359106264064254969208091013421226669214277393261326133786862395060

## Paired: entry-2.5 minus entry-2.0

Summary: {'available': 1, 'maximum': 0.18399999999928696, 'mean': 0.18399999999928696, 'mean_ci': None, 'median': 0.18399999999928696, 'minimum': 0.18399999999928696, 'missing': 0, 'p05': 0.18399999999928696, 'p25': 0.18399999999928696, 'p75': 0.18399999999928696, 'p95': 0.18399999999928696, 'requested': 1, 'standard_deviation': None, 'standard_error': None, 'variance': None}
Bootstrap: None
Positive / negative / tied: 100.000% / 0.000% / 0.000%.
t = unavailable; two-sided p = unavailable; paired standardised effect = unavailable.
Paired two-sided t test: H0 E[D]=0; H1 E[D] differs from zero. Test undefined: insufficient observations or zero estimated variance. Statistical significance is not strategy validity or practical value.

## Interpretation

entry-2.0: observed mean net_pnl=-0.524; losing/negative outcomes 100.0%. entry-2.5: observed mean net_pnl=-0.34; losing/negative outcomes 100.0%. Compare the full distributions and paired uncertainty with the original hypothesis. These conditional model outcomes do not establish real-world alpha, safety or an optimal parameter. Interpretation remains reviewable.

## Limitations

- One historical path, not independent Monte Carlo trials; no generalisation claim.
- Training/evaluation boundaries are explicit and fitting is causal. Fixed unit sizing is not beta neutral.
- Next-close bar paper execution; terminal inventory is marked, not falsely liquidated.

Quantiles use linear interpolation; SD uses n−1. Markout distributions use per-session available-unit means, with session and unit coverage retained. A confidence interval concerns the model's mean, not the range of future outcomes.
