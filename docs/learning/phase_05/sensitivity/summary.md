# QuantLab synthetic research experiment

What trade-offs change as k changes?

**Prediction registered before execution:** Increasing inventory sensitivity reduces average absolute inventory; changes in P&L and markouts are uncertain. This sweep explores trade-offs without selecting an optimum.

Status: complete. Pool: development. Sessions per variant: 100. Root seed: 20260911.

Synthetic performance is not evidence of real-world alpha.

## strategy.inventory_skew_ticks=0

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average_absolute_inventory | units | 100/100 | 3.10129 | 3.04182 | 1.27171 | 0.127171 | 1.41745 | 2.08019 | 4.10272 | 5.08702 |
| average_effective_spread | GBP/unit | 100/100 | 0.0349271 | 0.0352174 | 0.00427131 | 0.000427131 | 0.0276648 | 0.0324519 | 0.0375368 | 0.0417717 |
| average_inventory | units | 100/100 | 0.0972424 | 0.47016 | 3.04011 | 0.304011 | -4.56954 | -2.66973 | 2.19621 | 4.55706 |
| average_quoted_spread | GBP/unit | 100/100 | 0.0431703 | 0.0431173 | 0.00153376 | 0.000153376 | 0.0409442 | 0.0421786 | 0.0440011 | 0.0460693 |
| buy_fills | execution records | 100/100 | 7.95 | 8 | 3.7642 | 0.37642 | 3 | 5 | 10 | 14 |
| buy_units | units | 100/100 | 10.25 | 10 | 4.34468 | 0.434468 | 3 | 7 | 13 | 17 |
| execution_edge | GBP | 100/100 | 0.384 | 0.3375 | 0.16385 | 0.016385 | 0.175 | 0.27 | 0.48 | 0.70625 |
| fees | GBP | 100/100 | 0.01999 | 0.019 | 0.00697397 | 0.000697397 | 0.01095 | 0.014 | 0.02425 | 0.03305 |
| fill_rate | fraction | 100/100 | 0.184863 | 0.176073 | 0.0606846 | 0.00606846 | 0.099661 | 0.14256 | 0.22663 | 0.29459 |
| final_inventory | units | 100/100 | 0.51 | 1.5 | 4.83776 | 0.483776 | -7 | -4 | 5 | 7 |
| gross_realised_pnl | GBP | 100/100 | 0.1667 | 0.165 | 0.179072 | 0.0179072 | -0.0905 | 0.06 | 0.2825 | 0.44 |
| inventory_movement | GBP | 100/100 | -0.2293 | -0.205 | 0.225552 | 0.0225552 | -0.622 | -0.37 | -0.04875 | 0.06675 |
| markout_1 | GBP/unit | 100/100 | 0.00587738 | 0.00614379 | 0.00489174 | 0.000489174 | -0.00105294 | 0.00222222 | 0.00866477 | 0.015 |
| markout_20 | GBP/unit | 100/100 | 0.00681556 | 0.00776389 | 0.0147808 | 0.00147808 | -0.024525 | -0.00102778 | 0.0153704 | 0.0267083 |
| markout_5 | GBP/unit | 100/100 | 0.00623698 | 0.00707143 | 0.00777014 | 0.000777014 | -0.00720313 | 0.00135417 | 0.0121627 | 0.0175227 |
| maximum_absolute_inventory | units | 100/100 | 6.03 | 6.5 | 1.27489 | 0.127489 | 3 | 6 | 7 | 7 |
| maximum_drawdown | GBP | 100/100 | 0.29528 | 0.254 | 0.168111 | 0.0168111 | 0.0706 | 0.1655 | 0.43975 | 0.57215 |
| net_pnl | GBP | 100/100 | 0.13471 | 0.139 | 0.230519 | 0.0230519 | -0.23385 | -0.03775 | 0.28225 | 0.47765 |
| realised_pnl | GBP | 100/100 | 0.14671 | 0.1455 | 0.175344 | 0.0175344 | -0.10655 | 0.0445 | 0.26225 | 0.40225 |
| rms_inventory | units | 100/100 | 3.60858 | 3.60504 | 1.28089 | 0.128089 | 1.77561 | 2.60439 | 4.64172 | 5.46799 |
| sell_fills | execution records | 100/100 | 7.19 | 7 | 3.2897 | 0.32897 | 3 | 5 | 9 | 14.05 |
| sell_units | units | 100/100 | 9.74 | 10 | 4.14051 | 0.414051 | 3.95 | 7 | 11.25 | 18.05 |
| turnover | GBP | 100/100 | 1999.02 | 1899.86 | 697.488 | 69.7488 | 1095.57 | 1400.23 | 2425.61 | 3307.05 |
| two_sided_quote_time_fraction | fraction | 100/100 | 0.763512 | 0.822794 | 0.168235 | 0.0168235 | 0.422819 | 0.663196 | 0.884121 | 0.94056 |
| unrealised_pnl | GBP | 100/100 | -0.012 | 0 | 0.143773 | 0.0143773 | -0.2535 | -0.0925 | 0.07 | 0.21525 |

