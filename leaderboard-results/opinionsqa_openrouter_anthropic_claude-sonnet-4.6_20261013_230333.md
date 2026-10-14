# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-sonnet-4.6
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 543.8s

## SynthBench Parity Score (SPS)

**SPS: 0.8079 [0.7881, 0.8268]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6759 [0.6434, 0.7094] | ███████░░░ |
| P_rank  Rank-Order | 0.7536 [0.7202, 0.7840] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3241 |
| Median JSD | 0.3245 |
| Mean Kendall's tau | 0.5072 |
| Composite Parity (legacy) | 0.7148 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1528 | +27% |
| random-baseline | 0.6495 | +0.0653 | +10% |

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
| 2017 | 0.6758 | 0.7530 | 0.3242 | 99 |
| 2018 | 0.6876 | 0.8162 | 0.3124 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Have you ever had your pay or hours reduced because your emp... | 0.0333 | 0.7071 |
| Not including in military combat or as part of your job, hav... | 0.0368 | 0.8165 |
| Do you think men and women are basically similar or basicall... | 0.0582 | 0.8165 |
| Have you participated in any of these groups during the last... | 0.0869 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| In the last 12 months, how often did you talk with any of yo... | 0.6598 | 0.1974 |
| On a different subject, would you say that society generally... | 0.6715 | -0.2357 |
| Would you favor or oppose the following? If the federal gove... | 0.6760 | 0.0000 |
| How likely is it that, at some point in your life, you will ... | 0.6766 | 0.0861 |
| The next question is about local elections, such as for mayo... | 0.7286 | 0.0000 |
