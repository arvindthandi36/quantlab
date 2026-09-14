# QuantLab synthetic research experiment

Does causal refitting improve this fixed strategy out of sample?

**Prediction registered before execution:** Refitting changes hedge estimates and turnover; improvement is not guaranteed.

Status: complete. Pool: evaluation. Sessions per variant: 32. Root seed: 10101001.

Synthetic performance is not evidence of real-world alpha.

## fixed

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average_trade | GBP | 32/32 | 0.765514 | 0.874833 | 1.11157 | 0.196499 | -1.06437 | 0.10125 | 1.381 | 2.31982 |
| costs | GBP | 32/32 | 1.64625 | 1.62 | 0.361268 | 0.0638638 | 1.146 | 1.44 | 1.785 | 2.241 |
| drawdown | GBP | 32/32 | 6.28953 | 5.23 | 4.80447 | 0.849318 | 2.84075 | 3.94625 | 7.38 | 10.7305 |
| max_gross | GBP | 32/32 | 948.638 | 958.03 | 60.0567 | 10.6166 | 836.708 | 908.97 | 1000.81 | 1016.85 |
| max_imbalance | GBP | 32/32 | 462.621 | 497.225 | 74.1818 | 13.1136 | 336.753 | 425.481 | 507.746 | 538.528 |
| mean_entry_z | units | 32/32 | 0.100357 | 0.208999 | 0.80981 | 0.143156 | -1.11694 | -0.38238 | 0.732125 | 1.2038 |
| mean_exit_z | units | 32/32 | -0.00687711 | -0.128508 | 0.412322 | 0.0728889 | -0.489654 | -0.272573 | 0.191021 | 0.766708 |
| mean_holding | observations | 32/32 | 11.7081 | 11.5143 | 3.23351 | 0.57161 | 6.8875 | 9.08929 | 14.0833 | 16.89 |
| median_trade | GBP | 32/32 | 0.853906 | 0.9425 | 1.01365 | 0.179189 | -0.55 | 0.0825 | 1.685 | 2.0565 |
| net_pnl | GBP | 32/32 | 4.72125 | 4.8 | 6.4569 | 1.14143 | -5.1375 | 0.5325 | 8.36 | 15.805 |
| probability_loss | fraction | 32/32 | 0.326228 | 0.333333 | 0.215678 | 0.0381268 | 0 | 0.166667 | 0.446429 | 0.704167 |
| residual_inventory | units | 32/32 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| return_on_capital | fraction | 32/32 | 0.000472125 | 0.00048 | 0.00064569 | 0.000114143 | -0.00051375 | 5.325e-05 | 0.000836 | 0.0015805 |
| trade_count | units | 32/32 | 6 | 6 | 1.19137 | 0.210606 | 4 | 5 | 7 | 8 |
| turnover | GBP | 32/32 | 10938.7 | 10830.2 | 2299.59 | 406.513 | 7594.62 | 9272.43 | 11750 | 14456.6 |
| win_rate | fraction | 32/32 | 0.667522 | 0.666667 | 0.220723 | 0.0390188 | 0.295833 | 0.5 | 0.833333 | 1 |
| worst_trade | GBP | 32/32 | -2.57687 | -2.38 | 2.7603 | 0.487957 | -5.4025 | -3.4575 | -1.36 | 0.57 |

Mean interval: {'confidence': 0.95, 'high': 7.049211116830148, 'low': 2.393288883169851, 'method': 'Student t mean'}
Bootstrap: {'estimate': 4.7212499999999995, 'interval': {'confidence': 0.95, 'high': 6.732718749999999, 'low': 2.6702109375000003, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 500, 'seed': 35168668522453630829099416922401630896988329562611378542901004748598323755884, 'standard_error': 1.0928992380273483}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -5.1375, 'probability_below': {'-0.25': 0.21875, '-0.5': 0.1875, '-1.0': 0.1875, '0.0': 0.21875}, 'tail_count': 2, 'worst': -9.18, 'worst_five_percent_mean': -7.365}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #14: -9.18; simulation seed 123828951959255198781572571056319414287509690925468688906610242719703587353357
- Run #12: -5.55; simulation seed 101084400728854829273848255373990313823795274882863305466535216531333085500643
- Run #26: -4.8; simulation seed 6656603674815097344247586247422561347208740039760328688015831756500931529221

