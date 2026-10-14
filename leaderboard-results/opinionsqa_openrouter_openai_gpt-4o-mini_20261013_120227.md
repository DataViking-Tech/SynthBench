# SynthBench Score Card

**Provider:** openrouter/openai/gpt-4o-mini
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 812.4s

## SynthBench Parity Score (SPS)

**SPS: 0.8165 [0.7923, 0.8375]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7024 [0.6670, 0.7384] | ███████░░░ |
| P_rank  Rank-Order | 0.7529 [0.7175, 0.7876] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2976 |
| Median JSD | 0.3063 |
| Mean Kendall's tau | 0.5058 |
| Composite Parity (legacy) | 0.7276 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1656 | +29% |
| random-baseline | 0.6495 | +0.0781 | +12% |

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
| 2017 | 0.7025 | 0.7522 | 0.2975 | 99 |
| 2018 | 0.6876 | 0.8162 | 0.3124 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| In the last 12 months, that is since September 2016, have yo... | 0.0016 | 1.0000 |
| Do you think men and women are basically similar or basicall... | 0.0125 | 1.0000 |
| Regardless of whether or not you own a gun, have you ever fi... | 0.0131 | 1.0000 |
| Have you ever taken any gun safety courses such as weapons t... | 0.0215 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How much do you agree or disagree with the following stateme... | 0.6761 | 0.0000 |
| How enthusiastic are you, if at all, about the development o... | 0.7223 | -0.3162 |
| Do you think men and women are basically similar or basicall... | 0.7490 | 0.0000 |
| Compared to 50 years ago, do you think... | 0.7640 | -0.2357 |
| How much of a problem was gun violence in the community wher... | 0.8343 | -0.3586 |
