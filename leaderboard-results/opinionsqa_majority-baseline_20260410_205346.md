# SynthBench Score Card

**Provider:** majority-baseline
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 0.0s

## SynthBench Parity Score (SPS)

**SPS: 0.6695 [0.4679, 0.5425]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.4502 [0.4058, 0.4916] | █████░░░░░ |
| P_rank  Rank-Order | 0.5641 [0.5283, 0.6027] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.5498 |
| Median JSD | 0.5400 |
| Mean Kendall's tau | 0.1282 |
| Composite Parity (legacy) | 0.5071 |

## What These Scores Mean

- **SPS** (SynthBench Parity Score): The overall score — average of all metrics. 0 = random noise, 1 = indistinguishable from real humans.
- **P_dist** (Distributional Parity): How closely does the AI's answer distribution match real humans? If 60% of humans say 'yes' and the AI says 'yes' 60% of the time, that's a perfect match. 0 = completely different, 1 = identical distributions.
- **P_rank** (Rank-Order Parity): Does the AI get the preference ordering right? If humans prefer A > B > C, does the AI agree — even if the exact percentages differ? 0 = reversed ordering, 1 = perfect agreement.
- **P_refuse** (Refusal Calibration): Does the AI refuse to answer at appropriate rates? Humans sometimes decline sensitive questions. An AI that never refuses, or refuses too often, is miscalibrated. 0 = rates completely off, 1 = perfect match.
- **P_cond** (Conditioning Fidelity): When told 'respond as a 65-year-old conservative,' does the AI actually shift its answers? Higher = better demographic role-playing. (When available.)
- **P_sub** (Subgroup Consistency): Is the AI equally accurate across all demographics, or does it nail some groups and miss others? (When available.)

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| If driverless vehicles become widespread, which of the follo... | 0.1034 | 0.8165 |
| If driverless vehicles become widespread, which of the follo... | 0.1186 | 0.8165 |
| Do you think the following are likely to happen as a result ... | 0.1241 | 0.8165 |
| Regardless of whether or not you own a gun, have you ever fi... | 0.1277 | 0.8165 |
| If driverless vehicles become widespread, which of the follo... | 0.1913 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How often, if ever, do you visit websites about guns, huntin... | 0.9259 | -0.3162 |
| Have you yourself ever lost a job because your employer repl... | 0.9288 | -0.2357 |
| How often, if ever, do you attend gun shows... | 0.9625 | -0.3162 |
| How often, if ever, do you listen to gun-oriented podcasts o... | 0.9692 | -0.3162 |
| How often, if ever, do you participate in online discussion ... | 0.9718 | -0.3162 |
