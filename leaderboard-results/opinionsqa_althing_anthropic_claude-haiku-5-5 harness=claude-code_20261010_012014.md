# SynthBench Score Card

**Provider:** althing/anthropic/claude-haiku-5-5 harness=claude-code
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 1180.7s

## SynthBench Parity Score (SPS)

**SPS: 0.7881 [0.7527, 0.8108]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7143 [0.6758, 0.7475] | ███████░░░ |
| P_rank  Rank-Order | 0.7508 [0.7084, 0.7868] | ████████░░ |
| P_refuse Refusal Cal. | 0.8991 [0.8612, 0.9321] | █████████░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2857 |
| Median JSD | 0.2538 |
| Mean Kendall's tau | 0.5016 |
| Composite Parity (legacy) | 0.7326 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1706 | +30% |
| random-baseline | 0.6495 | +0.0830 | +13% |

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
| 2017 | 0.7158 | 0.7517 | 0.2842 | 99 |
| 2018 | 0.5675 | 0.6581 | 0.4325 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| How well, if at all, do the following words or phrases descr... | 0.0253 | 0.8367 |
| Have you participated in any of these groups during the last... | 0.0338 | 1.0000 |
| Do you think men and women are basically similar or basicall... | 0.0373 | 0.3333 |
| Have you ever had your pay or hours reduced because your emp... | 0.0464 | 0.1826 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| In the last 12 months, how often did you talk with any of yo... | 0.5804 | -0.2333 |
| How much of a problem was gun violence in the community wher... | 0.8215 | 0.0000 |
| How well, if at all, do the following words or phrases descr... | 0.8690 | -0.3162 |
| How well, if at all, do the following words or phrases descr... | 0.8998 | -0.5976 |
| Which of the following statements comes closer to your feeli... | 0.9357 | -0.7071 |
