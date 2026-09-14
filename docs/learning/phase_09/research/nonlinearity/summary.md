# QuantLab synthetic research experiment

How does horizon change full versus delta-normal VaR on an executed hedged call?

**Prediction registered before execution:** Full-minus-delta VaR can change as option decay and curvature accumulate; delta neutrality alone will not remove loss.

Status: complete. Pool: evaluation. Sessions per variant: 128. Root seed: 9900902.

Synthetic performance is not evidence of real-world alpha.

## one_day

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| delta_var | GBP | 128/128 | 0.556862 | 0.556862 | 1.11459e-16 | 9.85164e-18 | 0.556862 | 0.556862 | 0.556862 | 0.556862 |
| es | GBP | 128/128 | 19.1844 | 19.1846 | 0.00479061 | 0.000423434 | 19.1769 | 19.1809 | 19.188 | 19.192 |
| es_minus_var | GBP | 128/128 | 0.0672034 | 0.0670539 | 0.0082356 | 0.000727931 | 0.0528695 | 0.0628805 | 0.072534 | 0.0793733 |
| full_minus_delta_var | GBP | 128/128 | 18.5604 | 18.5598 | 0.0122646 | 0.00108405 | 18.5421 | 18.5522 | 18.5678 | 18.5823 |
| mean_loss | GBP | 128/128 | -5.92105 | -5.89804 | 0.56546 | 0.0499801 | -6.86441 | -6.31642 | -5.5254 | -4.95164 |
| var | GBP | 128/128 | 19.1172 | 19.1167 | 0.0122646 | 0.00108405 | 19.099 | 19.1091 | 19.1247 | 19.1392 |

Mean interval: {'confidence': 0.95, 'high': 18.562527010409557, 'low': 18.558236743440364, 'method': 'Student t mean'}
Bootstrap: {'estimate': 18.56038187692496, 'interval': {'confidence': 0.95, 'high': 18.56246090339284, 'low': 18.558280264689056, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 500, 'seed': 60980916320477793869172914478271328795058121808763117840635073486256630985036, 'standard_error': 0.0010839852571260494}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': 18.542119601239133, 'probability_below': {'-0.25': 0.0, '-0.5': 0.0, '-1.0': 0.0, '0.0': 0.0}, 'tail_count': 7, 'worst': 18.526242995485457, 'worst_five_percent_mean': 18.537053024078258}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #63: 18.5262; simulation seed 214217974619330641788243455042162180938379809234995740340036246128241363172425
- Run #52: 18.5322; simulation seed 218030514312543032847207923440209209839908603161777618309045818348961909455623
- Run #19: 18.5374; simulation seed 179784918078539164355961908620903526028373136925542750969812732678260730428939

## five_days

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| delta_var | GBP | 128/128 | 1.24518 | 1.24518 | 2.22917e-16 | 1.97033e-17 | 1.24518 | 1.24518 | 1.24518 | 1.24518 |
| es | GBP | 128/128 | 99.441 | 99.4437 | 0.0233476 | 0.00206366 | 99.3995 | 99.4271 | 99.4575 | 99.4757 |
| es_minus_var | GBP | 128/128 | 0.366027 | 0.359357 | 0.0433983 | 0.0038359 | 0.300587 | 0.333027 | 0.396014 | 0.437514 |
| full_minus_delta_var | GBP | 128/128 | 97.8298 | 97.8334 | 0.0626571 | 0.00553816 | 97.7264 | 97.7945 | 97.879 | 97.9176 |
| mean_loss | GBP | 128/128 | -29.577 | -29.5536 | 2.27339 | 0.200941 | -32.9941 | -31.1163 | -28.2727 | -25.9316 |
| var | GBP | 128/128 | 99.075 | 99.0786 | 0.0626571 | 0.00553816 | 98.9716 | 99.0397 | 99.1242 | 99.1628 |

Mean interval: {'confidence': 0.95, 'high': 97.84079012694973, 'low': 97.81887208471018, 'method': 'Student t mean'}
Bootstrap: {'estimate': 97.82983110582995, 'interval': {'confidence': 0.95, 'high': 97.84035230645416, 'low': 97.81881479840163, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 500, 'seed': 18750309322176543332942550307186802636364965818918445212707062731828875093579, 'standard_error': 0.005790413994972996}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': 97.72641553012225, 'probability_below': {'-0.25': 0.0, '-0.5': 0.0, '-1.0': 0.0, '0.0': 0.0}, 'tail_count': 7, 'worst': 97.63696371834733, 'worst_five_percent_mean': 97.69060172258976}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #111: 97.637; simulation seed 224077424134183423485798501623740716455041912872344677195779873200356827844771
- Run #116: 97.6625; simulation seed 207062540852996287057644670643241912677982192906640434912588068304835689801473
- Run #113: 97.6678; simulation seed 871865836683467407560943195541255379967564208260718342442158021794087170863

## Interpretation

five_days: observed mean full_minus_delta_var=97.8298; losing/negative outcomes 0.0%. one_day: observed mean full_minus_delta_var=18.5604; losing/negative outcomes 0.0%. Compare the full distributions and paired uncertainty with the original hypothesis. These conditional model outcomes do not establish real-world alpha, safety or an optimal parameter. Interpretation remains reviewable.

## Limitations

- Synthetic executed starting portfolios; fixed assumptions, not forecasts.
- Normal/t distributions share Gaussian shocks; transformed returns differ.
- Sample-size variants use nested path prefixes; uncertainty excludes model error.
- Different horizons are explicitly unpaired; no false identical-environment claim.

Quantiles use linear interpolation; SD uses n−1. Markout distributions use per-session available-unit means, with session and unit coverage retained. A confidence interval concerns the model's mean, not the range of future outcomes.
