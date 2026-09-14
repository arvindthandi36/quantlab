# QuantLab synthetic research experiment

How do unchanged fixed and inventory-aware policies differ under the same weather?

**Prediction registered before execution:** Inventory-aware quoting reduces average absolute inventory; its mean net P&L advantage over fixed quoting is uncertain. The unchanged Phase 4 parameters are frozen and no development sweep result changes them.

Status: complete. Pool: evaluation. Sessions per variant: 1000. Root seed: 20260911.

Synthetic performance is not evidence of real-world alpha.

## fixed

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average_absolute_inventory | units | 1000/1000 | 3.09813 | 3.00448 | 1.32712 | 0.0419671 | 1.06029 | 2.0805 | 4.09669 | 5.34548 |
| average_effective_spread | GBP/unit | 1000/1000 | 0.0345627 | 0.0347619 | 0.00442992 | 0.000140086 | 0.0271429 | 0.032 | 0.0371429 | 0.0414286 |
| average_inventory | units | 1000/1000 | -0.271031 | -0.3128 | 3.0666 | 0.0969743 | -5.03505 | -2.7918 | 2.18673 | 4.78736 |
| average_quoted_spread | GBP/unit | 1000/1000 | 0.0431671 | 0.0431948 | 0.00155807 | 4.92705e-05 | 0.0405212 | 0.0420926 | 0.044226 | 0.0456815 |
| buy_fills | execution records | 1000/1000 | 7.483 | 7 | 3.65281 | 0.115512 | 2 | 5 | 10 | 14 |
| buy_units | units | 1000/1000 | 9.98 | 10 | 4.47097 | 0.141385 | 3 | 7 | 13 | 18 |
| execution_edge | GBP | 1000/1000 | 0.38813 | 0.37 | 0.164072 | 0.00518842 | 0.16 | 0.275 | 0.485 | 0.68025 |
| fees | GBP | 1000/1000 | 0.020415 | 0.02 | 0.00741969 | 0.000234631 | 0.009 | 0.015 | 0.025 | 0.034 |
| fill_rate | fraction | 1000/1000 | 0.189294 | 0.185841 | 0.0664062 | 0.00209995 | 0.0842871 | 0.142857 | 0.23172 | 0.305137 |
| final_inventory | units | 1000/1000 | -0.455 | -1 | 4.74853 | 0.150162 | -7 | -5 | 4 | 7 |
| gross_realised_pnl | GBP | 1000/1000 | 0.18909 | 0.17 | 0.193225 | 0.00611032 | -0.09 | 0.0575 | 0.31 | 0.52 |
| inventory_movement | GBP | 1000/1000 | -0.209205 | -0.175 | 0.2356 | 0.00745033 | -0.65125 | -0.35 | -0.04 | 0.12 |
| markout_1 | GBP/unit | 999/1000 | 0.00586079 | 0.00575 | 0.00496916 | 0.000157217 | -0.00168182 | 0.0025 | 0.009 | 0.0144349 |
| markout_20 | GBP/unit | 999/1000 | 0.00747837 | 0.00875 | 0.0124435 | 0.000393694 | -0.0143375 | 0.00122024 | 0.0152778 | 0.0241731 |
| markout_5 | GBP/unit | 1000/1000 | 0.0070867 | 0.0075 | 0.00728049 | 0.000230229 | -0.00534608 | 0.00296429 | 0.0117857 | 0.0180492 |
| maximum_absolute_inventory | units | 1000/1000 | 5.839 | 6 | 1.45781 | 0.0460999 | 3 | 5 | 7 | 7 |
| maximum_drawdown | GBP | 1000/1000 | 0.274713 | 0.251 | 0.166496 | 0.00526507 | 0.055 | 0.13925 | 0.3735 | 0.58415 |
| net_pnl | GBP | 1000/1000 | 0.15851 | 0.17 | 0.26386 | 0.00834399 | -0.34605 | 0.01375 | 0.329 | 0.56905 |
| realised_pnl | GBP | 1000/1000 | 0.168675 | 0.147 | 0.188888 | 0.00597316 | -0.1052 | 0.036 | 0.2855 | 0.48905 |
| rms_inventory | units | 1000/1000 | 3.59421 | 3.59047 | 1.35477 | 0.0428415 | 1.42347 | 2.51909 | 4.62726 | 5.74 |
| sell_fills | execution records | 1000/1000 | 7.817 | 8 | 3.53893 | 0.111911 | 2 | 5 | 10 | 14 |
| sell_units | units | 1000/1000 | 10.435 | 10 | 4.33712 | 0.137152 | 3 | 7 | 13 | 18 |
| turnover | GBP | 1000/1000 | 2041.55 | 1999.93 | 741.971 | 23.4632 | 900.361 | 1500.64 | 2500.13 | 3399.44 |
| two_sided_quote_time_fraction | fraction | 1000/1000 | 0.755637 | 0.811683 | 0.175224 | 0.00554106 | 0.388793 | 0.673006 | 0.881851 | 0.946177 |
| unrealised_pnl | GBP | 1000/1000 | -0.010165 | 0.01 | 0.160775 | 0.00508415 | -0.35 | -0.06 | 0.08 | 0.22025 |

