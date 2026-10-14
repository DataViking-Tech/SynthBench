# SynthBench Score Card

**Provider:** althing/openrouter/google/gemini-3.5-flash-lite
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 274.9s

## SynthBench Parity Score (SPS)

**SPS: 0.8146 [0.7856, 0.8369]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6957 [0.6572, 0.7326] | ███████░░░ |
| P_rank  Rank-Order | 0.7759 [0.7301, 0.8102] | ████████░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3043 |
| Median JSD | 0.2810 |
| Mean Kendall's tau | 0.5518 |
| Composite Parity (legacy) | 0.7358 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1738 | +31% |
| random-baseline | 0.6495 | +0.0863 | +13% |

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
| Do you favor or oppose the death penalty for persons convict... | 0.0225 | 1.0000 |
| Do you happen to have in your home or garage any guns or rev... | 0.0379 | 0.9129 |
| Consider a person who believes that Black people are genetic... | 0.0478 | 0.3333 |
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| Please tell me whether or not you think it should be possibl... | 0.0728 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Would you say that most of the time people try to be helpful... | 0.6583 | -0.2357 |
| Which statement comes closest to expressing what you believe... | 0.6706 | 0.3563 |
| Do you believe there is a life after death?... | 0.7016 | -0.8165 |
| Do you agree strongly, agree somewhat, neither agree nor dis... | 0.7152 | -0.3464 |
| Do you think most people would try to take advantage of you ... | 0.7212 | -0.2357 |
