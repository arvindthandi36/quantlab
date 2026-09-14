# QuantLab synthetic research experiment

Phase 8 frequency: one long ATM call, multiplier 100, twenty ACT/365 days

**Prediction registered before execution:** More frequent hedging is expected to reduce interval delta exposure and the dispersion of terminal hedging P&L, while increasing execution costs. Mean net P&L need not improve. Compare daily, five-day, twenty-day and no hedge.

Status: complete. Pool: development. Sessions per variant: 1000. Root seed: 88042.

Synthetic performance is not evidence of real-world alpha.

## every-1

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
Bootstrap: {'estimate': -3.893468, 'interval': {'confidence': 0.95, 'high': -1.8424802000000007, 'low': -6.11824735, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 1000, 'seed': 34880713908191796771168398708802707067679883240310248119935081521636237512002, 'standard_error': 1.1144368830344313}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -67.9538, 'probability_below': {'-0.25': 0.558, '-0.5': 0.549, '-1.0': 0.547, '0.0': 0.563}, 'tail_count': 50, 'worst': -129.3056, 'worst_five_percent_mean': -84.23944}

Exploratory correlations (not causal effects):

- fees vs turnover: {'available': 1000, 'correlation': 1.0, 'covariance': 4.297055291291291, 'missing': 0}

Worst primary outcomes:

- Run #596: -129.306; simulation seed 200556071473365317118323792899703798660345551118903974316191309322342132589280
- Run #408: -112.39; simulation seed 130604122038318885070276996727877473371342963613813978285214965334800873961320
- Run #740: -111.372; simulation seed 81398217676142447045512471123367543257654463245981020995165110901040874214346

## every-5

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| absolute_residual_delta | underlying units | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| cash | GBP | 1000/1000 | -5.82928 | -9.5496 | 78.1644 | 2.47178 | -129.332 | -56.7806 | 37.3429 | 129.79 |
| drawdown | GBP | 1000/1000 | 67.6442 | 59.8899 | 39.0213 | 1.23396 | 16.0759 | 37.0706 | 93.4578 | 140.992 |
| fees | GBP | 1000/1000 | 0.199914 | 0.197 | 0.0389293 | 0.00123105 | 0.152 | 0.16 | 0.238 | 0.256 |
| financing | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| gross_hedging_error | GBP | 1000/1000 | -5.62937 | -9.3936 | 78.1737 | 2.47207 | -129.146 | -56.5461 | 37.5964 | 129.972 |
| hedge_gross_pnl | GBP | 1000/1000 | 6.61623 | 97.095 | 272.136 | 8.6057 | -560.375 | -93.5775 | 188.685 | 279.57 |
| hedges | executed hedge occasions | 1000/1000 | 4.866 | 5 | 0.360797 | 0.0114094 | 4 | 5 | 5 | 5 |
| max_absolute_delta | underlying units | 1000/1000 | 66.4821 | 54 | 18.9274 | 0.598537 | 50.9338 | 50.9338 | 85 | 100 |
| max_absolute_gamma | underlying units per GBP stock move | 1000/1000 | 17.8912 | 15.0897 | 8.84196 | 0.279607 | 8.63093 | 10.5239 | 23.9847 | 36.925 |
| max_absolute_vega | GBP per 1.00 absolute annual volatility | 1000/1000 | 933.597 | 933.597 | 3.41231e-13 | 1.07907e-14 | 933.597 | 933.597 | 933.597 | 933.597 |
| net_pnl | GBP | 1000/1000 | -5.82928 | -9.5496 | 78.1644 | 2.47178 | -129.332 | -56.7806 | 37.3429 | 129.79 |
| option_cash | GBP | 1000/1000 | -12.2956 | -188.304 | 285.832 | 9.0388 | -188.304 | -188.304 | 91.6964 | 599.796 |
| option_fees | GBP | 1000/1000 | 0.05 | 0.05 | 6.94237e-18 | 2.19537e-19 | 0.05 | 0.05 | 0.05 | 0.05 |
| option_gross_pnl | GBP | 1000/1000 | -12.2456 | -188.254 | 285.832 | 9.0388 | -188.254 | -188.254 | 91.7464 | 599.846 |
| option_realised_gross | GBP | 1000/1000 | -12.2456 | -188.254 | 285.832 | 9.0388 | -188.254 | -188.254 | 91.7464 | 599.846 |
| option_unrealised | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| option_value | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| realised_volatility | annual decimal; close-to-close quadratic variation | 1000/1000 | 0.198642 | 0.19719 | 0.0329132 | 0.00104081 | 0.145607 | 0.176197 | 0.21926 | 0.257493 |
| residual_delta | underlying units | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rms_delta | underlying units | 1000/1000 | 13.7285 | 12.9482 | 4.74307 | 0.149989 | 7.66815 | 10.1862 | 16.3807 | 22.7986 |
| stock_cash | GBP | 1000/1000 | 6.46632 | 96.946 | 272.16 | 8.60644 | -560.575 | -93.7655 | 188.509 | 279.41 |
| stock_fees | GBP | 1000/1000 | 0.149914 | 0.147 | 0.0389293 | 0.00123105 | 0.102 | 0.11 | 0.188 | 0.206 |
| stock_realised_gross | GBP | 1000/1000 | 6.61623 | 97.095 | 272.136 | 8.6057 | -560.375 | -93.5775 | 188.685 | 279.57 |
| stock_unrealised | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| stock_value | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| total_pnl | GBP | 1000/1000 | -5.82928 | -9.5496 | 78.1644 | 2.47178 | -129.332 | -56.7806 | 37.3429 | 129.79 |
| turnover | underlying units traded | 1000/1000 | 149.914 | 147 | 38.9293 | 1.23105 | 102 | 110 | 188 | 206 |

