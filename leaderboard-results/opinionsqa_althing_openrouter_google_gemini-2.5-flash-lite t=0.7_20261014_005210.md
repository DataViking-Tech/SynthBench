# SynthBench Score Card

**Provider:** althing/openrouter/google/gemini-2.5-flash-lite t=0.7
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 311.9s

## SynthBench Parity Score (SPS)

**SPS: 0.8154 [0.7956, 0.8338]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6924 [0.6596, 0.7266] | ███████░░░ |
| P_rank  Rank-Order | 0.7594 [0.7295, 0.7885] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3076 |
| Median JSD | 0.3313 |
| Mean Kendall's tau | 0.5189 |
| Composite Parity (legacy) | 0.7259 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1639 | +29% |
| random-baseline | 0.6495 | +0.0764 | +12% |

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
| 2017 | 0.6925 | 0.7589 | 0.3075 | 99 |
| 2018 | 0.6876 | 0.8162 | 0.3124 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have you ever taken any gun safety courses such as weapons t... | 0.0028 | 1.0000 |
| Do you think men and women are basically similar or basicall... | 0.0051 | 1.0000 |
| Do you think the following are likely to happen as a result ... | 0.0058 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| If driverless vehicles become widespread, which of the follo... | 0.0231 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How well, if at all, do the following words or phrases descr... | 0.6041 | 0.3586 |
| Do you think it is very likely, somewhat likely, not very li... | 0.6101 | 0.3586 |
| Do you personally know anyone who has lost a job, or had the... | 0.6144 | 0.0000 |
| On a different subject, would you say that society generally... | 0.6715 | -0.2357 |
| How often, if ever, do you listen to gun-oriented podcasts o... | 0.7285 | 0.3162 |
