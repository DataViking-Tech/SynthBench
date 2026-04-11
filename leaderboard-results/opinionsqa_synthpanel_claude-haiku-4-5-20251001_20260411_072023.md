# SynthBench Score Card

**Provider:** synthpanel/claude-haiku-4-5-20251001
**Dataset:** opinionsqa (429 questions)
**Samples per question:** 50
**Elapsed:** 498.1s

## SynthBench Parity Score (SPS)

**SPS: 0.7713 [0.6628, 0.6701]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.8254 [0.8199, 0.8307] | ████████░░ |
| P_rank  Rank-Order | 0.5069 [0.5032, 0.5133] | █████░░░░░ |
| P_refuse Refusal Cal. | 0.9816 [0.9702, 0.9867] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.1746 |
| Median JSD | 0.1688 |
| Mean Kendall's tau | 0.0139 |
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
| 2017 | 0.8178 | 0.5299 | 0.1822 | 44 |
| 2018 | 0.8383 | 0.5000 | 0.1617 | 78 |
| 2019 | 0.8191 | 0.5048 | 0.1809 | 153 |
| 2020 | 0.8151 | 0.5000 | 0.1849 | 56 |
| 2022 | 0.8343 | 0.5095 | 0.1657 | 98 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Which of the following, if any, do you restrict or limit eat... | 0.0005 | 0.0000 |
| Have you participated in any of these groups during the last... | 0.0039 | 1.0000 |
| Which of the following, if any, do you restrict or limit eat... | 0.0040 | 0.0000 |
| Which of the following, if any, do you restrict or limit eat... | 0.0129 | 0.0000 |
| Which of the following, if any, do you restrict or limit eat... | 0.0315 | 0.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Which of these statements comes closer to your view, even if... | 0.3609 | 0.0000 |
| How much do you think to push an agenda or viewpoint is a re... | 0.3669 | 0.0000 |
| How often, if ever, do you participate in online discussion ... | 0.3720 | 0.0000 |
| How important, if at all, do you think knowing how to get al... | 0.3869 | 0.0000 |
| Do you think of yourself as... | 0.4572 | 0.0000 |
