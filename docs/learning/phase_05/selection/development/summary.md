# QuantLab synthetic research experiment

Can selecting the best of equal-skill variants create apparent skill?

**Prediction registered before execution:** The selected development winner will tend to overstate its untouched evaluation mean; all variants have known true mean zero. This is a statistical control, not trade P&L.

Status: complete. Pool: development. Sessions per variant: 40. Root seed: 113222207025201800389088784922897608555813991227298903875767394167900211115691.

Synthetic performance is not evidence of real-world alpha.

## variant-00

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.191989 | -0.00830131 | 0.930823 | 0.147176 | -1.75412 | -0.719737 | 0.24104 | 0.794389 |

Mean interval: {'confidence': 0.95, 'high': 0.10570227210886218, 'low': -0.48968086994691395, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.19198929891902589, 'interval': {'confidence': 0.95, 'high': 0.0968112882911023, 'low': -0.485002280865632, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 47360044999514030693699744865667071304313865702948055940581915008854716055250, 'standard_error': 0.14690035162602794}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.7541226599318456, 'probability_below': {'-0.25': 0.375, '-0.5': 0.275, '-1.0': 0.175, '0.0': 0.525}, 'tail_count': 2, 'worst': -2.130343368995711, 'worst_five_percent_mean': -1.9845990316669446}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #7: -2.13034; simulation seed 42810676843598314886338763320918203137855958466555930066835539095178234705324
- Run #31: -1.83885; simulation seed 213111858892867346191887386419863323302432529151035227571676170859234418431210
- Run #18: -1.74966; simulation seed 178550663874872547796473692807573760876420110184197945286668025882135345997650

## variant-01

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.169367 | -0.0106598 | 0.880025 | 0.139144 | -0.994411 | -0.471271 | 0.597097 | 1.61244 |

Mean interval: {'confidence': 0.95, 'high': 0.45081254987779795, 'low': -0.11207881220803037, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.1693668688348838, 'interval': {'confidence': 0.95, 'high': 0.4222631362757284, 'low': -0.08850646200221446, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 48570103144245811067561123851758355940990006041227983464949336455420291794889, 'standard_error': 0.13352081955111345}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -0.9944111790781025, 'probability_below': {'-0.25': 0.3, '-0.5': 0.25, '-1.0': 0.05, '0.0': 0.5}, 'tail_count': 2, 'worst': -1.4943580751123005, 'worst_five_percent_mean': -1.3041366225653759}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #31: -1.49436; simulation seed 213111858892867346191887386419863323302432529151035227571676170859234418431210
- Run #23: -1.11392; simulation seed 139073535557910357261445892962952209406170864229888947255931707236835204994106
- Run #8: -0.988121; simulation seed 204361413067686439161865448608322207517466203634819304169414683236897188257826

## variant-02

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.109021 | -0.0972635 | 1.02159 | 0.161528 | -1.44467 | -0.721498 | 0.426754 | 1.26591 |

Mean interval: {'confidence': 0.95, 'high': 0.2176988928126199, 'low': -0.4357417721650666, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.10902143967622335, 'interval': {'confidence': 0.95, 'high': 0.1966068486633333, 'low': -0.4180360732229628, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 73709851773615128505101011791064783340719847759725095219467943937589274960798, 'standard_error': 0.15661810438085866}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.4446725117037738, 'probability_below': {'-0.25': 0.475, '-0.5': 0.4, '-1.0': 0.2, '0.0': 0.525}, 'tail_count': 2, 'worst': -2.6858091628007625, 'worst_five_percent_mean': -2.2106976230167708}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #31: -2.68581; simulation seed 213111858892867346191887386419863323302432529151035227571676170859234418431210
- Run #22: -1.73559; simulation seed 109006795979948863018140189240777738983241616203327246037960535496267672217726
- Run #13: -1.42936; simulation seed 73601954897173572534615624734910873188415705380033639422684526662524016138332

## variant-03

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.343342 | -0.396431 | 0.951223 | 0.150402 | -1.51281 | -1.16032 | 0.320854 | 1.20305 |

Mean interval: {'confidence': 0.95, 'high': -0.03912611615085032, 'low': -0.6475576296113523, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.3433418728811013, 'interval': {'confidence': 0.95, 'high': -0.04091160897216399, 'low': -0.6246890528532318, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 59354839890235212984878395609677565632869698800294727042066850441624567312071, 'standard_error': 0.15127808964164144}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.5128103749231472, 'probability_below': {'-0.25': 0.575, '-0.5': 0.475, '-1.0': 0.35, '0.0': 0.675}, 'tail_count': 2, 'worst': -2.174742500730324, 'worst_five_percent_mean': -1.9075845085065297}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #3: -2.17474; simulation seed 20017752270695680152233888760251353643806194965790066604834736282325242445588
- Run #14: -1.64043; simulation seed 75701110788388667600665545747971688395814180086946499837669146343925562470824
- Run #15: -1.50609; simulation seed 108558290286211770509424072769078288340019663611797643275114130610000873221760

## variant-04

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.13792 | -0.188753 | 0.960265 | 0.151831 | -1.51789 | -0.694495 | 0.555867 | 1.27914 |

Mean interval: {'confidence': 0.95, 'high': 0.16918770613990222, 'low': -0.4450273591067614, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.13791982648342957, 'interval': {'confidence': 0.95, 'high': 0.1427463218915659, 'low': -0.43699374133234986, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 39834822589550445323980944756601244703017277282189208325292059003037488732849, 'standard_error': 0.1492979287793081}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.5178872289680225, 'probability_below': {'-0.25': 0.425, '-0.5': 0.375, '-1.0': 0.175, '0.0': 0.6}, 'tail_count': 2, 'worst': -2.4953448693980365, 'worst_five_percent_mean': -2.0344061732781356}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #22: -2.49534; simulation seed 109006795979948863018140189240777738983241616203327246037960535496267672217726
- Run #19: -1.57347; simulation seed 99003629409724868636513946294053693718806502664384300739864858705948429835720
- Run #12: -1.51496; simulation seed 1484383136199096780328585456327142417348231669794117112239693326182654934430

## variant-05

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.0406411 | -0.0931389 | 1.03302 | 0.163335 | -1.41271 | -0.774944 | 0.628209 | 1.48828 |

Mean interval: {'confidence': 0.95, 'high': 0.28973554698067927, 'low': -0.3710177294500069, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.04064109123466379, 'interval': {'confidence': 0.95, 'high': 0.272418471220866, 'low': -0.37525164636422, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 84329421308923773892475441813114634774744039931139851090644671282887815219355, 'standard_error': 0.16364182775639008}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.412712387020966, 'probability_below': {'-0.25': 0.425, '-0.5': 0.375, '-1.0': 0.15, '0.0': 0.525}, 'tail_count': 2, 'worst': -2.695718763270434, 'worst_five_percent_mean': -2.2770001435515788}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #14: -2.69572; simulation seed 75701110788388667600665545747971688395814180086946499837669146343925562470824
- Run #0: -1.85828; simulation seed 92032980692353128645868760521166338187439201860391185903062731514006809240266
- Run #26: -1.38926; simulation seed 95520444881240503472865108893167928833856663538983263927089402611660252121048

## variant-06

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.15449 | -0.0220618 | 0.957881 | 0.151454 | -1.06963 | -0.404221 | 0.783065 | 1.6719 |