Mean interval: {'confidence': 0.95, 'high': -0.9788160550323699, 'low': -10.679751944967629, 'method': 'Student t mean'}
Bootstrap: {'estimate': -5.8292839999999995, 'interval': {'confidence': 0.95, 'high': -1.2071549500000005, 'low': -10.670226099999999, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 1000, 'seed': 14992921658586604911441350630827918291560494990387109378720259444992759268779, 'standard_error': 2.4297480315126427}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -129.3321, 'probability_below': {'-0.25': 0.548, '-0.5': 0.547, '-1.0': 0.544, '0.0': 0.549}, 'tail_count': 50, 'worst': -174.5136, 'worst_five_percent_mean': -146.85031999999998}

Exploratory correlations (not causal effects):

- fees vs turnover: {'available': 1000, 'correlation': 0.9999999999999997, 'covariance': 1.515488092092092, 'missing': 0}

Worst primary outcomes:

- Run #999: -174.514; simulation seed 103802767025902014497416119175634702568208429029867851356602274473334116080504
- Run #342: -174.154; simulation seed 2551860552482641149704949272749521626440697547149136217485218518966056924920
- Run #878: -172.86; simulation seed 23783564980653526781215931064636381528407397512510786043052847361217004565730

## every-20

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| absolute_residual_delta | underlying units | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| cash | GBP | 1000/1000 | -4.65478 | -36.4256 | 145.189 | 4.59128 | -176.167 | -119.901 | 79.7069 | 282.86 |
| drawdown | GBP | 1000/1000 | 137.972 | 134.518 | 54.7444 | 1.73117 | 55.6274 | 97.3515 | 173.835 | 228.621 |
| fees | GBP | 1000/1000 | 0.152 | 0.152 | 0 | 0 | 0.152 | 0.152 | 0.152 | 0.152 |
| financing | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| gross_hedging_error | GBP | 1000/1000 | -4.50278 | -36.2736 | 145.189 | 4.59128 | -176.015 | -119.749 | 79.8589 | 283.012 |
| hedge_gross_pnl | GBP | 1000/1000 | 7.74282 | 17.85 | 239.649 | 7.57836 | -402.951 | -143.82 | 166.898 | 397.851 |
| hedges | executed hedge occasions | 1000/1000 | 2 | 2 | 0 | 0 | 2 | 2 | 2 | 2 |
| max_absolute_delta | underlying units | 1000/1000 | 51 | 51 | 0 | 0 | 51 | 51 | 51 | 51 |
| max_absolute_gamma | underlying units per GBP stock move | 1000/1000 | 17.8912 | 15.0897 | 8.84196 | 0.279607 | 8.63093 | 10.5239 | 23.9847 | 36.925 |
| max_absolute_vega | GBP per 1.00 absolute annual volatility | 1000/1000 | 933.597 | 933.597 | 3.41231e-13 | 1.07907e-14 | 933.597 | 933.597 | 933.597 | 933.597 |
| net_pnl | GBP | 1000/1000 | -4.65478 | -36.4256 | 145.189 | 4.59128 | -176.167 | -119.901 | 79.7069 | 282.86 |
| option_cash | GBP | 1000/1000 | -12.2956 | -188.304 | 285.832 | 9.0388 | -188.304 | -188.304 | 91.6964 | 599.796 |
| option_fees | GBP | 1000/1000 | 0.05 | 0.05 | 6.94237e-18 | 2.19537e-19 | 0.05 | 0.05 | 0.05 | 0.05 |
| option_gross_pnl | GBP | 1000/1000 | -12.2456 | -188.254 | 285.832 | 9.0388 | -188.254 | -188.254 | 91.7464 | 599.846 |
| option_realised_gross | GBP | 1000/1000 | -12.2456 | -188.254 | 285.832 | 9.0388 | -188.254 | -188.254 | 91.7464 | 599.846 |
| option_unrealised | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| option_value | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| realised_volatility | annual decimal; close-to-close quadratic variation | 1000/1000 | 0.198642 | 0.19719 | 0.0329132 | 0.00104081 | 0.145607 | 0.176197 | 0.21926 | 0.257493 |
| residual_delta | underlying units | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rms_delta | underlying units | 1000/1000 | 27.8265 | 27.9034 | 8.141 | 0.257441 | 14.5335 | 21.4352 | 33.9541 | 41.1937 |
| stock_cash | GBP | 1000/1000 | 7.64082 | 17.748 | 239.649 | 7.57836 | -403.053 | -143.922 | 166.796 | 397.749 |
| stock_fees | GBP | 1000/1000 | 0.102 | 0.102 | 4.16542e-17 | 1.31722e-18 | 0.102 | 0.102 | 0.102 | 0.102 |
| stock_realised_gross | GBP | 1000/1000 | 7.74282 | 17.85 | 239.649 | 7.57836 | -402.951 | -143.82 | 166.898 | 397.851 |
| stock_unrealised | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| stock_value | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| total_pnl | GBP | 1000/1000 | -4.65478 | -36.4256 | 145.189 | 4.59128 | -176.167 | -119.901 | 79.7069 | 282.86 |
| turnover | underlying units traded | 1000/1000 | 102 | 102 | 0 | 0 | 102 | 102 | 102 | 102 |

