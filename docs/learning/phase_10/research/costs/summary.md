# QuantLab synthetic research experiment

How do higher two-leg execution costs affect net outcomes?

**Prediction registered before execution:** Higher spreads and fees should reduce net P&L under this fixed environment.

Status: complete. Pool: evaluation. Sessions per variant: 32. Root seed: 10101002.

Synthetic performance is not evidence of real-world alpha.

## low

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average_trade | GBP | 32/32 | 0.856603 | 0.921667 | 0.877004 | 0.155034 | -0.678738 | 0.499821 | 1.37354 | 2.06168 |
| costs | GBP | 32/32 | 1.66875 | 1.62 | 0.393502 | 0.0695619 | 1.02 | 1.44 | 1.9125 | 2.127 |
| drawdown | GBP | 32/32 | 5.37719 | 4.685 | 2.84562 | 0.503039 | 2.574 | 3.68 | 5.96875 | 12.048 |
| max_gross | GBP | 32/32 | 944.16 | 945.58 | 67.1292 | 11.8669 | 830.256 | 913.393 | 998.438 | 1041.3 |
| max_imbalance | GBP | 32/32 | 487.348 | 486.978 | 48.2502 | 8.52951 | 428.039 | 448.284 | 507.125 | 579.471 |
| mean_entry_z | units | 32/32 | -0.0668111 | -0.160767 | 0.784918 | 0.138755 | -1.20468 | -0.607763 | 0.474917 | 1.16521 |
| mean_exit_z | units | 32/32 | 0.0638576 | 0.151024 | 0.415421 | 0.0734368 | -0.502637 | -0.306055 | 0.375345 | 0.635634 |
| mean_holding | observations | 32/32 | 10.6324 | 10.3095 | 2.44254 | 0.431785 | 7.20625 | 8.40476 | 12.6583 | 14.26 |
| median_trade | GBP | 32/32 | 0.89 | 0.9225 | 0.9574 | 0.169246 | -0.6375 | 0.525 | 1.50625 | 2.21725 |
| net_pnl | GBP | 32/32 | 4.97531 | 5.805 | 5.07515 | 0.897168 | -5.1675 | 3.09 | 7.8375 | 10.924 |
| probability_loss | fraction | 32/32 | 0.302307 | 0.333333 | 0.181082 | 0.0320111 | 0 | 0.160714 | 0.38125 | 0.584286 |
| residual_inventory | units | 32/32 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| return_on_capital | fraction | 32/32 | 0.000497531 | 0.0005805 | 0.000507515 | 8.97168e-05 | -0.00051675 | 0.000309 | 0.00078375 | 0.0010924 |
| trade_count | units | 32/32 | 6.15625 | 6 | 1.34667 | 0.238059 | 4 | 6 | 7 | 8.45 |
| turnover | GBP | 32/32 | 11094.3 | 10965 | 2538.21 | 448.697 | 6962.26 | 9970.58 | 12983.1 | 14703.9 |
| win_rate | fraction | 32/32 | 0.697693 | 0.666667 | 0.181082 | 0.0320111 | 0.415714 | 0.61875 | 0.839286 | 1 |
| worst_trade | GBP | 32/32 | -1.87406 | -1.78 | 1.78173 | 0.314968 | -4.8595 | -2.625 | -0.925 | 0.3335 |

Mean interval: {'confidence': 0.95, 'high': 6.80509968508421, 'low': 3.1455253149157882, 'method': 'Student t mean'}
Bootstrap: {'estimate': 4.975312499999999, 'interval': {'confidence': 0.95, 'high': 6.458156249999999, 'low': 3.1818125, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 500, 'seed': 1342163372209693511194979380204593345999623667612435469252648656562823033392, 'standard_error': 0.8460521313228154}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -5.1675, 'probability_below': {'-0.25': 0.125, '-0.5': 0.125, '-1.0': 0.125, '0.0': 0.125}, 'tail_count': 2, 'worst': -7.249999999999999, 'worst_five_percent_mean': -7.24}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #2: -7.25; simulation seed 52219916624095494269924839294554775344632821031312823243896568474613596782095
- Run #23: -7.23; simulation seed 127525783872057766191645690191515358214084053508311769126313418422930800268315
- Run #31: -3.48; simulation seed 12542480203082973179537671929148517787680378962871859417391738717003908287113

