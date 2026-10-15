# SynthBench Score Card

**Provider:** althing/openrouter/meta-llama/llama-3.3-70b-instruct
**Dataset:** opinionsqa (684 questions)
**Samples per question:** 30
**Elapsed:** 11253.3s

## SynthBench Parity Score (SPS)

**SPS: 0.8087 [0.8019, 0.8158]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6747 [0.6639, 0.6858] | ███████░░░ |
| P_rank  Rank-Order | 0.7620 [0.7493, 0.7732] | ████████░░ |
| P_refuse Refusal Cal. | 0.9895 [0.9885, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3253 |
| Median JSD | 0.3281 |
| Mean Kendall's tau | 0.5240 |
| Composite Parity (legacy) | 0.7184 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1564 | +28% |
| random-baseline | 0.6495 | +0.0688 | +11% |

## What These Scores Mean

- **SPS** (SynthBench Parity Score): The overall score — average of all metrics. 0 = random noise, 1 = indistinguishable from real humans.
- **P_dist** (Distributional Parity): How closely does the AI's answer distribution match real humans? If 60% of humans say 'yes' and the AI says 'yes' 60% of the time, that's a perfect match. 0 = completely different, 1 = identical distributions.
- **P_rank** (Rank-Order Parity): Does the AI get the preference ordering right? If humans prefer A > B > C, does the AI agree — even if the exact percentages differ? 0 = reversed ordering, 1 = perfect agreement.
- **P_refuse** (Refusal Calibration): Does the AI refuse to answer at appropriate rates? Humans sometimes decline sensitive questions. An AI that never refuses, or refuses too often, is miscalibrated. 0 = rates completely off, 1 = perfect match.
- **P_cond** (Conditioning Fidelity): When told 'respond as a 65-year-old conservative,' does the AI actually shift its answers? Higher = better demographic role-playing. (When available.)
- **P_sub** (Subgroup Consistency): Is the AI equally accurate across all demographics, or does it nail some groups and miss others? (When available.)

## Temporal Breakdown (by Survey Year)

Scores stratified by Pew ATP survey wave year. Rising P_dist in recent years may indicate training-data contamination.

| Year | P_dist | P_rank | Mean JSD | Questions |
|------|--------|--------|----------|-----------|
| 2017 | 0.6777 | 0.7398 | 0.3223 | 99 |
| 2018 | 0.6668 | 0.7245 | 0.3332 | 124 |
| 2019 | 0.6845 | 0.7789 | 0.3155 | 218 |
| 2020 | 0.6667 | 0.7671 | 0.3333 | 101 |
| 2022 | 0.6703 | 0.7806 | 0.3297 | 142 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How do you feel about the average American's ability to reco... | 0.0065 | 1.0000 |
| Please indicate whether or not each has happened to you beca... | 0.0116 | 1.0000 |
| Please indicate whether or not each has happened to you beca... | 0.0139 | 1.0000 |
| How do you feel about the average American's ability to reco... | 0.0187 | 1.0000 |
| Next, please think about the leadership styles of people in ... | 0.0199 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have you or anyone in your household received unemployment b... | 0.7008 | 0.3333 |
| Which of the following, if any, do you restrict or limit eat... | 0.7214 | -1.0000 |
| By 2050, do you expect that people who are married will be... | 0.7378 | -0.2357 |
| Do you think same-sex marriages being legal in the U.S. is g... | 0.7501 | -0.3464 |
| Thinking about the adults in your life, who is the person yo... | 0.7800 | 0.2485 |
