# SynthBench Score Card

**Provider:** openrouter/google/gemini-2.5-flash-lite
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 125.1s

## SynthBench Parity Score (SPS)

**SPS: 0.8259 [0.8052, 0.8460]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7365 [0.7029, 0.7711] | ███████░░░ |
| P_rank  Rank-Order | 0.7469 [0.7115, 0.7784] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2635 |
| Median JSD | 0.2695 |
| Mean Kendall's tau | 0.4938 |
| Composite Parity (legacy) | 0.7417 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1797 | +32% |
| random-baseline | 0.6495 | +0.0922 | +14% |

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
| 2017 | 0.7370 | 0.7462 | 0.2630 | 99 |
| 2018 | 0.6876 | 0.8162 | 0.3124 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have you ever been a victim of a violent crime, whether a gu... | 0.0023 | 1.0000 |
| Have you participated in any of these groups during the last... | 0.0045 | 1.0000 |
| In the last 12 months, that is since September 2016, have yo... | 0.0119 | 1.0000 |
| Has anyone ever used a gun to threaten or intimidate you or ... | 0.0137 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How enthusiastic are you, if at all, about the development o... | 0.6034 | -0.1195 |
| Would you favor or oppose the following? If people had the o... | 0.6201 | 0.0000 |
| On a different subject, would you say that society generally... | 0.6715 | -0.2357 |
| Do you think it is very likely, somewhat likely, not very li... | 0.7108 | 0.0000 |
| Do you think men and women are basically similar or basicall... | 0.7490 | 0.0000 |
