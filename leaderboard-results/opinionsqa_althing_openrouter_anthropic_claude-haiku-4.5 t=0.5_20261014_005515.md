# SynthBench Score Card

**Provider:** althing/openrouter/anthropic/claude-haiku-4.5 t=0.5
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 682.9s

## SynthBench Parity Score (SPS)

**SPS: 0.8210 [0.8015, 0.8385]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6975 [0.6665, 0.7317] | ███████░░░ |
| P_rank  Rank-Order | 0.7714 [0.7396, 0.7969] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3025 |
| Median JSD | 0.3273 |
| Mean Kendall's tau | 0.5427 |
| Composite Parity (legacy) | 0.7344 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1724 | +31% |
| random-baseline | 0.6495 | +0.0849 | +13% |

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
| 2017 | 0.6988 | 0.7725 | 0.3012 | 99 |
| 2018 | 0.5675 | 0.6581 | 0.4325 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| In the last 12 months, that is since September 2016, have yo... | 0.0186 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Have you participated in any of these groups during the last... | 0.0226 | 1.0000 |
| Have you ever had your pay or hours reduced because your emp... | 0.0333 | 0.7071 |
| Not including in military combat or as part of your job, hav... | 0.0368 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How often, if ever, did you use air guns, such as paintball,... | 0.5850 | 0.0000 |
| How often, if ever, do you visit websites about guns, huntin... | 0.6507 | 0.3162 |
| On a different subject, would you say that society generally... | 0.6715 | -0.2357 |
| In the last 12 months, how often did you and your neighbors ... | 0.7292 | 0.0000 |
| Compared to 50 years ago, do you think... | 0.7640 | -0.2357 |