Mean interval: {'confidence': 0.95, 'high': 0.460835384900871, 'low': -0.15185511557257608, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.15449013466414746, 'interval': {'confidence': 0.95, 'high': 0.44971020706609105, 'low': -0.14518706390708297, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 331524606383076124718412061513415348846891558336937564067735642322523714444, 'standard_error': 0.14951263204413148}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.0696268654710475, 'probability_below': {'-0.25': 0.275, '-0.5': 0.225, '-1.0': 0.075, '0.0': 0.5}, 'tail_count': 2, 'worst': -2.1558503186463773, 'worst_five_percent_mean': -1.9150894511988168}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #34: -2.15585; simulation seed 198300089775388583939360880316385849716397225375629180861738053159499708594058
- Run #28: -1.67433; simulation seed 18595632659765746113308128204685501682783722886651005644751658978085567577786
- Run #30: -1.0378; simulation seed 75189268677950391107092024914092833256509564730917004615110696444503482148566

## variant-07

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.219452 | -0.405827 | 1.14813 | 0.181536 | -1.60783 | -0.851137 | 0.218175 | 1.41833 |

Mean interval: {'confidence': 0.95, 'high': 0.14773878205208107, 'low': -0.5866426838086158, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.21945195087826735, 'interval': {'confidence': 0.95, 'high': 0.1584232980347491, 'low': -0.546197147634132, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 35079674156946810680234786381473323672712991995356747679489070433189065417156, 'standard_error': 0.17818648281535487}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.6078278724350399, 'probability_below': {'-0.25': 0.55, '-0.5': 0.45, '-1.0': 0.225, '0.0': 0.65}, 'tail_count': 2, 'worst': -2.255154578901192, 'worst_five_percent_mean': -2.0397048278857386}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #28: -2.25515; simulation seed 18595632659765746113308128204685501682783722886651005644751658978085567577786
- Run #7: -1.82426; simulation seed 42810676843598314886338763320918203137855958466555930066835539095178234705324
- Run #33: -1.59644; simulation seed 209728915717659796388982345698829672177467233564060939135774466664656725017160

## variant-08

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.0519149 | 0.00733306 | 1.07969 | 0.170714 | -1.61148 | -0.761763 | 0.816903 | 1.83612 |

Mean interval: {'confidence': 0.95, 'high': 0.3972165402186717, 'low': -0.2933867661489239, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.05191488703487392, 'interval': {'confidence': 0.95, 'high': 0.3882950618585608, 'low': -0.27703500588049645, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 39479375521952736098850192103715749515306511716149288459356474550327224186318, 'standard_error': 0.17099807343211726}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.6114795177184478, 'probability_below': {'-0.25': 0.375, '-0.5': 0.275, '-1.0': 0.2, '0.0': 0.5}, 'tail_count': 2, 'worst': -1.7441240875316169, 'worst_five_percent_mean': -1.6886161441355334}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #13: -1.74412; simulation seed 73601954897173572534615624734910873188415705380033639422684526662524016138332
- Run #31: -1.63311; simulation seed 213111858892867346191887386419863323302432529151035227571676170859234418431210
- Run #25: -1.61034; simulation seed 191463871824032581839690000654146240923037665899998486620379150717548373926490

## variant-09

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.195733 | 0.19162 | 1.09516 | 0.17316 | -1.22378 | -0.764204 | 0.869063 | 2.11649 |

Mean interval: {'confidence': 0.95, 'high': 0.5459826626368749, 'low': -0.15451585692190817, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.19573340285748336, 'interval': {'confidence': 0.95, 'high': 0.539024049983988, 'low': -0.11719626380134968, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 12405358693996408762024045579348995304685139263989418359387190607963079764758, 'standard_error': 0.16831296367448612}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.2237800424647804, 'probability_below': {'-0.25': 0.325, '-0.5': 0.3, '-1.0': 0.2, '0.0': 0.45}, 'tail_count': 2, 'worst': -1.9804629671332747, 'worst_five_percent_mean': -1.6424874716642286}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #23: -1.98046; simulation seed 139073535557910357261445892962952209406170864229888947255931707236835204994106
- Run #26: -1.30451; simulation seed 95520444881240503472865108893167928833856663538983263927089402611660252121048
- Run #6: -1.21953; simulation seed 61220899501351337825269833788851712250170152754735481862445654282643994058602

## variant-10

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.00606909 | -0.13028 | 1.10628 | 0.174919 | -1.69654 | -0.79248 | 0.577489 | 2.02511 |

Mean interval: {'confidence': 0.95, 'high': 0.34773717957895517, 'low': -0.3598753665006909, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.006069093460867886, 'interval': {'confidence': 0.95, 'high': 0.33720744968839933, 'low': -0.3384827360952414, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 112351232090835134389396128881648510554570562416429252823458470885024169409675, 'standard_error': 0.1745367352097478}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.6965398235080158, 'probability_below': {'-0.25': 0.45, '-0.5': 0.375, '-1.0': 0.125, '0.0': 0.55}, 'tail_count': 2, 'worst': -2.0749238509403303, 'worst_five_percent_mean': -2.065415996145186}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #18: -2.07492; simulation seed 178550663874872547796473692807573760876420110184197945286668025882135345997650
- Run #35: -2.05591; simulation seed 16752202956147647847956636392610453463630813977030108188685636334056991806130
- Run #34: -1.67763; simulation seed 198300089775388583939360880316385849716397225375629180861738053159499708594058

## variant-11

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.0478329 | 0.19992 | 1.01499 | 0.160484 | -1.56127 | -0.600975 | 0.808293 | 1.64297 |

Mean interval: {'confidence': 0.95, 'high': 0.37244346038438486, 'low': -0.2767776196394139, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.047832920372485495, 'interval': {'confidence': 0.95, 'high': 0.3432855472437517, 'low': -0.2645535451442576, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 113145197654581955840402503008707690883236057231564421260924694638592922685209, 'standard_error': 0.15862455332385672}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.561270480104071, 'probability_below': {'-0.25': 0.35, '-0.5': 0.325, '-1.0': 0.2, '0.0': 0.475}, 'tail_count': 2, 'worst': -2.459838992282301, 'worst_five_percent_mean': -2.093528951122262}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #23: -2.45984; simulation seed 139073535557910357261445892962952209406170864229888947255931707236835204994106
- Run #1: -1.72722; simulation seed 48712727525638387086227277731330558232683157834994424498578994155713837664794
- Run #31: -1.55254; simulation seed 213111858892867346191887386419863323302432529151035227571676170859234418431210

## variant-12

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.185004 | 0.0681946 | 0.929017 | 0.14689 | -1.53631 | -0.299293 | 0.716106 | 1.78026 |

Mean interval: {'confidence': 0.95, 'high': 0.48211833950647554, 'low': -0.11210978714497422, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.18500427618075066, 'interval': {'confidence': 0.95, 'high': 0.4541817894553337, 'low': -0.09914941186867612, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 2752764274523407466166164231337670846943768677601476621893273489427634678894, 'standard_error': 0.14396701393508737}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.536305037076753, 'probability_below': {'-0.25': 0.275, '-0.5': 0.175, '-1.0': 0.075, '0.0': 0.45}, 'tail_count': 2, 'worst': -2.1241294939142614, 'worst_five_percent_mean': -1.8706589231585289}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #11: -2.12413; simulation seed 17641730239132819337919723489863790959992625965063867607216452210026545554218
- Run #31: -1.61719; simulation seed 213111858892867346191887386419863323302432529151035227571676170859234418431210
- Run #18: -1.53205; simulation seed 178550663874872547796473692807573760876420110184197945286668025882135345997650

## variant-13

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.0756885 | -0.160268 | 1.0427 | 0.164865 | -1.62073 | -0.547786 | 0.857612 | 1.62264 |

