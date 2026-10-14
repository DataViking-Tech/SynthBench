# SynthBench Score Card

**Provider:** althing/openrouter/qwen/qwen3.8-flash
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 1075.7s

## SynthBench Parity Score (SPS)

**SPS: 0.8661 [0.8476, 0.8813]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7859 [0.7591, 0.8119] | ████████░░ |
| P_rank  Rank-Order | 0.8181 [0.7874, 0.8443] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2141 |
| Median JSD | 0.1979 |
| Mean Kendall's tau | 0.6361 |
| Composite Parity (legacy) | 0.8020 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.2400 | +43% |
| random-baseline | 0.6495 | +0.1525 | +23% |

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
| 2017 | 0.7864 | 0.8183 | 0.2136 | 99 |
| 2018 | 0.7391 | 0.7988 | 0.2609 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Thinking about the people you know, including yourself, do y... | 0.0018 | 1.0000 |
| Regardless of whether or not you own a gun, have you ever fi... | 0.0027 | 1.0000 |
| Do you think the following are likely to happen as a result ... | 0.0166 | 0.3333 |
| Compared to 50 years ago, do you think... | 0.0192 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think the following will or will not happen in the ne... | 0.4470 | 0.3162 |
| Do you think men and women are basically similar or basicall... | 0.4757 | 0.0000 |
| The next question is about local elections, such as for mayo... | 0.5062 | 0.3162 |
| On a different subject, would you say that society generally... | 0.5129 | -0.1826 |
| Which of the following statements comes closer to your feeli... | 0.5266 | -0.5477 |