Mean interval: {'confidence': 0.95, 'high': 0.18044994754599034, 'low': 0.08897005245400966, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.13471, 'interval': {'confidence': 0.95, 'high': 0.17893125000000001, 'low': 0.08897324999999999, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 50103134853913059689607251091583509402992880962827845656355832272409443987016, 'standard_error': 0.022930042006502845}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -0.23385, 'probability_below': {'-0.25': 0.04, '-0.5': 0.0, '-1.0': 0.0, '0.0': 0.29}, 'tail_count': 5, 'worst': -0.43, 'worst_five_percent_mean': -0.2956}

Exploratory correlations (not causal effects):

- average_absolute_inventory vs net_pnl: {'available': 100, 'correlation': -0.38122523260148117, 'covariance': -0.11175732582628622, 'missing': 0}
- fill_rate vs markout_1: {'available': 100, 'correlation': -0.10324480353261324, 'covariance': -3.064857989050677e-05, 'missing': 0}
- maximum_absolute_inventory vs maximum_drawdown: {'available': 100, 'correlation': 0.6897522255688193, 'covariance': 0.14782989898989898, 'missing': 0}
- turnover vs fees: {'available': 100, 'correlation': 0.9999994658165191, 'covariance': 4.86425573939394, 'missing': 0}

Worst primary outcomes:

- Run #83: -0.43; simulation seed 213784530665346043537354841796936441057077261688185306632739253664375158897584
- Run #57: -0.272; simulation seed 26889556514929835526247768203750984551705884665156319974961260082893035346728
- Run #81: -0.267; simulation seed 68773215051095044401838658870669618944010391119203694634658264614024507519944

## strategy.inventory_skew_ticks=1/4

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average_absolute_inventory | units | 100/100 | 2.17992 | 2.10704 | 0.833592 | 0.0833592 | 1.07467 | 1.55956 | 2.71179 | 3.62271 |
| average_effective_spread | GBP/unit | 100/100 | 0.0376325 | 0.0380564 | 0.00447263 | 0.000447263 | 0.03 | 0.0337292 | 0.0413988 | 0.0439257 |
| average_inventory | units | 100/100 | -0.0931794 | 0.249833 | 1.8414 | 0.18414 | -3.02987 | -1.45566 | 1.19771 | 2.62652 |
| average_quoted_spread | GBP/unit | 100/100 | 0.0474902 | 0.0475676 | 0.00133146 | 0.000133146 | 0.045031 | 0.0465154 | 0.0486086 | 0.0492691 |
| buy_fills | execution records | 100/100 | 8.53 | 8 | 3.48577 | 0.348577 | 4 | 6 | 10 | 15 |
| buy_units | units | 100/100 | 10.97 | 10.5 | 3.81241 | 0.381241 | 5 | 9 | 14 | 17 |
| execution_edge | GBP | 100/100 | 0.4256 | 0.4075 | 0.171387 | 0.0171387 | 0.18925 | 0.31375 | 0.51625 | 0.72825 |
| fees | GBP | 100/100 | 0.0217 | 0.021 | 0.00711734 | 0.000711734 | 0.01 | 0.017 | 0.026 | 0.036 |
| fill_rate | fraction | 100/100 | 0.187642 | 0.181048 | 0.064525 | 0.0064525 | 0.0833333 | 0.142857 | 0.224707 | 0.313043 |
| final_inventory | units | 100/100 | 0.24 | 0 | 3.20706 | 0.320706 | -5 | -2.25 | 2 | 5 |
| gross_realised_pnl | GBP | 100/100 | 0.0222 | 0.09 | 0.257727 | 0.0257727 | -0.4475 | -0.1225 | 0.17 | 0.3405 |
| inventory_movement | GBP | 100/100 | -0.44845 | -0.335 | 0.386548 | 0.0386548 | -1.16525 | -0.625 | -0.18375 | -0.0245 |
| markout_1 | GBP/unit | 100/100 | 0.00465231 | 0.00513889 | 0.00518457 | 0.000518457 | -0.00416667 | 0.00112013 | 0.00859375 | 0.0121892 |
| markout_20 | GBP/unit | 100/100 | -0.000789643 | 0.00353365 | 0.01644 | 0.001644 | -0.0308542 | -0.0120536 | 0.0106458 | 0.0197143 |
| markout_5 | GBP/unit | 100/100 | 0.00424294 | 0.00484375 | 0.00838537 | 0.000838537 | -0.00910556 | -0.00178125 | 0.010614 | 0.0169593 |
| maximum_absolute_inventory | units | 100/100 | 5.18 | 5 | 1.31333 | 0.131333 | 3 | 4 | 6 | 7 |
| maximum_drawdown | GBP | 100/100 | 0.36297 | 0.232 | 0.325733 | 0.0325733 | 0.06095 | 0.126 | 0.501 | 1.02805 |
| net_pnl | GBP | 100/100 | -0.04455 | 0.0395 | 0.339113 | 0.0339113 | -0.7342 | -0.15975 | 0.16725 | 0.33415 |
| realised_pnl | GBP | 100/100 | 0.0005 | 0.07 | 0.258328 | 0.0258328 | -0.47185 | -0.14425 | 0.151 | 0.31735 |
| rms_inventory | units | 100/100 | 2.62028 | 2.58436 | 0.872588 | 0.0872588 | 1.36159 | 1.96309 | 3.19064 | 4.19195 |
| sell_fills | execution records | 100/100 | 7.9 | 7 | 3.31358 | 0.331358 | 3 | 6 | 9 | 14 |
| sell_units | units | 100/100 | 10.73 | 10 | 3.99205 | 0.399205 | 5 | 8 | 13 | 18.05 |
| turnover | GBP | 100/100 | 2170.25 | 2099.74 | 712.182 | 71.2182 | 999.875 | 1698.85 | 2599.84 | 3602.11 |
| two_sided_quote_time_fraction | fraction | 100/100 | 0.855773 | 0.862092 | 0.0715827 | 0.00715827 | 0.72662 | 0.816071 | 0.905044 | 0.954493 |
| unrealised_pnl | GBP | 100/100 | -0.04505 | 0 | 0.184113 | 0.0184113 | -0.4305 | -0.0725 | 0.03 | 0.1005 |

