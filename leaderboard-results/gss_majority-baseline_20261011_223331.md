# SynthBench Score Card

**Provider:** majority-baseline
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 0.0s

## SynthBench Parity Score (SPS)

**SPS: 0.7211 [0.6879, 0.7532]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5417 [0.4906, 0.5977] | █████░░░░░ |
| P_rank  Rank-Order | 0.6497 [0.6011, 0.6976] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4583 |
| Median JSD | 0.4678 |
| Mean Kendall's tau | 0.2993 |
| Composite Parity (legacy) | 0.5957 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0337 | +6% |
| random-baseline | 0.6495 | -0.0538 | -8% |

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
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| Would you be for or against sex education in the public scho... | 0.0798 | 0.8165 |
| Please tell me whether or not you think it should be possibl... | 0.1067 | 0.8165 |
| Consider somebody who is against all churches and religion. ... | 0.1190 | 0.8165 |
| We are faced with many problems in this country, none of whi... | 0.1350 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Compared with American families in general, would you say yo... | 0.8147 | -0.1155 |
| Which statement comes closest to expressing what you believe... | 0.8377 | -0.1782 |
| I am going to name an institution in this country. As far as... | 0.8429 | -0.2357 |
| Please indicate whether you strongly agree, agree, disagree,... | 0.8456 | -0.3162 |
| I'm going to show you a seven-point scale on which the polit... | 0.8896 | -0.5000 |
