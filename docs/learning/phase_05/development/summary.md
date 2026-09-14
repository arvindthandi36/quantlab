# QuantLab synthetic research experiment

How do unchanged fixed and inventory-aware policies differ under the same weather?

**Prediction registered before execution:** Inventory-aware quoting reduces average absolute inventory; its mean net P&L advantage over fixed quoting is uncertain. Parameters and sample size are fixed before observing results.

Status: complete. Pool: development. Sessions per variant: 1600. Root seed: 20260911.

Synthetic performance is not evidence of real-world alpha.

## fixed

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average_absolute_inventory | units | 1600/1600 | 3.07439 | 3.02711 | 1.28172 | 0.0320429 | 1.09175 | 2.0489 | 4.03827 | 5.26292 |
| average_effective_spread | GBP/unit | 1600/1600 | 0.0346002 | 0.0347368 | 0.00436075 | 0.000109019 | 0.0271429 | 0.032069 | 0.0375 | 0.0413636 |
| average_inventory | units | 1600/1600 | -0.0656905 | -0.0940449 | 3.01684 | 0.0754211 | -4.83349 | -2.58142 | 2.42424 | 4.74189 |
| average_quoted_spread | GBP/unit | 1600/1600 | 0.0431951 | 0.0431813 | 0.00151136 | 3.77841e-05 | 0.0408087 | 0.0420941 | 0.0442503 | 0.0457134 |
| buy_fills | execution records | 1600/1600 | 7.8325 | 8 | 3.68499 | 0.0921248 | 2 | 5 | 10 | 14 |
| buy_units | units | 1600/1600 | 10.3831 | 10 | 4.42237 | 0.110559 | 3 | 7 | 13 | 18 |
| execution_edge | GBP | 1600/1600 | 0.394125 | 0.38 | 0.161458 | 0.00403644 | 0.16 | 0.28 | 0.49 | 0.695 |
| fees | GBP | 1600/1600 | 0.0207688 | 0.02 | 0.00723268 | 0.000180817 | 0.009 | 0.016 | 0.026 | 0.034 |
| fill_rate | fraction | 1600/1600 | 0.191519 | 0.19 | 0.0646071 | 0.00161518 | 0.0882095 | 0.144144 | 0.234318 | 0.306935 |
| final_inventory | units | 1600/1600 | -0.0025 | 0 | 4.73064 | 0.118266 | -7 | -4 | 4 | 7 |
| gross_realised_pnl | GBP | 1600/1600 | 0.200337 | 0.19 | 0.19119 | 0.00477974 | -0.06 | 0.06 | 0.31 | 0.55 |
| inventory_movement | GBP | 1600/1600 | -0.190984 | -0.16 | 0.23268 | 0.005817 | -0.615 | -0.325 | -0.035 | 0.13525 |
| markout_1 | GBP/unit | 1599/1600 | 0.00574029 | 0.00571429 | 0.00475857 | 0.000119002 | -0.00222222 | 0.0025 | 0.00868993 | 0.0135029 |
| markout_20 | GBP/unit | 1599/1600 | 0.00819936 | 0.00954545 | 0.0125119 | 0.000312894 | -0.0143474 | 0.00220486 | 0.0162772 | 0.0255182 |
| markout_5 | GBP/unit | 1600/1600 | 0.00698818 | 0.0075 | 0.00688243 | 0.000172061 | -0.00526389 | 0.00294118 | 0.0116667 | 0.0175 |
| maximum_absolute_inventory | units | 1600/1600 | 5.88187 | 6 | 1.40905 | 0.0352262 | 3 | 5 | 7 | 7 |
| maximum_drawdown | GBP | 1600/1600 | 0.272317 | 0.25 | 0.16172 | 0.00404301 | 0.06 | 0.14475 | 0.3695 | 0.56025 |
| net_pnl | GBP | 1600/1600 | 0.182372 | 0.1885 | 0.255528 | 0.00638821 | -0.2591 | 0.032 | 0.34225 | 0.59505 |
| realised_pnl | GBP | 1600/1600 | 0.179569 | 0.166 | 0.186886 | 0.00467215 | -0.079 | 0.047 | 0.289 | 0.52005 |
| rms_inventory | units | 1600/1600 | 3.5633 | 3.62644 | 1.30104 | 0.032526 | 1.43605 | 2.51516 | 4.58181 | 5.6612 |
| sell_fills | execution records | 1600/1600 | 7.69062 | 7 | 3.40711 | 0.0851778 | 3 | 5 | 10 | 14 |
| sell_units | units | 1600/1600 | 10.3856 | 10 | 4.21759 | 0.10544 | 3 | 7 | 13 | 17 |
| turnover | GBP | 1600/1600 | 2076.91 | 2000.4 | 723.256 | 18.0814 | 900.319 | 1599.29 | 2598.32 | 3399.87 |
| two_sided_quote_time_fraction | fraction | 1600/1600 | 0.765322 | 0.815039 | 0.159893 | 0.00399733 | 0.427859 | 0.688858 | 0.879675 | 0.947351 |
| unrealised_pnl | GBP | 1600/1600 | 0.00280313 | 0.01 | 0.156701 | 0.00391751 | -0.29 | -0.06 | 0.08125 | 0.24 |

