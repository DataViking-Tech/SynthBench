# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-haiku-5.5
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 401.4s

## SynthBench Parity Score (SPS)

**SPS: 0.7127 [0.6636, 0.7505]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6514 [0.6053, 0.6893] | ███████░░░ |
| P_rank  Rank-Order | 0.6893 [0.6452, 0.7271] | ███████░░░ |
| P_refuse Refusal Cal. | 0.7972 [0.7136, 0.8602] | ████████░░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3486 |
| Median JSD | 0.3267 |
| Mean Kendall's tau | 0.3786 |
| Composite Parity (legacy) | 0.6704 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1084 | +19% |
| random-baseline | 0.6495 | +0.0209 | +3% |

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
| 2017 | 0.6523 | 0.6918 | 0.3477 | 99 |
| 2018 | 0.5635 | 0.4402 | 0.4365 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| How well, if at all, do the following words or phrases descr... | 0.0322 | 0.8367 |
| Have you ever had your pay or hours reduced because your emp... | 0.0333 | 0.7071 |
| Not including in military combat or as part of your job, hav... | 0.0368 | 0.8165 |
| How often, if ever, do you participate in online discussion ... | 0.0893 | 0.6325 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How well, if at all, do the following words or phrases descr... | 0.8690 | -0.3162 |
| How well, if at all, do the following words or phrases descr... | 0.9118 | -0.3162 |
| Have you participated in any of these groups during the last... | 0.9722 | -0.8165 |
| How much of a problem was gun violence in the community wher... | 0.9838 | -0.6325 |
| In the last 12 months, that is since September 2016, have yo... | 0.9858 | -0.8165 |
