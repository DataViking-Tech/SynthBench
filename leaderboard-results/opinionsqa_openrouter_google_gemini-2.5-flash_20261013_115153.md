# SynthBench Score Card

**Provider:** openrouter/google/gemini-2.5-flash
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 179.0s

## SynthBench Parity Score (SPS)

**SPS: 0.8274 [0.8095, 0.8451]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7291 [0.6998, 0.7577] | ███████░░░ |
| P_rank  Rank-Order | 0.7591 [0.7297, 0.7869] | ████████░░ |
| P_refuse Refusal Cal. | 0.9940 [0.9928, 0.9947] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2709 |
| Median JSD | 0.2611 |
| Mean Kendall's tau | 0.5181 |
| Composite Parity (legacy) | 0.7441 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1821 | +32% |
| random-baseline | 0.6495 | +0.0946 | +15% |

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
| 2017 | 0.7295 | 0.7585 | 0.2705 | 99 |
| 2018 | 0.6876 | 0.8162 | 0.3124 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Does anyone else in your household own any guns (not includi... | 0.0098 | 1.0000 |
| Do you personally own any guns (not including air guns, such... | 0.0113 | 1.0000 |
| Do you personally know anyone who has lost a job, or had the... | 0.0119 | 1.0000 |
| Has anyone ever used a gun to threaten or intimidate you or ... | 0.0210 | 1.0000 |
| If driverless vehicles become widespread, which of the follo... | 0.0509 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How much, if at all, do you worry about the following happen... | 0.5762 | 0.2357 |
| On a different subject, would you say that society generally... | 0.5953 | -0.1826 |
| How well, if at all, do the following words or phrases descr... | 0.5986 | 0.3586 |
| How much of a problem was gun violence in the community wher... | 0.6141 | 0.1195 |
| How much do you agree or disagree with the following stateme... | 0.6761 | 0.0000 |