Mean interval: {'confidence': 0.95, 'high': 0.022737446346963314, 'low': -0.1118374463469633, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.04454999999999999, 'interval': {'confidence': 0.95, 'high': 0.01956274999999987, 'low': -0.10926875000000001, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 54948378471766960093217350534232042565440552171156067956249244353033520105178, 'standard_error': 0.033357838837324634}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -0.7342, 'probability_below': {'-0.25': 0.21, '-0.5': 0.1, '-1.0': 0.02, '0.0': 0.4}, 'tail_count': 5, 'worst': -1.366, 'worst_five_percent_mean': -1.0474}

Exploratory correlations (not causal effects):

- average_absolute_inventory vs net_pnl: {'available': 100, 'correlation': -0.6586086058157805, 'covariance': -0.1861768047753367, 'missing': 0}
- fill_rate vs markout_1: {'available': 100, 'correlation': -0.13094201547164389, 'covariance': -4.380465314656108e-05, 'missing': 0}
- maximum_absolute_inventory vs maximum_drawdown: {'available': 100, 'correlation': 0.7374297886018029, 'covariance': 0.31547010101010103, 'missing': 0}
- turnover vs fees: {'available': 100, 'correlation': 0.9999984283316339, 'covariance': 5.068831929292931, 'missing': 0}

Worst primary outcomes:

- Run #87: -1.366; simulation seed 11743892100036479364658758705601003740538728049255705128329279118622358822812
- Run #24: -1.066; simulation seed 192252103020309354053258320894013241524653815353629070803561255375009684798440
- Run #81: -0.978; simulation seed 68773215051095044401838658870669618944010391119203694634658264614024507519944

