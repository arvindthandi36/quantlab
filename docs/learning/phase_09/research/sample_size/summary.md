# QuantLab synthetic research experiment

How does path count affect the variability of estimated VaR?

**Prediction registered before execution:** Across independent seed addresses, larger nested samples should reduce estimation variability, not model error.

Status: complete. Pool: evaluation. Sessions per variant: 128. Root seed: 9900903.

Synthetic performance is not evidence of real-world alpha.

## small

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| delta_var | GBP | 128/128 | 131.588 | 131.588 | 2.85334e-14 | 2.52202e-15 | 131.588 | 131.588 | 131.588 | 131.588 |
| es | GBP | 128/128 | 162.934 | 162.795 | 13.2852 | 1.17426 | 141.424 | 153.761 | 172.784 | 185.538 |
| es_minus_var | GBP | 128/128 | 32.3925 | 31.7253 | 8.53861 | 0.754713 | 19.0444 | 26.8266 | 38.121 | 47.9074 |
| full_minus_delta_var | GBP | 128/128 | -1.04643 | -1.51593 | 11.0065 | 0.972849 | -21.9467 | -8.04005 | 6.65678 | 17.4102 |
| mean_loss | GBP | 128/128 | 0.0756795 | 0.0175175 | 5.03884 | 0.445375 | -7.49109 | -3.46922 | 3.42932 | 8.27754 |
| var | GBP | 128/128 | 130.542 | 130.072 | 11.0065 | 0.972849 | 109.642 | 123.548 | 138.245 | 148.999 |

Mean interval: {'confidence': 0.95, 'high': 132.46695739104126, 'low': 128.61677186439078, 'method': 'Student t mean'}
Bootstrap: {'estimate': 130.54186462771602, 'interval': {'confidence': 0.95, 'high': 132.3695259816703, 'low': 128.60806208274383, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 500, 'seed': 37886683388939990236068554020865539706096978330586345808077115496470730936061, 'standard_error': 0.950464807948049}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': 109.64157995226022, 'probability_below': {'-0.25': 0.0, '-0.5': 0.0, '-1.0': 0.0, '0.0': 0.0}, 'tail_count': 7, 'worst': 105.77292128049199, 'worst_five_percent_mean': 108.54043925048843}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #65: 105.773; simulation seed 228778534871278908517834116315507541379672413520542795692910172000146985412441
- Run #95: 108.498; simulation seed 59350606691205533530350867379521856083562957572616605312969324043787569888281
- Run #36: 108.621; simulation seed 176697983625087207925189109480735983959186478579781821259494816993316146044645

## large

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| delta_var | GBP | 128/128 | 131.588 | 131.588 | 2.85334e-14 | 2.52202e-15 | 131.588 | 131.588 | 131.588 | 131.588 |
| es | GBP | 128/128 | 165.028 | 164.833 | 2.86888 | 0.253575 | 160.398 | 163.054 | 167.041 | 169.921 |
| es_minus_var | GBP | 128/128 | 33.5088 | 33.4392 | 1.95711 | 0.172985 | 30.1738 | 32.4281 | 34.9303 | 36.2291 |
| full_minus_delta_var | GBP | 128/128 | -0.0687097 | -0.0037431 | 2.38977 | 0.211228 | -3.78004 | -1.89086 | 1.56735 | 3.78905 |
| mean_loss | GBP | 128/128 | 0.163168 | 0.0995853 | 1.05785 | 0.0935018 | -1.4093 | -0.531732 | 0.885901 | 1.99192 |
| var | GBP | 128/128 | 131.52 | 131.585 | 2.38977 | 0.211228 | 127.808 | 129.697 | 133.156 | 135.377 |

Mean interval: {'confidence': 0.95, 'high': 131.937562993797, 'low': 131.1015980021567, 'method': 'Student t mean'}
Bootstrap: {'estimate': 131.51958049797685, 'interval': {'confidence': 0.95, 'high': 131.89777296756677, 'low': 131.12619838684844, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 500, 'seed': 33256509970776264160607076523527055435184888542499618901233286215227652800279, 'standard_error': 0.20204205801521957}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': 127.80824645287706, 'probability_below': {'-0.25': 0.0, '-0.5': 0.0, '-1.0': 0.0, '0.0': 0.0}, 'tail_count': 7, 'worst': 126.25318419696052, 'worst_five_percent_mean': 127.20695818821316}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #127: 126.253; simulation seed 102148795095761326865589870083640394574623126206364668658479752358916882487775
- Run #50: 126.578; simulation seed 96877478182453646205419927166789611153751013186236179449857768614001118663719
- Run #72: 126.931; simulation seed 11043681180669899752520912054882450821485494349956253646685390867696391402067

## Paired: large minus small

Summary: {'available': 128, 'maximum': 26.45107898690327, 'mean': 0.9777158702608315, 'mean_ci': {'confidence': 0.95, 'high': 2.9322717419985986, 'low': -0.9768400014769358, 'method': 'Student t mean'}, 'median': 1.8338976876519695, 'minimum': -26.454265244489335, 'missing': 0, 'p05': -16.983076261400683, 'p25': -7.659120452658698, 'p75': 8.677764708496092, 'p95': 20.472553381681344, 'requested': 128, 'standard_deviation': 11.174983362563555, 'standard_error': 0.987738314414442, 'variance': 124.88025315357227}
Bootstrap: {'estimate': 0.9777158702608315, 'interval': {'confidence': 0.95, 'high': 3.014577937367956, 'low': -0.9936768905117964, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete matched session pair', 'resamples': 500, 'seed': 21406321159792553761958432362118183168657008276556462834693161805058298370053, 'standard_error': 0.9920265451821771}
Positive / negative / tied: 55.469% / 44.531% / 0.000%.
t = 0.989853; two-sided p = 0.324128; paired standardised effect = 0.0874915.
Paired two-sided t test: H0 E[D]=0; H1 E[D] differs from zero. Statistical significance is not strategy validity or practical value.

## Interpretation

large: observed mean var=131.52; losing/negative outcomes 0.0%. small: observed mean var=130.542; losing/negative outcomes 0.0%. Compare the full distributions and paired uncertainty with the original hypothesis. These conditional model outcomes do not establish real-world alpha, safety or an optimal parameter. Interpretation remains reviewable.

## Limitations

- Synthetic executed starting portfolios; fixed assumptions, not forecasts.
- Normal/t distributions share Gaussian shocks; transformed returns differ.
- Sample-size variants use nested path prefixes; uncertainty excludes model error.
- Different horizons are explicitly unpaired; no false identical-environment claim.

Quantiles use linear interpolation; SD uses n−1. Markout distributions use per-session available-unit means, with session and unit coverage retained. A confidence interval concerns the model's mean, not the range of future outcomes.
