# SynthBench Score Card

**Provider:** synthpanel/openrouter/anthropic/claude-haiku-4-5
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 342.6s

## SynthBench Parity Score (SPS)

**SPS: 0.8032 [0.7672, 0.8308]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7136 [0.6638, 0.7592] | ███████░░░ |
| P_rank  Rank-Order | 0.7240 [0.6662, 0.7722] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2864 |
| Median JSD | 0.2194 |
| Mean Kendall's tau | 0.4479 |
| Composite Parity (legacy) | 0.7188 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1568 | +28% |
| random-baseline | 0.6495 | +0.0693 | +11% |

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
| I am going to name an institution in this country. As far as... | 0.0083 | 1.0000 |
| I am going to name an institution in this country. As far as... | 0.0124 | 1.0000 |
| I am going to name an institution in this country. As far as... | 0.0228 | 0.6667 |
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| I am going to name an institution in this country. As far as... | 0.0607 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Generally speaking, would you say that most people can be tr... | 0.6191 | -0.6667 |
| Do you think most people would try to take advantage of you ... | 0.6386 | -0.1826 |
| Do you believe there is a life after death?... | 0.7016 | -0.8165 |
| Do you think a person has the right to end his or her own li... | 0.8751 | -0.8165 |
| When a person has a disease that cannot be cured, do you thi... | 0.8895 | -0.8165 |
