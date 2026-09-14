# QuantLab synthetic research experiment

What happens when a previously stable residual acquires a unit root and drift?

**Prediction registered before execution:** An old relationship may fail despite stops and reassuring training fits.

Status: complete. Pool: evaluation. Sessions per variant: 32. Root seed: 10101003.

Synthetic performance is not evidence of real-world alpha.

## stable

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average_trade | GBP | 32/32 | 0.976807 | 0.994792 | 0.984358 | 0.174012 | -0.9296 | 0.585417 | 1.51363 | 2.25375 |
| costs | GBP | 32/32 | 1.71563 | 1.77 | 0.412779 | 0.0729697 | 1.08 | 1.4625 | 1.89 | 2.43 |
| drawdown | GBP | 32/32 | 5.60094 | 5.355 | 2.42555 | 0.428781 | 2.45375 | 4.1575 | 6.9125 | 9.648 |
| max_gross | GBP | 32/32 | 940.131 | 936.62 | 53.8012 | 9.51079 | 868.343 | 900.145 | 980.5 | 1030.35 |
| max_imbalance | GBP | 32/32 | 479.687 | 495.865 | 62.0393 | 10.9671 | 419.047 | 434.59 | 512.546 | 531.928 |
| mean_entry_z | units | 32/32 | 0.393599 | 0.341028 | 0.878398 | 0.15528 | -0.806705 | -0.289213 | 0.905185 | 1.84237 |
| mean_exit_z | units | 32/32 | 0.0639389 | 0.033758 | 0.357689 | 0.063231 | -0.38338 | -0.258059 | 0.327044 | 0.61797 |
| mean_holding | observations | 32/32 | 10.7551 | 10.0714 | 3.15573 | 0.55786 | 7.38466 | 8.62946 | 12.4833 | 16.86 |
| median_trade | GBP | 32/32 | 1.14625 | 1.17 | 1.28797 | 0.227683 | -1.449 | 0.77 | 2.07 | 2.83775 |
| net_pnl | GBP | 32/32 | 6.39719 | 7.26 | 5.51144 | 0.974294 | -4.648 | 4.1675 | 9.6975 | 13.5225 |
| probability_loss | fraction | 32/32 | 0.282544 | 0.236111 | 0.210479 | 0.0372078 | 0 | 0.142857 | 0.372727 | 0.6675 |
| residual_inventory | units | 32/32 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| return_on_capital | fraction | 32/32 | 0.000639719 | 0.000726 | 0.000551144 | 9.74294e-05 | -0.0004648 | 0.00041675 | 0.00096975 | 0.00135225 |
| trade_count | units | 32/32 | 6.3125 | 6 | 1.5951 | 0.281977 | 4 | 5 | 7 | 9 |
| turnover | GBP | 32/32 | 11386.2 | 11269.1 | 2785.63 | 492.435 | 6985.07 | 9859.56 | 12643.3 | 15831.6 |
| win_rate | fraction | 32/32 | 0.712992 | 0.732143 | 0.20893 | 0.036934 | 0.3325 | 0.627273 | 0.839286 | 1 |
| worst_trade | GBP | 32/32 | -2.04344 | -1.66 | 2.12214 | 0.375145 | -5.3585 | -3.645 | -0.2675 | 0.8545 |

Mean interval: {'confidence': 0.95, 'high': 8.384273887771002, 'low': 4.410101112228998, 'method': 'Student t mean'}
Bootstrap: {'estimate': 6.397187499999999, 'interval': {'confidence': 0.95, 'high': 8.341085937499997, 'low': 4.642296875, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 500, 'seed': 15978447075806357004300137016985531366972715107363217330391684832426228282624, 'standard_error': 0.9093434438350223}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -4.648, 'probability_below': {'-0.25': 0.09375, '-0.5': 0.09375, '-1.0': 0.09375, '0.0': 0.09375}, 'tail_count': 2, 'worst': -7.829999999999999, 'worst_five_percent_mean': -6.854999999999999}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #14: -7.83; simulation seed 106149197002843453626647190750617984123681658375005056160345241913835861576631
- Run #5: -5.88; simulation seed 159734144456664067177823255967332062267102130934940199441790055937313798374127
- Run #29: -3.64; simulation seed 143684243275370597616326741944180291356663388421022947830845745534024908621183

