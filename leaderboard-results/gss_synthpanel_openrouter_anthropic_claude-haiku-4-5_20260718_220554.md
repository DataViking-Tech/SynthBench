# SynthBench Score Card

**Provider:** synthpanel/openrouter/anthropic/claude-haiku-4-5
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 360.4s

## SynthBench Parity Score (SPS)

**SPS: 0.8062 [0.7700, 0.8335]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7181 [0.6678, 0.7638] | ███████░░░ |
| P_rank  Rank-Order | 0.7285 [0.6737, 0.7779] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2819 |
| Median JSD | 0.2090 |
| Mean Kendall's tau | 0.4571 |
| Composite Parity (legacy) | 0.7233 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1613 | +29% |
| random-baseline | 0.6495 | +0.0738 | +11% |

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
| I am going to name an institution in this country. As far as... | 0.0292 | 1.0000 |
| I am going to name an institution in this country. As far as... | 0.0334 | 1.0000 |
| I am going to name an institution in this country. As far as... | 0.0382 | 0.5477 |
| I am going to name an institution in this country. As far as... | 0.0482 | 1.0000 |
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Which statement comes closest to expressing what you believe... | 0.6446 | 0.1974 |
| Do you believe there is a life after death?... | 0.7016 | -0.8165 |
| Do you think most people would try to take advantage of you ... | 0.7212 | -0.2357 |
| Do you think a person has the right to end his or her own li... | 0.8751 | -0.8165 |
| When a person has a disease that cannot be cured, do you thi... | 0.8895 | -0.8165 |
