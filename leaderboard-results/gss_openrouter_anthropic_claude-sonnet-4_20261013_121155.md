# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-sonnet-4
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 384.1s

## SynthBench Parity Score (SPS)

**SPS: 0.7234 [0.6800, 0.7632]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6161 [0.5573, 0.6675] | ██████░░░░ |
| P_rank  Rank-Order | 0.6582 [0.5968, 0.7088] | ███████░░░ |
| P_refuse Refusal Cal. | 0.8959 [0.8300, 0.9332] | █████████░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3839 |
| Median JSD | 0.3122 |
| Mean Kendall's tau | 0.3164 |
| Composite Parity (legacy) | 0.6372 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0752 | +13% |
| random-baseline | 0.6495 | -0.0124 | -2% |

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
| We are faced with many problems in this country, none of whi... | 0.0971 | 0.0000 |
| Please tell me whether or not you think it should be possibl... | 0.1067 | 0.8165 |
| I am going to name an institution in this country. As far as... | 0.1124 | 0.5477 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please tell me whether or not you think it should be possibl... | 0.8901 | -0.8165 |
| Do you consider the amount of federal income tax which you h... | 0.9111 | -0.2357 |
| If you were asked to use one of four names for your social c... | 0.9565 | -0.6325 |
| Compared with American families in general, would you say yo... | 0.9693 | -0.5774 |
| Would you say your own health, in general, is excellent, goo... | 0.9958 | -0.6325 |
