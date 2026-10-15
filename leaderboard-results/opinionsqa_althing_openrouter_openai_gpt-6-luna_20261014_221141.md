# SynthBench Score Card

**Provider:** althing/openrouter/openai/gpt-6-luna
**Dataset:** opinionsqa (684 questions)
**Samples per question:** 30
**Elapsed:** 16470.7s

## SynthBench Parity Score (SPS)

**SPS: 0.8299 [0.8225, 0.8367]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7176 [0.7061, 0.7288] | ███████░░░ |
| P_rank  Rank-Order | 0.7840 [0.7723, 0.7956] | ████████░░ |
| P_refuse Refusal Cal. | 0.9881 [0.9819, 0.9898] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2824 |
| Median JSD | 0.2894 |
| Mean Kendall's tau | 0.5679 |
| Composite Parity (legacy) | 0.7508 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1888 | +34% |
| random-baseline | 0.6495 | +0.1013 | +16% |

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
| 2017 | 0.7225 | 0.7751 | 0.2775 | 99 |
| 2018 | 0.7286 | 0.7994 | 0.2714 | 124 |
| 2019 | 0.7222 | 0.7840 | 0.2778 | 218 |
| 2020 | 0.7194 | 0.7846 | 0.2806 | 101 |
| 2022 | 0.6964 | 0.7762 | 0.3036 | 142 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| If driverless vehicles become widespread, which of the follo... | 0.0043 | 1.0000 |
| All in all, do you favor or oppose the use of animals in sci... | 0.0078 | 0.8165 |
| How important, if at all, do you think a good work ethic is ... | 0.0088 | 0.9129 |
| Do you use twitter?... | 0.0108 | 1.0000 |
| Thinking about the people you know, including yourself, do y... | 0.0124 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Who do you think has the most responsibility to reduce the a... | 0.6772 | 0.2582 |
| Thinking about when you were growing up, as far as you know,... | 0.6841 | -0.1826 |
| Please indicate whether or not each has happened to you beca... | 0.7562 | -0.3333 |
| Do you think of yourself as... | 0.7606 | -0.0772 |
| Now thinking about your own experiences have you ever person... | 0.7906 | -0.8165 |