## strategy.inventory_skew_ticks=1/2

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average_absolute_inventory | units | 100/100 | 1.73033 | 1.67024 | 0.642587 | 0.0642587 | 0.809356 | 1.28868 | 2.09193 | 2.78817 |
| average_effective_spread | GBP/unit | 100/100 | 0.0355493 | 0.0357143 | 0.00440013 | 0.000440013 | 0.0287435 | 0.0323739 | 0.0385046 | 0.0412843 |
| average_inventory | units | 100/100 | -0.0423122 | -0.0742643 | 1.19602 | 0.119602 | -2.38205 | -0.8679 | 0.85863 | 1.73631 |
| average_quoted_spread | GBP/unit | 100/100 | 0.0452488 | 0.0453171 | 0.00137768 | 0.000137768 | 0.0431394 | 0.0441833 | 0.0461936 | 0.0474806 |
| buy_fills | execution records | 100/100 | 9.29 | 9 | 3.35537 | 0.335537 | 5 | 7 | 11 | 15.05 |
| buy_units | units | 100/100 | 12.05 | 11 | 3.82014 | 0.382014 | 7 | 9 | 15 | 18 |
| execution_edge | GBP | 100/100 | 0.4155 | 0.385 | 0.165986 | 0.0165986 | 0.19975 | 0.28875 | 0.5325 | 0.7305 |
| fees | GBP | 100/100 | 0.02392 | 0.023 | 0.00719242 | 0.000719242 | 0.01395 | 0.019 | 0.03 | 0.0342 |
| fill_rate | fraction | 100/100 | 0.203359 | 0.198291 | 0.0635653 | 0.00635653 | 0.11625 | 0.158333 | 0.253659 | 0.322034 |
| final_inventory | units | 100/100 | 0.18 | 0 | 2.64911 | 0.264911 | -4 | -1 | 1 | 5 |
| gross_realised_pnl | GBP | 100/100 | -0.1103 | 0.005 | 0.355983 | 0.0355983 | -0.8735 | -0.2225 | 0.105 | 0.24 |
| inventory_movement | GBP | 100/100 | -0.5938 | -0.465 | 0.526676 | 0.0526676 | -1.73675 | -0.72875 | -0.24125 | -0.0645 |
| markout_1 | GBP/unit | 100/100 | 0.00319909 | 0.0036159 | 0.0051585 | 0.00051585 | -0.00458696 | -0.000413043 | 0.00665455 | 0.0104343 |
| markout_20 | GBP/unit | 100/100 | -0.00670249 | -0.000674603 | 0.0213057 | 0.00213057 | -0.0561122 | -0.0165769 | 0.0082598 | 0.01689 |
| markout_5 | GBP/unit | 100/100 | 0.000413696 | 0.00218071 | 0.00924446 | 0.000924446 | -0.0198542 | -0.005 | 0.00678632 | 0.0118387 |
| maximum_absolute_inventory | units | 100/100 | 4.83 | 5 | 1.26375 | 0.126375 | 3 | 4 | 6 | 7 |
| maximum_drawdown | GBP | 100/100 | 0.4402 | 0.3165 | 0.436024 | 0.0436024 | 0.06485 | 0.1575 | 0.5525 | 1.3896 |
| net_pnl | GBP | 100/100 | -0.20222 | -0.072 | 0.468073 | 0.0468073 | -1.306 | -0.2965 | 0.0915 | 0.2249 |
| realised_pnl | GBP | 100/100 | -0.13422 | -0.0225 | 0.357777 | 0.0357777 | -0.9017 | -0.243 | 0.08775 | 0.21425 |
| rms_inventory | units | 100/100 | 2.1999 | 2.16478 | 0.699399 | 0.0699399 | 1.21747 | 1.77931 | 2.62238 | 3.34368 |
| sell_fills | execution records | 100/100 | 8.74 | 8 | 3.11276 | 0.311276 | 4 | 7 | 11 | 14 |
| sell_units | units | 100/100 | 11.87 | 11 | 3.84459 | 0.384459 | 7 | 9 | 15 | 18.05 |
| turnover | GBP | 100/100 | 2392.27 | 2298.64 | 719.68 | 71.968 | 1394.18 | 1899.43 | 2998.78 | 3422.31 |
| two_sided_quote_time_fraction | fraction | 100/100 | 0.846363 | 0.855617 | 0.0666985 | 0.00666985 | 0.726331 | 0.810245 | 0.895458 | 0.939718 |
| unrealised_pnl | GBP | 100/100 | -0.068 | 0 | 0.207002 | 0.0207002 | -0.4705 | -0.08 | 0.01625 | 0.0605 |

Mean interval: {'confidence': 0.95, 'high': -0.10934421720374553, 'low': -0.2950957827962544, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.20221999999999998, 'interval': {'confidence': 0.95, 'high': -0.11519500000000003, 'low': -0.2965757499999999, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 95719908220865075752858432636907437347609548503165165982017615684539026279559, 'standard_error': 0.04692203465460619}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.306, 'probability_below': {'-0.25': 0.32, '-0.5': 0.15, '-1.0': 0.07, '0.0': 0.59}, 'tail_count': 5, 'worst': -1.864, 'worst_five_percent_mean': -1.7386}

Exploratory correlations (not causal effects):

- average_absolute_inventory vs net_pnl: {'available': 100, 'correlation': -0.7065221598427583, 'covariance': -0.2125058750407677, 'missing': 0}
- fill_rate vs markout_1: {'available': 100, 'correlation': -0.36882227708490817, 'covariance': -0.00012093726124466689, 'missing': 0}
- maximum_absolute_inventory vs maximum_drawdown: {'available': 100, 'correlation': 0.7253938875799825, 'covariance': 0.39971111111111113, 'missing': 0}
- turnover vs fees: {'available': 100, 'correlation': 0.9999971327508493, 'covariance': 5.17622974949495, 'missing': 0}

Worst primary outcomes:

- Run #24: -1.864; simulation seed 192252103020309354053258320894013241524653815353629070803561255375009684798440
- Run #3: -1.831; simulation seed 209553395530555786858897643695940882884174153996724501254507505339832443478374
- Run #81: -1.822; simulation seed 68773215051095044401838658870669618944010391119203694634658264614024507519944

