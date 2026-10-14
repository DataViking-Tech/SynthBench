# SynthBench Score Card

**Provider:** openrouter/qwen/qwen3.8-flash
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 990.9s

## SynthBench Parity Score (SPS)

**SPS: 0.8598 [0.8430, 0.8765]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7837 [0.7577, 0.8076] | ████████░░ |
| P_rank  Rank-Order | 0.8015 [0.7716, 0.8289] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2163 |
| Median JSD | 0.2105 |
| Mean Kendall's tau | 0.6030 |
| Composite Parity (legacy) | 0.7926 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.2306 | +41% |
| random-baseline | 0.6495 | +0.1431 | +22% |

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
| 2017 | 0.7823 | 0.8003 | 0.2177 | 99 |
| 2018 | 0.9238 | 0.9183 | 0.0762 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think the following are likely to happen as a result ... | 0.0052 | 1.0000 |
| Which of the following statements best describes how you fee... | 0.0101 | 0.3333 |
| Do you think the following are likely to happen as a result ... | 0.0195 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Have you ever had your pay or hours reduced because your emp... | 0.0333 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| In the last 12 months, how often did you talk with any of yo... | 0.4044 | 0.3290 |
| Do you think men and women are basically similar or basicall... | 0.4466 | 0.0000 |
| Do you think men and women are basically similar or basicall... | 0.4757 | 0.0000 |
| Please consider the following scenario - in the future, robo... | 0.5261 | 0.2357 |
| Do you think men and women are basically similar or basicall... | 0.7490 | 0.0000 |
