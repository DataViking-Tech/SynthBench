# SynthBench Score Card

**Provider:** synthpanel/openrouter/anthropic/claude-haiku-4-5 tpl=structured
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 131.2s

## SynthBench Parity Score (SPS)

**SPS: 0.7915 [0.7539, 0.8180]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6661 [0.6184, 0.7073] | ███████░░░ |
| P_rank  Rank-Order | 0.7363 [0.6780, 0.7829] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3339 |
| Median JSD | 0.2835 |
| Mean Kendall's tau | 0.4726 |
| Composite Parity (legacy) | 0.7012 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1392 | +25% |
| random-baseline | 0.6495 | +0.0517 | +8% |

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
| I am going to name an institution in this country. As far as... | 0.1195 | 0.5477 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think most people would try to take advantage of you ... | 0.7212 | -0.2357 |
| Generally speaking, would you say that most people can be tr... | 0.7427 | -0.2357 |
| Some people say that because of past discrimination, Black p... | 0.7666 | -0.8367 |
| Do you think a person has the right to end his or her own li... | 0.8751 | -0.8165 |
| When a person has a disease that cannot be cured, do you thi... | 0.8895 | -0.8165 |
