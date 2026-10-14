# SynthBench Score Card

**Provider:** openrouter/qwen/qwen3.8-flash
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 889.2s

## SynthBench Parity Score (SPS)

**SPS: 0.8259 [0.8069, 0.8422]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7404 [0.7117, 0.7685] | ███████░░░ |
| P_rank  Rank-Order | 0.7574 [0.7233, 0.7864] | ████████░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2596 |
| Median JSD | 0.2435 |
| Mean Kendall's tau | 0.5147 |
| Composite Parity (legacy) | 0.7489 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1869 | +33% |
| random-baseline | 0.6495 | +0.0994 | +15% |

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
| If a doctor or provider performed an abortion in a situation... | 0.0061 | 0.3333 |
| Please indicate if you have attended a concert over the past... | 0.0145 | 1.0000 |
| Did you refuse to answer the previous question?... | 0.0149 | 0.8165 |
| Do you think the United States’ decision to withdraw all tro... | 0.0242 | 0.8165 |
| If an abortion was carried out in a situation where it was i... | 0.0288 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How acceptable do you think it is to use computer programs, ... | 0.5379 | 0.3464 |
| Just to confirm, do you think there are any exceptions when ... | 0.5494 | 0.0000 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.5839 | 0.0000 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.6221 | 0.0000 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.6822 | -0.3162 |