## strategy.inventory_skew_ticks=1

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average_absolute_inventory | units | 100/100 | 1.43365 | 1.37076 | 0.596677 | 0.0596677 | 0.590676 | 1.06383 | 1.71976 | 2.51485 |
| average_effective_spread | GBP/unit | 100/100 | 0.0340748 | 0.03375 | 0.00477741 | 0.000477741 | 0.0285238 | 0.0308818 | 0.0365385 | 0.0418141 |
| average_inventory | units | 100/100 | -0.00840597 | 0.0639589 | 0.899611 | 0.0899611 | -1.50951 | -0.437507 | 0.564162 | 1.16438 |
| average_quoted_spread | GBP/unit | 100/100 | 0.0444909 | 0.0440871 | 0.00180221 | 0.000180221 | 0.0421874 | 0.0432118 | 0.0457706 | 0.0478396 |
| buy_fills | execution records | 100/100 | 10.25 | 10 | 3.42709 | 0.342709 | 5.95 | 8 | 12 | 17 |
| buy_units | units | 100/100 | 13.37 | 13 | 3.82088 | 0.382088 | 7.95 | 11 | 16 | 20 |
| execution_edge | GBP | 100/100 | 0.37525 | 0.36 | 0.160909 | 0.0160909 | 0.15425 | 0.2575 | 0.4775 | 0.661 |
| fees | GBP | 100/100 | 0.02644 | 0.026 | 0.0073914 | 0.00073914 | 0.016 | 0.02175 | 0.03125 | 0.038 |
| fill_rate | fraction | 100/100 | 0.223199 | 0.216667 | 0.0640334 | 0.00640334 | 0.133333 | 0.181618 | 0.266667 | 0.325129 |
| final_inventory | units | 100/100 | 0.3 | 0 | 2.19043 | 0.219043 | -3 | -1 | 1 | 5 |
| gross_realised_pnl | GBP | 100/100 | -0.3401 | -0.145 | 0.554055 | 0.0554055 | -1.594 | -0.4725 | 0.03 | 0.141 |
| inventory_movement | GBP | 100/100 | -0.76415 | -0.545 | 0.67915 | 0.067915 | -2.06825 | -0.9 | -0.35625 | -0.14925 |
| markout_1 | GBP/unit | 100/100 | -0.0016914 | -0.00137771 | 0.00747165 | 0.000747165 | -0.0107177 | -0.00532527 | 0.00380952 | 0.00642211 |
| markout_20 | GBP/unit | 100/100 | -0.0164355 | -0.00758929 | 0.0255342 | 0.00255342 | -0.0702273 | -0.0292788 | 0.00117788 | 0.0109406 |
| markout_5 | GBP/unit | 100/100 | -0.00442994 | -0.00306548 | 0.00962586 | 0.000962586 | -0.022 | -0.00931277 | 0.00182416 | 0.00864205 |
| maximum_absolute_inventory | units | 100/100 | 4.41 | 4 | 1.27204 | 0.127204 | 2.95 | 3 | 5 | 6.05 |
| maximum_drawdown | GBP | 100/100 | 0.6025 | 0.359 | 0.650505 | 0.0650505 | 0.0635 | 0.18575 | 0.72625 | 1.94585 |
| net_pnl | GBP | 100/100 | -0.41534 | -0.2035 | 0.638832 | 0.0638832 | -1.7774 | -0.5305 | -0.0015 | 0.13215 |
| realised_pnl | GBP | 100/100 | -0.36654 | -0.1675 | 0.556424 | 0.0556424 | -1.6231 | -0.49675 | -0.001 | 0.12565 |
| rms_inventory | units | 100/100 | 1.89497 | 1.81524 | 0.677184 | 0.0677184 | 0.94945 | 1.4164 | 2.23768 | 3.17081 |
| sell_fills | execution records | 100/100 | 9.68 | 9 | 3.2 | 0.32 | 5 | 7 | 12 | 15 |
| sell_units | units | 100/100 | 13.07 | 13 | 3.88796 | 0.388796 | 8 | 10 | 16 | 19 |
| turnover | GBP | 100/100 | 2644.31 | 2600.8 | 739.804 | 73.9804 | 1600.82 | 2173.29 | 3129.42 | 3802.59 |
| two_sided_quote_time_fraction | fraction | 100/100 | 0.826894 | 0.833668 | 0.0671052 | 0.00671052 | 0.697052 | 0.784165 | 0.876589 | 0.914423 |
| unrealised_pnl | GBP | 100/100 | -0.0488 | 0 | 0.147985 | 0.0147985 | -0.3305 | -0.035 | 0 | 0.04025 |