Mean interval: {'confidence': 0.95, 'high': 0.19490202587198746, 'low': 0.16984172412801246, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.18237187499999996, 'interval': {'confidence': 0.95, 'high': 0.194352453125, 'low': 0.17012303125000003, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 14761565359702914036206387565707142974635071493977376372979716448930645117508, 'standard_error': 0.0062615231310238955}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -0.2591, 'probability_below': {'-0.25': 0.0525, '-0.5': 0.01, '-1.0': 0.0, '0.0': 0.208125}, 'tail_count': 80, 'worst': -0.923, 'worst_five_percent_mean': -0.4084125}

Exploratory correlations (not causal effects):

- average_absolute_inventory vs net_pnl: {'available': 1600, 'correlation': -0.31362852130735047, 'covariance': -0.10271800606958743, 'missing': 0}
- fill_rate vs markout_1: {'available': 1599, 'correlation': -0.07106043010132033, 'covariance': -2.183539449887502e-05, 'missing': 1}
- maximum_absolute_inventory vs maximum_drawdown: {'available': 1600, 'correlation': 0.7087502095599804, 'covariance': 0.1615039958567855, 'missing': 0}
- turnover vs fees: {'available': 1600, 'correlation': 0.9999994863839975, 'covariance': 5.231078777829894, 'missing': 0}

Worst primary outcomes:

- Run #1171: -0.923; simulation seed 112353891322922293821531925947736417456662186260260542656568240613111912381080
- Run #853: -0.899; simulation seed 57861505459782766139968436361208919475915025851989966118251865931604178731910
- Run #1567: -0.801; simulation seed 182161522415855053184014675537557290686721564253024379811227821161624778609242

## inventory

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average_absolute_inventory | units | 1600/1600 | 1.78947 | 1.75279 | 0.6654 | 0.016635 | 0.801506 | 1.29957 | 2.21525 | 2.90169 |
| average_effective_spread | GBP/unit | 1600/1600 | 0.0363078 | 0.0364286 | 0.00462051 | 0.000115513 | 0.02875 | 0.0332 | 0.0392659 | 0.0435729 |
| average_inventory | units | 1600/1600 | -0.0891556 | -0.0943067 | 1.31703 | 0.0329258 | -2.23421 | -0.997229 | 0.849189 | 2.0759 |
| average_quoted_spread | GBP/unit | 1600/1600 | 0.0452456 | 0.0452113 | 0.00145043 | 3.62607e-05 | 0.0429885 | 0.0442523 | 0.0461521 | 0.0476871 |
| buy_fills | execution records | 1600/1600 | 9.44125 | 9 | 3.47172 | 0.086793 | 4 | 7 | 12 | 16 |
| buy_units | units | 1600/1600 | 12.5113 | 12 | 4.12877 | 0.103219 | 6 | 10 | 15 | 19 |
| execution_edge | GBP | 1600/1600 | 0.437994 | 0.41 | 0.181837 | 0.00454592 | 0.18 | 0.305 | 0.55125 | 0.76 |
| fees | GBP | 1600/1600 | 0.0250381 | 0.025 | 0.0078571 | 0.000196427 | 0.012 | 0.019 | 0.03 | 0.038 |
| fill_rate | fraction | 1600/1600 | 0.21291 | 0.210084 | 0.0687387 | 0.00171847 | 0.1 | 0.163793 | 0.258621 | 0.330508 |
| final_inventory | units | 1600/1600 | -0.015625 | 0 | 2.55234 | 0.0638086 | -4 | -2 | 2 | 4 |
| gross_realised_pnl | GBP | 1600/1600 | -0.0804562 | 0.01 | 0.354595 | 0.00886489 | -0.82 | -0.21 | 0.14 | 0.31 |
| inventory_movement | GBP | 1600/1600 | -0.548884 | -0.43 | 0.454466 | 0.0113617 | -1.525 | -0.735 | -0.225 | -0.065 |
| markout_1 | GBP/unit | 1600/1600 | 0.0022194 | 0.0025431 | 0.00599129 | 0.000149782 | -0.00833333 | -0.00130721 | 0.0062125 | 0.011 |
| markout_20 | GBP/unit | 1600/1600 | -0.00445713 | -0.000555556 | 0.01831 | 0.000457751 | -0.039253 | -0.0135877 | 0.00796591 | 0.0177273 |
| markout_5 | GBP/unit | 1600/1600 | 0.000859833 | 0.00174457 | 0.00868345 | 0.000217086 | -0.0148304 | -0.00414511 | 0.00675874 | 0.0135714 |
| maximum_absolute_inventory | units | 1600/1600 | 4.76063 | 5 | 1.40073 | 0.0350183 | 2 | 4 | 6 | 7 |
| maximum_drawdown | GBP | 1600/1600 | 0.412709 | 0.284 | 0.388651 | 0.00971629 | 0.05 | 0.136 | 0.563 | 1.2081 |
| net_pnl | GBP | 1600/1600 | -0.135929 | -0.023 | 0.4026 | 0.010065 | -0.9781 | -0.29375 | 0.12 | 0.29115 |
| realised_pnl | GBP | 1600/1600 | -0.105494 | -0.011 | 0.356104 | 0.00890261 | -0.848 | -0.23425 | 0.117 | 0.2811 |
| rms_inventory | units | 1600/1600 | 2.23422 | 2.20457 | 0.73512 | 0.018378 | 1.11534 | 1.6819 | 2.72818 | 3.45547 |
| sell_fills | execution records | 1600/1600 | 9.15062 | 9 | 3.36917 | 0.0842292 | 4 | 7 | 11 | 15 |
| sell_units | units | 1600/1600 | 12.5269 | 12 | 4.13249 | 0.103312 | 6 | 10 | 15 | 20 |
| turnover | GBP | 1600/1600 | 2503.95 | 2498.75 | 785.73 | 19.6433 | 1200.21 | 1901.41 | 3004.23 | 3800.9 |
| two_sided_quote_time_fraction | fraction | 1600/1600 | 0.838707 | 0.842778 | 0.0685048 | 0.00171262 | 0.714471 | 0.796898 | 0.886661 | 0.942767 |
| unrealised_pnl | GBP | 1600/1600 | -0.0304344 | 0 | 0.151212 | 0.0037803 | -0.31 | -0.03125 | 0.02 | 0.105 |

