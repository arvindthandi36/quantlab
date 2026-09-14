# QuantLab synthetic research experiment

How robust is the same maker policy across controlled scenarios?

**Prediction registered before execution:** Execution, inventory and tail outcomes can differ despite the same policy.

Status: complete. Pool: development. Sessions per variant: 3. Root seed: 131042.

Synthetic performance is not evidence of real-world alpha.

## normal

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average_absolute_inventory | units | 3/3 | 2.8971 | 2.41986 | 1.32815 | 0.766807 | 1.92814 | 2.14668 | 3.40889 | 4.20011 |
| average_effective_spread | GBP/unit | 3/3 | 0.0383419 | 0.0376923 | 0.00144715 | 0.000835511 | 0.0373692 | 0.0375128 | 0.0388462 | 0.0397692 |
| average_inventory | units | 3/3 | -2.40022 | -2.41986 | 2.0076 | 1.15909 | -4.20011 | -3.40889 | -1.40136 | -0.586567 |
| average_quoted_spread | GBP/unit | 3/3 | 0.0439827 | 0.0440909 | 0.00209039 | 0.00120689 | 0.0420653 | 0.0429656 | 0.0450539 | 0.0458242 |
| buy_fills | execution records | 3/3 | 4 | 4 | 2 | 1.1547 | 2.2 | 3 | 5 | 5.8 |
| buy_units | units | 3/3 | 6.33333 | 6 | 2.51661 | 1.45297 | 4.2 | 5 | 7.5 | 8.7 |
| execution_edge | GBP | 3/3 | 0.31 | 0.3 | 0.0264575 | 0.0152753 | 0.291 | 0.295 | 0.32 | 0.336 |
| fees | GBP | 3/3 | 0.0153333 | 0.015 | 0.00152753 | 0.000881917 | 0.0141 | 0.0145 | 0.016 | 0.0168 |
| fill_rate | fraction | 3/3 | 0.408333 | 0.375 | 0.0803638 | 0.046398 | 0.3525 | 0.3625 | 0.4375 | 0.4875 |
| final_inventory | units | 3/3 | -2.66667 | -5 | 4.93288 | 2.848 | -5.9 | -5.5 | -1 | 2.2 |
| gross_realised_pnl | GBP | 3/3 | 0.0466667 | 0.16 | 0.250067 | 0.144376 | -0.2 | -0.04 | 0.19 | 0.214 |
| inventory_movement | GBP | 3/3 | -0.195 | 0.005 | 0.440483 | 0.254313 | -0.6295 | -0.3475 | 0.0575 | 0.0995 |
| markout_1 | GBP/unit | 3/3 | 0.00685185 | 0.005 | 0.0032075 | 0.00185185 | 0.005 | 0.005 | 0.00777778 | 0.01 |
| markout_20 | GBP/unit | 3/3 | 0.00408333 | 0.006 | 0.021107 | 0.0121862 | -0.015525 | -0.00595833 | 0.0150833 | 0.02235 |
| markout_5 | GBP/unit | 3/3 | 0.0158279 | 0.0140909 | 0.00330822 | 0.00191 | 0.0137841 | 0.0139205 | 0.0168669 | 0.0190877 |
| maximum_absolute_inventory | units | 3/3 | 5.66667 | 6 | 1.52753 | 0.881917 | 4.2 | 5 | 6.5 | 6.9 |
| maximum_drawdown | GBP | 3/3 | 0.314333 | 0.078 | 0.414548 | 0.23934 | 0.0726 | 0.075 | 0.4355 | 0.7215 |
| net_pnl | GBP | 3/3 | 0.0996667 | 0.29 | 0.415587 | 0.239939 | -0.3103 | -0.0435 | 0.338 | 0.3764 |
| realised_pnl | GBP | 3/3 | 0.0313333 | 0.146 | 0.251441 | 0.145169 | -0.2167 | -0.0555 | 0.1755 | 0.1991 |
| rms_inventory | units | 3/3 | 3.34208 | 3.01267 | 1.3692 | 0.790509 | 2.25214 | 2.59015 | 3.9293 | 4.66261 |
| sell_fills | execution records | 3/3 | 5.66667 | 6 | 2.51661 | 1.45297 | 3.3 | 4.5 | 7 | 7.8 |
| sell_units | units | 3/3 | 9 | 10 | 2.64575 | 1.52753 | 6.4 | 8 | 10.5 | 10.9 |
| turnover | GBP | 3/3 | 1533.68 | 1499.99 | 153.66 | 88.7159 | 1409.69 | 1449.83 | 1600.69 | 1681.25 |
| two_sided_quote_time_fraction | fraction | 3/3 | 0.622696 | 0.665882 | 0.104004 | 0.0600466 | 0.520239 | 0.584969 | 0.682016 | 0.694923 |
| unrealised_pnl | GBP | 3/3 | 0.0683333 | 0.085 | 0.180578 | 0.104257 | -0.0995 | -0.0175 | 0.1625 | 0.2245 |

