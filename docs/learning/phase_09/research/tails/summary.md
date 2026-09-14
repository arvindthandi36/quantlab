# QuantLab synthetic research experiment

How do covariance-matched heavy tails affect option Expected Shortfall?

**Prediction registered before execution:** Covariance-matched t(5) shocks may worsen ES for a short gamma portfolio; normal VaR need not order the tails.

Status: complete. Pool: evaluation. Sessions per variant: 128. Root seed: 9900901.

Synthetic performance is not evidence of real-world alpha.

## normal

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| delta_var | GBP | 128/128 | 0.8601 | 0.8601 | 1.11459e-16 | 9.85164e-18 | 0.8601 | 0.8601 | 0.8601 | 0.8601 |
| es | GBP | 128/128 | 239.245 | 239.271 | 7.00081 | 0.61879 | 227.887 | 234.937 | 243.934 | 250.592 |
| es_minus_var | GBP | 128/128 | 84.8494 | 85.3677 | 4.91285 | 0.434239 | 76.437 | 81.5544 | 88.3641 | 91.6978 |
| full_minus_delta_var | GBP | 128/128 | 153.536 | 153.555 | 5.71608 | 0.505235 | 143.88 | 149.762 | 157.639 | 162.483 |
| mean_loss | GBP | 128/128 | 11.9212 | 11.8689 | 0.888945 | 0.0785724 | 10.4958 | 11.3498 | 12.5702 | 13.2415 |
| var | GBP | 128/128 | 154.396 | 154.415 | 5.71608 | 0.505235 | 144.74 | 150.622 | 158.499 | 163.343 |

Mean interval: {'confidence': 0.95, 'high': 240.46954927072656, 'low': 238.02060199475565, 'method': 'Student t mean'}
Bootstrap: {'estimate': 239.2450756327411, 'interval': {'confidence': 0.95, 'high': 240.3528686696335, 'low': 238.08316511560895, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 500, 'seed': 60105070272173411984120740440297579902394278368161355635201445262849945958632, 'standard_error': 0.6050977078700367}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': 227.88705194751407, 'probability_below': {'-0.25': 0.0, '-0.5': 0.0, '-1.0': 0.0, '0.0': 0.0}, 'tail_count': 7, 'worst': 223.69956886753403, 'worst_five_percent_mean': 226.30218853759337}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #82: 223.7; simulation seed 205063485072578736797253665183328571974089901201199569169547731332075892138387
- Run #124: 225.234; simulation seed 93355956159319196690343946856538996590674348616099680909572889371214614807451
- Run #16: 226.238; simulation seed 17631177041327382013051614503179969194921051338205936978830928840783446321929

## student_5

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| delta_var | GBP | 128/128 | 0.8601 | 0.8601 | 1.11459e-16 | 9.85164e-18 | 0.8601 | 0.8601 | 0.8601 | 0.8601 |
| es | GBP | 128/128 | 360.601 | 359.962 | 23.3456 | 2.06348 | 323.331 | 346.27 | 375.044 | 402.658 |
| es_minus_var | GBP | 128/128 | 200.279 | 199.231 | 20.9931 | 1.85554 | 166.943 | 187.161 | 212.834 | 238.891 |
| full_minus_delta_var | GBP | 128/128 | 159.461 | 159.241 | 7.34376 | 0.649103 | 146.466 | 154.904 | 163.826 | 171.947 |
| mean_loss | GBP | 128/128 | 11.2672 | 11.2885 | 1.56498 | 0.138326 | 8.75875 | 10.146 | 12.255 | 13.8252 |
| var | GBP | 128/128 | 160.321 | 160.101 | 7.34376 | 0.649103 | 147.326 | 155.764 | 164.686 | 172.807 |

Mean interval: {'confidence': 0.95, 'high': 364.6840898504732, 'low': 356.51757513399565, 'method': 'Student t mean'}
Bootstrap: {'estimate': 360.6008324922344, 'interval': {'confidence': 0.95, 'high': 364.68538979982344, 'low': 356.37242187923084, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 500, 'seed': 89448401624725293315316400992190080059768786990442439568621774335749451424511, 'standard_error': 2.0961041813370813}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': 323.3305816050696, 'probability_below': {'-0.25': 0.0, '-0.5': 0.0, '-1.0': 0.0, '0.0': 0.0}, 'tail_count': 7, 'worst': 298.6985667942487, 'worst_five_percent_mean': 313.2134966113833}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #47: 298.699; simulation seed 4853779244507632278552020385116837701125648166965137673998027725060542931627
- Run #26: 308.56; simulation seed 19546428864983486158832591833180148793477712961776857856024421465027628393081
- Run #87: 313.565; simulation seed 73679682600886565538959729129485696563057113513810281784643385195865488090901

## Paired: student_5 minus normal

Summary: {'available': 128, 'maximum': 174.17897317372348, 'mean': 121.35575685949334, 'mean_ci': {'confidence': 0.95, 'high': 125.20700388950809, 'low': 117.5045098294786, 'method': 'Student t mean'}, 'median': 119.84106258832449, 'minimum': 70.27012330634352, 'missing': 0, 'p05': 87.61770780224319, 'p25': 109.09965354824283, 'p75': 136.58826875929645, 'p95': 156.16355509508622, 'requested': 128, 'standard_deviation': 22.019130845961932, 'standard_error': 1.9462345921266953, 'variance': 484.84212321159225}
Bootstrap: {'estimate': 121.35575685949334, 'interval': {'confidence': 0.95, 'high': 125.14992127352323, 'low': 117.81922754305705, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete matched session pair', 'resamples': 500, 'seed': 76952852964267671230126294478027102368277714687943484210792678964571393407510, 'standard_error': 1.917582290154316}
Positive / negative / tied: 100.000% / 0.000% / 0.000%.
t = 62.3541; two-sided p = 4.1049e-97; paired standardised effect = 5.51138.
Paired two-sided t test: H0 E[D]=0; H1 E[D] differs from zero. Statistical significance is not strategy validity or practical value.

## Interpretation

normal: observed mean es=239.245; losing/negative outcomes 0.0%. student_5: observed mean es=360.601; losing/negative outcomes 0.0%. Compare the full distributions and paired uncertainty with the original hypothesis. These conditional model outcomes do not establish real-world alpha, safety or an optimal parameter. Interpretation remains reviewable.

## Limitations

- Synthetic executed starting portfolios; fixed assumptions, not forecasts.
- Normal/t distributions share Gaussian shocks; transformed returns differ.
- Sample-size variants use nested path prefixes; uncertainty excludes model error.
- Different horizons are explicitly unpaired; no false identical-environment claim.

Quantiles use linear interpolation; SD uses n−1. Markout distributions use per-session available-unit means, with session and unit coverage retained. A confidence interval concerns the model's mean, not the range of future outcomes.