Mean interval: {'confidence': 0.95, 'high': -0.2885819369872219, 'low': -0.5420980630127782, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.41534000000000004, 'interval': {'confidence': 0.95, 'high': -0.2936897500000001, 'low': -0.5421485, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 62631267762930373758930429026820955458907659677605389051766266950340041626421, 'standard_error': 0.06258658706184277}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.7774, 'probability_below': {'-0.25': 0.48, '-0.5': 0.29, '-1.0': 0.12, '0.0': 0.75}, 'tail_count': 5, 'worst': -3.186, 'worst_five_percent_mean': -2.4731999999999994}

Exploratory correlations (not causal effects):

- average_absolute_inventory vs net_pnl: {'available': 100, 'correlation': -0.7975123511694612, 'covariance': -0.3039925962173468, 'missing': 0}
- fill_rate vs markout_1: {'available': 100, 'correlation': -0.19160009348238566, 'covariance': -9.166823091823098e-05, 'missing': 0}
- maximum_absolute_inventory vs maximum_drawdown: {'available': 100, 'correlation': 0.7485972598496333, 'covariance': 0.619439393939394, 'missing': 0}
- turnover vs fees: {'available': 100, 'correlation': 0.9999946964614027, 'covariance': 5.46815275959596, 'missing': 0}

Worst primary outcomes:

- Run #24: -3.186; simulation seed 192252103020309354053258320894013241524653815353629070803561255375009684798440
- Run #81: -2.878; simulation seed 68773215051095044401838658870669618944010391119203694634658264614024507519944
- Run #3: -2.284; simulation seed 209553395530555786858897643695940882884174153996724501254507505339832443478374

## strategy.inventory_skew_ticks=2

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| average_absolute_inventory | units | 100/100 | 1.21348 | 1.10244 | 0.560821 | 0.0560821 | 0.529875 | 0.784872 | 1.49253 | 2.25577 |
| average_effective_spread | GBP/unit | 100/100 | 0.0332911 | 0.0331561 | 0.00575037 | 0.000575037 | 0.0253654 | 0.029272 | 0.0369616 | 0.0419345 |
| average_inventory | units | 100/100 | -0.0683446 | 0.0198315 | 0.651557 | 0.0651557 | -1.14431 | -0.370477 | 0.324103 | 0.981908 |
| average_quoted_spread | GBP/unit | 100/100 | 0.0465917 | 0.0456592 | 0.00362754 | 0.000362754 | 0.0429502 | 0.0442803 | 0.0473392 | 0.0531403 |
| buy_fills | execution records | 100/100 | 11.18 | 11 | 3.68009 | 0.368009 | 5.95 | 8 | 13 | 17 |
| buy_units | units | 100/100 | 14.39 | 14 | 4.02491 | 0.402491 | 8 | 12 | 17 | 22 |
| execution_edge | GBP | 100/100 | 0.29695 | 0.24 | 0.206294 | 0.0206294 | 0.04375 | 0.15375 | 0.44 | 0.68075 |
| fees | GBP | 100/100 | 0.02867 | 0.028 | 0.00786638 | 0.000786638 | 0.016 | 0.024 | 0.034 | 0.04205 |
| fill_rate | fraction | 100/100 | 0.240802 | 0.233333 | 0.066981 | 0.0066981 | 0.133333 | 0.2 | 0.283333 | 0.356052 |
| final_inventory | units | 100/100 | 0.11 | 0 | 2.00452 | 0.200452 | -3 | -1 | 1 | 4.05 |
| gross_realised_pnl | GBP | 100/100 | -0.6476 | -0.35 | 0.871393 | 0.0871393 | -2.523 | -0.8375 | -0.0675 | 0.0705 |
| inventory_movement | GBP | 100/100 | -1.022 | -0.7275 | 1.07947 | 0.107947 | -3.835 | -1.095 | -0.375 | -0.1535 |
| markout_1 | GBP/unit | 100/100 | -0.00676692 | -0.00549679 | 0.00955257 | 0.000955257 | -0.0226736 | -0.011616 | -0.00012931 | 0.00565366 |
| markout_20 | GBP/unit | 100/100 | -0.0266812 | -0.0171645 | 0.0343595 | 0.00343595 | -0.10926 | -0.0353929 | -0.00522059 | 0.00543931 |
| markout_5 | GBP/unit | 100/100 | -0.012913 | -0.00915179 | 0.0159191 | 0.00159191 | -0.0415635 | -0.0191648 | -0.00297115 | 0.00447222 |
| maximum_absolute_inventory | units | 100/100 | 3.98 | 4 | 1.29474 | 0.129474 | 2 | 3 | 5 | 6 |
| maximum_drawdown | GBP | 100/100 | 0.88308 | 0.477 | 1.08346 | 0.108346 | 0.08695 | 0.24775 | 0.945 | 3.37145 |
| net_pnl | GBP | 100/100 | -0.75372 | -0.391 | 1.03586 | 0.103586 | -3.2765 | -0.86075 | -0.12825 | 0.04145 |
| realised_pnl | GBP | 100/100 | -0.67627 | -0.374 | 0.873808 | 0.0873808 | -2.55695 | -0.86975 | -0.09075 | 0.04835 |
| rms_inventory | units | 100/100 | 1.65722 | 1.54766 | 0.642235 | 0.0642235 | 0.886164 | 1.19311 | 1.94409 | 2.78141 |
| sell_fills | execution records | 100/100 | 10.5 | 10 | 3.31053 | 0.331053 | 5 | 8 | 13 | 16 |
| sell_units | units | 100/100 | 14.28 | 14 | 4.09257 | 0.409257 | 8 | 12 | 17 | 21 |
| turnover | GBP | 100/100 | 2867.42 | 2798.64 | 787.283 | 78.7283 | 1599.79 | 2398.72 | 3400.98 | 4207.28 |
| two_sided_quote_time_fraction | fraction | 100/100 | 0.817331 | 0.826572 | 0.0652443 | 0.00652443 | 0.684579 | 0.776264 | 0.861949 | 0.909419 |
| unrealised_pnl | GBP | 100/100 | -0.07745 | 0 | 0.258103 | 0.0258103 | -0.5515 | -0.025 | 0 | 0.02525 |

