# SynthBench Score Card

**Provider:** althing/anthropic/claude-sonnet-4-6 harness=claude-code
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 2295.4s

## SynthBench Parity Score (SPS)

**SPS: 0.8134 [0.7841, 0.8360]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6939 [0.6530, 0.7314] | ███████░░░ |
| P_rank  Rank-Order | 0.7742 [0.7289, 0.8076] | ████████░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3061 |
| Median JSD | 0.2679 |
| Mean Kendall's tau | 0.5483 |
| Composite Parity (legacy) | 0.7340 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1720 | +31% |
| random-baseline | 0.6495 | +0.0845 | +13% |

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
| Consider a person who believes that Black people are genetic... | 0.0617 | 0.3333 |
| I am going to name an institution in this country. As far as... | 0.0726 | 0.9129 |
| Would you be for or against sex education in the public scho... | 0.0798 | 0.8165 |
| Please tell me whether or not you think it should be possibl... | 0.1067 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Would you say that most of the time people try to be helpful... | 0.6583 | -0.2357 |
| Which statement comes closest to expressing what you believe... | 0.6706 | 0.3563 |
| Do you believe there is a life after death?... | 0.7016 | -0.8165 |
| Do you agree strongly, agree somewhat, neither agree nor dis... | 0.7152 | -0.3464 |
| How often do you attend religious services?... | 0.7321 | 0.2357 |
