# SynthBench Score Card

**Provider:** althing/openrouter/google/gemini-2.5-flash-lite t=2.0
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 328.7s

## SynthBench Parity Score (SPS)

**SPS: 0.8406 [0.8210, 0.8585]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7556 [0.7232, 0.7874] | ████████░░ |
| P_rank  Rank-Order | 0.7721 [0.7424, 0.8014] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2444 |
| Median JSD | 0.2350 |
| Mean Kendall's tau | 0.5442 |
| Composite Parity (legacy) | 0.7638 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.2018 | +36% |
| random-baseline | 0.6495 | +0.1143 | +18% |

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
| 2017 | 0.7541 | 0.7706 | 0.2459 | 99 |
| 2018 | 0.8991 | 0.9183 | 0.1009 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Has anyone ever used a gun to threaten or intimidate you or ... | 0.0022 | 1.0000 |
| Do you think men and women are basically similar or basicall... | 0.0035 | 1.0000 |
| Have you participated in any of these groups during the last... | 0.0035 | 1.0000 |
| In the last 12 months, that is since September 2016, have yo... | 0.0040 | 1.0000 |
| Have you ever taken any gun safety courses such as weapons t... | 0.0046 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please consider the following scenario - in the future, robo... | 0.5261 | 0.2357 |
| How well, if at all, do the following words or phrases descr... | 0.5362 | 0.3162 |
| How well, if at all, do the following words or phrases descr... | 0.5770 | 0.1195 |
| Do you personally know anyone who has lost a job, or had the... | 0.6144 | 0.0000 |
| On a different subject, would you say that society generally... | 0.6715 | -0.2357 |