Mean interval: {'confidence': 0.95, 'high': 0.4091595229115686, 'low': -0.257782585754005, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.0756884685787818, 'interval': {'confidence': 0.95, 'high': 0.4009670802859765, 'low': -0.24148206369118705, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 85509359485946766181732425798280535979361203433312315067462195994723304359788, 'standard_error': 0.16297455570148214}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.6207256860055446, 'probability_below': {'-0.25': 0.425, '-0.5': 0.275, '-1.0': 0.075, '0.0': 0.575}, 'tail_count': 2, 'worst': -2.627630765839422, 'worst_five_percent_mean': -2.1490660065889275}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #21: -2.62763; simulation seed 210418427453984090683183467486756509570132888221518903018895496491673128929918
- Run #31: -1.6705; simulation seed 213111858892867346191887386419863323302432529151035227571676170859234418431210
- Run #18: -1.61811; simulation seed 178550663874872547796473692807573760876420110184197945286668025882135345997650

## variant-14

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.209426 | 0.336535 | 1.14179 | 0.180533 | -1.28065 | -0.367229 | 0.847025 | 1.87597 |

Mean interval: {'confidence': 0.95, 'high': 0.5745885022212135, 'low': -0.15573562030662003, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.20942644095729673, 'interval': {'confidence': 0.95, 'high': 0.5558871251062428, 'low': -0.13788030625608566, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 98187944968580717423127267179039606965796099483447831021769698987176507758096, 'standard_error': 0.17631843030251843}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.280652805268638, 'probability_below': {'-0.25': 0.275, '-0.5': 0.225, '-1.0': 0.125, '0.0': 0.425}, 'tail_count': 2, 'worst': -2.8003031347001492, 'worst_five_percent_mean': -2.465930179580401}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #31: -2.8003; simulation seed 213111858892867346191887386419863323302432529151035227571676170859234418431210
- Run #28: -2.13156; simulation seed 18595632659765746113308128204685501682783722886651005644751658978085567577786
- Run #14: -1.23587; simulation seed 75701110788388667600665545747971688395814180086946499837669146343925562470824

## variant-15

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.0384146 | 0.138672 | 0.893373 | 0.141255 | -1.26386 | -0.427239 | 0.481405 | 1.47756 |

Mean interval: {'confidence': 0.95, 'high': 0.3241291518070943, 'low': -0.24729998382131496, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.038414583992889655, 'interval': {'confidence': 0.95, 'high': 0.3172999600751732, 'low': -0.23729524268825555, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 26756254536480435143933620277650520947378930047417207341983601834475658672134, 'standard_error': 0.14072910626159552}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.2638619306394818, 'probability_below': {'-0.25': 0.4, '-0.5': 0.225, '-1.0': 0.15, '0.0': 0.425}, 'tail_count': 2, 'worst': -2.0433816152409277, 'worst_five_percent_mean': -1.7658488245306738}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #14: -2.04338; simulation seed 75701110788388667600665545747971688395814180086946499837669146343925562470824
- Run #17: -1.48832; simulation seed 158973220242278192154016132699624820965419819268112219037686635952891334791332
- Run #11: -1.25205; simulation seed 17641730239132819337919723489863790959992625965063867607216452210026545554218

## variant-16

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.137845 | 0.15753 | 1.04982 | 0.165991 | -1.8525 | -0.99646 | 0.606758 | 1.29916 |

Mean interval: {'confidence': 0.95, 'high': 0.1979040467879902, 'low': -0.4735935729952423, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.13784476310362606, 'interval': {'confidence': 0.95, 'high': 0.17234095992282264, 'low': -0.4615805602934203, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 48161139985865803249492137327938872763751426861911112973025232746918572226664, 'standard_error': 0.16550736847848613}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.8525031219009622, 'probability_below': {'-0.25': 0.45, '-0.5': 0.425, '-1.0': 0.25, '0.0': 0.475}, 'tail_count': 2, 'worst': -2.3617283904766775, 'worst_five_percent_mean': -2.1631367540265574}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #31: -2.36173; simulation seed 213111858892867346191887386419863323302432529151035227571676170859234418431210
- Run #18: -1.96455; simulation seed 178550663874872547796473692807573760876420110184197945286668025882135345997650
- Run #8: -1.84661; simulation seed 204361413067686439161865448608322207517466203634819304169414683236897188257826

## variant-17

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.0295461 | 0.0738335 | 1.08044 | 0.170832 | -1.45406 | -0.789024 | 0.749571 | 1.12571 |

Mean interval: {'confidence': 0.95, 'high': 0.37508603487724745, 'low': -0.3159937976100705, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.029546118633588442, 'interval': {'confidence': 0.95, 'high': 0.38379973499463116, 'low': -0.28922868621249015, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 32841088076932769247061397471177362638039118332348400253534204672156909675210, 'standard_error': 0.1721670469273526}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.4540582130082023, 'probability_below': {'-0.25': 0.4, '-0.5': 0.35, '-1.0': 0.15, '0.0': 0.425}, 'tail_count': 2, 'worst': -2.505222520496204, 'worst_five_percent_mean': -2.0219047258788403}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #31: -2.50522; simulation seed 213111858892867346191887386419863323302432529151035227571676170859234418431210
- Run #15: -1.53859; simulation seed 108558290286211770509424072769078288340019663611797643275114130610000873221760
- Run #13: -1.44961; simulation seed 73601954897173572534615624734910873188415705380033639422684526662524016138332

## variant-18

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.207658 | 0.237735 | 0.920557 | 0.145553 | -1.50689 | -0.317284 | 0.78467 | 1.47606 |

Mean interval: {'confidence': 0.95, 'high': 0.5020665499774738, 'low': -0.08674996988231518, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.20765829004757932, 'interval': {'confidence': 0.95, 'high': 0.4985254798766643, 'low': -0.08224980287800357, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 125444173930562926518843342900654040743866304282417904948545394648997791234, 'standard_error': 0.1455173736572109}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.5068891653501613, 'probability_below': {'-0.25': 0.275, '-0.5': 0.2, '-1.0': 0.1, '0.0': 0.35}, 'tail_count': 2, 'worst': -1.8664812641002162, 'worst_five_percent_mean': -1.7444144639178634}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #18: -1.86648; simulation seed 178550663874872547796473692807573760876420110184197945286668025882135345997650
- Run #22: -1.62235; simulation seed 109006795979948863018140189240777738983241616203327246037960535496267672217726
- Run #7: -1.50081; simulation seed 42810676843598314886338763320918203137855958466555930066835539095178234705324

## variant-19

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.124403 | 0.0944239 | 0.853875 | 0.13501 | -1.12017 | -0.328055 | 0.567904 | 1.41133 |

Mean interval: {'confidence': 0.95, 'high': 0.39748514085989917, 'low': -0.14868006048393448, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.12440254018798233, 'interval': {'confidence': 0.95, 'high': 0.38488350001604876, 'low': -0.14290098355100864, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 61100709329978179871172363616556237618921956419001516429784583876494449929531, 'standard_error': 0.1384041625618183}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.12016522458109, 'probability_below': {'-0.25': 0.3, '-0.5': 0.175, '-1.0': 0.1, '0.0': 0.45}, 'tail_count': 2, 'worst': -1.5766451755638125, 'worst_five_percent_mean': -1.3857417782621018}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #37: -1.57665; simulation seed 72423591542693302093580607880055037519138694330852904494077515863697709801238
- Run #7: -1.19484; simulation seed 42810676843598314886338763320918203137855958466555930066835539095178234705324
- Run #28: -1.11624; simulation seed 18595632659765746113308128204685501682783722886651005644751658978085567577786

## variant-20

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.218227 | -0.191185 | 0.932847 | 0.147496 | -1.62219 | -0.908817 | 0.386554 | 1.31018 |

