# SynthBench Score Card

**Provider:** althing/openrouter/qwen/qwen3.8-flash
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 1311.3s

## SynthBench Parity Score (SPS)

**SPS: 0.8300 [0.8070, 0.8482]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7367 [0.7040, 0.7678] | ███████░░░ |
| P_rank  Rank-Order | 0.7738 [0.7451, 0.8024] | ████████░░ |
| P_refuse Refusal Cal. | 0.9796 [0.9395, 0.9900] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2633 |
| Median JSD | 0.2583 |
| Mean Kendall's tau | 0.5476 |
| Composite Parity (legacy) | 0.7553 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1933 | +34% |
| random-baseline | 0.6495 | +0.1057 | +16% |

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
| Which statement comes closer to your view, even if neither i... | 0.0096 | 0.3333 |
| Please choose the statement that comes closer to your own vi... | 0.0097 | 1.0000 |
| Do you personally know someone (such as a close friend, fami... | 0.0104 | 0.3333 |
| Do you think artificial intelligence (AI) would do better, w... | 0.0123 | 0.8000 |
| If an abortion was carried out in a situation where it was i... | 0.0155 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think being the first person in the family to go to c... | 0.5011 | 0.2357 |
| Which country in Africa is known for having the largest popu... | 0.5123 | 0.3464 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.5839 | 0.0000 |
| Did you refuse to answer the previous question?... | 0.6582 | -0.3333 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.6822 | -0.3162 |
