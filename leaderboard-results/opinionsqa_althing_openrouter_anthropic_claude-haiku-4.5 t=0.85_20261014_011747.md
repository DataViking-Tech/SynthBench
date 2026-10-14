# SynthBench Score Card

**Provider:** althing/openrouter/anthropic/claude-haiku-4.5 t=0.85
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 660.1s

## SynthBench Parity Score (SPS)

**SPS: 0.8262 [0.8084, 0.8427]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7090 [0.6802, 0.7422] | ███████░░░ |
| P_rank  Rank-Order | 0.7754 [0.7464, 0.7999] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2910 |
| Median JSD | 0.3130 |
| Mean Kendall's tau | 0.5508 |
| Composite Parity (legacy) | 0.7422 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1802 | +32% |
| random-baseline | 0.6495 | +0.0927 | +14% |

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
| 2017 | 0.7096 | 0.7751 | 0.2904 | 99 |
| 2018 | 0.6499 | 0.7988 | 0.3501 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| In the last 12 months, that is since September 2016, have yo... | 0.0068 | 1.0000 |
| Do you think men and women are basically similar or basicall... | 0.0142 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| How often, if ever, do you participate in online discussion ... | 0.0232 | 0.8367 |
| How much have you seen or heard about the effort to develop ... | 0.0280 | 0.5477 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How often, if ever, do you visit websites about guns, huntin... | 0.5569 | 0.5976 |
| How often, if ever, did you use air guns, such as paintball,... | 0.5850 | 0.0000 |
| In the last 12 months, how often did you and your neighbors ... | 0.6589 | 0.1974 |
| Compared to 50 years ago, do you think... | 0.6684 | 0.1826 |
| On a different subject, would you say that society generally... | 0.6715 | -0.2357 |
