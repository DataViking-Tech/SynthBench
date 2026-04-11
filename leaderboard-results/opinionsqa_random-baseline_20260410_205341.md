# SynthBench Score Card

**Provider:** random-baseline
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 10
**Elapsed:** 0.0s

## SynthBench Parity Score (SPS)

**SPS: 0.7235 [0.5515, 0.6248]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7226 [0.6928, 0.7501] | ███████░░░ |
| P_rank  Rank-Order | 0.4536 [0.4014, 0.5044] | █████░░░░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2774 |
| Median JSD | 0.2617 |
| Mean Kendall's tau | -0.0928 |
| Composite Parity (legacy) | 0.5881 |

## What These Scores Mean

- **SPS** (SynthBench Parity Score): The overall score — average of all metrics. 0 = random noise, 1 = indistinguishable from real humans.
- **P_dist** (Distributional Parity): How closely does the AI's answer distribution match real humans? If 60% of humans say 'yes' and the AI says 'yes' 60% of the time, that's a perfect match. 0 = completely different, 1 = identical distributions.
- **P_rank** (Rank-Order Parity): Does the AI get the preference ordering right? If humans prefer A > B > C, does the AI agree — even if the exact percentages differ? 0 = reversed ordering, 1 = perfect agreement.
- **P_refuse** (Refusal Calibration): Does the AI refuse to answer at appropriate rates? Humans sometimes decline sensitive questions. An AI that never refuses, or refuses too often, is miscalibrated. 0 = rates completely off, 1 = perfect match.
- **P_cond** (Conditioning Fidelity): When told 'respond as a 65-year-old conservative,' does the AI actually shift its answers? Higher = better demographic role-playing. (When available.)
- **P_sub** (Subgroup Consistency): Is the AI equally accurate across all demographics, or does it nail some groups and miss others? (When available.)

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| If driverless vehicles become widespread, do you think that ... | 0.0091 | 0.9129 |
| Do you feel that society in general tends to look at most gu... | 0.0309 | 1.0000 |
| Thinking about the people you know, including yourself, do y... | 0.0449 | 1.0000 |
| How much, if at all, do you think the ease with which people... | 0.0469 | 0.6708 |
| Do you think it is very likely, somewhat likely, not very li... | 0.0668 | 0.5976 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Which of the following statements best describes how you fee... | 0.5863 | -1.0000 |
| Have you ever had your pay or hours reduced because your emp... | 0.6206 | -0.8165 |
| The next question is about local elections, such as for mayo... | 0.6411 | -0.6708 |
| How often, if ever, do you attend gun shows... | 0.7140 | -0.5270 |
| How often, if ever, do you participate in online discussion ... | 0.7644 | -0.6000 |