## high

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average_trade | GBP | 32/32 | -0.677761 | -0.618333 | 0.908006 | 0.160514 | -2.37874 | -1.07268 | -0.120625 | 0.593095 |
| costs | GBP | 32/32 | 11.125 | 10.8 | 2.62334 | 0.463746 | 6.8 | 9.6 | 12.75 | 14.18 |
| drawdown | GBP | 32/32 | 8.54719 | 7.56 | 4.40647 | 0.778962 | 3.905 | 5.085 | 9.645 | 17.976 |
| max_gross | GBP | 32/32 | 944.16 | 945.58 | 67.1292 | 11.8669 | 830.256 | 913.393 | 998.438 | 1041.3 |
| max_imbalance | GBP | 32/32 | 487.348 | 486.978 | 48.2502 | 8.52951 | 428.039 | 448.284 | 507.125 | 579.471 |
| mean_entry_z | units | 32/32 | -0.0668111 | -0.160767 | 0.784918 | 0.138755 | -1.20468 | -0.607763 | 0.474917 | 1.16521 |
| mean_exit_z | units | 32/32 | 0.0638576 | 0.151024 | 0.415421 | 0.0734368 | -0.502637 | -0.306055 | 0.375345 | 0.635634 |
| mean_holding | observations | 32/32 | 10.6324 | 10.3095 | 2.44254 | 0.431785 | 7.20625 | 8.40476 | 12.6583 | 14.26 |
| median_trade | GBP | 32/32 | -0.63375 | -0.56 | 0.983778 | 0.173909 | -2.244 | -1.105 | 0.0475 | 0.6125 |
| net_pnl | GBP | 32/32 | -4.48094 | -3.915 | 5.74292 | 1.01521 | -16.635 | -6.8175 | -0.6825 | 3.277 |
| probability_loss | fraction | 32/32 | 0.562178 | 0.585714 | 0.201285 | 0.0355825 | 0.2125 | 0.5 | 0.666667 | 0.844048 |
| residual_inventory | units | 32/32 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| return_on_capital | fraction | 32/32 | -0.000448094 | -0.0003915 | 0.000574292 | 0.000101521 | -0.0016635 | -0.00068175 | -6.825e-05 | 0.0003277 |
| trade_count | units | 32/32 | 6.15625 | 6 | 1.34667 | 0.238059 | 4 | 6 | 7 | 8.45 |
| turnover | GBP | 32/32 | 11094.3 | 10965 | 2538.21 | 448.697 | 6962.26 | 9970.58 | 12983.1 | 14703.9 |
| win_rate | fraction | 32/32 | 0.437822 | 0.414286 | 0.201285 | 0.0355825 | 0.155952 | 0.333333 | 0.5 | 0.7875 |
| worst_trade | GBP | 32/32 | -3.42 | -3.16 | 1.81161 | 0.32025 | -6.466 | -4.155 | -2.3425 | -1.062 |

Mean interval: {'confidence': 0.95, 'high': -2.4103948131960276, 'low': -6.551480186803971, 'method': 'Student t mean'}
Bootstrap: {'estimate': -4.4809375, 'interval': {'confidence': 0.95, 'high': -2.526695312500001, 'low': -6.594749999999998, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 500, 'seed': 107059146018034751668943596439621353781025489993099502201491435338463837626400, 'standard_error': 1.0338209569902064}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -16.634999999999998, 'probability_below': {'-0.25': 0.78125, '-0.5': 0.75, '-1.0': 0.71875, '0.0': 0.78125}, 'tail_count': 2, 'worst': -19.15, 'worst_five_percent_mean': -18.965}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #2: -19.15; simulation seed 52219916624095494269924839294554775344632821031312823243896568474613596782095
- Run #31: -18.78; simulation seed 12542480203082973179537671929148517787680378962871859417391738717003908287113
- Run #23: -14.88; simulation seed 127525783872057766191645690191515358214084053508311769126313418422930800268315

## Paired: high minus low

Summary: {'available': 32, 'maximum': -4.589999999999998, 'mean': -9.45625, 'mean_ci': {'confidence': 0.95, 'high': -8.652305982177225, 'low': -10.260194017822776, 'method': 'Student t mean'}, 'median': -9.18, 'minimum': -15.3, 'missing': 0, 'p05': -12.052999999999999, 'p25': -10.8375, 'p75': -8.16, 'p95': -5.78, 'requested': 32, 'standard_deviation': 2.229842682140777, 'standard_error': 0.3941842203802356, 'variance': 4.972198387096774}
Bootstrap: {'estimate': -9.45625, 'interval': {'confidence': 0.95, 'high': -8.717015625, 'low': -10.1709140625, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete matched session pair', 'resamples': 500, 'seed': 14920358537321133205334559452089502402886648192122602870516008116535932871828, 'standard_error': 0.3828843450740453}
Positive / negative / tied: 0.000% / 100.000% / 0.000%.
t = -23.9894; two-sided p = 1.39881e-21; paired standardised effect = -4.24077.
Paired two-sided t test: H0 E[D]=0; H1 E[D] differs from zero. Statistical significance is not strategy validity or practical value.

## Interpretation

high: observed mean net_pnl=-4.48094; losing/negative outcomes 78.1%. low: observed mean net_pnl=4.97531; losing/negative outcomes 12.5%. Compare the full distributions and paired uncertainty with the original hypothesis. These conditional model outcomes do not establish real-world alpha, safety or an optimal parameter. Interpretation remains reviewable.

## Limitations

- Synthetic results do not establish real-market alpha.
- Training-selected performance is optimistic; evaluation never selects thresholds.
- The initial fit origin differs across disjoint time blocks; blocks may have different lengths.
- Confidence intervals exclude process, liquidity and model uncertainty.

Quantiles use linear interpolation; SD uses n−1. Markout distributions use per-session available-unit means, with session and unit coverage retained. A confidence interval concerns the model's mean, not the range of future outcomes.
