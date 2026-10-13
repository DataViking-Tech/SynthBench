# SynthBench Score Card

**Provider:** raw-anthropic/claude-haiku-5-5 harness=claude-code
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 2141.0s

## SynthBench Parity Score (SPS)

**SPS: 0.7261 [0.6925, 0.7545]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5899 [0.5403, 0.6344] | ██████░░░░ |
| P_rank  Rank-Order | 0.6169 [0.5671, 0.6578] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9715 [0.9326, 0.9844] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4101 |
| Median JSD | 0.3957 |
| Mean Kendall's tau | 0.2339 |
| Composite Parity (legacy) | 0.6034 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0414 | +7% |
| random-baseline | 0.6495 | -0.0461 | -7% |

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
| If you were looking for work, would you want to apply for a ... | 0.0129 | 1.0000 |
| Before taking this survey, how much thought would you say yo... | 0.0282 | 0.7379 |
| Please indicate if you have attended a concert over the past... | 0.0288 | 1.0000 |
| Do you think people have ever assumed that you benefited unf... | 0.0342 | 1.0000 |
| Do you think whether a relative attended the school should b... | 0.0347 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think abortion should be...... | 0.9364 | -0.6325 |
| Do you think abortion should be...... | 0.9401 | -0.6325 |
| As you may know, the Supreme Court’s decision found that the... | 0.9406 | -0.6325 |
| Do you think abortion should be...... | 0.9442 | -0.6325 |
| Do you think abortion should be…... | 0.9526 | -0.6325 |
