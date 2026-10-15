# SynthBench Score Card

**Provider:** althing/openrouter/anthropic/claude-haiku-5.5
**Dataset:** opinionsqa (684 questions)
**Samples per question:** 30
**Elapsed:** 10760.7s

## SynthBench Parity Score (SPS)

**SPS: 0.8146 [0.8073, 0.8221]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6892 [0.6778, 0.6997] | ███████░░░ |
| P_rank  Rank-Order | 0.7688 [0.7561, 0.7810] | ████████░░ |
| P_refuse Refusal Cal. | 0.9859 [0.9801, 0.9882] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3108 |
| Median JSD | 0.3188 |
| Mean Kendall's tau | 0.5375 |
| Composite Parity (legacy) | 0.7290 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1670 | +30% |
| random-baseline | 0.6495 | +0.0795 | +12% |

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
| 2017 | 0.7056 | 0.7689 | 0.2944 | 99 |
| 2018 | 0.6812 | 0.7511 | 0.3188 | 124 |
| 2019 | 0.6986 | 0.7767 | 0.3014 | 218 |
| 2020 | 0.7091 | 0.8000 | 0.2909 | 101 |
| 2022 | 0.6563 | 0.7496 | 0.3437 | 142 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you currently have enough income to lead the kind of life... | 0.0014 | 0.8165 |
| Are colleges and universities having a positive or negative ... | 0.0095 | 1.0000 |
| Do you think men and women are basically similar or basicall... | 0.0125 | 1.0000 |
| Do you think changing a baby's genetic characteristics to re... | 0.0179 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| When it comes to people who have immigrated to the U.S illeg... | 0.6979 | -0.3586 |
| Do you think abortion should be... | 0.7145 | -0.3333 |
| Which of the following, if any, do you restrict or limit eat... | 0.7214 | -1.0000 |
| Compared to 50 years ago, do you think... | 0.7640 | -0.2357 |
| If you had to choose, would you rather have... | 0.8483 | -0.3333 |