Mean interval: {'confidence': 0.95, 'high': 4.354879480630058, 'low': -13.664439480630055, 'method': 'Student t mean'}
Bootstrap: {'estimate': -4.654779999999998, 'interval': {'confidence': 0.95, 'high': 4.724382749999998, 'low': -14.568339749999996, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 1000, 'seed': 21919657049401725113579321793635398726931589486686644661801621712452339106034, 'standard_error': 4.849395786991163}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -176.1671, 'probability_below': {'-0.25': 0.589, '-0.5': 0.588, '-1.0': 0.585, '0.0': 0.589}, 'tail_count': 50, 'worst': -188.4056, 'worst_five_percent_mean': -182.81160000000003}

Exploratory correlations (not causal effects):

- fees vs turnover: {'available': 1000, 'correlation': None, 'covariance': 0.0, 'missing': 0}

Worst primary outcomes:

- Run #646: -188.406; simulation seed 107569341000011846843443398546742958235163151362087031836742993252322134703388
- Run #864: -187.956; simulation seed 223630455505374432713388785860380338305738151808116699031499918039282903968650
- Run #345: -187.896; simulation seed 210450932103667976992138448414649573631784657010982764712360200604117749431962

## no-hedge

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| absolute_residual_delta | underlying units | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| cash | GBP | 1000/1000 | -12.2956 | -188.304 | 285.832 | 9.0388 | -188.304 | -188.304 | 91.6964 | 599.796 |
| drawdown | GBP | 1000/1000 | 255.9 | 226.123 | 100.357 | 3.17356 | 144.969 | 188.304 | 301.165 | 467.272 |
| fees | GBP | 1000/1000 | 0.05 | 0.05 | 6.94237e-18 | 2.19537e-19 | 0.05 | 0.05 | 0.05 | 0.05 |
| financing | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| gross_hedging_error | GBP | 1000/1000 | -12.2456 | -188.254 | 285.832 | 9.0388 | -188.254 | -188.254 | 91.7464 | 599.846 |
| hedge_gross_pnl | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| hedges | executed hedge occasions | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| max_absolute_delta | underlying units | 1000/1000 | 78.5795 | 79.7017 | 18.9569 | 0.599469 | 50.9338 | 59.6569 | 99.6224 | 100 |
| max_absolute_gamma | underlying units per GBP stock move | 1000/1000 | 17.8912 | 15.0897 | 8.84196 | 0.279607 | 8.63093 | 10.5239 | 23.9847 | 36.925 |
| max_absolute_vega | GBP per 1.00 absolute annual volatility | 1000/1000 | 933.597 | 933.597 | 3.41231e-13 | 1.07907e-14 | 933.597 | 933.597 | 933.597 | 933.597 |
| net_pnl | GBP | 1000/1000 | -12.2956 | -188.304 | 285.832 | 9.0388 | -188.304 | -188.304 | 91.6964 | 599.796 |
| option_cash | GBP | 1000/1000 | -12.2956 | -188.304 | 285.832 | 9.0388 | -188.304 | -188.304 | 91.6964 | 599.796 |
| option_fees | GBP | 1000/1000 | 0.05 | 0.05 | 6.94237e-18 | 2.19537e-19 | 0.05 | 0.05 | 0.05 | 0.05 |
| option_gross_pnl | GBP | 1000/1000 | -12.2456 | -188.254 | 285.832 | 9.0388 | -188.254 | -188.254 | 91.7464 | 599.846 |
| option_realised_gross | GBP | 1000/1000 | -12.2456 | -188.254 | 285.832 | 9.0388 | -188.254 | -188.254 | 91.7464 | 599.846 |
| option_unrealised | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| option_value | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| realised_volatility | annual decimal; close-to-close quadratic variation | 1000/1000 | 0.198642 | 0.19719 | 0.0329132 | 0.00104081 | 0.145607 | 0.176197 | 0.21926 | 0.257493 |
| residual_delta | underlying units | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rms_delta | underlying units | 1000/1000 | 53.3353 | 51.7413 | 20.9527 | 0.662584 | 21.8557 | 35.3182 | 71.9185 | 86.5981 |
| stock_cash | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| stock_fees | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| stock_realised_gross | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| stock_unrealised | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| stock_value | GBP | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| total_pnl | GBP | 1000/1000 | -12.2956 | -188.304 | 285.832 | 9.0388 | -188.304 | -188.304 | 91.6964 | 599.796 |
| turnover | underlying units traded | 1000/1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Mean interval: {'confidence': 0.95, 'high': 5.441617040856757, 'low': -30.032817040856727, 'method': 'Student t mean'}
Bootstrap: {'estimate': -12.295599999999984, 'interval': {'confidence': 0.95, 'high': 5.900100000000011, 'low': -29.514924999999984, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 1000, 'seed': 101811058415933162150706398475200517084349256469667774530094182200994931238359, 'standard_error': 9.348223739509175}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -188.3036, 'probability_below': {'-0.25': 0.694, '-0.5': 0.694, '-1.0': 0.694, '0.0': 0.694}, 'tail_count': 50, 'worst': -188.3036, 'worst_five_percent_mean': -188.30359999999996}

