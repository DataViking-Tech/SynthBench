# SynthBench Score Card

**Provider:** althing/openrouter/meta-llama/llama-3.3-70b-instruct
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 328.0s

## SynthBench Parity Score (SPS)

**SPS: 0.8139 [0.7907, 0.8340]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6874 [0.6473, 0.7214] | ███████░░░ |
| P_rank  Rank-Order | 0.7824 [0.7453, 0.8135] | ████████░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3126 |
| Median JSD | 0.2817 |
| Mean Kendall's tau | 0.5648 |
| Composite Parity (legacy) | 0.7349 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1729 | +31% |
| random-baseline | 0.6495 | +0.0854 | +13% |

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
| I am going to name an institution in this country. As far as... | 0.0436 | 0.5477 |
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| Would you be for or against sex education in the public scho... | 0.0798 | 0.8165 |
| Do you believe there is a life after death?... | 0.0841 | 0.3333 |
| Please tell me whether or not you think it should be possibl... | 0.1067 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How often do you attend religious services?... | 0.6390 | 0.0745 |
| Would you say that most of the time people try to be helpful... | 0.6583 | -0.2357 |
| What is your opinion about a married person having sexual re... | 0.6656 | 0.3162 |
| Do you agree strongly, agree somewhat, neither agree nor dis... | 0.7077 | -0.1155 |
| Generally speaking, would you say that most people can be tr... | 0.7427 | -0.2357 |
