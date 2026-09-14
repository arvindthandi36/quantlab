# QuantLab synthetic research experiment

Does the best unrelated training pair survive an untouched test?

**Prediction registered before execution:** Ranking 28 null pairs creates winner's curse; selected in-sample success need not persist.

Status: complete. Pool: evaluation. Sessions per variant: 16. Root seed: 10101004.

Synthetic performance is not evidence of real-world alpha.

## in_sample

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average_trade | GBP | 16/16 | 4.3888 | 4.2525 | 1.8036 | 0.4509 | 1.96458 | 3.63875 | 5.71125 | 6.97083 |
| costs | GBP | 16/16 | 0.984375 | 0.9 | 0.33821 | 0.0845526 | 0.525 | 0.81 | 1.08 | 1.665 |
| drawdown | GBP | 16/16 | 5.85313 | 4.905 | 3.03982 | 0.759955 | 2.5825 | 3.99 | 6.49375 | 12.1075 |
| max_gross | GBP | 16/16 | 927.746 | 910.61 | 56.5704 | 14.1426 | 863.88 | 894.915 | 963.445 | 1014.05 |
| max_imbalance | GBP | 16/16 | 256.069 | 298.155 | 131.155 | 32.7888 | 104.45 | 118.351 | 329.803 | 432.885 |
| mean_entry_z | units | 16/16 | 0.433991 | 0.02496 | 1.45536 | 0.363839 | -1.22823 | -0.618521 | 1.74691 | 2.53688 |
| mean_exit_z | units | 16/16 | 0.0231587 | 0.0405679 | 0.5506 | 0.13765 | -0.894547 | -0.199301 | 0.44691 | 0.690708 |
| mean_holding | observations | 16/16 | 9.75 | 8 | 5.23264 | 1.30816 | 4.91667 | 7.375 | 10.8333 | 17.375 |
| median_trade | GBP | 16/16 | 4.41125 | 4.27 | 1.80759 | 0.451897 | 1.81875 | 3.5775 | 5.2 | 7.1575 |
| net_pnl | GBP | 16/16 | 14.7606 | 13.65 | 5.40496 | 1.35124 | 7.7275 | 12.7425 | 17.64 | 22.5375 |
| probability_loss | fraction | 16/16 | 0.0677083 | 0 | 0.122545 | 0.0306363 | 0 | 0 | 0.0625 | 0.270833 |
| residual_inventory | units | 16/16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| return_on_capital | fraction | 16/16 | 0.00147606 | 0.001365 | 0.000540496 | 0.000135124 | 0.00077275 | 0.00127425 | 0.001764 | 0.00225375 |
| trade_count | units | 16/16 | 3.5625 | 3 | 1.15289 | 0.288224 | 2 | 3 | 4 | 6 |
| turnover | GBP | 16/16 | 6558.58 | 6014.26 | 2213.02 | 553.256 | 3649.05 | 5362.99 | 7149.1 | 10885.4 |
| win_rate | fraction | 16/16 | 0.932292 | 1 | 0.122545 | 0.0306363 | 0.729167 | 0.9375 | 1 | 1 |
| worst_trade | GBP | 16/16 | 1.81688 | 2.865 | 3.18874 | 0.797186 | -3.1025 | 0.25 | 3.9425 | 5.12 |