Mean interval: {'confidence': 0.95, 'high': 1.1320413446704787, 'low': -0.9327080113371454, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.09966666666666667, 'interval': {'confidence': 0.95, 'high': 0.37079999999999974, 'low': -0.377, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 100, 'seed': 29954209203791163857134012043590026102609063388040163578069124326500414747666, 'standard_error': 0.20453442892344378}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -0.3103, 'probability_below': {'-0.25': 0.3333333333333333, '-0.5': 0.0, '-1.0': 0.0, '0.0': 0.3333333333333333}, 'tail_count': 1, 'worst': -0.377, 'worst_five_percent_mean': -0.377}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #0: -0.377; simulation seed 147165143500359106264064254969208091013421226669214277393261326133786862395060
- Run #1: 0.29; simulation seed 167854092204374731823186454209794847382854549882414974893384488656268542627726
- Run #2: 0.386; simulation seed 78407036672706857540100530307986319563653042403145764954741857789301978133098

## high_volatility

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average_absolute_inventory | units | 3/3 | 2.06686 | 2.37954 | 0.789766 | 0.455971 | 1.28972 | 1.77408 | 2.51598 | 2.62513 |
| average_effective_spread | GBP/unit | 3/3 | 0.0381111 | 0.04 | 0.00800231 | 0.00462014 | 0.0304 | 0.0346667 | 0.0425 | 0.0445 |
| average_inventory | units | 3/3 | -1.12834 | -1.67343 | 1.59519 | 0.920986 | -2.30893 | -2.02648 | -0.502737 | 0.433815 |
| average_quoted_spread | GBP/unit | 3/3 | 0.0461773 | 0.0453586 | 0.00328158 | 0.00189462 | 0.0435801 | 0.0443706 | 0.0475747 | 0.0493475 |
| buy_fills | execution records | 3/3 | 4.66667 | 4 | 1.1547 | 0.666667 | 4 | 4 | 5 | 5.8 |
| buy_units | units | 3/3 | 7.66667 | 7 | 2.08167 | 1.20185 | 6.1 | 6.5 | 8.5 | 9.7 |
| execution_edge | GBP | 3/3 | 0.356667 | 0.35 | 0.035473 | 0.0204803 | 0.3275 | 0.3375 | 0.3725 | 0.3905 |
| fees | GBP | 3/3 | 0.017 | 0.017 | 0.001 | 0.00057735 | 0.0161 | 0.0165 | 0.0175 | 0.0179 |
| fill_rate | fraction | 3/3 | 0.432456 | 0.447368 | 0.0281386 | 0.0162458 | 0.404737 | 0.423684 | 0.448684 | 0.449737 |
| final_inventory | units | 3/3 | -1.66667 | -3 | 3.21455 | 1.85592 | -3.9 | -3.5 | -0.5 | 1.5 |
| gross_realised_pnl | GBP | 3/3 | 0.166667 | 0.15 | 0.0472582 | 0.0272845 | 0.132 | 0.14 | 0.185 | 0.213 |
| inventory_movement | GBP | 3/3 | -0.35 | -0.285 | 0.22951 | 0.132508 | -0.573 | -0.445 | -0.2225 | -0.1725 |
| markout_1 | GBP/unit | 3/3 | 0.000847222 | 0.001875 | 0.00218912 | 0.00126389 | -0.0013125 | 0.000104167 | 0.00210417 | 0.0022875 |
| markout_20 | GBP/unit | 3/3 | 0.000487845 | -0.00227273 | 0.00594175 | 0.00343047 | -0.00344156 | -0.00292208 | 0.00251748 | 0.00634965 |
| markout_5 | GBP/unit | 3/3 | 0.00289773 | 0.009375 | 0.0133907 | 0.0077311 | -0.0103125 | -0.0015625 | 0.0105966 | 0.0115739 |
| maximum_absolute_inventory | units | 3/3 | 4.33333 | 4 | 0.57735 | 0.333333 | 4 | 4 | 4.5 | 4.9 |
| maximum_drawdown | GBP | 3/3 | 0.266 | 0.109 | 0.282388 | 0.163037 | 0.0982 | 0.103 | 0.3505 | 0.5437 |
| net_pnl | GBP | 3/3 | -0.0103333 | 0.092 | 0.250688 | 0.144735 | -0.2572 | -0.102 | 0.1325 | 0.1649 |
| realised_pnl | GBP | 3/3 | 0.149667 | 0.133 | 0.0482113 | 0.0278348 | 0.1141 | 0.1225 | 0.1685 | 0.1969 |
| rms_inventory | units | 3/3 | 2.42843 | 2.83131 | 0.832672 | 0.480744 | 1.60698 | 2.15112 | 2.90717 | 2.96786 |
| sell_fills | execution records | 3/3 | 5.33333 | 5 | 0.57735 | 0.333333 | 5 | 5 | 5.5 | 5.9 |
| sell_units | units | 3/3 | 9.33333 | 10 | 1.1547 | 0.666667 | 8.2 | 9 | 10 | 10 |
| turnover | GBP | 3/3 | 1699.71 | 1699.87 | 99.7351 | 57.5821 | 1609.9 | 1649.88 | 1749.62 | 1789.42 |
| two_sided_quote_time_fraction | fraction | 3/3 | 0.625399 | 0.600689 | 0.0735931 | 0.042489 | 0.570676 | 0.584015 | 0.654428 | 0.69742 |
| unrealised_pnl | GBP | 3/3 | -0.16 | -0.02 | 0.295973 | 0.17088 | -0.452 | -0.26 | 0.01 | 0.034 |