Mean interval: {'confidence': 0.95, 'high': 0.08011220454734691, 'low': -0.516565931207809, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.21822686333023106, 'interval': {'confidence': 0.95, 'high': 0.059614901458036273, 'low': -0.4944826922944876, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 48498478200111796721140206489738561013824877203060590557844560219136840281207, 'standard_error': 0.14486619544485368}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.6221868670590807, 'probability_below': {'-0.25': 0.475, '-0.5': 0.35, '-1.0': 0.2, '0.0': 0.65}, 'tail_count': 2, 'worst': -2.451953071332343, 'worst_five_percent_mean': -2.0632435556977953}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #14: -2.45195; simulation seed 75701110788388667600665545747971688395814180086946499837669146343925562470824
- Run #22: -1.67453; simulation seed 109006795979948863018140189240777738983241616203327246037960535496267672217726
- Run #18: -1.61943; simulation seed 178550663874872547796473692807573760876420110184197945286668025882135345997650

## variant-21

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.0475705 | 0.199741 | 0.908433 | 0.143636 | -1.42112 | -0.507302 | 0.720863 | 1.16272 |

Mean interval: {'confidence': 0.95, 'high': 0.3381014652828856, 'low': -0.24296038454963595, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.047570540366624815, 'interval': {'confidence': 0.95, 'high': 0.31376642296039065, 'low': -0.23482398672760854, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 72171727613051857699350854471183131958201688437942006107806294413590996331658, 'standard_error': 0.1412651189454069}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.4211193367124142, 'probability_below': {'-0.25': 0.4, '-0.5': 0.25, '-1.0': 0.15, '0.0': 0.475}, 'tail_count': 2, 'worst': -2.167399476034819, 'worst_five_percent_mean': -2.001514489645209}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #15: -2.1674; simulation seed 108558290286211770509424072769078288340019663611797643275114130610000873221760
- Run #7: -1.83563; simulation seed 42810676843598314886338763320918203137855958466555930066835539095178234705324
- Run #18: -1.3993; simulation seed 178550663874872547796473692807573760876420110184197945286668025882135345997650

## variant-22

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.195451 | -0.0828313 | 1.04775 | 0.165664 | -1.76123 | -0.896046 | 0.467029 | 1.285 |

Mean interval: {'confidence': 0.95, 'high': 0.13963593201823338, 'low': -0.5305375411999793, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.195450804590873, 'interval': {'confidence': 0.95, 'high': 0.1349735961147005, 'low': -0.5221989930322251, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 22172807873023220517487090848562603458608779360057163101609144672066379230494, 'standard_error': 0.16412935328561643}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.7612258681208006, 'probability_below': {'-0.25': 0.475, '-0.5': 0.425, '-1.0': 0.25, '0.0': 0.575}, 'tail_count': 2, 'worst': -2.741447567672663, 'worst_five_percent_mean': -2.273228225597459}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #37: -2.74145; simulation seed 72423591542693302093580607880055037519138694330852904494077515863697709801238
- Run #14: -1.80501; simulation seed 75701110788388667600665545747971688395814180086946499837669146343925562470824
- Run #13: -1.75892; simulation seed 73601954897173572534615624734910873188415705380033639422684526662524016138332

## variant-23

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.0785434 | 0.035168 | 0.817271 | 0.129222 | -1.27913 | -0.438315 | 0.331013 | 1.09188 |

Mean interval: {'confidence': 0.95, 'high': 0.18283245936685324, 'low': -0.3399191805957519, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.0785433606144493, 'interval': {'confidence': 0.95, 'high': 0.15635876986892566, 'low': -0.3327795339264809, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 20081303795724627060008352754830005954154164949146620233672240972048034168317, 'standard_error': 0.125897118719466}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.2791336284176598, 'probability_below': {'-0.25': 0.4, '-0.5': 0.225, '-1.0': 0.125, '0.0': 0.475}, 'tail_count': 2, 'worst': -2.1658921859800224, 'worst_five_percent_mean': -1.784077279488948}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #38: -2.16589; simulation seed 171880834199780400212358911574398663149818641122693387650655771300801879823130
- Run #31: -1.40226; simulation seed 213111858892867346191887386419863323302432529151035227571676170859234418431210
- Run #24: -1.27265; simulation seed 212360039819845956615547715377096424712330639207303677741122503117296081117318

## variant-24

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.224977 | -0.344105 | 0.921129 | 0.145643 | -1.49068 | -0.819166 | 0.255477 | 1.3176 |

Mean interval: {'confidence': 0.95, 'high': 0.06961433614836388, 'low': -0.519568176028617, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.22497691994012659, 'interval': {'confidence': 0.95, 'high': 0.04744232289332405, 'low': -0.5087768453051303, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 64317206050685961465022892307816723028112424083956079100674742424970929294844, 'standard_error': 0.14171011039408357}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.4906849536357152, 'probability_below': {'-0.25': 0.525, '-0.5': 0.35, '-1.0': 0.2, '0.0': 0.625}, 'tail_count': 2, 'worst': -2.086383071419172, 'worst_five_percent_mean': -1.9435877682440619}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #22: -2.08638; simulation seed 109006795979948863018140189240777738983241616203327246037960535496267672217726
- Run #33: -1.80079; simulation seed 209728915717659796388982345698829672177467233564060939135774466664656725017160
- Run #6: -1.47436; simulation seed 61220899501351337825269833788851712250170152754735481862445654282643994058602

## variant-25

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.255177 | -0.17195 | 0.848552 | 0.134168 | -1.46001 | -0.820729 | 0.213624 | 0.900618 |

Mean interval: {'confidence': 0.95, 'high': 0.01620339819217076, 'low': -0.5265569359353974, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.25517676887161334, 'interval': {'confidence': 0.95, 'high': 0.0017393528264831716, 'low': -0.5200254097572043, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 47393559258569300701856724330668996472927501914068974553064255492691448435409, 'standard_error': 0.13054113273436108}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.4600143457785029, 'probability_below': {'-0.25': 0.45, '-0.5': 0.375, '-1.0': 0.175, '0.0': 0.625}, 'tail_count': 2, 'worst': -2.2969719709803393, 'worst_five_percent_mean': -2.1592659858174845}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #14: -2.29697; simulation seed 75701110788388667600665545747971688395814180086946499837669146343925562470824
- Run #18: -2.02156; simulation seed 178550663874872547796473692807573760876420110184197945286668025882135345997650
- Run #6: -1.43046; simulation seed 61220899501351337825269833788851712250170152754735481862445654282643994058602

## variant-26

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.25225 | -0.174711 | 0.953018 | 0.150685 | -1.91667 | -0.855888 | 0.396884 | 0.927173 |

Mean interval: {'confidence': 0.95, 'high': 0.05253996408014211, 'low': -0.557039847407008, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.25224994166343295, 'interval': {'confidence': 0.95, 'high': 0.036117920735784355, 'low': -0.5451302762180643, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 92544664062734591025961654853657639456837201542611898696169937744884374794216, 'standard_error': 0.1484333891005097}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.9166744650454315, 'probability_below': {'-0.25': 0.475, '-0.5': 0.4, '-1.0': 0.225, '0.0': 0.6}, 'tail_count': 2, 'worst': -2.495227339075328, 'worst_five_percent_mean': -2.222303303109089}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #14: -2.49523; simulation seed 75701110788388667600665545747971688395814180086946499837669146343925562470824
- Run #8: -1.94938; simulation seed 204361413067686439161865448608322207517466203634819304169414683236897188257826
- Run #24: -1.91495; simulation seed 212360039819845956615547715377096424712330639207303677741122503117296081117318

## variant-27

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.0514862 | 0.0230106 | 1.00753 | 0.159304 | -1.50327 | -0.693648 | 0.731522 | 1.67975 |