## walk_forward

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average_trade | GBP | 32/32 | 0.76668 | 0.692778 | 0.878048 | 0.155218 | -0.475571 | 0.242643 | 1.23775 | 2.39275 |
| costs | GBP | 32/32 | 1.75687 | 1.71 | 0.418056 | 0.0739025 | 1.2 | 1.44 | 1.9725 | 2.5305 |
| drawdown | GBP | 32/32 | 5.71547 | 5.18 | 2.56918 | 0.45417 | 2.721 | 4.005 | 7.00875 | 10.5595 |
| max_gross | GBP | 32/32 | 989.52 | 993.635 | 31.0078 | 5.48146 | 941.046 | 966.093 | 1010.83 | 1035.94 |
| max_imbalance | GBP | 32/32 | 527.135 | 510.356 | 39.2878 | 6.94518 | 482.164 | 499.497 | 553 | 600.621 |
| mean_entry_z | units | 32/32 | -0.00520195 | 0.0153136 | 0.899254 | 0.158967 | -1.15446 | -0.710457 | 0.513086 | 1.65212 |
| mean_exit_z | units | 32/32 | -0.0231152 | 0.017478 | 0.354885 | 0.0627355 | -0.515135 | -0.249843 | 0.165075 | 0.565593 |
| mean_holding | observations | 32/32 | 11.7355 | 10.8125 | 3.46812 | 0.613083 | 7.65 | 8.77857 | 14.95 | 17.3071 |
| median_trade | GBP | 32/32 | 0.971406 | 0.7625 | 1.04771 | 0.18521 | -0.30075 | 0.2575 | 1.4875 | 3.0425 |
| net_pnl | GBP | 32/32 | 4.86469 | 4.04 | 5.624 | 0.994192 | -2.9775 | 1.3025 | 8.78 | 15.5505 |
| probability_loss | fraction | 32/32 | 0.312847 | 0.333333 | 0.173087 | 0.0305978 | 0 | 0.191667 | 0.428571 | 0.5 |
| residual_inventory | units | 32/32 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| return_on_capital | fraction | 32/32 | 0.000486469 | 0.000404 | 0.0005624 | 9.94192e-05 | -0.00029775 | 0.00013025 | 0.000878 | 0.00155505 |
| trade_count | units | 32/32 | 6.4375 | 6 | 1.38977 | 0.245678 | 5 | 5.75 | 7 | 9 |
| turnover | GBP | 32/32 | 11674.4 | 11039.4 | 2667.63 | 471.575 | 8635.96 | 9871.71 | 13171.1 | 16675.1 |
| win_rate | fraction | 32/32 | 0.687153 | 0.666667 | 0.173087 | 0.0305978 | 0.5 | 0.571429 | 0.808333 | 1 |
| worst_trade | GBP | 32/32 | -2.36125 | -2.09 | 2.23491 | 0.39508 | -6.586 | -3.255 | -0.715 | 0.543 |

Mean interval: {'confidence': 0.95, 'high': 6.892355665170461, 'low': 2.83701933482954, 'method': 'Student t mean'}
Bootstrap: {'estimate': 4.8646875000000005, 'interval': {'confidence': 0.95, 'high': 6.637648437499999, 'low': 2.9291484375000003, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 500, 'seed': 79483177262054865963025119815827615800692698964621166834829909119867677518035, 'standard_error': 0.9713966344508985}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -2.9775, 'probability_below': {'-0.25': 0.1875, '-0.5': 0.1875, '-1.0': 0.15625, '0.0': 0.1875}, 'tail_count': 2, 'worst': -3.8899999999999997, 'worst_five_percent_mean': -3.75}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #3: -3.89; simulation seed 51936309435518958547303392581121249216627170702337495010644927431905602189081
- Run #7: -3.61; simulation seed 230991559526475809458651298094922290659496134162060821961009975195703010210291
- Run #31: -2.46; simulation seed 71450223345182876387589485312320564874487800399983597899965813547147288796497

## Paired: walk_forward minus fixed

Summary: {'available': 32, 'maximum': 23.59, 'mean': 0.1434375000000001, 'mean_ci': {'confidence': 0.95, 'high': 2.7919020518950837, 'low': -2.5050270518950835, 'method': 'Student t mean'}, 'median': 0.08499999999999952, 'minimum': -20.94, 'missing': 0, 'p05': -7.425, 'p25': -4.5075, 'p75': 3.710000000000001, 'p95': 9.675, 'requested': 32, 'standard_deviation': 7.345858877022416, 'standard_error': 1.2985766563954868, 'variance': 53.96164264112903}
Bootstrap: {'estimate': 0.1434375000000001, 'interval': {'confidence': 0.95, 'high': 2.721218749999999, 'low': -2.3093359374999993, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete matched session pair', 'resamples': 500, 'seed': 98082103786998382441123347866966726759382413933310851742054996763361927029121, 'standard_error': 1.3193316925803347}
Positive / negative / tied: 53.125% / 46.875% / 0.000%.
t = 0.110457; two-sided p = 0.912759; paired standardised effect = 0.0195263.
Paired two-sided t test: H0 E[D]=0; H1 E[D] differs from zero. Statistical significance is not strategy validity or practical value.

## Interpretation

fixed: observed mean net_pnl=4.72125; losing/negative outcomes 21.9%. walk_forward: observed mean net_pnl=4.86469; losing/negative outcomes 18.8%. Compare the full distributions and paired uncertainty with the original hypothesis. These conditional model outcomes do not establish real-world alpha, safety or an optimal parameter. Interpretation remains reviewable.

## Limitations

- Synthetic results do not establish real-market alpha.
- Training-selected performance is optimistic; evaluation never selects thresholds.
- The initial fit origin differs across disjoint time blocks; blocks may have different lengths.
- Confidence intervals exclude process, liquidity and model uncertainty.

Quantiles use linear interpolation; SD uses n−1. Markout distributions use per-session available-unit means, with session and unit coverage retained. A confidence interval concerns the model's mean, not the range of future outcomes.