Mean interval: {'confidence': 0.95, 'high': 0.17488375834623687, 'low': 0.1421362416537631, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.15850999999999998, 'interval': {'confidence': 0.95, 'high': 0.174828525, 'low': 0.142119525, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 30122129462042358097189527162122711876870430264871250804082705237828653697694, 'standard_error': 0.008393366094311407}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -0.34604999999999997, 'probability_below': {'-0.25': 0.072, '-0.5': 0.014, '-1.0': 0.0, '0.0': 0.232}, 'tail_count': 50, 'worst': -0.716, 'worst_five_percent_mean': -0.4677}

Exploratory correlations (not causal effects):

- average_absolute_inventory vs net_pnl: {'available': 1000, 'correlation': -0.38202165882388767, 'covariance': -0.1337736200151051, 'missing': 0}
- fill_rate vs markout_1: {'available': 999, 'correlation': -0.08142984253988617, 'covariance': -2.6792756783951722e-05, 'missing': 1}
- maximum_absolute_inventory vs maximum_drawdown: {'available': 1000, 'correlation': 0.7153262265795405, 'covariance': 0.1736234164164164, 'missing': 0}
- turnover vs fees: {'available': 1000, 'correlation': 0.9999995510175159, 'covariance': 5.505192526926926, 'missing': 0}

Worst primary outcomes:

- Run #83: -0.716; simulation seed 213784530665346043537354841796936441057077261688185306632739253664375158897585
- Run #96: -0.671; simulation seed 196118185018177131077072151949794626712003084051476168662514575919126901445191
- Run #77: -0.617; simulation seed 164279276442642384964161944793024601857228098747610839769753229991956878105199

## inventory

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average_absolute_inventory | units | 1000/1000 | 1.79332 | 1.72368 | 0.68576 | 0.0216856 | 0.782407 | 1.28169 | 2.27166 | 3.01446 |
| average_effective_spread | GBP/unit | 1000/1000 | 0.0362462 | 0.0361325 | 0.00474977 | 0.000150201 | 0.0288868 | 0.03323 | 0.0393333 | 0.0441176 |
| average_inventory | units | 1000/1000 | -0.174693 | -0.207434 | 1.33956 | 0.0423607 | -2.36778 | -1.08216 | 0.765237 | 2.05827 |
| average_quoted_spread | GBP/unit | 1000/1000 | 0.0452392 | 0.0451254 | 0.00171661 | 5.4284e-05 | 0.0428118 | 0.0441269 | 0.0462789 | 0.0477139 |
| buy_fills | execution records | 1000/1000 | 9.392 | 9 | 3.53367 | 0.111744 | 4 | 7 | 12 | 15 |
| buy_units | units | 1000/1000 | 12.454 | 12 | 4.18586 | 0.132368 | 6 | 10 | 15 | 19 |
| execution_edge | GBP | 1000/1000 | 0.436255 | 0.415 | 0.181853 | 0.00575071 | 0.17 | 0.305 | 0.545 | 0.755 |
| fees | GBP | 1000/1000 | 0.025045 | 0.025 | 0.00790604 | 0.000250011 | 0.013 | 0.02 | 0.03 | 0.038 |
| fill_rate | fraction | 1000/1000 | 0.213244 | 0.211864 | 0.0694107 | 0.00219496 | 0.108333 | 0.166667 | 0.258621 | 0.327434 |
| final_inventory | units | 1000/1000 | -0.137 | 0 | 2.45973 | 0.0777836 | -4 | -2 | 1 | 4 |
| gross_realised_pnl | GBP | 1000/1000 | -0.1117 | 0.01 | 0.400388 | 0.0126614 | -0.8815 | -0.2525 | 0.14 | 0.31 |
| inventory_movement | GBP | 1000/1000 | -0.57242 | -0.445 | 0.474338 | 0.0149999 | -1.45025 | -0.785 | -0.215 | -0.06 |
| markout_1 | GBP/unit | 1000/1000 | 0.00218401 | 0.00285714 | 0.00629993 | 0.000199221 | -0.00950119 | -0.00166667 | 0.00625 | 0.0116708 |
| markout_20 | GBP/unit | 1000/1000 | -0.00567694 | -0.00195048 | 0.018176 | 0.000574775 | -0.0421892 | -0.015 | 0.00709821 | 0.0175114 |
| markout_5 | GBP/unit | 1000/1000 | 0.000905658 | 0.00218254 | 0.00929037 | 0.000293787 | -0.015758 | -0.00442842 | 0.00733824 | 0.0134342 |
| maximum_absolute_inventory | units | 1000/1000 | 4.793 | 5 | 1.41639 | 0.0447901 | 2 | 4 | 6 | 7 |
| maximum_drawdown | GBP | 1000/1000 | 0.438723 | 0.2815 | 0.422973 | 0.0133756 | 0.047 | 0.12975 | 0.607 | 1.2666 |
| net_pnl | GBP | 1000/1000 | -0.16121 | -0.026 | 0.430234 | 0.0136052 | -1.02405 | -0.33675 | 0.126 | 0.2991 |
| realised_pnl | GBP | 1000/1000 | -0.136745 | -0.0115 | 0.402018 | 0.0127129 | -0.91515 | -0.27725 | 0.12325 | 0.2811 |
| rms_inventory | units | 1000/1000 | 2.24092 | 2.18741 | 0.755759 | 0.0238992 | 1.06193 | 1.68224 | 2.78281 | 3.54843 |
| sell_fills | execution records | 1000/1000 | 9.244 | 9 | 3.32619 | 0.105183 | 4 | 7 | 11 | 15 |
| sell_units | units | 1000/1000 | 12.591 | 13 | 4.09347 | 0.129447 | 6 | 10 | 15 | 19 |
| turnover | GBP | 1000/1000 | 2504.77 | 2500.28 | 790.815 | 25.0078 | 1299.82 | 1998.43 | 3002.89 | 3801.74 |
| two_sided_quote_time_fraction | fraction | 1000/1000 | 0.838992 | 0.842961 | 0.0670832 | 0.00212136 | 0.724857 | 0.796211 | 0.885517 | 0.939853 |
| unrealised_pnl | GBP | 1000/1000 | -0.024465 | 0 | 0.131939 | 0.00417227 | -0.2605 | -0.03 | 0.02 | 0.1005 |