Mean interval: {'confidence': 0.95, 'high': 0.37370974347810265, 'low': -0.27073730624212095, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.05148621861799084, 'interval': {'confidence': 0.95, 'high': 0.35893102316111314, 'low': -0.25379197448542873, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 7778487759009004474918414488648619293485212828612796448380873706921551268164, 'standard_error': 0.15493514406091208}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.503266510528955, 'probability_below': {'-0.25': 0.4, '-0.5': 0.325, '-1.0': 0.125, '0.0': 0.475}, 'tail_count': 2, 'worst': -2.1874568693508643, 'worst_five_percent_mean': -2.0283245006980564}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #23: -2.18746; simulation seed 139073535557910357261445892962952209406170864229888947255931707236835204994106
- Run #11: -1.86919; simulation seed 17641730239132819337919723489863790959992625965063867607216452210026545554218
- Run #34: -1.48401; simulation seed 198300089775388583939360880316385849716397225375629180861738053159499708594058

## variant-28

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.125345 | -0.107172 | 0.736242 | 0.11641 | -1.24653 | -0.721252 | 0.441681 | 0.948487 |

Mean interval: {'confidence': 0.95, 'high': 0.11011686957865935, 'low': -0.3608064578102695, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.12534479411580507, 'interval': {'confidence': 0.95, 'high': 0.09387170366398875, 'low': -0.34327096842484894, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 48676850808385139186281613216049282332176345206160027139977398498979479270299, 'standard_error': 0.11347646702485246}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.2465326161818706, 'probability_below': {'-0.25': 0.45, '-0.5': 0.325, '-1.0': 0.1, '0.0': 0.525}, 'tail_count': 2, 'worst': -1.6444759374220426, 'worst_five_percent_mean': -1.5275396402075592}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #35: -1.64448; simulation seed 16752202956147647847956636392610453463630813977030108188685636334056991806130
- Run #31: -1.4106; simulation seed 213111858892867346191887386419863323302432529151035227571676170859234418431210
- Run #11: -1.2379; simulation seed 17641730239132819337919723489863790959992625965063867607216452210026545554218

## variant-29

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.104634 | 0.169324 | 0.962804 | 0.152233 | -1.32634 | -0.841814 | 0.984187 | 1.48591 |

Mean interval: {'confidence': 0.95, 'high': 0.41255366181601305, 'low': -0.20328550441531934, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.10463407870034684, 'interval': {'confidence': 0.95, 'high': 0.3960667775651794, 'low': -0.1847655395386229, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 31408496156583561869522368080383967602484142841758872255724227976608836872523, 'standard_error': 0.14542420563927078}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.3263398773941162, 'probability_below': {'-0.25': 0.325, '-0.5': 0.275, '-1.0': 0.175, '0.0': 0.425}, 'tail_count': 2, 'worst': -1.6296333000030216, 'worst_five_percent_mean': -1.5904584935943502}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #18: -1.62963; simulation seed 178550663874872547796473692807573760876420110184197945286668025882135345997650
- Run #10: -1.55128; simulation seed 195391840130457500980818502305404431979912181103234576935600666320141516061872
- Run #37: -1.3145; simulation seed 72423591542693302093580607880055037519138694330852904494077515863697709801238

## variant-30

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.117002 | 0.0258832 | 0.831363 | 0.13145 | -1.15367 | -0.456233 | 0.717762 | 1.25839 |

Mean interval: {'confidence': 0.95, 'high': 0.3828852706712138, 'low': -0.14888048326401349, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.11700239370360017, 'interval': {'confidence': 0.95, 'high': 0.3801546368217069, 'low': -0.13962022472277724, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 66337185671300215151139071271184243258292224191685271354876923940370189745240, 'standard_error': 0.131647439074112}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.1536694913299075, 'probability_below': {'-0.25': 0.35, '-0.5': 0.225, '-1.0': 0.125, '0.0': 0.45}, 'tail_count': 2, 'worst': -1.345454540074596, 'worst_five_percent_mean': -1.2962862873996235}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #37: -1.34545; simulation seed 72423591542693302093580607880055037519138694330852904494077515863697709801238
- Run #34: -1.24712; simulation seed 198300089775388583939360880316385849716397225375629180861738053159499708594058
- Run #33: -1.14875; simulation seed 209728915717659796388982345698829672177467233564060939135774466664656725017160

## variant-31

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.0375154 | 0.0416264 | 0.957455 | 0.151387 | -1.64446 | -0.703201 | 0.765031 | 1.61484 |

Mean interval: {'confidence': 0.95, 'high': 0.3437244524952957, 'low': -0.2686935853419191, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.037515433576688295, 'interval': {'confidence': 0.95, 'high': 0.33243429284397363, 'low': -0.24508137676348252, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 67171447732872901422088422045911716020074416629396405872647385842534526181815, 'standard_error': 0.14775950733554655}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.6444567294708168, 'probability_below': {'-0.25': 0.35, '-0.5': 0.3, '-1.0': 0.125, '0.0': 0.475}, 'tail_count': 2, 'worst': -1.7260641402018764, 'worst_five_percent_mean': -1.6859193812685689}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #6: -1.72606; simulation seed 61220899501351337825269833788851712250170152754735481862445654282643994058602
- Run #14: -1.64577; simulation seed 75701110788388667600665545747971688395814180086946499837669146343925562470824
- Run #11: -1.64439; simulation seed 17641730239132819337919723489863790959992625965063867607216452210026545554218

## variant-32

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.143717 | -0.299908 | 1.07395 | 0.169806 | -1.89892 | -0.701029 | 0.637573 | 1.72559 |

Mean interval: {'confidence': 0.95, 'high': 0.19974893071012184, 'low': -0.4871826609022855, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.14371686509608184, 'interval': {'confidence': 0.95, 'high': 0.1865653242817354, 'low': -0.4673006006121118, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 60118440368483654392604334033683709219916398194393429403449111025935133448867, 'standard_error': 0.1673065808510472}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.8989213432414556, 'probability_below': {'-0.25': 0.525, '-0.5': 0.35, '-1.0': 0.2, '0.0': 0.6}, 'tail_count': 2, 'worst': -2.534920031388364, 'worst_five_percent_mean': -2.2410743172853476}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #34: -2.53492; simulation seed 198300089775388583939360880316385849716397225375629180861738053159499708594058
- Run #17: -1.94723; simulation seed 158973220242278192154016132699624820965419819268112219037686635952891334791332
- Run #7: -1.89638; simulation seed 42810676843598314886338763320918203137855958466555930066835539095178234705324

## variant-33

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.231082 | 0.349662 | 0.865871 | 0.136906 | -1.63512 | -0.162222 | 0.625522 | 1.63178 |

Mean interval: {'confidence': 0.95, 'high': 0.5080013131315337, 'low': -0.045836352340227204, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.23108248039565327, 'interval': {'confidence': 0.95, 'high': 0.49462276958052714, 'low': -0.027403750517284952, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 52366991814254680196096030216087736434570475574612998700951777096745107452863, 'standard_error': 0.13296447394678218}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.6351194159578666, 'probability_below': {'-0.25': 0.2, '-0.5': 0.125, '-1.0': 0.075, '0.0': 0.375}, 'tail_count': 2, 'worst': -1.9526175815450928, 'worst_five_percent_mean': -1.8637459469655018}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #26: -1.95262; simulation seed 95520444881240503472865108893167928833856663538983263927089402611660252121048
- Run #18: -1.77487; simulation seed 178550663874872547796473692807573760876420110184197945286668025882135345997650
- Run #31: -1.62776; simulation seed 213111858892867346191887386419863323302432529151035227571676170859234418431210

## variant-34

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.0751481 | -0.108879 | 1.10902 | 0.175352 | -1.65906 | -0.852572 | 0.881003 | 1.50803 |

