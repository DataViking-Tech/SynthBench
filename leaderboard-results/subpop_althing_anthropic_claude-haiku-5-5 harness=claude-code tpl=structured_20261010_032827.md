# SynthBench Score Card

**Provider:** althing/anthropic/claude-haiku-5-5 harness=claude-code tpl=structured
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 1117.7s

## SynthBench Parity Score (SPS)

**SPS: 0.7260 [0.6909, 0.7572]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5717 [0.5230, 0.6153] | ██████░░░░ |
| P_rank  Rank-Order | 0.6263 [0.5721, 0.6728] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4283 |
| Median JSD | 0.4049 |
| Mean Kendall's tau | 0.2527 |
| Composite Parity (legacy) | 0.5990 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0370 | +7% |
| random-baseline | 0.6495 | -0.0505 | -8% |

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
| If you were looking for work, would you want to apply for a ... | 0.0103 | 1.0000 |
| Do you think gender should be a major factor, minor factor, ... | 0.0485 | 0.6667 |
| Do you think high school grades should be a major factor, mi... | 0.0499 | 0.9129 |
| How much, if anything, have you heard or read about thousand... | 0.0529 | 0.9129 |
| Do you think abortion should be legal or illegal in the situ... | 0.0924 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Thinking about abortion policies around the country, which i... | 0.9202 | -0.8165 |
| Do you think abortion should be...... | 0.9364 | -0.6325 |
| Do you think abortion should be...... | 0.9401 | -0.6325 |
| Do you think abortion should be…... | 0.9526 | -0.6325 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
