# QuantLab synthetic research experiment

Phase 8 volatility: one long ATM call, multiplier 100, twenty ACT/365 days

**Prediction registered before execution:** At fixed 20% quote volatility, higher underlying process variance should raise average long-call daily-hedged P&L. Discrete hedges, costs and individual path variation prevent a guaranteed per-path ordering.

Status: complete. Pool: development. Sessions per variant: 1000. Root seed: 88042.

Synthetic performance is not evidence of real-world alpha.

## process-vol-0.15

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| absolute_residual_delta | underlying units | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| cash | GBP | 1000/1000 | -50.9796 | -48.9656 | 31.8492 | 1.00716 | -109.317 | -69.8096 | -28.6816 | -3.266 |
| drawdown | GBP | 1000/1000 | 58.0466 | 55.8655 | 28.3585 | 0.896775 | 16.5517 | 37.0682 | 75.8454 | 112.154 |
| fees | GBP | 1000/1000 | 0.267978 | 0.274 | 0.0544279 | 0.00172116 | 0.172 | 0.226 | 0.308 | 0.352 |
| financing | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| gross_hedging_error | GBP | 1000/1000 | -50.7117 | -48.6436 | 31.841 | 1.0069 | -109.026 | -69.5411 | -28.3986 | -3.0076 |
| hedge_gross_pnl | GBP | 1000/1000 | 5.58894 | 93.8 | 205.469 | 6.49749 | -415.594 | -77.855 | 145.403 | 178.971 |
| hedges | executed hedge occasions | 1000/1000 | 19.115 | 20 | 1.87971 | 0.0594416 | 15 | 18 | 21 | 21 |
| max_absolute_delta | underlying units | 1000/1000 | 69.1004 | 50.9338 | 21.6999 | 0.68621 | 50.9338 | 50.9338 | 98 | 100 |
| max_absolute_gamma | underlying units per GBP stock move | 1000/1000 | 19.3816 | 16.8129 | 9.29571 | 0.293956 | 8.89835 | 11.4055 | 26.1603 | 37.5151 |
| max_absolute_vega | GBP per 1.00 absolute annual volatility | 1000/1000 | 933.597 | 933.597 | 3.41231e-13 | 1.07907e-14 | 933.597 | 933.597 | 933.597 | 933.597 |
| net_pnl | GBP | 1000/1000 | -50.9796 | -48.9656 | 31.8492 | 1.00716 | -109.317 | -69.8096 | -28.6816 | -3.266 |
| option_cash | GBP | 1000/1000 | -56.3506 | -188.304 | 212.767 | 6.72829 | -188.304 | -188.304 | 22.6964 | 398.796 |
| option_fees | GBP | 1000/1000 | 0.05 | 0.05 | 6.94237e-18 | 2.19537e-19 | 0.05 | 0.05 | 0.05 | 0.05 |
| option_gross_pnl | GBP | 1000/1000 | -56.3006 | -188.254 | 212.767 | 6.72829 | -188.254 | -188.254 | 22.7464 | 398.846 |
| option_realised_gross | GBP | 1000/1000 | -56.3006 | -188.254 | 212.767 | 6.72829 | -188.254 | -188.254 | 22.7464 | 398.846 |
| option_unrealised | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| option_value | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| realised_volatility | annual decimal; close-to-close quadratic variation | 1000/1000 | 0.148978 | 0.147918 | 0.0246889 | 0.000780731 | 0.109168 | 0.132056 | 0.164645 | 0.192994 |
| residual_delta | underlying units | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rms_delta | underlying units | 1000/1000 | 0.275072 | 0.275891 | 0.0293526 | 0.000928209 | 0.226492 | 0.253863 | 0.295595 | 0.323665 |
| stock_cash | GBP | 1000/1000 | 5.37096 | 93.597 | 205.489 | 6.49815 | -415.84 | -78.147 | 145.14 | 178.808 |
| stock_fees | GBP | 1000/1000 | 0.217978 | 0.224 | 0.0544279 | 0.00172116 | 0.122 | 0.176 | 0.258 | 0.302 |
| stock_realised_gross | GBP | 1000/1000 | 5.58894 | 93.8 | 205.469 | 6.49749 | -415.594 | -77.855 | 145.403 | 178.971 |
| stock_unrealised | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| stock_value | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| total_pnl | GBP | 1000/1000 | -50.9796 | -48.9656 | 31.8492 | 1.00716 | -109.317 | -69.8096 | -28.6816 | -3.266 |
| turnover | underlying units traded | 1000/1000 | 217.978 | 224 | 54.4279 | 1.72116 | 122 | 176 | 258 | 302 |