Mean interval: {'confidence': 0.95, 'high': 0.27953483069384977, 'low': -0.42983096914542207, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.07514806922578614, 'interval': {'confidence': 0.95, 'high': 0.2638155987658358, 'low': -0.4106816889362598, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 38892399337842280556188693644253625458584491875233792838827965404902830050838, 'standard_error': 0.1714212294462439}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.6590568516295772, 'probability_below': {'-0.25': 0.45, '-0.5': 0.35, '-1.0': 0.225, '0.0': 0.55}, 'tail_count': 2, 'worst': -2.1156762744937496, 'worst_five_percent_mean': -1.986212111941247}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #6: -2.11568; simulation seed 61220899501351337825269833788851712250170152754735481862445654282643994058602
- Run #14: -1.85675; simulation seed 75701110788388667600665545747971688395814180086946499837669146343925562470824
- Run #37: -1.64865; simulation seed 72423591542693302093580607880055037519138694330852904494077515863697709801238

## variant-35

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.0812052 | 0.105002 | 1.06414 | 0.168255 | -1.55999 | -0.616913 | 0.572484 | 2.11482 |

Mean interval: {'confidence': 0.95, 'high': 0.4215327165823551, 'low': -0.25912233754572117, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.08120518951831697, 'interval': {'confidence': 0.95, 'high': 0.4252464751358312, 'low': -0.22956970788933823, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 96151864682851390834016464790876983943833733718978077482001574318245951595090, 'standard_error': 0.1663472873339671}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.559986040670831, 'probability_below': {'-0.25': 0.35, '-0.5': 0.3, '-1.0': 0.15, '0.0': 0.45}, 'tail_count': 2, 'worst': -1.764375100079216, 'worst_five_percent_mean': -1.682203195168849}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #36: -1.76438; simulation seed 167581798649470180704402953808071333323210882384825611522511921981363999529758
- Run #6: -1.60003; simulation seed 61220899501351337825269833788851712250170152754735481862445654282643994058602
- Run #14: -1.55788; simulation seed 75701110788388667600665545747971688395814180086946499837669146343925562470824

## variant-36

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.203922 | 0.0382626 | 0.916466 | 0.144906 | -1.04302 | -0.68317 | 0.832551 | 1.68056 |

Mean interval: {'confidence': 0.95, 'high': 0.4970218278516445, 'low': -0.08917821968731399, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.20392180408216526, 'interval': {'confidence': 0.95, 'high': 0.48408116371861376, 'low': -0.06259352919323638, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 12145698473248664610333745758540303281530943528001317472921315587947269844550, 'standard_error': 0.13777245308583616}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.0430157153514907, 'probability_below': {'-0.25': 0.35, '-0.5': 0.3, '-1.0': 0.075, '0.0': 0.5}, 'tail_count': 2, 'worst': -1.1649197976664947, 'worst_five_percent_mean': -1.1389270367277569}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #26: -1.16492; simulation seed 95520444881240503472865108893167928833856663538983263927089402611660252121048
- Run #30: -1.11293; simulation seed 75189268677950391107092024914092833256509564730917004615110696444503482148566
- Run #28: -1.03934; simulation seed 18595632659765746113308128204685501682783722886651005644751658978085567577786

## variant-37

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.218665 | -0.156537 | 1.04556 | 0.165317 | -1.97924 | -0.881693 | 0.429659 | 1.24289 |

Mean interval: {'confidence': 0.95, 'high': 0.11572064908536384, 'low': -0.5530504018272132, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.2186648763709247, 'interval': {'confidence': 0.95, 'high': 0.10413625557914269, 'low': -0.5438045235682225, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 89494800510375298394435335311110289795750033282561750852749001687050836334259, 'standard_error': 0.16276904550562235}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.9792445737976438, 'probability_below': {'-0.25': 0.425, '-0.5': 0.375, '-1.0': 0.2, '0.0': 0.6}, 'tail_count': 2, 'worst': -2.1495590763542536, 'worst_five_percent_mean': -2.0752706819136}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #25: -2.14956; simulation seed 191463871824032581839690000654146240923037665899998486620379150717548373926490
- Run #18: -2.00098; simulation seed 178550663874872547796473692807573760876420110184197945286668025882135345997650
- Run #22: -1.9781; simulation seed 109006795979948863018140189240777738983241616203327246037960535496267672217726

## variant-38

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.0930782 | -0.0877949 | 1.05738 | 0.167187 | -1.77024 | -0.657191 | 0.520646 | 1.63355 |

Mean interval: {'confidence': 0.95, 'high': 0.24508901243434802, 'low': -0.43124544254354613, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.09307821505459904, 'interval': {'confidence': 0.95, 'high': 0.23338523202052533, 'low': -0.4277031831650209, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 96579965193967700867636702914141760888776045537163518233320557538275204297967, 'standard_error': 0.1689472934526684}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.7702386706925382, 'probability_below': {'-0.25': 0.4, '-0.5': 0.3, '-1.0': 0.2, '0.0': 0.6}, 'tail_count': 2, 'worst': -2.55938127761406, 'worst_five_percent_mean': -2.517412816999954}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #19: -2.55938; simulation seed 99003629409724868636513946294053693718806502664384300739864858705948429835720
- Run #38: -2.47544; simulation seed 171880834199780400212358911574398663149818641122693387650655771300801879823130
- Run #7: -1.73312; simulation seed 42810676843598314886338763320918203137855958466555930066835539095178234705324

## variant-39

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.0556793 | -0.102425 | 1.09382 | 0.172948 | -2.12256 | -0.786333 | 0.717664 | 1.5923 |

Mean interval: {'confidence': 0.95, 'high': 0.294140988393439, 'low': -0.40549954745970246, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.055679279533131745, 'interval': {'confidence': 0.95, 'high': 0.28262752258181323, 'low': -0.40747620003005464, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 49096743839557309377764831226231522985889704136959199917063462070912238181187, 'standard_error': 0.17065194347258678}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -2.1225603815432827, 'probability_below': {'-0.25': 0.425, '-0.5': 0.35, '-1.0': 0.2, '0.0': 0.55}, 'tail_count': 2, 'worst': -2.47874546022114, 'worst_five_percent_mean': -2.396629211464436}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #33: -2.47875; simulation seed 209728915717659796388982345698829672177467233564060939135774466664656725017160
- Run #14: -2.31451; simulation seed 75701110788388667600665545747971688395814180086946499837669146343925562470824
- Run #31: -2.11246; simulation seed 213111858892867346191887386419863323302432529151035227571676170859234418431210

## variant-40

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.103407 | 0.000840976 | 0.928879 | 0.146869 | -1.29055 | -0.503824 | 0.733589 | 1.51221 |

Mean interval: {'confidence': 0.95, 'high': 0.40047674336489014, 'low': -0.19366320285628416, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.10340677025430298, 'interval': {'confidence': 0.95, 'high': 0.3741322275740164, 'low': -0.17409521576785456, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 89089359605410776448492871951062515728484771018211701388859565637457187187357, 'standard_error': 0.1438961337270004}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.2905479732879794, 'probability_below': {'-0.25': 0.375, '-0.5': 0.25, '-1.0': 0.1, '0.0': 0.5}, 'tail_count': 2, 'worst': -2.0296789114218514, 'worst_five_percent_mean': -1.889568185530799}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #18: -2.02968; simulation seed 178550663874872547796473692807573760876420110184197945286668025882135345997650
- Run #33: -1.74946; simulation seed 209728915717659796388982345698829672177467233564060939135774466664656725017160
- Run #24: -1.26639; simulation seed 212360039819845956615547715377096424712330639207303677741122503117296081117318

## variant-41

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.115251 | 0.0261589 | 0.958432 | 0.151541 | -1.87649 | -0.836678 | 0.392057 | 1.19631 |

