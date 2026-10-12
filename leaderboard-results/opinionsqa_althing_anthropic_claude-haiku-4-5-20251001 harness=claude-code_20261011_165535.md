# SynthBench Score Card

**Provider:** althing/anthropic/claude-haiku-4-5-20251001 harness=claude-code
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 4724.3s

## SynthBench Parity Score (SPS)

**SPS: 0.8287 [0.8044, 0.8479]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7488 [0.7187, 0.7773] | ███████░░░ |
| P_rank  Rank-Order | 0.7954 [0.7654, 0.8236] | ████████░░ |
| P_refuse Refusal Cal. | 0.9420 [0.8972, 0.9673] | █████████░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2512 |
| Median JSD | 0.2590 |
| Mean Kendall's tau | 0.5908 |
| Composite Parity (legacy) | 0.7721 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.2101 | +37% |
| random-baseline | 0.6495 | +0.1226 | +19% |

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
| 2017 | 0.7493 | 0.7954 | 0.2507 | 99 |
| 2018 | 0.7002 | 0.7988 | 0.2998 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have you ever personally experienced discrimination or been ... | 0.0027 | 1.0000 |
| Have you participated in any of these groups during the last... | 0.0043 | 1.0000 |
| If driverless vehicles become widespread, which of the follo... | 0.0056 | 1.0000 |
| Do you think men and women are basically similar or basicall... | 0.0208 | 0.8165 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How much of a problem was gun violence in the community wher... | 0.4964 | 0.3586 |
| The next question is about local elections, such as for mayo... | 0.5062 | 0.3162 |
| How likely is it that, at some point in your life, you will ... | 0.5318 | 0.3464 |
| Have you participated in any of these groups during the last... | 0.5569 | 0.0000 |
| On a different subject, would you say that society generally... | 0.6715 | -0.2357 |