Mean interval: {'confidence': 0.95, 'high': 0.612409487647062, 'low': -0.6330761543137287, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.010333333333333325, 'interval': {'confidence': 0.95, 'high': 0.17299999999999996, 'low': -0.296, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 100, 'seed': 94138759401149363686509797039621497488155481228137385575857424477626045774169, 'standard_error': 0.13004895478138467}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -0.2572, 'probability_below': {'-0.25': 0.3333333333333333, '-0.5': 0.0, '-1.0': 0.0, '0.0': 0.3333333333333333}, 'tail_count': 1, 'worst': -0.296, 'worst_five_percent_mean': -0.296}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #2: -0.296; simulation seed 78407036672706857540100530307986319563653042403145764954741857789301978133098
- Run #1: 0.092; simulation seed 167854092204374731823186454209794847382854549882414974893384488656268542627726
- Run #0: 0.173; simulation seed 147165143500359106264064254969208091013421226669214277393261326133786862395060

## toxic_flow

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average_absolute_inventory | units | 3/3 | 1.7479 | 1.91218 | 0.479141 | 0.276632 | 1.27862 | 1.5602 | 2.01773 | 2.10218 |
| average_effective_spread | GBP/unit | 3/3 | 0.0466014 | 0.046 | 0.00443288 | 0.00255933 | 0.04285 | 0.04425 | 0.0486522 | 0.0507739 |
| average_inventory | units | 3/3 | -1.35634 | -1.14439 | 0.485869 | 0.280516 | -1.8354 | -1.52828 | -1.07842 | -1.02564 |
| average_quoted_spread | GBP/unit | 3/3 | 0.0435705 | 0.0437801 | 0.00265307 | 0.00153175 | 0.0411149 | 0.0422994 | 0.0449463 | 0.0458792 |
| buy_fills | execution records | 3/3 | 7.33333 | 7 | 0.57735 | 0.333333 | 7 | 7 | 7.5 | 7.9 |
| buy_units | units | 3/3 | 9 | 9 | 0 | 0 | 9 | 9 | 9 | 9 |
| execution_edge | GBP | 3/3 | 0.455 | 0.47 | 0.0304138 | 0.0175594 | 0.425 | 0.445 | 0.4725 | 0.4745 |
| fees | GBP | 3/3 | 0.0216667 | 0.022 | 0.00152753 | 0.000881917 | 0.0202 | 0.021 | 0.0225 | 0.0229 |
| fill_rate | fraction | 3/3 | 0.54594 | 0.55 | 0.0312879 | 0.0180641 | 0.516538 | 0.53141 | 0.5625 | 0.5725 |
| final_inventory | units | 3/3 | -3.66667 | -4 | 1.52753 | 0.881917 | -4.9 | -4.5 | -3 | -2.2 |
| gross_realised_pnl | GBP | 3/3 | 0.353333 | 0.34 | 0.051316 | 0.0296273 | 0.313 | 0.325 | 0.375 | 0.403 |
| inventory_movement | GBP | 3/3 | -0.06 | -0.095 | 0.219602 | 0.126787 | -0.2435 | -0.1775 | 0.04 | 0.148 |
| markout_1 | GBP/unit | 3/3 | 0.0135335 | 0.0120588 | 0.00271496 | 0.00156748 | 0.0118934 | 0.0119669 | 0.0143627 | 0.0162059 |
| markout_20 | GBP/unit | 3/3 | 0.0154351 | 0.0142857 | 0.0087139 | 0.00503097 | 0.00804622 | 0.0108193 | 0.0194762 | 0.0236286 |
| markout_5 | GBP/unit | 3/3 | 0.0167212 | 0.0204762 | 0.00977549 | 0.00564388 | 0.00711012 | 0.0130506 | 0.0222693 | 0.0237039 |
| maximum_absolute_inventory | units | 3/3 | 5 | 5 | 1 | 0.57735 | 4.1 | 4.5 | 5.5 | 5.9 |
| maximum_drawdown | GBP | 3/3 | 0.364 | 0.35 | 0.169434 | 0.097823 | 0.2168 | 0.276 | 0.445 | 0.521 |
| net_pnl | GBP | 3/3 | 0.373333 | 0.302 | 0.229472 | 0.132486 | 0.1994 | 0.245 | 0.466 | 0.5972 |
| realised_pnl | GBP | 3/3 | 0.331667 | 0.317 | 0.0525579 | 0.0303443 | 0.2909 | 0.3025 | 0.3535 | 0.3827 |
| rms_inventory | units | 3/3 | 2.3655 | 2.53433 | 0.564336 | 0.32582 | 1.81585 | 2.13517 | 2.68024 | 2.79697 |
| sell_fills | execution records | 3/3 | 9.33333 | 8 | 3.21455 | 1.85592 | 7.1 | 7.5 | 10.5 | 12.5 |
| sell_units | units | 3/3 | 12.6667 | 13 | 1.52753 | 0.881917 | 11.2 | 12 | 13.5 | 13.9 |
| turnover | GBP | 3/3 | 2166.77 | 2199.91 | 153.006 | 88.3379 | 2019.91 | 2099.91 | 2250.2 | 2290.43 |
| two_sided_quote_time_fraction | fraction | 3/3 | 0.531428 | 0.513414 | 0.0601051 | 0.0347017 | 0.485493 | 0.497902 | 0.555947 | 0.589974 |
| unrealised_pnl | GBP | 3/3 | 0.0416667 | -0.015 | 0.176942 | 0.102157 | -0.0915 | -0.0575 | 0.1125 | 0.2145 |

