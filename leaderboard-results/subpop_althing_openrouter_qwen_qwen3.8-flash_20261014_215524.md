# SynthBench Score Card

**Provider:** althing/openrouter/qwen/qwen3.8-flash
**Dataset:** subpop (525 questions)
**Samples per question:** 30
**Elapsed:** 14235.6s

## SynthBench Parity Score (SPS)

**SPS: 0.8445 [0.8361, 0.8517]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7475 [0.7357, 0.7610] | ███████░░░ |
| P_rank  Rank-Order | 0.8022 [0.7903, 0.8139] | ████████░░ |
| P_refuse Refusal Cal. | 0.9838 [0.9750, 0.9883] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2525 |
| Median JSD | 0.2493 |
| Mean Kendall's tau | 0.6044 |
| Composite Parity (legacy) | 0.7749 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.2129 | +38% |
| random-baseline | 0.6495 | +0.1253 | +19% |

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
| Have there been times in the past 12 months when you did not... | 0.0008 | 1.0000 |
| Please indicate if you have attended a concert over the past... | 0.0023 | 1.0000 |
| Have you helped friends or neighbors by delivering groceries... | 0.0024 | 1.0000 |
| Are you spending less money than usual mainly because...... | 0.0045 | 1.0000 |
| Have you volunteered or made a donation through a nonreligio... | 0.0059 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| In the past month, how often, if ever, have you worn a mask ... | 0.6408 | 0.4140 |
| Did you refuse to answer the previous question?... | 0.7239 | -0.3333 |
| Have you ever moved out of where you were living, either per... | 0.7766 | 0.2357 |
| Is the national unemployment rate as reported by the governm... | 0.7782 | -0.0658 |
| Did you refuse to answer the previous question?... | 0.8945 | -0.3333 |
