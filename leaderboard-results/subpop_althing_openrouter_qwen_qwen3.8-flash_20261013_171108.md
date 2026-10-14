# SynthBench Score Card

**Provider:** althing/openrouter/qwen/qwen3.8-flash
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 1311.8s

## SynthBench Parity Score (SPS)

**SPS: 0.8280 [0.8025, 0.8458]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7420 [0.7092, 0.7719] | ███████░░░ |
| P_rank  Rank-Order | 0.7620 [0.7314, 0.7897] | ████████░░ |
| P_refuse Refusal Cal. | 0.9800 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2580 |
| Median JSD | 0.2247 |
| Mean Kendall's tau | 0.5240 |
| Composite Parity (legacy) | 0.7520 |

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
| Please choose the statement that comes closer to your own vi... | 0.0057 | 0.3333 |
| If you were looking for work, would you want to apply for a ... | 0.0103 | 1.0000 |
| Have there been times in the past 12 months when you did not... | 0.0123 | 0.6667 |
| Please indicate if you have attended a concert over the past... | 0.0145 | 1.0000 |
| Would you favor or oppose employers’ use of artificial intel... | 0.0145 | 0.6667 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Thinking about the use of artificial intelligence (AI) in th... | 0.5382 | 0.0000 |
| Regardless of whether you think abortion should be legal or ... | 0.5389 | -0.0861 |
| As you may know, the Supreme Court’s decision found that the... | 0.5493 | -0.3162 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.5839 | 0.0000 |
| Did you refuse to answer the previous question?... | 0.7603 | -0.3333 |