Exploratory correlations (not causal effects):

- fees vs turnover: {'available': 1000, 'correlation': None, 'covariance': 0.0, 'missing': 0}

Worst primary outcomes:

- Run #1: -188.304; simulation seed 230706286731173967985022995246945512553649746032000549486556029545651266702150
- Run #2: -188.304; simulation seed 38960867926330442867409554224242070518663875598697425889170260378961154831688
- Run #4: -188.304; simulation seed 91683933221311242169127348666512488084598233989494451572208671698812622650656

## Paired: every-20 minus every-1

Summary: {'available': 1000, 'maximum': 652.71, 'mean': -0.7613119999999994, 'mean_ci': {'confidence': 0.95, 'high': 7.907238535804193, 'low': -9.429862535804192, 'method': 'Student t mean'}, 'median': -32.73, 'minimum': -252.32, 'missing': 0, 'p05': -175.85580000000002, 'p25': -103.54549999999999, 'p75': 79.40450000000001, 'p95': 276.5639999999999, 'requested': 1000, 'standard_deviation': 139.6921190748364, 'standard_error': 4.417452674519363, 'variance': 19513.88813161827}
Bootstrap: {'estimate': -0.7613119999999994, 'interval': {'confidence': 0.95, 'high': 7.822720450000001, 'low': -9.18058575, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete matched session pair', 'resamples': 1000, 'seed': 14652190049970803324399706233319812937829506870948934042707707995214394469181, 'standard_error': 4.384398488331654}
Positive / negative / tied: 41.000% / 59.000% / 0.000%.
t = -0.172342; two-sided p = 0.863204; paired standardised effect = -0.00544993.
Paired two-sided t test: H0 E[D]=0; H1 E[D] differs from zero. Statistical significance is not strategy validity or practical value.

## Paired: every-5 minus every-1

Summary: {'available': 1000, 'maximum': 280.62800000000004, 'mean': -1.9358160000000002, 'mean_ci': {'confidence': 0.95, 'high': 2.329835023560017, 'low': -6.201467023560017, 'method': 'Student t mean'}, 'median': -1.726, 'minimum': -208.75799999999998, 'missing': 0, 'p05': -115.70500000000001, 'p25': -44.177, 'p75': 35.247, 'p95': 115.88079999999984, 'requested': 1000, 'standard_deviation': 68.74019229093223, 'standard_error': 2.1737557443729365, 'variance': 4725.214036194339}
Bootstrap: {'estimate': -1.9358160000000002, 'interval': {'confidence': 0.95, 'high': 2.3673365499999983, 'low': -6.0995551500000005, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete matched session pair', 'resamples': 1000, 'seed': 8511793963463025047607764738432854472608064050976259966095175360218983521870, 'standard_error': 2.1679179737633842}
Positive / negative / tied: 48.800% / 51.200% / 0.000%.
t = -0.89054; two-sided p = 0.373391; paired standardised effect = -0.0281613.
Paired two-sided t test: H0 E[D]=0; H1 E[D] differs from zero. Statistical significance is not strategy validity or practical value.

## Paired: no-hedge minus every-1

Summary: {'available': 1000, 'maximum': 1537.152, 'mean': -8.40213199999999, 'mean_ci': {'confidence': 0.95, 'high': 9.21411975555653, 'low': -26.018383755556506, 'method': 'Student t mean'}, 'median': -144.95599999999996, 'minimum': -307.714, 'missing': 0, 'p05': -235.808, 'p25': -189.5555, 'p75': 97.1135, 'p95': 584.0595999999997, 'requested': 1000, 'standard_deviation': 283.88270077278855, 'standard_error': 8.97715922762054, 'variance': 80589.38779805262}
Bootstrap: {'estimate': -8.40213199999999, 'interval': {'confidence': 0.95, 'high': 9.5194822, 'low': -26.101680999999985, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete matched session pair', 'resamples': 1000, 'seed': 82962031252327457746867502461816491665675694972493380315061978096465275614097, 'standard_error': 9.11617804483116}
Positive / negative / tied: 31.200% / 68.800% / 0.000%.
t = -0.935946; two-sided p = 0.349527; paired standardised effect = -0.0295972.
Paired two-sided t test: H0 E[D]=0; H1 E[D] differs from zero. Statistical significance is not strategy validity or practical value.

## Interpretation

every-1: observed mean net_pnl=-3.89347; losing/negative outcomes 56.3%. every-20: observed mean net_pnl=-4.65478; losing/negative outcomes 58.9%. every-5: observed mean net_pnl=-5.82928; losing/negative outcomes 54.9%. no-hedge: observed mean net_pnl=-12.2956; losing/negative outcomes 69.4%. Compare the full distributions and paired uncertainty with the original hypothesis. These conditional model outcomes do not establish real-world alpha, safety or an optimal parameter. Interpretation remains reviewable.

## Limitations

- Synthetic performance is not evidence of real-world alpha.
- Independent sessions conditional on one model; uncertainty excludes model error.
- Exploratory metrics/intervals are not corrected for multiple testing.
- Missing metrics are reported with coverage, not replaced by zero.

Quantiles use linear interpolation; SD uses n−1. Markout distributions use per-session available-unit means, with session and unit coverage retained. A confidence interval concerns the model's mean, not the range of future outcomes.
