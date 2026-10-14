# SynthBench Score Card

**Provider:** openrouter/qwen/qwen3.8-flash
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 848.2s

## SynthBench Parity Score (SPS)

**SPS: 0.8582 [0.8409, 0.8728]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7815 [0.7545, 0.8049] | ████████░░ |
| P_rank  Rank-Order | 0.7987 [0.7727, 0.8243] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2185 |
| Median JSD | 0.2168 |
| Mean Kendall's tau | 0.5975 |
| Composite Parity (legacy) | 0.7901 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.2281 | +41% |
| random-baseline | 0.6495 | +0.1406 | +22% |

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
| 2017 | 0.7801 | 0.7975 | 0.2199 | 99 |
| 2018 | 0.9153 | 0.9183 | 0.0847 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| If driverless vehicles become widespread, which of the follo... | 0.0081 | 1.0000 |
| Do you think the following are likely to happen as a result ... | 0.0086 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Have you ever had your pay or hours reduced because your emp... | 0.0333 | 0.7071 |
| Not including in military combat or as part of your job, hav... | 0.0368 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How worried are you, if at all, about the development of dri... | 0.4219 | 0.3162 |
| Do you think men and women are basically similar or basicall... | 0.4466 | 0.0000 |
| Do you think men and women are basically similar or basicall... | 0.4757 | 0.0000 |
| Please consider the following scenario - in the future, robo... | 0.5261 | 0.2357 |
| Do you think men and women are basically similar or basicall... | 0.7490 | 0.0000 |