## drift

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average_trade | GBP | 32/32 | -5.81375 | -5.526 | 2.49777 | 0.441548 | -10.0281 | -7.02388 | -4.121 | -2.43237 |
| costs | GBP | 32/32 | 1.38188 | 1.35 | 0.274102 | 0.0484548 | 1.026 | 1.185 | 1.62 | 1.8405 |
| drawdown | GBP | 32/32 | 31.92 | 30.8825 | 8.69479 | 1.53704 | 17.641 | 27.3212 | 36.045 | 47.067 |
| max_gross | GBP | 32/32 | 960.693 | 960.025 | 53.3267 | 9.42692 | 882.786 | 907.517 | 997.612 | 1038.47 |
| max_imbalance | GBP | 32/32 | 475.983 | 490.857 | 62.775 | 11.0972 | 414.554 | 428.451 | 509.062 | 535.895 |
| mean_entry_z | units | 32/32 | 2.17697 | 2.37054 | 0.542682 | 0.0959334 | 1.24321 | 2.04414 | 2.52777 | 2.7201 |
| mean_exit_z | units | 32/32 | 1.42304 | 1.32255 | 0.413496 | 0.0730964 | 0.980108 | 1.14271 | 1.62726 | 2.16262 |
| mean_holding | observations | 32/32 | 23.3721 | 23.1167 | 3.80632 | 0.672869 | 17.9786 | 21.2917 | 26.1 | 29.9 |
| median_trade | GBP | 32/32 | -6.34016 | -6.33 | 2.59079 | 0.457992 | -10.195 | -7.8 | -4.9125 | -2.31475 |
| net_pnl | GBP | 32/32 | -28.9497 | -27.63 | 10.3952 | 1.83762 | -46.486 | -35.06 | -23.4275 | -11.9805 |
| probability_loss | fraction | 32/32 | 0.829092 | 0.816667 | 0.144429 | 0.0255317 | 0.6 | 0.741071 | 1 | 1 |
| residual_inventory | units | 32/32 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| return_on_capital | fraction | 32/32 | -0.00289497 | -0.002763 | 0.00103952 | 0.000183762 | -0.0046486 | -0.003506 | -0.00234275 | -0.00119805 |
| trade_count | units | 32/32 | 5.15625 | 5 | 0.883883 | 0.15625 | 4 | 4.75 | 6 | 6.45 |
| turnover | GBP | 32/32 | 9362.41 | 8959.77 | 1713.14 | 302.843 | 7231.84 | 8128.22 | 10615.5 | 12210.1 |
| win_rate | fraction | 32/32 | 0.170908 | 0.183333 | 0.144429 | 0.0255317 | 0 | 0 | 0.258929 | 0.4 |
| worst_trade | GBP | 32/32 | -11.8569 | -11.275 | 3.68417 | 0.651275 | -18.8125 | -13.6275 | -9.45 | -6.612 |

Mean interval: {'confidence': 0.95, 'high': -25.201832990731734, 'low': -32.69754200926826, 'method': 'Student t mean'}
Bootstrap: {'estimate': -28.9496875, 'interval': {'confidence': 0.95, 'high': -25.607640625, 'low': -32.61184375, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 500, 'seed': 25075499692874152813304176255428522815275630417282953585177539732955653351545, 'standard_error': 1.7835960217278417}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -46.486, 'probability_below': {'-0.25': 1.0, '-0.5': 1.0, '-1.0': 1.0, '0.0': 1.0}, 'tail_count': 2, 'worst': -52.8, 'worst_five_percent_mean': -51.974999999999994}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #22: -52.8; simulation seed 207276985011957444843598841103703723854605725491896624962560863837145118589913
- Run #17: -51.15; simulation seed 142383261985665436903536301948857758924900866329161768047039355026080936963843
- Run #2: -42.67; simulation seed 41732618488736918462198714411923217049700200370113671699223009359809925311437

## Interpretation

drift: observed mean net_pnl=-28.9497; losing/negative outcomes 100.0%. stable: observed mean net_pnl=6.39719; losing/negative outcomes 9.4%. Compare the full distributions and paired uncertainty with the original hypothesis. These conditional model outcomes do not establish real-world alpha, safety or an optimal parameter. Interpretation remains reviewable.

## Limitations

- Synthetic results do not establish real-market alpha.
- Training-selected performance is optimistic; evaluation never selects thresholds.
- The initial fit origin differs across disjoint time blocks; blocks may have different lengths.
- Confidence intervals exclude process, liquidity and model uncertainty.

Quantiles use linear interpolation; SD uses n−1. Markout distributions use per-session available-unit means, with session and unit coverage retained. A confidence interval concerns the model's mean, not the range of future outcomes.
