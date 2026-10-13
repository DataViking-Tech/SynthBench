# SynthBench Score Card

**Provider:** raw-anthropic/claude-haiku-5-5 harness=claude-code
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 1767.3s

## SynthBench Parity Score (SPS)

**SPS: 0.6952 [0.6541, 0.7347]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5735 [0.5115, 0.6289] | ██████░░░░ |
| P_rank  Rank-Order | 0.5457 [0.4841, 0.6052] | █████░░░░░ |
| P_refuse Refusal Cal. | 0.9665 [0.9515, 0.9738] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4265 |
| Median JSD | 0.3687 |
| Mean Kendall's tau | 0.0914 |
| Composite Parity (legacy) | 0.5596 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | -0.0024 | -0% |
| random-baseline | 0.6495 | -0.0899 | -14% |

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
| Generally speaking, would you say that most people can be tr... | 0.0189 | 1.0000 |
| We are faced with many problems in this country, none of whi... | 0.0571 | 0.9129 |
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| We are faced with many problems in this country, none of whi... | 0.0775 | 0.9129 |
| We are faced with many problems in this country, none of whi... | 0.0784 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please indicate whether you strongly agree, agree, disagree,... | 0.8833 | -0.1195 |
| When a person has a disease that cannot be cured, do you thi... | 0.8895 | -0.8165 |
| Please tell me whether or not you think it should be possibl... | 0.8901 | -0.8165 |
| Please indicate whether you strongly agree, agree, disagree,... | 0.9567 | -0.6325 |
| Which statement comes closest to expressing what you believe... | 0.9802 | -0.5345 |
