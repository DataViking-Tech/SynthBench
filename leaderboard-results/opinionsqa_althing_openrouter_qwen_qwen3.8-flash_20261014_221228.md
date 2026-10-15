# SynthBench Score Card

**Provider:** althing/openrouter/qwen/qwen3.8-flash
**Dataset:** opinionsqa (684 questions)
**Samples per question:** 30
**Elapsed:** 16517.0s

## SynthBench Parity Score (SPS)

**SPS: 0.8650 [0.8588, 0.8708]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7817 [0.7720, 0.7910] | ████████░░ |
| P_rank  Rank-Order | 0.8239 [0.8117, 0.8335] | ████████░░ |
| P_refuse Refusal Cal. | 0.9895 [0.9885, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2183 |
| Median JSD | 0.2106 |
| Mean Kendall's tau | 0.6477 |
| Composite Parity (legacy) | 0.8028 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.2408 | +43% |
| random-baseline | 0.6495 | +0.1533 | +24% |

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
| 2017 | 0.7954 | 0.8234 | 0.2046 | 99 |
| 2018 | 0.7977 | 0.8187 | 0.2023 | 124 |
| 2019 | 0.7736 | 0.8348 | 0.2264 | 218 |
| 2020 | 0.8132 | 0.8447 | 0.1868 | 101 |
| 2022 | 0.7484 | 0.7971 | 0.2516 | 142 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Which of the following, if any, do you restrict or limit eat... | 0.0001 | 1.0000 |
| Which of the following, if any, do you restrict or limit eat... | 0.0002 | 1.0000 |
| Which of the following, if any, do you restrict or limit eat... | 0.0009 | 1.0000 |
| Do you regularly wear a smart watch or a wearable fitness tr... | 0.0016 | 1.0000 |
| How important, if at all, do you think knowing how to get al... | 0.0037 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think greater social acceptance of people who are tra... | 0.5556 | 0.0861 |
| Would you say China is doing a good or bad job dealing with ... | 0.6030 | 0.1195 |
| Which of the following, if any, do you restrict or limit eat... | 0.6205 | -1.0000 |
| Do you think an increase in the number of guns in the U.S. i... | 0.6319 | 0.1155 |
| Do you think the government of China respects the personal f... | 0.6528 | 0.0000 |
