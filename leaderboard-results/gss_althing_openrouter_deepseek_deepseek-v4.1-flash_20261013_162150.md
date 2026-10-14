# SynthBench Score Card

**Provider:** althing/openrouter/deepseek/deepseek-v4.1-flash
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 448.7s

## SynthBench Parity Score (SPS)

**SPS: 0.8225 [0.7985, 0.8417]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7100 [0.6810, 0.7409] | ███████░░░ |
| P_rank  Rank-Order | 0.7854 [0.7454, 0.8171] | ████████░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2900 |
| Median JSD | 0.2715 |
| Mean Kendall's tau | 0.5709 |
| Composite Parity (legacy) | 0.7477 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1857 | +33% |
| random-baseline | 0.6495 | +0.0982 | +15% |

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
| Do you favor or oppose the death penalty for persons convict... | 0.0429 | 0.3333 |
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| Would you be for or against sex education in the public scho... | 0.0798 | 0.8165 |
| Please tell me whether or not you think it should be possibl... | 0.1067 | 0.8165 |
| Do you consider the amount of federal income tax which you h... | 0.1175 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How often do you attend religious services?... | 0.5088 | 0.4734 |
| If a man and a woman have sexual relations before marriage, ... | 0.5243 | 0.3586 |
| Generally speaking, do you usually think of yourself as a Re... | 0.5361 | 0.5000 |
| Do you agree strongly, agree somewhat, neither agree nor dis... | 0.5484 | -0.2582 |
| Do you believe there is a life after death?... | 0.7016 | -0.8165 |