Mean interval: {'confidence': 0.95, 'high': -49.003245150766176, 'low': -52.95603084923383, 'method': 'Student t mean'}
Bootstrap: {'estimate': -50.979638, 'interval': {'confidence': 0.95, 'high': -48.956324699999996, 'low': -52.907785749999995, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 1000, 'seed': 16701173418244127843448762494014380706341912588230110911892663467162190181466, 'standard_error': 1.037821642420337}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -109.3172, 'probability_below': {'-0.25': 0.958, '-0.5': 0.957, '-1.0': 0.957, '0.0': 0.958}, 'tail_count': 50, 'worst': -151.2136, 'worst_five_percent_mean': -122.98839999999998}

Exploratory correlations (not causal effects):

- fees vs turnover: {'available': 1000, 'correlation': 1.0, 'covariance': 2.962397913913914, 'missing': 0}

Worst primary outcomes:

- Run #596: -151.214; simulation seed 200556071473365317118323792899703798660345551118903974316191309322342132589280
- Run #408: -141.986; simulation seed 130604122038318885070276996727877473371342963613813978285214965334800873961320
- Run #813: -141.712; simulation seed 204855649926867683622177647429085212878004559364291429783944858416482166854954

## process-vol-0.2

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| absolute_residual_delta | underlying units | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| cash | GBP | 1000/1000 | -3.89347 | -4.2736 | 36.6346 | 1.15849 | -67.9538 | -25.3606 | 17.8194 | 58.9881 |
| drawdown | GBP | 1000/1000 | 33.0131 | 28.312 | 20.9397 | 0.662172 | 8.22126 | 17.2774 | 43.3448 | 76.4946 |
| fees | GBP | 1000/1000 | 0.287458 | 0.29 | 0.0655519 | 0.00207293 | 0.174 | 0.242 | 0.336 | 0.392 |
| financing | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| gross_hedging_error | GBP | 1000/1000 | -3.60601 | -3.9986 | 36.6427 | 1.15875 | -67.6946 | -25.1511 | 18.0214 | 59.3459 |
| hedge_gross_pnl | GBP | 1000/1000 | 8.63959 | 145.28 | 283.869 | 8.97673 | -583.837 | -96.8425 | 189.89 | 236.126 |
| hedges | executed hedge occasions | 1000/1000 | 18.598 | 19 | 2.47154 | 0.0781569 | 13 | 17 | 20 | 21 |
| max_absolute_delta | underlying units | 1000/1000 | 70.1427 | 50.9338 | 22.3562 | 0.706966 | 50.9338 | 50.9338 | 100 | 100 |
| max_absolute_gamma | underlying units per GBP stock move | 1000/1000 | 17.8912 | 15.0897 | 8.84196 | 0.279607 | 8.63093 | 10.5239 | 23.9847 | 36.925 |
| max_absolute_vega | GBP per 1.00 absolute annual volatility | 1000/1000 | 933.597 | 933.597 | 3.41231e-13 | 1.07907e-14 | 933.597 | 933.597 | 933.597 | 933.597 |
| net_pnl | GBP | 1000/1000 | -3.89347 | -4.2736 | 36.6346 | 1.15849 | -67.9538 | -25.3606 | 17.8194 | 58.9881 |
| option_cash | GBP | 1000/1000 | -12.2956 | -188.304 | 285.832 | 9.0388 | -188.304 | -188.304 | 91.6964 | 599.796 |
| option_fees | GBP | 1000/1000 | 0.05 | 0.05 | 6.94237e-18 | 2.19537e-19 | 0.05 | 0.05 | 0.05 | 0.05 |
| option_gross_pnl | GBP | 1000/1000 | -12.2456 | -188.254 | 285.832 | 9.0388 | -188.254 | -188.254 | 91.7464 | 599.846 |
| option_realised_gross | GBP | 1000/1000 | -12.2456 | -188.254 | 285.832 | 9.0388 | -188.254 | -188.254 | 91.7464 | 599.846 |
| option_unrealised | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| option_value | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| realised_volatility | annual decimal; close-to-close quadratic variation | 1000/1000 | 0.198642 | 0.19719 | 0.0329132 | 0.00104081 | 0.145607 | 0.176197 | 0.21926 | 0.257493 |
| residual_delta | underlying units | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rms_delta | underlying units | 1000/1000 | 0.268742 | 0.271013 | 0.0322352 | 0.00101937 | 0.213238 | 0.247604 | 0.290677 | 0.319002 |
| stock_cash | GBP | 1000/1000 | 8.40213 | 144.956 | 283.883 | 8.97716 | -584.06 | -97.1135 | 189.555 | 235.808 |
| stock_fees | GBP | 1000/1000 | 0.237458 | 0.24 | 0.0655519 | 0.00207293 | 0.124 | 0.192 | 0.286 | 0.342 |
| stock_realised_gross | GBP | 1000/1000 | 8.63959 | 145.28 | 283.869 | 8.97673 | -583.837 | -96.8425 | 189.89 | 236.126 |
| stock_unrealised | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| stock_value | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| total_pnl | GBP | 1000/1000 | -3.89347 | -4.2736 | 36.6346 | 1.15849 | -67.9538 | -25.3606 | 17.8194 | 58.9881 |
| turnover | underlying units traded | 1000/1000 | 237.458 | 240 | 65.5519 | 2.07293 | 124 | 192 | 286 | 342 |

