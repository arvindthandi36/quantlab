# QuantLab synthetic research experiment

Does training-selected performance persist on untouched future observations?

**Prediction registered before execution:** Selecting the best of three training thresholds creates optimism; held-out outcomes may weaken.

Status: complete. Pool: evaluation. Sessions per variant: 32. Root seed: 10101000.

Synthetic performance is not evidence of real-world alpha.

## in_sample

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average_trade | GBP | 32/32 | 1.34002 | 1.24625 | 0.917294 | 0.162156 | 0.039 | 0.7275 | 1.785 | 3.0875 |
| costs | GBP | 32/32 | 1.03594 | 1.08 | 0.374389 | 0.0661832 | 0.48 | 0.72 | 1.35 | 1.62 |
| drawdown | GBP | 32/32 | 3.65266 | 3.6225 | 1.52991 | 0.270453 | 1.085 | 2.8075 | 4.7525 | 6.133 |
| max_gross | GBP | 32/32 | 915.815 | 924.015 | 66.8109 | 11.8106 | 803.578 | 883.933 | 961.85 | 1006.91 |
| max_imbalance | GBP | 32/32 | 462.901 | 466.327 | 63.708 | 11.2621 | 352.498 | 421.929 | 498.312 | 562.801 |
| mean_entry_z | units | 32/32 | -0.125323 | 0.148116 | 1.12193 | 0.198331 | -2.7222 | -0.670771 | 0.437027 | 1.18478 |
| mean_exit_z | units | 32/32 | 0.000922675 | -0.0275029 | 0.578456 | 0.102258 | -1.03798 | -0.373216 | 0.38598 | 0.971299 |
| mean_holding | observations | 32/32 | 10.2016 | 9.53333 | 3.65291 | 0.64575 | 5.8875 | 8 | 10.8125 | 15.9417 |
| median_trade | GBP | 32/32 | 1.28875 | 1.145 | 0.98601 | 0.174304 | -0.27775 | 0.775 | 1.7925 | 3.0875 |
| net_pnl | GBP | 32/32 | 4.97781 | 4.37 | 3.48481 | 0.616034 | 0.09 | 2.6375 | 7.26 | 10.4205 |
| probability_loss | fraction | 32/32 | 0.232812 | 0.225 | 0.221168 | 0.0390974 | 0 | 0 | 0.333333 | 0.63 |
| residual_inventory | units | 32/32 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| return_on_capital | fraction | 32/32 | 0.000497781 | 0.000437 | 0.000348481 | 6.16034e-05 | 9e-06 | 0.00026375 | 0.000726 | 0.00104205 |
| trade_count | units | 32/32 | 3.84375 | 4 | 1.37041 | 0.242257 | 2 | 3 | 5 | 6 |
| turnover | GBP | 32/32 | 6932.49 | 7247.29 | 2538.33 | 448.717 | 3237.84 | 4853 | 8926.14 | 10826.8 |
| win_rate | fraction | 32/32 | 0.760937 | 0.75 | 0.223029 | 0.0394264 | 0.37 | 0.65 | 1 | 1 |
| worst_trade | GBP | 32/32 | -0.480313 | -0.635 | 1.54587 | 0.273274 | -2.2745 | -1.775 | 0.3425 | 2.3485 |

