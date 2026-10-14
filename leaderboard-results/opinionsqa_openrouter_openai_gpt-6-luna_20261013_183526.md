# SynthBench Score Card

**Provider:** openrouter/openai/gpt-6-luna
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 2578.4s

## SynthBench Parity Score (SPS)

**SPS: 0.7141 [0.6771, 0.7488]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5558 [0.4950, 0.6093] | ██████░░░░ |
| P_rank  Rank-Order | 0.5923 [0.5400, 0.6449] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4442 |
| Median JSD | 0.3550 |
| Mean Kendall's tau | 0.1846 |
| Composite Parity (legacy) | 0.5741 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0121 | +2% |
| random-baseline | 0.6495 | -0.0755 | -12% |

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
| 2017 | 0.5578 | 0.5950 | 0.4422 | 99 |
| 2018 | 0.3630 | 0.3207 | 0.6370 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think the following are likely to happen as a result ... | 0.0158 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Which of the following statements best describes how you fee... | 0.0298 | 0.3333 |
| Would you favor or oppose the following? If robots and compu... | 0.0780 | 0.8367 |
| How often, if ever, do you participate in online discussion ... | 0.0893 | 0.6325 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How much of a problem was gun violence in the community wher... | 0.9838 | -0.6325 |
| In the last 12 months, that is since September 2016, have yo... | 0.9858 | -0.8165 |
| In the last 12 months, how often did you and your neighbors ... | 0.9858 | -0.5345 |
| Have you ever personally experienced discrimination or been ... | 0.9884 | -0.8165 |
| Have you ever been told by a doctor or other health professi... | 0.9903 | -0.8165 |