Mean interval: {'confidence': 0.95, 'high': -0.5481837482599989, 'low': -0.959256251740001, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.75372, 'interval': {'confidence': 0.95, 'high': -0.5674900000000002, 'low': -0.96123275, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 622942150995516286839838586443579278855766739733464996655223518758599638524, 'standard_error': 0.10141329557163276}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -3.2765, 'probability_below': {'-0.25': 0.63, '-0.5': 0.43, '-1.0': 0.21, '0.0': 0.89}, 'tail_count': 5, 'worst': -4.689, 'worst_five_percent_mean': -4.2482}

Exploratory correlations (not causal effects):

- average_absolute_inventory vs net_pnl: {'available': 100, 'correlation': -0.8059369224346972, 'covariance': -0.46819288230661293, 'missing': 0}
- fill_rate vs markout_1: {'available': 100, 'correlation': -0.238302380195169, 'covariance': -0.00015247560666374366, 'missing': 0}
- maximum_absolute_inventory vs maximum_drawdown: {'available': 100, 'correlation': 0.7489236849832732, 'covariance': 1.0505975757575758, 'missing': 0}
- turnover vs fees: {'available': 100, 'correlation': 0.9999911085234493, 'covariance': 6.193011579797981, 'missing': 0}

Worst primary outcomes:

- Run #24: -4.689; simulation seed 192252103020309354053258320894013241524653815353629070803561255375009684798440
- Run #3: -4.476; simulation seed 209553395530555786858897643695940882884174153996724501254507505339832443478374
- Run #85: -4.368; simulation seed 189000482693834741321792731578025201364043489063515531936506982388185155077188

## Paired: strategy.inventory_skew_ticks=1 minus strategy.inventory_skew_ticks=0

