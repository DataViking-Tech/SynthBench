# SynthBench Score Card

**Provider:** synthpanel/claude-haiku-4-5-20251001
**Dataset:** opinionsqa (175 questions)
**Samples per question:** 50
**Elapsed:** 273.8s

## SynthBench Parity Score (SPS)

**SPS: 0.7648 [0.6601, 0.6735]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.8166 [0.8058, 0.8264] | ████████░░ |
| P_rank  Rank-Order | 0.5158 [0.5078, 0.5287] | █████░░░░░ |
| P_refuse Refusal Cal. | 0.9620 [0.9382, 0.9783] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.1834 |
| Median JSD | 0.1718 |
| Mean Kendall's tau | 0.0317 |
| Composite Parity (legacy) | 0.6662 |

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
| 2017 | 0.8005 | 0.5135 | 0.1995 | 37 |
| 2018 | 0.8139 | 0.5000 | 0.1861 | 39 |
| 2019 | 0.8371 | 0.5183 | 0.1629 | 50 |
| 2020 | 0.8031 | 0.5000 | 0.1969 | 31 |
| 2022 | 0.8215 | 0.5754 | 0.1785 | 18 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Still thinking ahead 30 years, which do you think is more li... | 0.0695 | 0.0000 |
| Still thinking ahead 30 years, which do you think is more li... | 0.0715 | 0.0000 |
| Still thinking ahead 30 years, which do you think is more li... | 0.0721 | 0.0000 |
| Would you say China has done a good or bad job dealing with ... | 0.0743 | 0.4000 |
| Overall, how much has your family's financial situation when... | 0.0745 | 0.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| In the last 12 months, have you had someone take over your s... | 0.3457 | 0.0000 |
| Have you ever had your pay or hours reduced because your emp... | 0.4048 | 0.0000 |
| How important, if at all, do you think a good work ethic is ... | 0.4123 | 0.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.4420 | 0.0000 |
| Would you say the World Health Organization, or WHO has done... | 0.5459 | 0.3162 |
