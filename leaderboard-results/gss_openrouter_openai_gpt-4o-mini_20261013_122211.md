# SynthBench Score Card

**Provider:** openrouter/openai/gpt-4o-mini
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 489.5s

## SynthBench Parity Score (SPS)

**SPS: 0.8042 [0.7764, 0.8282]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6855 [0.6467, 0.7213] | ███████░░░ |
| P_rank  Rank-Order | 0.7551 [0.7083, 0.7919] | ████████░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3145 |
| Median JSD | 0.2900 |
| Mean Kendall's tau | 0.5102 |
| Composite Parity (legacy) | 0.7203 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1583 | +28% |
| random-baseline | 0.6495 | +0.0708 | +11% |

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
| Do you favor or oppose the death penalty for persons convict... | 0.0774 | 0.3333 |
| Would you be for or against sex education in the public scho... | 0.0798 | 0.8165 |
| Please tell me whether or not you think it should be possibl... | 0.1067 | 0.8165 |
| Consider somebody who is against all churches and religion. ... | 0.1190 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| We are interested in how people are getting along financiall... | 0.5771 | -0.2357 |
| Some people say that because of past discrimination, Black p... | 0.6992 | 0.0000 |
| Do you believe there is a life after death?... | 0.7016 | -0.8165 |
| If a man and a woman have sexual relations before marriage, ... | 0.7275 | 0.0000 |
| Which statement comes closest to expressing what you believe... | 0.8643 | -0.3290 |
