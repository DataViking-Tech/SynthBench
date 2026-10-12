# SynthBench Score Card

**Provider:** althing/anthropic/claude-haiku-4-5-20251001 harness=claude-code
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 5002.2s

## SynthBench Parity Score (SPS)

**SPS: 0.7253 [0.6847, 0.7583]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6705 [0.6309, 0.7037] | ███████░░░ |
| P_rank  Rank-Order | 0.7140 [0.6738, 0.7481] | ███████░░░ |
| P_refuse Refusal Cal. | 0.7914 [0.7241, 0.8454] | ████████░░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3295 |
| Median JSD | 0.3143 |
| Mean Kendall's tau | 0.4279 |
| Composite Parity (legacy) | 0.6923 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1303 | +23% |
| random-baseline | 0.6495 | +0.0427 | +7% |

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
| Please choose the statement that comes closer to your own vi... | 0.0169 | 1.0000 |
| Which statement comes closer to your view, even if neither i... | 0.0229 | 0.3333 |
| Do you personally know someone (such as a close friend, fami... | 0.0329 | 1.0000 |
| Do you think abortion should be legal or illegal in the situ... | 0.0501 | 0.9129 |
| Have there been times in the past 12 months when you did not... | 0.0519 | 0.6667 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How important is your religion in shaping your views about a... | 0.6375 | 0.1782 |
| Do you think abortion should be...... | 0.9364 | -0.6325 |
| Do you think abortion should be…... | 0.9526 | -0.6325 |
| Just to confirm, do you think there are any exceptions when ... | 0.9809 | -0.8165 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
