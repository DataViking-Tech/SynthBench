# SynthBench Score Card

**Provider:** althing/openrouter/anthropic/claude-haiku-5.5
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 487.5s

## SynthBench Parity Score (SPS)

**SPS: 0.8228 [0.8036, 0.8397]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7004 [0.6732, 0.7328] | ███████░░░ |
| P_rank  Rank-Order | 0.7756 [0.7430, 0.8039] | ████████░░ |
| P_refuse Refusal Cal. | 0.9924 [0.9876, 0.9940] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2996 |
| Median JSD | 0.3248 |
| Mean Kendall's tau | 0.5511 |
| Composite Parity (legacy) | 0.7380 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1760 | +31% |
| random-baseline | 0.6495 | +0.0885 | +14% |

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
| 2017 | 0.7018 | 0.7768 | 0.2982 | 99 |
| 2018 | 0.5675 | 0.6581 | 0.4325 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think men and women are basically similar or basicall... | 0.0036 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Thinking about the people you know, including yourself, do y... | 0.0226 | 1.0000 |
| Have you ever had your pay or hours reduced because your emp... | 0.0333 | 0.7071 |
| How often, if ever, do you participate in online discussion ... | 0.0366 | 0.8367 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| If driverless vehicles become widespread, which of the follo... | 0.5482 | 0.0000 |
| How often, if ever, do you visit websites about guns, huntin... | 0.5569 | 0.5976 |
| In the last 12 months, how often did you and your neighbors ... | 0.5608 | 0.3563 |
| How often, if ever, did you use air guns, such as paintball,... | 0.5850 | 0.0000 |
| Compared to 50 years ago, do you think... | 0.7640 | -0.2357 |