Mean interval: {'confidence': 0.95, 'high': -1.620120179030958, 'low': -6.166815820969042, 'method': 'Student t mean'}
Bootstrap: {'estimate': -3.893468, 'interval': {'confidence': 0.95, 'high': -1.6997711000000009, 'low': -6.209949399999999, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 1000, 'seed': 42570439685954356322885563762516069969360764474131131825713613717992768281797, 'standard_error': 1.1626506264316119}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -67.9538, 'probability_below': {'-0.25': 0.558, '-0.5': 0.549, '-1.0': 0.547, '0.0': 0.563}, 'tail_count': 50, 'worst': -129.3056, 'worst_five_percent_mean': -84.23944}

Exploratory correlations (not causal effects):

- fees vs turnover: {'available': 1000, 'correlation': 1.0, 'covariance': 4.297055291291291, 'missing': 0}

Worst primary outcomes:

- Run #596: -129.306; simulation seed 200556071473365317118323792899703798660345551118903974316191309322342132589280
- Run #408: -112.39; simulation seed 130604122038318885070276996727877473371342963613813978285214965334800873961320
- Run #740: -111.372; simulation seed 81398217676142447045512471123367543257654463245981020995165110901040874214346

## process-vol-0.3

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| absolute_residual_delta | underlying units | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| cash | GBP | 1000/1000 | 90.9188 | 77.2044 | 69.2332 | 2.18935 | 7.1335 | 41.5619 | 125.035 | 228.568 |
| drawdown | GBP | 1000/1000 | 15.4833 | 12.4127 | 11.2825 | 0.356783 | 3.56566 | 7.87369 | 19.6094 | 38.8065 |
| fees | GBP | 1000/1000 | 0.314736 | 0.31 | 0.0855031 | 0.00270385 | 0.17 | 0.256 | 0.376 | 0.458 |
| financing | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| gross_hedging_error | GBP | 1000/1000 | 91.2336 | 77.5014 | 69.282 | 2.19089 | 7.4229 | 41.7739 | 125.336 | 228.955 |
| hedge_gross_pnl | GBP | 1000/1000 | 15.3102 | 220.45 | 449.132 | 14.2028 | -941.933 | -133.7 | 277.467 | 387.293 |
| hedges | executed hedge occasions | 1000/1000 | 17.387 | 19 | 3.46081 | 0.10944 | 10 | 15 | 20 | 21 |
| max_absolute_delta | underlying units | 1000/1000 | 71.5252 | 51.7531 | 22.8694 | 0.723193 | 50.9338 | 50.9338 | 100 | 100 |
| max_absolute_gamma | underlying units per GBP stock move | 1000/1000 | 16.1716 | 13.154 | 8.03241 | 0.254007 | 8.51908 | 9.64477 | 21.0939 | 35.1045 |
| max_absolute_vega | GBP per 1.00 absolute annual volatility | 1000/1000 | 933.597 | 933.597 | 3.41231e-13 | 1.07907e-14 | 933.597 | 933.597 | 933.597 | 933.597 |
| net_pnl | GBP | 1000/1000 | 90.9188 | 77.2044 | 69.2332 | 2.18935 | 7.1335 | 41.5619 | 125.035 | 228.568 |
| option_cash | GBP | 1000/1000 | 75.8734 | -188.304 | 435.179 | 13.7616 | -188.304 | -188.304 | 225.696 | 1007.85 |
| option_fees | GBP | 1000/1000 | 0.05 | 0.05 | 6.94237e-18 | 2.19537e-19 | 0.05 | 0.05 | 0.05 | 0.05 |
| option_gross_pnl | GBP | 1000/1000 | 75.9234 | -188.254 | 435.179 | 13.7616 | -188.254 | -188.254 | 225.746 | 1007.9 |
| option_realised_gross | GBP | 1000/1000 | 75.9234 | -188.254 | 435.179 | 13.7616 | -188.254 | -188.254 | 225.746 | 1007.9 |
| option_unrealised | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| option_value | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| realised_volatility | annual decimal; close-to-close quadratic variation | 1000/1000 | 0.297973 | 0.295885 | 0.0493849 | 0.00156169 | 0.218367 | 0.26409 | 0.329163 | 0.386257 |
| residual_delta | underlying units | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rms_delta | underlying units | 1000/1000 | 0.261361 | 0.265104 | 0.0390743 | 0.00123564 | 0.190119 | 0.237794 | 0.2891 | 0.32019 |
| stock_cash | GBP | 1000/1000 | 15.0454 | 220.265 | 449.133 | 14.2028 | -942.158 | -133.994 | 277.079 | 386.938 |
| stock_fees | GBP | 1000/1000 | 0.264736 | 0.26 | 0.0855031 | 0.00270385 | 0.12 | 0.206 | 0.326 | 0.408 |
| stock_realised_gross | GBP | 1000/1000 | 15.3102 | 220.45 | 449.132 | 14.2028 | -941.933 | -133.7 | 277.467 | 387.293 |
| stock_unrealised | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| stock_value | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| total_pnl | GBP | 1000/1000 | 90.9188 | 77.2044 | 69.2332 | 2.18935 | 7.1335 | 41.5619 | 125.035 | 228.568 |
| turnover | underlying units traded | 1000/1000 | 264.736 | 260 | 85.5031 | 2.70385 | 120 | 206 | 326 | 408 |

