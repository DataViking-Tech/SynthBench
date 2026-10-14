# SynthBench Score Card

**Provider:** openrouter/openai/gpt-4o
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 336.4s

## SynthBench Parity Score (SPS)

**SPS: 0.8255 [0.8020, 0.8469]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7486 [0.7143, 0.7805] | ███████░░░ |
| P_rank  Rank-Order | 0.7335 [0.6916, 0.7687] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2514 |
| Median JSD | 0.2366 |
| Mean Kendall's tau | 0.4671 |
| Composite Parity (legacy) | 0.7411 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1791 | +32% |
| random-baseline | 0.6495 | +0.0916 | +14% |

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
| 2017 | 0.7530 | 0.7365 | 0.2470 | 99 |
| 2018 | 0.3187 | 0.4402 | 0.6813 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have you ever had your pay or hours reduced because your emp... | 0.0034 | 0.9129 |
| Have you participated in any of these groups during the last... | 0.0091 | 1.0000 |
| Do you think men and women are basically similar or basicall... | 0.0185 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| How often, if ever, do you participate in online discussion ... | 0.0297 | 0.5270 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think it is very likely, somewhat likely, not very li... | 0.6022 | 0.0000 |
| Have you ever been a victim of a violent crime, whether a gu... | 0.6588 | -0.3333 |
| On a different subject, would you say that society generally... | 0.6715 | -0.2357 |
| Please tell us whether you are satisfied or dissatisfied wit... | 0.6813 | -0.1195 |
| Compared to 50 years ago, do you think... | 0.7640 | -0.2357 |
