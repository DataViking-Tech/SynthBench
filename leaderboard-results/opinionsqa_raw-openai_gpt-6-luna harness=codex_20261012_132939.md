# SynthBench Score Card

**Provider:** raw-openai/gpt-6-luna harness=codex
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 3408.1s

## SynthBench Parity Score (SPS)

**SPS: 0.7270 [0.6941, 0.7585]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5843 [0.5245, 0.6383] | ██████░░░░ |
| P_rank  Rank-Order | 0.6024 [0.5550, 0.6510] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4157 |
| Median JSD | 0.3764 |
| Mean Kendall's tau | 0.2049 |
| Composite Parity (legacy) | 0.5934 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0314 | +6% |
| random-baseline | 0.6495 | -0.0561 | -9% |

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
| 2017 | 0.5859 | 0.6029 | 0.4141 | 99 |
| 2018 | 0.4256 | 0.5527 | 0.5744 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| If driverless vehicles become widespread, which of the follo... | 0.0025 | 1.0000 |
| Do you think the following are likely to happen as a result ... | 0.0036 | 1.0000 |
| Do you think the following are likely to happen as a result ... | 0.0158 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Which of the following statements best describes how you fee... | 0.0222 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Does anyone else in your household own any guns (not includi... | 0.9440 | -0.8165 |
| Has anyone ever used a gun to threaten or intimidate you or ... | 0.9828 | -0.8165 |
| How much of a problem was gun violence in the community wher... | 0.9838 | -0.6325 |
| How often, if ever, did you use air guns, such as paintball,... | 0.9838 | -0.6325 |
| Have you ever been told by a doctor or other health professi... | 0.9903 | -0.8165 |
