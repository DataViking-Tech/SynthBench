# SynthBench Score Card

**Provider:** althing/openrouter/google/gemini-2.5-flash-lite t=1.8
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 341.6s

## SynthBench Parity Score (SPS)

**SPS: 0.8407 [0.8211, 0.8590]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7507 [0.7197, 0.7824] | ████████░░ |
| P_rank  Rank-Order | 0.7772 [0.7464, 0.8057] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2493 |
| Median JSD | 0.2379 |
| Mean Kendall's tau | 0.5544 |
| Composite Parity (legacy) | 0.7640 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.2020 | +36% |
| random-baseline | 0.6495 | +0.1144 | +18% |

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
| 2017 | 0.7491 | 0.7758 | 0.2509 | 99 |
| 2018 | 0.9083 | 0.9183 | 0.0917 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Has anyone ever used a gun to threaten or intimidate you or ... | 0.0022 | 1.0000 |
| Have you ever taken any gun safety courses such as weapons t... | 0.0029 | 1.0000 |
| Have you participated in any of these groups during the last... | 0.0035 | 1.0000 |
| Do you think the following are likely to happen as a result ... | 0.0133 | 1.0000 |
| If driverless vehicles become widespread, which of the follo... | 0.0157 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Compared to 50 years ago, do you think... | 0.5277 | 0.1826 |
| How well, if at all, do the following words or phrases descr... | 0.5362 | 0.3162 |
| How well, if at all, do the following words or phrases descr... | 0.5855 | 0.1195 |
| Do you personally know anyone who has lost a job, or had the... | 0.6144 | 0.0000 |
| On a different subject, would you say that society generally... | 0.6715 | -0.2357 |
