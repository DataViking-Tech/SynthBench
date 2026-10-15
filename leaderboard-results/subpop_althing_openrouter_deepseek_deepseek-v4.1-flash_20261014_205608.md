# SynthBench Score Card

**Provider:** althing/openrouter/deepseek/deepseek-v4.1-flash
**Dataset:** subpop (525 questions)
**Samples per question:** 30
**Elapsed:** 10679.4s

## SynthBench Parity Score (SPS)

**SPS: 0.8203 [0.8115, 0.8276]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6890 [0.6772, 0.7020] | ███████░░░ |
| P_rank  Rank-Order | 0.7881 [0.7769, 0.7992] | ████████░░ |
| P_refuse Refusal Cal. | 0.9839 [0.9751, 0.9884] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3110 |
| Median JSD | 0.3076 |
| Mean Kendall's tau | 0.5761 |
| Composite Parity (legacy) | 0.7385 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1765 | +31% |
| random-baseline | 0.6495 | +0.0890 | +14% |

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
| Have you helped friends or neighbors by delivering groceries... | 0.0022 | 1.0000 |
| Please indicate if you have attended a concert over the past... | 0.0029 | 1.0000 |
| Since the coronavirus outbreak began in February 2020, have ... | 0.0044 | 1.0000 |
| Do you think it is possible or not possible for people to de... | 0.0054 | 0.9129 |
| Please choose the statement that comes closer to your own vi... | 0.0105 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| In the past month, how often, if ever, have you worn a mask ... | 0.7480 | 0.4472 |
| Is the national unemployment rate as reported by the governm... | 0.7616 | -0.0658 |
| In the past month, how often, if ever, have you worn a mask ... | 0.7789 | 0.4303 |
| Did you refuse to answer the previous question?... | 0.8945 | -0.3333 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