Mean interval: {'confidence': 0.95, 'high': 0.9433730280575282, 'low': -0.19670636139086162, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.3733333333333333, 'interval': {'confidence': 0.95, 'high': 0.5780666666666657, 'low': 0.22599999999999998, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 100, 'seed': 47420996894226818341551516282069211098384576435220486526146650973607535143128, 'standard_error': 0.10600532015533262}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': 0.1994, 'probability_below': {'-0.25': 0.0, '-0.5': 0.0, '-1.0': 0.0, '0.0': 0.0}, 'tail_count': 1, 'worst': 0.188, 'worst_five_percent_mean': 0.188}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #2: 0.188; simulation seed 78407036672706857540100530307986319563653042403145764954741857789301978133098
- Run #1: 0.302; simulation seed 167854092204374731823186454209794847382854549882414974893384488656268542627726
- Run #0: 0.63; simulation seed 147165143500359106264064254969208091013421226669214277393261326133786862395060

## Interpretation

high_volatility: observed mean net_pnl=-0.0103333; losing/negative outcomes 33.3%. normal: observed mean net_pnl=0.0996667; losing/negative outcomes 33.3%. toxic_flow: observed mean net_pnl=0.373333; losing/negative outcomes 0.0%. Compare the full distributions and paired uncertainty with the original hypothesis. These conditional model outcomes do not establish real-world alpha, safety or an optimal parameter. Interpretation remains reviewable.

## Limitations

- Controlled scenario comparison; never a forecast of real-market performance.
- Independent scenario-specific streams; unpaired comparisons, conditional on the model.
- Arrival rates and model volatility differ; the paths are not claimed to be identical.

Quantiles use linear interpolation; SD uses n−1. Markout distributions use per-session available-unit means, with session and unit coverage retained. A confidence interval concerns the model's mean, not the range of future outcomes.
