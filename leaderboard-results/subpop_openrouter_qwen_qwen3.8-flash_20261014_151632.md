# SynthBench Score Card

**Provider:** openrouter/qwen/qwen3.8-flash
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 600.7s

## SynthBench Parity Score (SPS)

**SPS: 0.8235 [0.8057, 0.8395]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7435 [0.7153, 0.7692] | ███████░░░ |
| P_rank  Rank-Order | 0.7470 [0.7151, 0.7763] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2565 |
| Median JSD | 0.2406 |
| Mean Kendall's tau | 0.4941 |
| Composite Parity (legacy) | 0.7453 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1833 | +33% |
| random-baseline | 0.6495 | +0.0957 | +15% |

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
| Did you refuse to answer the previous question?... | 0.0149 | 0.8165 |
| Please indicate if you have attended a concert over the past... | 0.0215 | 0.8165 |
| Here’s a list of activities some people do and others do not... | 0.0343 | 0.3333 |
| If a doctor or provider performed an abortion in a situation... | 0.0466 | 0.1826 |
| If an abortion was carried out in a situation where it was i... | 0.0600 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Which country in Africa is known for having the largest popu... | 0.5123 | 0.3464 |
| Just to confirm, do you think there are any exceptions when ... | 0.5494 | 0.0000 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.5839 | 0.0000 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.6221 | 0.0000 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.6822 | -0.3162 |
