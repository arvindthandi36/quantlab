# QuantLab synthetic research experiment

Does the development winner retain its measured advantage on untouched sessions?

**Prediction registered before execution:** The selected development winner will tend to overstate its untouched evaluation mean; all variants have known true mean zero. This is a statistical control, not trade P&L.

Status: complete. Pool: evaluation. Sessions per variant: 400. Root seed: 113222207025201800389088784922897608555813991227298903875767394167900211115691.

Synthetic performance is not evidence of real-world alpha.

## variant-49

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 400/400 | 0.0308025 | -0.0169206 | 0.970999 | 0.0485499 | -1.53593 | -0.658072 | 0.629259 | 1.73535 |

Mean interval: {'confidence': 0.95, 'high': 0.12624810531851122, 'low': -0.06464319040180191, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.030802457458354658, 'interval': {'confidence': 0.95, 'high': 0.1299147853519378, 'low': -0.07023613224615005, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 843259262093909778387094244554843994815109961193377943842284927721875832189, 'standard_error': 0.049171886667480694}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.5359337851266242, 'probability_below': {'-0.25': 0.395, '-0.5': 0.3025, '-1.0': 0.135, '0.0': 0.5125}, 'tail_count': 20, 'worst': -2.6614951247562577, 'worst_five_percent_mean': -1.9001577048353357}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #359: -2.6615; simulation seed 196041326228531741033538064096268509460653708509302453622710568946319180832307
- Run #36: -2.43875; simulation seed 167581798649470180704402953808071333323210882384825611522511921981363999529759
- Run #220: -2.11471; simulation seed 23133749355746596811168654443901450335368840545698042918895166729237982155093

## Interpretation

variant-49: observed mean net_pnl=0.0308025; losing/negative outcomes 51.2%. Compare the full distributions and paired uncertainty with the original hypothesis. These conditional model outcomes do not establish real-world alpha, safety or an optimal parameter. Interpretation remains reviewable.

## Limitations

- Synthetic performance is not evidence of real-world alpha.
- Independent sessions conditional on one model; uncertainty excludes model error.
- Exploratory metrics/intervals are not corrected for multiple testing.
- Missing metrics are reported with coverage, not replaced by zero.

Quantiles use linear interpolation; SD uses n−1. Markout distributions use per-session available-unit means, with session and unit coverage retained. A confidence interval concerns the model's mean, not the range of future outcomes.
