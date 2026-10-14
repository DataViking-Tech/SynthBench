# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-sonnet-4
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 443.4s

## SynthBench Parity Score (SPS)

**SPS: 0.7200 [0.6787, 0.7574]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6107 [0.5545, 0.6592] | ██████░░░░ |
| P_rank  Rank-Order | 0.6514 [0.5944, 0.7025] | ███████░░░ |
| P_refuse Refusal Cal. | 0.8980 [0.8329, 0.9365] | █████████░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3893 |
| Median JSD | 0.3167 |
| Mean Kendall's tau | 0.3027 |
| Composite Parity (legacy) | 0.6310 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0690 | +12% |
| random-baseline | 0.6495 | -0.0185 | -3% |

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
| Consider somebody who is against all churches and religion. ... | 0.1190 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Some people say that because of past discrimination, Black p... | 0.8489 | -0.6325 |
| Do you consider the amount of federal income tax which you h... | 0.9111 | -0.2357 |
| If you were asked to use one of four names for your social c... | 0.9565 | -0.6325 |
| Compared with American families in general, would you say yo... | 0.9693 | -0.5774 |
| Would you say your own health, in general, is excellent, goo... | 0.9958 | -0.6325 |
