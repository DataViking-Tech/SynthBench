# SynthBench Score Card

**Provider:** althing/openrouter/deepseek/deepseek-v4.1-flash
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 716.6s

## SynthBench Parity Score (SPS)

**SPS: 0.8158 [0.7876, 0.8342]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6900 [0.6569, 0.7201] | ███████░░░ |
| P_rank  Rank-Order | 0.7774 [0.7481, 0.8045] | ████████░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3100 |
| Median JSD | 0.2866 |
| Mean Kendall's tau | 0.5549 |
| Composite Parity (legacy) | 0.7337 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1717 | +31% |
| random-baseline | 0.6495 | +0.0842 | +13% |

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
| Please indicate if you have attended a concert over the past... | 0.0023 | 1.0000 |
| If an abortion was carried out in a situation where it was i... | 0.0627 | 1.0000 |
| In the news you are receiving about the Biden administration... | 0.0642 | 1.0000 |
| Do you think that you have ever been at an advantage in your... | 0.0721 | 0.9129 |
| If a doctor or provider performed an abortion in a situation... | 0.0723 | 0.6667 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Just to confirm, do you think there are any exceptions when ... | 0.5494 | 0.0000 |
| Regardless of whether you think abortion should be legal or ... | 0.5502 | 0.3464 |
| Do you think race or ethnicity should be a major factor, min... | 0.6062 | 0.2357 |
| Regardless of whether you think abortion should be legal or ... | 0.6451 | -0.1155 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
