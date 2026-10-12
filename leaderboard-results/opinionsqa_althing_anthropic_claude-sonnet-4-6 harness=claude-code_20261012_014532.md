# SynthBench Score Card

**Provider:** althing/anthropic/claude-sonnet-4-6 harness=claude-code
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 3019.9s

## SynthBench Parity Score (SPS)

**SPS: 0.8115 [0.7915, 0.8295]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6809 [0.6488, 0.7137] | ███████░░░ |
| P_rank  Rank-Order | 0.7595 [0.7275, 0.7895] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3191 |
| Median JSD | 0.3248 |
| Mean Kendall's tau | 0.5190 |
| Composite Parity (legacy) | 0.7202 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1582 | +28% |
| random-baseline | 0.6495 | +0.0707 | +11% |

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
| 2017 | 0.6791 | 0.7579 | 0.3209 | 99 |
| 2018 | 0.8542 | 0.9183 | 0.1458 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| If driverless vehicles become widespread, which of the follo... | 0.0157 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Do you think men and women are basically similar or basicall... | 0.0241 | 1.0000 |
| Have you ever had your pay or hours reduced because your emp... | 0.0333 | 0.7071 |
| Not including in military combat or as part of your job, hav... | 0.0368 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How often, if ever, do you visit websites about guns, huntin... | 0.6507 | 0.3162 |
| On a different subject, would you say that society generally... | 0.6715 | -0.2357 |
| How often, if ever, do you attend gun shows... | 0.6877 | 0.3162 |
| How often, if ever, do you participate in online discussion ... | 0.7219 | 0.3162 |
| Do you think it is very likely, somewhat likely, not very li... | 0.7404 | -0.3162 |