Mean interval: {'confidence': 0.95, 'high': 17.640722927719068, 'low': 11.88052707228093, 'method': 'Student t mean'}
Bootstrap: {'estimate': 14.760625, 'interval': {'confidence': 0.95, 'high': 17.346828125, 'low': 12.050078124999999, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 500, 'seed': 38675853578892066530411850116133764646042555523260575391139652609920875057648, 'standard_error': 1.3302709723443231}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': 7.727499999999999, 'probability_below': {'-0.25': 0.0, '-0.5': 0.0, '-1.0': 0.0, '0.0': 0.0}, 'tail_count': 1, 'worst': 1.57, 'worst_five_percent_mean': 1.57}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #11: 1.57; simulation seed 123647579460923056394700877448067862078342089580143800204210178256369312610397
- Run #1: 9.78; simulation seed 222289496290815104440648873937602027334509914121095289444552873410046839087689
- Run #9: 11.14; simulation seed 48247515445128790758161334255681031553084766975943734520889173082909293576973

## out_of_sample

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average_trade | GBP | 12/16 | -1.97314 | 0.4125 | 8.08004 | 2.33251 | -15.1092 | -4.9275 | 2.4855 | 5.55175 |
| costs | GBP | 16/16 | 0.553125 | 0.54 | 0.417704 | 0.104426 | 0 | 0.2025 | 0.9 | 1.1475 |
| drawdown | GBP | 16/16 | 9.72813 | 8.0775 | 8.16681 | 2.0417 | 0 | 4.1475 | 16.8075 | 23.01 |
| max_gross | GBP | 16/16 | 699.263 | 912.51 | 418.24 | 104.56 | 0 | 661.41 | 936.358 | 989.317 |
| max_imbalance | GBP | 16/16 | 193.002 | 215.975 | 149.955 | 37.4887 | 0 | 82.6154 | 296.498 | 374.705 |
| mean_entry_z | units | 12/16 | -0.155631 | -0.231026 | 1.67314 | 0.482994 | -2.6234 | -0.989095 | 0.680673 | 2.50453 |
| mean_exit_z | units | 12/16 | 0.0459409 | 0.0458304 | 0.862639 | 0.249022 | -1.07416 | -0.277722 | 0.36733 | 1.19868 |
| mean_holding | observations | 12/16 | 16.4361 | 16.25 | 6.21992 | 1.79554 | 9.09667 | 12.4583 | 18.25 | 26.325 |
| median_trade | GBP | 12/16 | -2.12542 | 0.94 | 7.7936 | 2.24982 | -15.1092 | -4.9275 | 3.0025 | 3.50025 |
| net_pnl | GBP | 16/16 | -0.01875 | 0 | 11.6347 | 2.90868 | -18.3975 | -4.6825 | 6.57 | 18.4925 |
| probability_loss | fraction | 12/16 | 0.363889 | 0.333333 | 0.359702 | 0.103837 | 0 | 0 | 0.5 | 1 |
| residual_inventory | units | 16/16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| return_on_capital | fraction | 16/16 | -1.875e-06 | 0 | 0.00116347 | 0.000290868 | -0.00183975 | -0.00046825 | 0.000657 | 0.00184925 |
| trade_count | units | 16/16 | 2 | 2 | 1.50555 | 0.376386 | 0 | 0.75 | 3 | 4.25 |
| turnover | GBP | 16/16 | 3677.98 | 3667.8 | 2753.89 | 688.472 | 0 | 1313.93 | 5846.13 | 7548.22 |
| win_rate | fraction | 12/16 | 0.636111 | 0.666667 | 0.359702 | 0.103837 | 0 | 0.5 | 1 | 1 |
| worst_trade | GBP | 12/16 | -6.2475 | -4.215 | 8.41784 | 2.43002 | -18.456 | -13.7925 | 1.155 | 2.66 |

Mean interval: {'confidence': 0.95, 'high': 6.180945707081251, 'low': -6.21844570708125, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.018750000000000044, 'interval': {'confidence': 0.95, 'high': 5.57790625, 'low': -5.617453124999997, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 500, 'seed': 53551247262395097513269166958865870411422681916451738861355811265571508636804, 'standard_error': 2.8565319149889086}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -18.3975, 'probability_below': {'-0.25': 0.3125, '-0.5': 0.3125, '-1.0': 0.3125, '0.0': 0.3125}, 'tail_count': 1, 'worst': -23.34, 'worst_five_percent_mean': -23.34}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #11: -23.34; simulation seed 123647579460923056394700877448067862078342089580143800204210178256369312610397
- Run #5: -16.75; simulation seed 129648124251930685360041903102709248713166340925260326105852243514488445886299
- Run #7: -12.66; simulation seed 217503974352107979972190641799874616147948909063526613955799792225918679070715

## Paired: out_of_sample minus in_sample

Summary: {'available': 16, 'maximum': -2.59, 'mean': -14.779374999999998, 'mean_ci': {'confidence': 0.95, 'high': -10.003371525000343, 'low': -19.555378474999653, 'method': 'Student t mean'}, 'median': -12.735, 'minimum': -30.39, 'missing': 0, 'p05': -29.8875, 'p25': -21.985, 'p75': -8.135000000000002, 'p95': -3.9175000000000004, 'requested': 16, 'standard_deviation': 8.96292100359401, 'standard_error': 2.2407302508985025, 'variance': 80.33395291666666}
Bootstrap: {'estimate': -14.779374999999998, 'interval': {'confidence': 0.95, 'high': -10.770875000000002, 'low': -19.24675, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete matched session pair', 'resamples': 500, 'seed': 18858386039623925827695002112007177962058300551223626338016908023716877820692, 'standard_error': 2.2350648977659913}
Positive / negative / tied: 0.000% / 100.000% / 0.000%.
t = -6.59579; two-sided p = 8.49796e-06; paired standardised effect = -1.64895.
Paired two-sided t test: H0 E[D]=0; H1 E[D] differs from zero. Statistical significance is not strategy validity or practical value.

## Interpretation

in_sample: observed mean net_pnl=14.7606; losing/negative outcomes 0.0%. out_of_sample: observed mean net_pnl=-0.01875; losing/negative outcomes 31.2%. Compare the full distributions and paired uncertainty with the original hypothesis. These conditional model outcomes do not establish real-world alpha, safety or an optimal parameter. Interpretation remains reviewable.

## Limitations

- Synthetic results do not establish real-market alpha.
- Training-selected performance is optimistic; evaluation never selects thresholds.
- The initial fit origin differs across disjoint time blocks; blocks may have different lengths.
- Confidence intervals exclude process, liquidity and model uncertainty.

Quantiles use linear interpolation; SD uses n−1. Markout distributions use per-session available-unit means, with session and unit coverage retained. A confidence interval concerns the model's mean, not the range of future outcomes.