Mean interval: {'confidence': 0.95, 'high': 0.1912703057864227, 'low': -0.4217726083244563, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.11525115126901678, 'interval': {'confidence': 0.95, 'high': 0.16821806205712703, 'low': -0.40341877569586054, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 84962451132213878662285167519059110996903131542447221020786609417688784950849, 'standard_error': 0.14951138254911958}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.8764861561039412, 'probability_below': {'-0.25': 0.375, '-0.5': 0.325, '-1.0': 0.2, '0.0': 0.5}, 'tail_count': 2, 'worst': -2.0771682984496054, 'worst_five_percent_mean': -2.062380701245744}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #24: -2.07717; simulation seed 212360039819845956615547715377096424712330639207303677741122503117296081117318
- Run #31: -2.04759; simulation seed 213111858892867346191887386419863323302432529151035227571676170859234418431210
- Run #33: -1.86748; simulation seed 209728915717659796388982345698829672177467233564060939135774466664656725017160

## variant-42

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.035725 | -0.0871248 | 1.02142 | 0.161501 | -1.25795 | -0.701246 | 0.686481 | 1.43828 |

Mean interval: {'confidence': 0.95, 'high': 0.3623921595595205, 'low': -0.2909422084118151, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.035724975573852694, 'interval': {'confidence': 0.95, 'high': 0.3550104424471723, 'low': -0.2579949221437342, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 58541933555161180057591039955835927457231409161748449668749746084007304197146, 'standard_error': 0.1631434152002325}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.2579459879766643, 'probability_below': {'-0.25': 0.4, '-0.5': 0.325, '-1.0': 0.125, '0.0': 0.525}, 'tail_count': 2, 'worst': -2.1656479092099454, 'worst_five_percent_mean': -1.7562455646005801}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #31: -2.16565; simulation seed 213111858892867346191887386419863323302432529151035227571676170859234418431210
- Run #7: -1.34684; simulation seed 42810676843598314886338763320918203137855958466555930066835539095178234705324
- Run #35: -1.25327; simulation seed 16752202956147647847956636392610453463630813977030108188685636334056991806130

## variant-43

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.136115 | -0.158621 | 0.920758 | 0.145585 | -1.37905 | -0.881189 | 0.709181 | 1.10538 |

Mean interval: {'confidence': 0.95, 'high': 0.15835819114884317, 'low': -0.43058723090306406, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.13611451987711046, 'interval': {'confidence': 0.95, 'high': 0.1413870997195208, 'low': -0.428247807115867, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 46228179498590637348762078079393180702598338382300813183642045416262216127744, 'standard_error': 0.14587078969337494}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.379051247555226, 'probability_below': {'-0.25': 0.475, '-0.5': 0.425, '-1.0': 0.175, '0.0': 0.575}, 'tail_count': 2, 'worst': -2.30522089723721, 'worst_five_percent_mean': -1.9521036893010346}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #38: -2.30522; simulation seed 171880834199780400212358911574398663149818641122693387650655771300801879823130
- Run #21: -1.59899; simulation seed 210418427453984090683183467486756509570132888221518903018895496491673128929918
- Run #31: -1.36748; simulation seed 213111858892867346191887386419863323302432529151035227571676170859234418431210

## variant-44

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.020079 | 0.305194 | 0.999766 | 0.158077 | -1.50571 | -0.905049 | 0.704901 | 1.23955 |

Mean interval: {'confidence': 0.95, 'high': 0.3398196240890294, 'low': -0.29966166633531804, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.02007897887685569, 'interval': {'confidence': 0.95, 'high': 0.32561931384018894, 'low': -0.2751100592867174, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 48477370591061059950000911204225290812487260469491988691803981189733927153352, 'standard_error': 0.15455311440736938}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.5057077609026346, 'probability_below': {'-0.25': 0.375, '-0.5': 0.35, '-1.0': 0.225, '0.0': 0.425}, 'tail_count': 2, 'worst': -1.6813033708654244, 'worst_five_percent_mean': -1.610545473470213}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #34: -1.6813; simulation seed 198300089775388583939360880316385849716397225375629180861738053159499708594058
- Run #35: -1.53979; simulation seed 16752202956147647847956636392610453463630813977030108188685636334056991806130
- Run #24: -1.50391; simulation seed 212360039819845956615547715377096424712330639207303677741122503117296081117318

## variant-45

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | -0.080631 | -0.246564 | 0.959429 | 0.151699 | -1.61171 | -0.601106 | 0.433439 | 1.4743 |

Mean interval: {'confidence': 0.95, 'high': 0.22620937737285485, 'low': -0.38747129445410255, 'method': 'Student t mean'}
Bootstrap: {'estimate': -0.08063095854062385, 'interval': {'confidence': 0.95, 'high': 0.19991157168281354, 'low': -0.35755536239471386, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 2268917404577513929251035775166301088958437819092340513328565787819078369647, 'standard_error': 0.1463061256545905}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.611712487785027, 'probability_below': {'-0.25': 0.5, '-0.5': 0.3, '-1.0': 0.125, '0.0': 0.625}, 'tail_count': 2, 'worst': -2.086505964167109, 'worst_five_percent_mean': -2.0194762342115964}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #26: -2.08651; simulation seed 95520444881240503472865108893167928833856663538983263927089402611660252121048
- Run #23: -1.95245; simulation seed 139073535557910357261445892962952209406170864229888947255931707236835204994106
- Run #21: -1.59378; simulation seed 210418427453984090683183467486756509570132888221518903018895496491673128929918

## variant-46

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.149393 | 0.289938 | 0.931623 | 0.147302 | -1.75017 | -0.431236 | 0.672573 | 1.5056 |

Mean interval: {'confidence': 0.95, 'high': 0.4473403454506141, 'low': -0.14855432049793157, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.14939301247634126, 'interval': {'confidence': 0.95, 'high': 0.43501166254440576, 'low': -0.14310937382535538, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 81374175585451580760372251512347367132304345525314316049788410588380062526224, 'standard_error': 0.14766130778829417}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.7501659051770126, 'probability_below': {'-0.25': 0.375, '-0.5': 0.2, '-1.0': 0.075, '0.0': 0.4}, 'tail_count': 2, 'worst': -1.901669076812948, 'worst_five_percent_mean': -1.840639089385742}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #6: -1.90167; simulation seed 61220899501351337825269833788851712250170152754735481862445654282643994058602
- Run #30: -1.77961; simulation seed 75189268677950391107092024914092833256509564730917004615110696444503482148566
- Run #12: -1.74862; simulation seed 1484383136199096780328585456327142417348231669794117112239693326182654934430

## variant-47

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.135948 | 0.277051 | 1.12912 | 0.178529 | -1.90795 | -0.653213 | 0.822552 | 1.63976 |

Mean interval: {'confidence': 0.95, 'high': 0.4970575205680782, 'low': -0.2251622195103587, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.13594765052885976, 'interval': {'confidence': 0.95, 'high': 0.4872247152485144, 'low': -0.20511172679488335, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 9656555365933110740573298544434246880266149228097154217286854206471809742041, 'standard_error': 0.17723000993042048}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.9079512286739158, 'probability_below': {'-0.25': 0.325, '-0.5': 0.275, '-1.0': 0.15, '0.0': 0.45}, 'tail_count': 2, 'worst': -2.244019212842248, 'worst_five_percent_mean': -2.124342303344133}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #14: -2.24402; simulation seed 75701110788388667600665545747971688395814180086946499837669146343925562470824
- Run #6: -2.00467; simulation seed 61220899501351337825269833788851712250170152754735481862445654282643994058602
- Run #13: -1.90286; simulation seed 73601954897173572534615624734910873188415705380033639422684526662524016138332

## variant-48

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.142164 | 0.321575 | 1.11684 | 0.176588 | -1.37101 | -0.680646 | 0.876057 | 1.64874 |