Summary: {'available': 100, 'maximum': 0.322, 'mean': -0.5500500000000001, 'mean_ci': {'confidence': 0.95, 'high': -0.4227932109544046, 'low': -0.6773067890455957, 'method': 'Student t mean'}, 'median': -0.3875, 'minimum': -3.131, 'missing': 0, 'p05': -1.7579500000000001, 'p25': -0.7377500000000001, 'p75': -0.15674999999999997, 'p95': 0.07899999999999999, 'requested': 100, 'standard_deviation': 0.6413451358927839, 'standard_error': 0.06413451358927838, 'variance': 0.4113235833333334}
Bootstrap: {'estimate': -0.5500500000000001, 'interval': {'confidence': 0.95, 'high': -0.4363142500000004, 'low': -0.6843747499999999, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete matched session pair', 'resamples': 2000, 'seed': 45901281756470368207433794538467565218837535005929031828658132453095771491995, 'standard_error': 0.06292396142844572}
Positive / negative / tied: 9.000% / 91.000% / 0.000%.
t = -8.57651; two-sided p = 1.37537e-13; paired standardised effect = -0.857651.
Paired two-sided t test: H0 E[D]=0; H1 E[D] differs from zero. Statistical significance is not strategy validity or practical value.

## Paired: strategy.inventory_skew_ticks=1/2 minus strategy.inventory_skew_ticks=0

Summary: {'available': 100, 'maximum': 0.552, 'mean': -0.33692999999999995, 'mean_ci': {'confidence': 0.95, 'high': -0.24577850927899325, 'low': -0.42808149072100665, 'method': 'Student t mean'}, 'median': -0.233, 'minimum': -2.308, 'missing': 0, 'p05': -1.3545500000000001, 'p25': -0.4415, 'p75': -0.10625000000000001, 'p95': 0.23879999999999996, 'requested': 100, 'standard_deviation': 0.45938268316944597, 'standard_error': 0.0459382683169446, 'variance': 0.2110324495959596}
Bootstrap: {'estimate': -0.33692999999999995, 'interval': {'confidence': 0.95, 'high': -0.24995725000000002, 'low': -0.43142074999999996, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete matched session pair', 'resamples': 2000, 'seed': 100085949514462759430091513802822949400507185672871953247223848864433860647586, 'standard_error': 0.045865067141624555}
Positive / negative / tied: 13.000% / 87.000% / 0.000%.
t = -7.33441; two-sided p = 6.20683e-11; paired standardised effect = -0.733441.
Paired two-sided t test: H0 E[D]=0; H1 E[D] differs from zero. Statistical significance is not strategy validity or practical value.

## Paired: strategy.inventory_skew_ticks=1/4 minus strategy.inventory_skew_ticks=0

Summary: {'available': 100, 'maximum': 0.34199999999999997, 'mean': -0.17926000000000003, 'mean_ci': {'confidence': 0.95, 'high': -0.1229174446652049, 'low': -0.23560255533479516, 'method': 'Student t mean'}, 'median': -0.1255, 'minimum': -1.3030000000000002, 'missing': 0, 'p05': -0.7166499999999999, 'p25': -0.2805, 'p75': -0.03025, 'p95': 0.1946999999999999, 'requested': 100, 'standard_deviation': 0.2839536034088824, 'standard_error': 0.028395360340888243, 'variance': 0.08062964888888889}
Bootstrap: {'estimate': -0.17926000000000003, 'interval': {'confidence': 0.95, 'high': -0.12735900000000008, 'low': -0.23873799999999995, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete matched session pair', 'resamples': 2000, 'seed': 51176416841354029786523434888518401348677486190020860355354267741344713923677, 'standard_error': 0.028623313216965873}
Positive / negative / tied: 21.000% / 79.000% / 0.000%.
t = -6.313; two-sided p = 7.78511e-09; paired standardised effect = -0.6313.
Paired two-sided t test: H0 E[D]=0; H1 E[D] differs from zero. Statistical significance is not strategy validity or practical value.

## Paired: strategy.inventory_skew_ticks=2 minus strategy.inventory_skew_ticks=0

Summary: {'available': 100, 'maximum': 0.12000000000000001, 'mean': -0.88843, 'mean_ci': {'confidence': 0.95, 'high': -0.6805314477034615, 'low': -1.0963285522965387, 'method': 'Student t mean'}, 'median': -0.47250000000000003, 'minimum': -4.953, 'missing': 0, 'p05': -3.2033, 'p25': -1.10125, 'p75': -0.25125, 'p95': -0.015950000000000002, 'requested': 100, 'standard_deviation': 1.047761194310531, 'standard_error': 0.1047761194310531, 'variance': 1.0978035203030303}
Bootstrap: {'estimate': -0.88843, 'interval': {'confidence': 0.95, 'high': -0.6992317500000004, 'low': -1.1066955, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete matched session pair', 'resamples': 2000, 'seed': 93017387262674550345039122237199420700616372253587817555313268448604612274619, 'standard_error': 0.10434900488707709}
Positive / negative / tied: 4.000% / 96.000% / 0.000%.
t = -8.47932; two-sided p = 2.23181e-13; paired standardised effect = -0.847932.
Paired two-sided t test: H0 E[D]=0; H1 E[D] differs from zero. Statistical significance is not strategy validity or practical value.

## Interpretation

strategy.inventory_skew_ticks=0: observed mean net_pnl=0.13471; losing/negative outcomes 29.0%. strategy.inventory_skew_ticks=1: observed mean net_pnl=-0.41534; losing/negative outcomes 75.0%. strategy.inventory_skew_ticks=1/2: observed mean net_pnl=-0.20222; losing/negative outcomes 59.0%. strategy.inventory_skew_ticks=1/4: observed mean net_pnl=-0.04455; losing/negative outcomes 40.0%. strategy.inventory_skew_ticks=2: observed mean net_pnl=-0.75372; losing/negative outcomes 89.0%. Compare the full distributions and paired uncertainty with the original hypothesis. These conditional model outcomes do not establish real-world alpha, safety or an optimal parameter. Interpretation remains reviewable.

## Limitations

- Synthetic performance is not evidence of real-world alpha.
- Independent sessions conditional on one model; uncertainty excludes model error.
- Exploratory metrics/intervals are not corrected for multiple testing.
- Missing metrics are reported with coverage, not replaced by zero.

Quantiles use linear interpolation; SD uses n−1. Markout distributions use per-session available-unit means, with session and unit coverage retained. A confidence interval concerns the model's mean, not the range of future outcomes.