Mean interval: {'confidence': 0.95, 'high': -0.13451198008330667, 'low': -0.18790801991669331, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.16121, 'interval': {'confidence': 0.95, 'high': -0.13564095, 'low': -0.18952549999999996, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 30521730631250932512490350898440101851919827374144143321892332125785287046854, 'standard_error': 0.013881258754528523}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.02405, 'probability_below': {'-0.25': 0.306, '-0.5': 0.18, '-1.0': 0.052, '0.0': 0.541}, 'tail_count': 50, 'worst': -2.606, 'worst_five_percent_mean': -1.3848200000000004}

Exploratory correlations (not causal effects):

- average_absolute_inventory vs net_pnl: {'available': 1000, 'correlation': -0.6850489723271767, 'covariance': -0.20211476675805012, 'missing': 0}
- fill_rate vs markout_1: {'available': 1000, 'correlation': -0.26625616342207487, 'covariance': -0.00011642901629871338, 'missing': 0}
- maximum_absolute_inventory vs maximum_drawdown: {'available': 1000, 'correlation': 0.7601025904559827, 'covariance': 0.455373034034034, 'missing': 0}
- turnover vs fees: {'available': 1000, 'correlation': 0.9999966284272561, 'covariance': 6.252193217217217, 'missing': 0}

Worst primary outcomes:

- Run #9: -2.606; simulation seed 103294260752327872464015633776233676025253411146473416695055922186794527873369
- Run #96: -2.324; simulation seed 196118185018177131077072151949794626712003084051476168662514575919126901445191
- Run #758: -2.136; simulation seed 5782535336731283779859921848227796006574355723424148394217503186162103058787

## Paired: inventory minus fixed

Summary: {'available': 1000, 'maximum': 0.544, 'mean': -0.31972, 'mean_ci': {'confidence': 0.95, 'high': -0.29611675877861293, 'low': -0.3433232412213871, 'method': 'Student t mean'}, 'median': -0.22199999999999998, 'minimum': -2.294, 'missing': 0, 'p05': -1.0553500000000002, 'p25': -0.5037499999999999, 'p75': -0.05875, 'p95': 0.11504999999999994, 'requested': 1000, 'standard_deviation': 0.38036194974367876, 'standard_error': 0.012028100964525232, 'variance': 0.14467521281281281}
Bootstrap: {'estimate': -0.31972, 'interval': {'confidence': 0.95, 'high': -0.29646140000000004, 'low': -0.34343742499999996, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete matched session pair', 'resamples': 2000, 'seed': 51004225178892715583040299523685753221163049508141213346907542163187863874524, 'standard_error': 0.012037118897602886}
Positive / negative / tied: 14.900% / 84.900% / 0.200%.
t = -26.5811; two-sided p = 3.62184e-118; paired standardised effect = -0.840568.
Paired two-sided t test: H0 E[D]=0; H1 E[D] differs from zero. Statistical significance is not strategy validity or practical value.

## Interpretation

fixed: observed mean net_pnl=0.15851; losing/negative outcomes 23.2%. inventory: observed mean net_pnl=-0.16121; losing/negative outcomes 54.1%. Compare the full distributions and paired uncertainty with the original hypothesis. These conditional model outcomes do not establish real-world alpha, safety or an optimal parameter. Interpretation remains reviewable.

## Limitations

- Synthetic performance is not evidence of real-world alpha.
- Independent sessions conditional on one model; uncertainty excludes model error.
- Exploratory metrics/intervals are not corrected for multiple testing.
- Missing metrics are reported with coverage, not replaced by zero.

Quantiles use linear interpolation; SD uses n−1. Markout distributions use per-session available-unit means, with session and unit coverage retained. A confidence interval concerns the model's mean, not the range of future outcomes.