Mean interval: {'confidence': 0.95, 'high': 0.4993465974903455, 'low': -0.21501795567182488, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.14216432090926032, 'interval': {'confidence': 0.95, 'high': 0.4829839622211211, 'low': -0.19867952380511145, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 57350558255765697981931395726540441843281340417852614472714468866852488771357, 'standard_error': 0.1728711556816245}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -1.3710090985620245, 'probability_below': {'-0.25': 0.375, '-0.5': 0.325, '-1.0': 0.15, '0.0': 0.425}, 'tail_count': 2, 'worst': -2.745581726872318, 'worst_five_percent_mean': -2.076419616369873}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #25: -2.74558; simulation seed 191463871824032581839690000654146240923037665899998486620379150717548373926490
- Run #31: -1.40726; simulation seed 213111858892867346191887386419863323302432529151035227571676170859234418431210
- Run #14: -1.3691; simulation seed 75701110788388667600665545747971688395814180086946499837669146343925562470824

## variant-49

| Metric | Unit | Available/total | Mean | Median | SD | SE | P05 | P25 | P75 | P95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| net_pnl | synthetic payoff units; not trade P&L | 40/40 | 0.368578 | 0.373374 | 0.875121 | 0.138369 | -0.957102 | -0.149541 | 0.767674 | 1.89244 |

Mean interval: {'confidence': 0.95, 'high': 0.6484551525455351, 'low': 0.08870058910373868, 'method': 'Student t mean'}
Bootstrap: {'estimate': 0.3685778708246369, 'interval': {'confidence': 0.95, 'high': 0.6506519421994084, 'low': 0.1064493789856967, 'method': 'percentile bootstrap'}, 'observational_unit': 'complete independent session', 'resamples': 2000, 'seed': 101474419648025159379188516580435480450633806851989459133720530586704488026171, 'standard_error': 0.13773157569986239}
Lower tail: {'convention': 'strict breaches; lower-tail mean uses ceil(0.05*n) sorted outcomes', 'p05': -0.9571015382770083, 'probability_below': {'-0.25': 0.25, '-0.5': 0.175, '-1.0': 0.05, '0.0': 0.325}, 'tail_count': 2, 'worst': -1.269584571392861, 'worst_five_percent_mean': -1.196250278253318}

Exploratory correlations (not causal effects):


Worst primary outcomes:

- Run #23: -1.26958; simulation seed 139073535557910357261445892962952209406170864229888947255931707236835204994106
- Run #14: -1.12292; simulation seed 75701110788388667600665545747971688395814180086946499837669146343925562470824
- Run #26: -0.948374; simulation seed 95520444881240503472865108893167928833856663538983263927089402611660252121048

## Interpretation

variant-00: observed mean net_pnl=-0.191989; losing/negative outcomes 52.5%. variant-01: observed mean net_pnl=0.169367; losing/negative outcomes 50.0%. variant-02: observed mean net_pnl=-0.109021; losing/negative outcomes 52.5%. variant-03: observed mean net_pnl=-0.343342; losing/negative outcomes 67.5%. variant-04: observed mean net_pnl=-0.13792; losing/negative outcomes 60.0%. variant-05: observed mean net_pnl=-0.0406411; losing/negative outcomes 52.5%. variant-06: observed mean net_pnl=0.15449; losing/negative outcomes 50.0%. variant-07: observed mean net_pnl=-0.219452; losing/negative outcomes 65.0%. variant-08: observed mean net_pnl=0.0519149; losing/negative outcomes 50.0%. variant-09: observed mean net_pnl=0.195733; losing/negative outcomes 45.0%. variant-10: observed mean net_pnl=-0.00606909; losing/negative outcomes 55.0%. variant-11: observed mean net_pnl=0.0478329; losing/negative outcomes 47.5%. variant-12: observed mean net_pnl=0.185004; losing/negative outcomes 45.0%. variant-13: observed mean net_pnl=0.0756885; losing/negative outcomes 57.5%. variant-14: observed mean net_pnl=0.209426; losing/negative outcomes 42.5%. variant-15: observed mean net_pnl=0.0384146; losing/negative outcomes 42.5%. variant-16: observed mean net_pnl=-0.137845; losing/negative outcomes 47.5%. variant-17: observed mean net_pnl=0.0295461; losing/negative outcomes 42.5%. variant-18: observed mean net_pnl=0.207658; losing/negative outcomes 35.0%. variant-19: observed mean net_pnl=0.124403; losing/negative outcomes 45.0%. variant-20: observed mean net_pnl=-0.218227; losing/negative outcomes 65.0%. variant-21: observed mean net_pnl=0.0475705; losing/negative outcomes 47.5%. variant-22: observed mean net_pnl=-0.195451; losing/negative outcomes 57.5%. variant-23: observed mean net_pnl=-0.0785434; losing/negative outcomes 47.5%. variant-24: observed mean net_pnl=-0.224977; losing/negative outcomes 62.5%. variant-25: observed mean net_pnl=-0.255177; losing/negative outcomes 62.5%. variant-26: observed mean net_pnl=-0.25225; losing/negative outcomes 60.0%. variant-27: observed mean net_pnl=0.0514862; losing/negative outcomes 47.5%. variant-28: observed mean net_pnl=-0.125345; losing/negative outcomes 52.5%. variant-29: observed mean net_pnl=0.104634; losing/negative outcomes 42.5%. variant-30: observed mean net_pnl=0.117002; losing/negative outcomes 45.0%. variant-31: observed mean net_pnl=0.0375154; losing/negative outcomes 47.5%. variant-32: observed mean net_pnl=-0.143717; losing/negative outcomes 60.0%. variant-33: observed mean net_pnl=0.231082; losing/negative outcomes 37.5%. variant-34: observed mean net_pnl=-0.0751481; losing/negative outcomes 55.0%. variant-35: observed mean net_pnl=0.0812052; losing/negative outcomes 45.0%. variant-36: observed mean net_pnl=0.203922; losing/negative outcomes 50.0%. variant-37: observed mean net_pnl=-0.218665; losing/negative outcomes 60.0%. variant-38: observed mean net_pnl=-0.0930782; losing/negative outcomes 60.0%. variant-39: observed mean net_pnl=-0.0556793; losing/negative outcomes 55.0%. variant-40: observed mean net_pnl=0.103407; losing/negative outcomes 50.0%. variant-41: observed mean net_pnl=-0.115251; losing/negative outcomes 50.0%. variant-42: observed mean net_pnl=0.035725; losing/negative outcomes 52.5%. variant-43: observed mean net_pnl=-0.136115; losing/negative outcomes 57.5%. variant-44: observed mean net_pnl=0.020079; losing/negative outcomes 42.5%. variant-45: observed mean net_pnl=-0.080631; losing/negative outcomes 62.5%. variant-46: observed mean net_pnl=0.149393; losing/negative outcomes 40.0%. variant-47: observed mean net_pnl=0.135948; losing/negative outcomes 45.0%. variant-48: observed mean net_pnl=0.142164; losing/negative outcomes 42.5%. variant-49: observed mean net_pnl=0.368578; losing/negative outcomes 32.5%. Compare the full distributions and paired uncertainty with the original hypothesis. These conditional model outcomes do not establish real-world alpha, safety or an optimal parameter. Interpretation remains reviewable.

## Limitations

- Synthetic performance is not evidence of real-world alpha.
- Independent sessions conditional on one model; uncertainty excludes model error.
- Exploratory metrics/intervals are not corrected for multiple testing.
- Missing metrics are reported with coverage, not replaced by zero.

Quantiles use linear interpolation; SD uses n−1. Markout distributions use per-session available-unit means, with session and unit coverage retained. A confidence interval concerns the model's mean, not the range of future outcomes.