Mean interval: {'confidence': 0.95, 'high': -0.11618679028077672, 'low': -0.15567070971922325, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.13592875, 'interval': {'confidence': 0.95, 'high': -0.11737037500000001, 'low': -0.15549167187499996, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 42565811603153781437434037447189251073996362825844538316417496229407014428376, 'standard_error': 0.009928612388071346}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -0.9781, 'probability_below': {'-0.25': 0.278125, '-0.5': 0.145625, '-1.0': 0.0475, '0.0': 0.540625}, 'tail_count': 80, 'worst': -2.973, 'worst_five_percent_mean': -1.3282875}

Exploratory correlations (not causal effects):

- average_absolute_inventory vs net_pnl: {'available': 1600, 'correlation': -0.6480180090284434, 'covariance': -0.1735974061600919, 'missing': 0}
- fill_rate vs markout_1: {'available': 1600, 'correlation': -0.18448948277174312, 'covariance': -7.597893984325269e-05, 'missing': 0}
- maximum_absolute_inventory vs maximum_drawdown: {'available': 1600, 'correlation': 0.7573601847609255, 'covariance': 0.41230437187304575, 'missing': 0}
- turnover vs fees: {'available': 1600, 'correlation': 0.9999969854733177, 'covariance': 6.173543053689807, 'missing': 0}

Worst primary outcomes:

- Run #364: -2.973; simulation seed 171698749878988825947678934792317802269864882465034216956146004400060017118772
- Run #1587: -2.117; simulation seed 22019445420066451417431790154715134145489428151571381930931847185653980532418
- Run #841: -2.022; simulation seed 185331220059999603717345589467890006901439255216720553622062230771301844716388

## Paired: inventory minus fixed

Summary: {'available': 1600, 'maximum': 0.645, 'mean': -0.318300625, 'mean_ci': {'confidence': 0.95, 'high': -0.2991663900804868, 'low': -0.3374348599195132, 'method': 'Student t mean'}, 'median': -0.23399999999999999, 'minimum': -2.552, 'missing': 0, 'p05': -1.098, 'p25': -0.47000000000000003, 'p75': -0.066, 'p95': 0.1363499999999997, 'requested': 1600, 'standard_deviation': 0.3902061788828867, 'standard_error': 0.009755154472072168, 'variance': 0.15226086203838338}
Bootstrap: {'estimate': -0.318300625, 'interval': {'confidence': 0.95, 'high': -0.30015275, 'low': -0.337579640625, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete matched session pair', 'resamples': 2000, 'seed': 22702083064044421242913089107780812204255450978412941285707644077297361631076, 'standard_error': 0.009624900748380873}
Positive / negative / tied: 15.812% / 84.125% / 0.062%.
t = -32.629; two-sided p = 2.02578e-179; paired standardised effect = -0.815724.
Paired two-sided t test: H0 E[D]=0; H1 E[D] differs from zero. Statistical significance is not strategy validity or practical value.

## Interpretation

fixed: observed mean net_pnl=0.182372; losing/negative outcomes 20.8%. inventory: observed mean net_pnl=-0.135929; losing/negative outcomes 54.1%. Compare the full distributions and paired uncertainty with the original hypothesis. These conditional model outcomes do not establish real-world alpha, safety or an optimal parameter. Interpretation remains reviewable.

## Limitations

- Synthetic performance is not evidence of real-world alpha.
- Independent sessions conditional on one model; uncertainty excludes model error.
- Exploratory metrics/intervals are not corrected for multiple testing.
- Missing metrics are reported with coverage, not replaced by zero.

Quantiles use linear interpolation; SD uses n−1. Markout distributions use per-session available-unit means, with session and unit coverage retained. A confidence interval concerns the model's mean, not the range of future outcomes.
