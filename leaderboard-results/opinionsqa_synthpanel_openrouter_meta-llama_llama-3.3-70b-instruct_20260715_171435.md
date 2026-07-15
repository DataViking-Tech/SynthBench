# SynthBench Score Card

**Provider:** synthpanel/openrouter/meta-llama/llama-3.3-70b-instruct
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 15
**Elapsed:** 178.9s

## SynthBench Parity Score (SPS)

**SPS: 0.7909 [0.7670, 0.8108]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6954 [0.6676, 0.7256] | ███████░░░ |
| P_rank  Rank-Order | 0.7425 [0.7126, 0.7720] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9348 [0.8933, 0.9597] | █████████░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3046 |
| Median JSD | 0.2974 |
| Mean Kendall's tau | 0.4851 |
| Composite Parity (legacy) | 0.7190 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1570 | +28% |
| random-baseline | 0.6495 | +0.0695 | +11% |

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
| 2017 | 0.6967 | 0.7434 | 0.3033 | 99 |
| 2018 | 0.5675 | 0.6581 | 0.4325 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you feel that people in your local community tend to look... | 0.0109 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Not including in military combat or as part of your job, hav... | 0.0368 | 0.8165 |
| Thinking about when you were growing up, as far as you know,... | 0.0519 | 0.5477 |
| Do you think men and women are basically similar or basicall... | 0.0582 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How often, if ever, did you use air guns, such as paintball,... | 0.5850 | 0.0000 |
| Do you personally know anyone who has lost a job, or had the... | 0.6144 | 0.0000 |
| Have you participated in any of these groups during the last... | 0.6340 | 0.0000 |
| Have you participated in any of these groups during the last... | 0.6707 | 0.0000 |
| On a different subject, would you say that society generally... | 0.6715 | -0.2357 |
