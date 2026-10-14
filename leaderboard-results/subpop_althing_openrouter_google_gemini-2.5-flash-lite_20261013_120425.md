# SynthBench Score Card

**Provider:** althing/openrouter/google/gemini-2.5-flash-lite
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 212.1s

## SynthBench Parity Score (SPS)

**SPS: 0.8128 [0.7938, 0.8294]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7037 [0.6736, 0.7310] | ███████░░░ |
| P_rank  Rank-Order | 0.7548 [0.7214, 0.7829] | ████████░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9396, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2963 |
| Median JSD | 0.2728 |
| Mean Kendall's tau | 0.5096 |
| Composite Parity (legacy) | 0.7293 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1673 | +30% |
| random-baseline | 0.6495 | +0.0797 | +12% |

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
| If a doctor or provider performed an abortion in a situation... | 0.0090 | 0.6667 |
| Did you refuse to answer the previous question?... | 0.0149 | 0.8165 |
| Do you personally know someone (such as a close friend, fami... | 0.0225 | 0.3333 |
| If an abortion was carried out in a situation where it was i... | 0.0239 | 1.0000 |
| Have there been times in the past 12 months when you did not... | 0.0242 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Before taking this survey, how much thought would you say yo... | 0.5900 | 0.0000 |
| Do you think being the first person in the family to go to c... | 0.6147 | -0.2357 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.6155 | -0.3586 |
| As you may know, the Supreme Court’s decision found that the... | 0.6451 | -0.5976 |
| Do you think that you have ever been at an advantage in your... | 0.6579 | 0.2357 |
