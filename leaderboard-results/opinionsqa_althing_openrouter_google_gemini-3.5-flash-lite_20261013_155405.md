# SynthBench Score Card

**Provider:** althing/openrouter/google/gemini-3.5-flash-lite
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 266.3s

## SynthBench Parity Score (SPS)

**SPS: 0.8394 [0.8212, 0.8566]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7344 [0.7047, 0.7633] | ███████░░░ |
| P_rank  Rank-Order | 0.7894 [0.7585, 0.8163] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2656 |
| Median JSD | 0.2575 |
| Mean Kendall's tau | 0.5788 |
| Composite Parity (legacy) | 0.7619 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1999 | +36% |
| random-baseline | 0.6495 | +0.1124 | +17% |

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
| 2017 | 0.7349 | 0.7891 | 0.2651 | 99 |
| 2018 | 0.6876 | 0.8162 | 0.3124 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| If driverless vehicles become widespread, which of the follo... | 0.0019 | 1.0000 |
| If driverless vehicles become widespread, which of the follo... | 0.0187 | 1.0000 |
| Do you think the following are likely to happen as a result ... | 0.0195 | 1.0000 |
| Do you think the following are likely to happen as a result ... | 0.0212 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please consider the following scenario - in the future, robo... | 0.5261 | 0.2357 |
| Which of the following statements comes closer to your feeli... | 0.5452 | -0.2357 |
| How worried are you right now about not having enough to pay... | 0.5640 | 0.0000 |
| How often, if ever, did you use air guns, such as paintball,... | 0.5850 | 0.0000 |
| On a different subject, would you say that society generally... | 0.6715 | -0.2357 |
