# SynthBench Score Card

**Provider:** openrouter/google/gemini-2.5-flash
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 177.9s

## SynthBench Parity Score (SPS)

**SPS: 0.7668 [0.7350, 0.7907]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6388 [0.5928, 0.6756] | ██████░░░░ |
| P_rank  Rank-Order | 0.6817 [0.6368, 0.7200] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9902] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3612 |
| Median JSD | 0.3208 |
| Mean Kendall's tau | 0.3633 |
| Composite Parity (legacy) | 0.6602 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0982 | +17% |
| random-baseline | 0.6495 | +0.0107 | +2% |

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
| Please indicate if you have attended a sporting event over t... | 0.0054 | 1.0000 |
| If an abortion was carried out in a situation where it was i... | 0.0697 | 0.3333 |
| Would you favor or oppose employers’ use of artificial intel... | 0.0754 | 0.6667 |
| Thinking about the use of artificial intelligence (AI) in he... | 0.0806 | 0.8944 |
| Please choose the statement that comes closer to your own vi... | 0.0813 | 0.3333 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think the United States’ decision to withdraw all tro... | 0.9246 | -0.8165 |
| Do you think abortion should be...... | 0.9364 | -0.6325 |
| Do you think abortion should be...... | 0.9401 | -0.6325 |
| Do you think abortion should be...... | 0.9442 | -0.6325 |
| Do you think abortion should be…... | 0.9526 | -0.6325 |