Mean interval: {'confidence': 0.95, 'high': 6.234221860832912, 'low': 3.721403139167087, 'method': 'Student t mean'}
Bootstrap: {'estimate': 4.9778125, 'interval': {'confidence': 0.95, 'high': 6.1962734374999995, 'low': 3.7535078125, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 500, 'seed': 15014054762002852405434676265090502917726121112249604063417702236847839793916, 'standard_error': 0.6333245893218021}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': 0.0900000000000003, 'probability_below': {'-0.25': 0.03125, '-0.5': 0.03125, '-1.0': 0.0, '0.0': 0.0625}, 'tail_count': 2, 'worst': -0.77, 'worst_five_percent_mean': -0.5049999999999999}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #18: -0.77; simulation seed 35549754700953627609106429323874777102453546679780840060643029969122787995581
- Run #17: -0.24; simulation seed 102082919404470512700910124786482885670969443192863717309476666608247488435949
- Run #25: 0.36; simulation seed 106475367817863998689229308657995491537992580351228146120386183272037972020885

## out_of_sample

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average_trade | GBP | 32/32 | 0.32054 | 0.249143 | 1.25182 | 0.221293 | -1.57762 | -0.375 | 1.10833 | 2.26017 |
| costs | GBP | 32/32 | 0.950625 | 0.81 | 0.419546 | 0.074166 | 0.273 | 0.72 | 1.35 | 1.647 |
| drawdown | GBP | 32/32 | 4.39031 | 4.29 | 1.7089 | 0.302094 | 2.153 | 3.01 | 5.83375 | 7.206 |
| max_gross | GBP | 32/32 | 905.364 | 911.13 | 62.7094 | 11.0856 | 810.5 | 851.26 | 959.48 | 985.428 |
| max_imbalance | GBP | 32/32 | 464.959 | 453.837 | 61.4154 | 10.8568 | 393.04 | 417.067 | 508.703 | 565.934 |
| mean_entry_z | units | 32/32 | 0.100622 | 0.0703829 | 1.5411 | 0.272431 | -2.89335 | -0.648463 | 0.836707 | 2.77389 |
| mean_exit_z | units | 32/32 | 0.124268 | 0.122554 | 0.614956 | 0.10871 | -0.63716 | -0.346035 | 0.350611 | 1.07517 |
| mean_holding | observations | 32/32 | 11.2275 | 10 | 5.43143 | 0.96015 | 4.66667 | 6.75 | 15.5 | 21.3 |
| median_trade | GBP | 32/32 | 0.3225 | 0.37 | 1.45413 | 0.257057 | -2.262 | -0.3525 | 1.19 | 2.647 |
| net_pnl | GBP | 32/32 | 1.51719 | 1.105 | 3.49394 | 0.617646 | -3.1 | -0.765 | 3.325 | 7.019 |
| probability_loss | fraction | 32/32 | 0.442039 | 0.414286 | 0.279566 | 0.0494208 | 0 | 0.25 | 0.616667 | 1 |
| residual_inventory | units | 32/32 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| return_on_capital | fraction | 32/32 | 0.000151719 | 0.0001105 | 0.000349394 | 6.17646e-05 | -0.00031 | -7.65e-05 | 0.0003325 | 0.0007019 |
| trade_count | units | 32/32 | 3.5625 | 3 | 1.52268 | 0.269174 | 1 | 3 | 5 | 6 |
| turnover | GBP | 32/32 | 6375.63 | 5517.47 | 2850.76 | 503.948 | 1859.16 | 4815.5 | 8843.58 | 11608.9 |
| win_rate | fraction | 32/32 | 0.557961 | 0.585714 | 0.279566 | 0.0494208 | 0 | 0.383333 | 0.75 | 1 |
| worst_trade | GBP | 32/32 | -1.6475 | -2.06 | 1.5061 | 0.266244 | -3.7505 | -2.6725 | -0.45 | 1.0215 |

Mean interval: {'confidence': 0.95, 'high': 2.7768854182996825, 'low': 0.25748958170031777, 'method': 'Student t mean'}
Bootstrap: {'estimate': 1.5171875000000001, 'interval': {'confidence': 0.95, 'high': 2.7716796875, 'low': 0.4005312500000005, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 500, 'seed': 111363486395440647314644634041889167558010761076747751062484173656671852662070, 'standard_error': 0.6097916377771408}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -3.0999999999999996, 'probability_below': {'-0.25': 0.34375, '-0.5': 0.3125, '-1.0': 0.25, '0.0': 0.34375}, 'tail_count': 2, 'worst': -5.1899999999999995, 'worst_five_percent_mean': -4.255}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #6: -5.19; simulation seed 20572267598549916490932519383673441016636805451594668813571135234645661993291
- Run #13: -3.32; simulation seed 197475917808641319805038420325434233518889388464580160262448230286083058081633
- Run #9: -2.92; simulation seed 107625050738539335988984122308574338105726843044685142777184633714764982401069

## Paired: out_of_sample minus in_sample

Summary: {'available': 32, 'maximum': 6.0, 'mean': -3.4606249999999994, 'mean_ci': {'confidence': 0.95, 'high': -1.5195812105209994, 'low': -5.401668789478999, 'method': 'Student t mean'}, 'median': -2.215, 'minimum': -14.49, 'missing': 0, 'p05': -12.1015, 'p25': -6.93, 'p75': 0.24999999999999956, 'p95': 4.8315, 'requested': 32, 'standard_deviation': 5.383735924058683, 'standard_error': 0.9517190450048795, 'variance': 28.9846125}
Bootstrap: {'estimate': -3.4606249999999994, 'interval': {'confidence': 0.95, 'high': -1.599921875, 'low': -5.152765624999999, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete matched session pair', 'resamples': 500, 'seed': 13174928829402032011515574762524486864347441164914314311788107383937566594234, 'standard_error': 0.9061193894018584}
Positive / negative / tied: 28.125% / 71.875% / 0.000%.
t = -3.63618; two-sided p = 0.000992633; paired standardised effect = -0.642792.
Paired two-sided t test: H0 E[D]=0; H1 E[D] differs from zero. Statistical significance is not strategy validity or practical value.

## Interpretation

in_sample: observed mean net_pnl=4.97781; losing/negative outcomes 6.2%. out_of_sample: observed mean net_pnl=1.51719; losing/negative outcomes 34.4%. Compare the full distributions and paired uncertainty with the original hypothesis. These conditional model outcomes do not establish real-world alpha, safety or an optimal parameter. Interpretation remains reviewable.

## Limitations

- Synthetic results do not establish real-market alpha.
- Training-selected performance is optimistic; evaluation never selects thresholds.
- The initial fit origin differs across disjoint time blocks; blocks may have different lengths.
- Confidence intervals exclude process, liquidity and model uncertainty.

Quantiles use linear interpolation; SD uses n−1. Markout distributions use per-session available-unit means, with session and unit coverage retained. A confidence interval concerns the model's mean, not the range of future outcomes.
