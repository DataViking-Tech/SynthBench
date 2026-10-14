# SynthBench Score Card

**Provider:** althing/openrouter/google/gemini-2.5-flash-lite t=1.2
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 354.4s

## SynthBench Parity Score (SPS)

**SPS: 0.8354 [0.8157, 0.8536]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7365 [0.7043, 0.7680] | ███████░░░ |
| P_rank  Rank-Order | 0.7755 [0.7454, 0.8044] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2635 |
| Median JSD | 0.2567 |
| Mean Kendall's tau | 0.5509 |
| Composite Parity (legacy) | 0.7560 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1940 | +35% |
| random-baseline | 0.6495 | +0.1065 | +16% |

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
| 2017 | 0.7353 | 0.7740 | 0.2647 | 99 |
| 2018 | 0.8542 | 0.9183 | 0.1458 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Regardless of whether or not you own a gun, have you ever fi... | 0.0014 | 1.0000 |
| Have you ever taken any gun safety courses such as weapons t... | 0.0045 | 1.0000 |
| Do you think the following are likely to happen as a result ... | 0.0087 | 1.0000 |
| Have you participated in any of these groups during the last... | 0.0135 | 1.0000 |
| Do you think men and women are basically similar or basicall... | 0.0198 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| In the last 12 months, how often did you and your neighbors ... | 0.5417 | 0.0658 |
| How often, if ever, do you listen to gun-oriented podcasts o... | 0.5633 | 0.5976 |
| How well, if at all, do the following words or phrases descr... | 0.5706 | 0.1195 |
| Do you personally know anyone who has lost a job, or had the... | 0.6144 | 0.0000 |
| On a different subject, would you say that society generally... | 0.6715 | -0.2357 |
