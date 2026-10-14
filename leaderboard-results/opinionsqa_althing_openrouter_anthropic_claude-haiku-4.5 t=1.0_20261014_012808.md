# SynthBench Score Card

**Provider:** althing/openrouter/anthropic/claude-haiku-4.5 t=1.0
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 617.0s

## SynthBench Parity Score (SPS)

**SPS: 0.8302 [0.8128, 0.8469]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7144 [0.6866, 0.7458] | ███████░░░ |
| P_rank  Rank-Order | 0.7820 [0.7523, 0.8079] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2856 |
| Median JSD | 0.3197 |
| Mean Kendall's tau | 0.5640 |
| Composite Parity (legacy) | 0.7482 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1862 | +33% |
| random-baseline | 0.6495 | +0.0987 | +15% |

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
| 2017 | 0.7146 | 0.7818 | 0.2854 | 99 |
| 2018 | 0.7002 | 0.7988 | 0.2998 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have you participated in any of these groups during the last... | 0.0152 | 1.0000 |
| In the last 12 months, that is since September 2016, have yo... | 0.0162 | 1.0000 |
| How much have you seen or heard about the effort to develop ... | 0.0198 | 0.9129 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| How often, if ever, do you listen to gun-oriented podcasts o... | 0.0320 | 0.8367 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How likely is it that, at some point in your life, you will ... | 0.5318 | 0.3464 |
| How well, if at all, do the following words or phrases descr... | 0.5362 | 0.3162 |
| How often, if ever, did you use air guns, such as paintball,... | 0.5850 | 0.0000 |
| On a different subject, would you say that society generally... | 0.6715 | -0.2357 |
| Compared to 50 years ago, do you think... | 0.7640 | -0.2357 |
