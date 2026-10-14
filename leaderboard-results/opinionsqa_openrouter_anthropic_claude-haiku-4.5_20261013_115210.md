# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-haiku-4.5
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 196.4s

## SynthBench Parity Score (SPS)

**SPS: 0.7646 [0.7319, 0.7909]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6726 [0.6370, 0.7089] | ███████░░░ |
| P_rank  Rank-Order | 0.7202 [0.6804, 0.7517] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9009 [0.8359, 0.9412] | █████████░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3274 |
| Median JSD | 0.3267 |
| Mean Kendall's tau | 0.4405 |
| Composite Parity (legacy) | 0.6964 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1344 | +24% |
| random-baseline | 0.6495 | +0.0469 | +7% |

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
| 2017 | 0.6725 | 0.7219 | 0.3275 | 99 |
| 2018 | 0.6845 | 0.5598 | 0.3155 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Have you ever had your pay or hours reduced because your emp... | 0.0333 | 0.7071 |
| Not including in military combat or as part of your job, hav... | 0.0368 | 0.8165 |
| If driverless vehicles become widespread, which of the follo... | 0.0806 | 1.0000 |
| Have you participated in any of these groups during the last... | 0.0869 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| On a different subject, would you say that society generally... | 0.6715 | -0.2357 |
| Have you ever personally experienced discrimination or been ... | 0.7603 | -0.3333 |
| Compared to 50 years ago, do you think... | 0.7640 | -0.2357 |
| The next question is about local elections, such as for mayo... | 0.8534 | -0.5976 |
| Do you feel that people in your local community tend to look... | 0.9279 | -0.8165 |