Mean interval: {'confidence': 0.95, 'high': 95.21506781210174, 'low': 86.62258018789824, 'method': 'Student t mean'}
Bootstrap: {'estimate': 90.91882399999999, 'interval': {'confidence': 0.95, 'high': 95.15336620000001, 'low': 86.57529115000001, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 1000, 'seed': 18486804262819679691682706504798773180686510670782920833865529311715470352199, 'standard_error': 2.2600681637558373}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': 7.133500000000001, 'probability_below': {'-0.25': 0.035, '-0.5': 0.035, '-1.0': 0.035, '0.0': 0.036}, 'tail_count': 50, 'worst': -68.6456, 'worst_five_percent_mean': -10.828560000000003}

Exploratory correlations (not causal effects):

- fees vs turnover: {'available': 1000, 'correlation': 1.0, 'covariance': 7.31078508908909, 'missing': 0}

Worst primary outcomes:

- Run #596: -68.6456; simulation seed 200556071473365317118323792899703798660345551118903974316191309322342132589280
- Run #408: -44.5896; simulation seed 130604122038318885070276996727877473371342963613813978285214965334800873961320
- Run #409: -43.5436; simulation seed 200183119298974893894502093676533592403062148337409960903953346814596909617672

## Paired: process-vol-0.2 minus process-vol-0.15

Summary: {'available': 1000, 'maximum': 105.116, 'mean': 47.086169999999996, 'mean_ci': {'confidence': 0.95, 'high': 48.202790617603455, 'low': 45.969549382396536, 'method': 'Student t mean'}, 'median': 44.602, 'minimum': 11.038, 'missing': 0, 'p05': 21.8478, 'p25': 33.546, 'p75': 58.05, 'p95': 81.63159999999998, 'requested': 1000, 'standard_deviation': 17.99413865460142, 'standard_error': 0.5690246268141838, 'variance': 323.789025921021}
Bootstrap: {'estimate': 47.086169999999996, 'interval': {'confidence': 0.95, 'high': 48.28302099999999, 'low': 46.033477, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete matched session pair', 'resamples': 1000, 'seed': 52297672747357035561103589911898445613658599504069044133430326783011914312846, 'standard_error': 0.5676696215189051}
Positive / negative / tied: 100.000% / 0.000% / 0.000%.
t = 82.7489; two-sided p = 0; paired standardised effect = 2.61675.
Paired two-sided t test: H0 E[D]=0; H1 E[D] differs from zero. Statistical significance is not strategy validity or practical value.

## Paired: process-vol-0.3 minus process-vol-0.15

Summary: {'available': 1000, 'maximum': 353.722, 'mean': 141.898462, 'mean_ci': {'confidence': 0.95, 'high': 145.88771370006896, 'low': 137.90921029993103, 'method': 'Student t mean'}, 'median': 134.051, 'minimum': 24.116, 'missing': 0, 'p05': 55.4171, 'p25': 90.90200000000002, 'p75': 182.05700000000002, 'p95': 264.3250999999999, 'requested': 1000, 'standard_deviation': 64.28606734237914, 'standard_error': 2.032903946168856, 'variance': 4132.698454348905}
Bootstrap: {'estimate': 141.898462, 'interval': {'confidence': 0.95, 'high': 145.81241260000002, 'low': 138.03308415, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete matched session pair', 'resamples': 1000, 'seed': 87561121880294964702056306800430533464307771561425219970860215949466272178202, 'standard_error': 2.021523849482813}
Positive / negative / tied: 100.000% / 0.000% / 0.000%.
t = 69.8009; two-sided p = 0; paired standardised effect = 2.2073.
Paired two-sided t test: H0 E[D]=0; H1 E[D] differs from zero. Statistical significance is not strategy validity or practical value.

## Interpretation

process-vol-0.15: observed mean net_pnl=-50.9796; losing/negative outcomes 95.8%. process-vol-0.2: observed mean net_pnl=-3.89347; losing/negative outcomes 56.3%. process-vol-0.3: observed mean net_pnl=90.9188; losing/negative outcomes 3.6%. Compare the full distributions and paired uncertainty with the original hypothesis. These conditional model outcomes do not establish real-world alpha, safety or an optimal parameter. Interpretation remains reviewable.

## Limitations

- Synthetic performance is not evidence of real-world alpha.
- Independent sessions conditional on one model; uncertainty excludes model error.
- Exploratory metrics/intervals are not corrected for multiple testing.
- Missing metrics are reported with coverage, not replaced by zero.

Quantiles use linear interpolation; SD uses n−1. Markout distributions use per-session available-unit means, with session and unit coverage retained. A confidence interval concerns the model's mean, not the range of future outcomes.
