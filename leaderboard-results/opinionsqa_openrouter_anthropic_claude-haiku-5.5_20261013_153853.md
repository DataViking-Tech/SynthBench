# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-haiku-5.5
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 396.8s

## SynthBench Parity Score (SPS)

**SPS: 0.7814 [0.7540, 0.8037]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7084 [0.6792, 0.7357] | ███████░░░ |
| P_rank  Rank-Order | 0.7154 [0.6777, 0.7476] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9206 [0.8563, 0.9603] | █████████░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2916 |
| Median JSD | 0.2590 |
| Mean Kendall's tau | 0.4307 |
| Composite Parity (legacy) | 0.7119 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1499 | +27% |
| random-baseline | 0.6495 | +0.0623 | +10% |

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
| 2017 | 0.7098 | 0.7159 | 0.2902 | 99 |
| 2018 | 0.5675 | 0.6581 | 0.4325 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Have you ever had your pay or hours reduced because your emp... | 0.0333 | 0.7071 |
| Not including in military combat or as part of your job, hav... | 0.0368 | 0.8165 |
| Have you participated in any of these groups during the last... | 0.0869 | 0.8165 |
| How often, if ever, do you participate in online discussion ... | 0.0893 | 0.6325 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Which of the following statements comes closer to your feeli... | 0.5452 | -0.2357 |
| If driverless vehicles become widespread, which of the follo... | 0.5482 | 0.0000 |
| Do you think men and women are basically similar or basicall... | 0.7490 | 0.0000 |
| Compared to 50 years ago, do you think... | 0.7640 | -0.2357 |
| Thinking about when you were growing up, as far as you know,... | 0.8239 | -0.2357 |
