# QuantLab synthetic research experiment

How does higher assumed correlation affect this executed two-stock portfolio?

**Prediction registered before execution:** With both stocks long and unchanged volatility, higher correlation should increase loss VaR on average.

Status: complete. Pool: evaluation. Sessions per variant: 128. Root seed: 9900900.

Synthetic performance is not evidence of real-world alpha.

## rho_0

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| delta_var | GBP | 128/128 | 118.612 | 118.612 | 4.28001e-14 | 3.78303e-15 | 118.612 | 118.612 | 118.612 | 118.612 |
| es | GBP | 128/128 | 148.542 | 148.609 | 2.1404 | 0.189186 | 144.981 | 147.244 | 149.808 | 151.82 |
| es_minus_var | GBP | 128/128 | 29.9727 | 30.0435 | 1.57127 | 0.138882 | 27.6046 | 28.9624 | 30.8506 | 32.6563 |
| full_minus_delta_var | GBP | 128/128 | -0.042605 | -0.0577224 | 1.98635 | 0.175571 | -2.94656 | -1.59902 | 1.17862 | 3.42937 |
| mean_loss | GBP | 128/128 | 0.0554784 | 0.0558208 | 1.03428 | 0.0914183 | -1.64604 | -0.683307 | 0.701225 | 1.72981 |
| var | GBP | 128/128 | 118.569 | 118.554 | 1.98635 | 0.175571 | 115.666 | 117.013 | 119.791 | 122.041 |

Mean interval: {'confidence': 0.95, 'high': 118.91689922495598, 'low': 118.22205441688996, 'method': 'Student t mean'}
Bootstrap: {'estimate': 118.56947682092297, 'interval': {'confidence': 0.95, 'high': 118.94461669305268, 'low': 118.2479535552782, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 500, 'seed': 106346102150512700485093196420630767963293199398934612820754829569696842854009, 'standard_error': 0.1786587125404414}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': 115.66551920518347, 'probability_below': {'-0.25': 0.0, '-0.5': 0.0, '-1.0': 0.0, '0.0': 0.0}, 'tail_count': 7, 'worst': 112.59737518117319, 'worst_five_percent_mean': 114.73373671487722}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #101: 112.597; simulation seed 225491476450838035096752218309022680536434540528883118977904714732218572235879
- Run #52: 114.563; simulation seed 213473502959517365265129865362966188904767668303777132268547201205373019901707
- Run #109: 114.705; simulation seed 155833853547206476840984820916620924103609789706914682720302099650615833319959

## rho_09

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| delta_var | GBP | 128/128 | 160.489 | 160.489 | 0 | 0 | 160.489 | 160.489 | 160.489 | 160.489 |
| es | GBP | 128/128 | 200.854 | 200.849 | 3.07704 | 0.271975 | 195.231 | 198.888 | 202.607 | 206.268 |
| es_minus_var | GBP | 128/128 | 40.5401 | 40.4954 | 2.31674 | 0.204773 | 36.9251 | 39.1368 | 41.9446 | 44.4853 |
| full_minus_delta_var | GBP | 128/128 | -0.174961 | -0.143328 | 2.92295 | 0.258355 | -4.76322 | -2.08069 | 1.97596 | 4.00193 |
| mean_loss | GBP | 128/128 | 0.0395138 | 0.122724 | 1.45548 | 0.128648 | -2.13093 | -1.03865 | 0.920453 | 2.47194 |
| var | GBP | 128/128 | 160.314 | 160.346 | 2.92295 | 0.258355 | 155.726 | 158.408 | 162.465 | 164.491 |

Mean interval: {'confidence': 0.95, 'high': 160.8254472425262, 'low': 159.8029707738304, 'method': 'Student t mean'}
Bootstrap: {'estimate': 160.3142090081783, 'interval': {'confidence': 0.95, 'high': 160.82062427366156, 'low': 159.79390611455196, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 500, 'seed': 16516570559932131444857183206255813274358543086622103626463898284827837943119, 'standard_error': 0.26004363491785154}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': 155.7259488467828, 'probability_below': {'-0.25': 0.0, '-0.5': 0.0, '-1.0': 0.0, '0.0': 0.0}, 'tail_count': 7, 'worst': 152.0462515676807, 'worst_five_percent_mean': 154.13486141958612}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #72: 152.046; simulation seed 194936855411964074793134247901599490273771438364261155146965847366038147271135
- Run #101: 152.841; simulation seed 225491476450838035096752218309022680536434540528883118977904714732218572235879
- Run #109: 154.115; simulation seed 155833853547206476840984820916620924103609789706914682720302099650615833319959

## Paired: rho_09 minus rho_0

Summary: {'available': 128, 'maximum': 50.76910335254982, 'mean': 41.7447321872553, 'mean_ci': {'confidence': 0.95, 'high': 42.19205373542876, 'low': 41.297410639081846, 'method': 'Student t mean'}, 'median': 41.87120894211999, 'minimum': 35.4270590603556, 'missing': 0, 'p05': 37.97128923999884, 'p25': 39.89671615690582, 'p75': 43.59559035928079, 'p95': 45.84408936947902, 'requested': 128, 'standard_deviation': 2.5575175060665662, 'standard_error': 0.22605474644287202, 'variance': 6.540895793836949}
Bootstrap: {'estimate': 41.7447321872553, 'interval': {'confidence': 0.95, 'high': 42.21739132200655, 'low': 41.293696070386154, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete matched session pair', 'resamples': 500, 'seed': 67700792436593666225198819442251964074692829467887395346752396177171152526363, 'standard_error': 0.23623126744724288}
Positive / negative / tied: 100.000% / 0.000% / 0.000%.
t = 184.666; two-sided p = 3.21899e-156; paired standardised effect = 16.3224.
Paired two-sided t test: H0 E[D]=0; H1 E[D] differs from zero. Statistical significance is not strategy validity or practical value.

## Interpretation

rho_0: observed mean var=118.569; losing/negative outcomes 0.0%. rho_09: observed mean var=160.314; losing/negative outcomes 0.0%. Compare the full distributions and paired uncertainty with the original hypothesis. These conditional model outcomes do not establish real-world alpha, safety or an optimal parameter. Interpretation remains reviewable.

## Limitations

- Synthetic executed starting portfolios; fixed assumptions, not forecasts.
- Normal/t distributions share Gaussian shocks; transformed returns differ.
- Sample-size variants use nested path prefixes; uncertainty excludes model error.
- Different horizons are explicitly unpaired; no false identical-environment claim.

Quantiles use linear interpolation; SD uses n−1. Markout distributions use per-session available-unit means, with session and unit coverage retained. A confidence interval concerns the model's mean, not the range of future outcomes.
