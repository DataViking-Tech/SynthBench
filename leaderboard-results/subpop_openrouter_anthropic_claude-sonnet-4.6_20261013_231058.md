# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-sonnet-4.6
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 440.8s

## SynthBench Parity Score (SPS)

**SPS: 0.7429 [0.7111, 0.7690]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5713 [0.5271, 0.6089] | ██████░░░░ |
| P_rank  Rank-Order | 0.6775 [0.6345, 0.7116] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4287 |
| Median JSD | 0.4308 |
| Mean Kendall's tau | 0.3550 |
| Composite Parity (legacy) | 0.6244 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0624 | +11% |
| random-baseline | 0.6495 | -0.0251 | -4% |

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
| Do you think gender should be a major factor, minor factor, ... | 0.1154 | 0.7071 |
| Have your personal views about abortion changed in any way o... | 0.1270 | 0.7071 |
| Do you think abortion should be legal or illegal in the situ... | 0.1278 | 0.7071 |
| Have there been times in the past 12 months when you did not... | 0.1495 | 0.5477 |
| Have there been times in the past 12 months when you did not... | 0.1497 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think abortion should be...... | 0.9401 | -0.6325 |
| Do you think abortion should be...... | 0.9442 | -0.6325 |
| Do you think abortion should be…... | 0.9526 | -0.6325 |
| Do you personally know someone (such as a close friend, fami... | 0.9667 | -0.8165 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
