# SynthBench Score Card

**Provider:** raw-anthropic/claude-sonnet-5-5 harness=claude-code
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 2813.8s

## SynthBench Parity Score (SPS)

**SPS: 0.6581 [0.6196, 0.6937]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.4616 [0.4048, 0.5154] | █████░░░░░ |
| P_rank  Rank-Order | 0.5327 [0.4820, 0.5866] | █████░░░░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.5384 |
| Median JSD | 0.4589 |
| Mean Kendall's tau | 0.0654 |
| Composite Parity (legacy) | 0.4971 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | -0.0649 | -12% |
| random-baseline | 0.6495 | -0.1524 | -23% |

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
| Do you think artificial intelligence (AI) would do better, w... | 0.0896 | 0.7379 |
| Do you think that you have ever been at an advantage in your... | 0.0931 | 0.9129 |
| Would you favor or oppose employers’ use of artificial intel... | 0.1184 | 0.9129 |
| Have there been times in the past 12 months when you did not... | 0.1343 | 0.5477 |
| Do you think people have ever assumed that you benefited unf... | 0.1475 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think race or ethnicity should be a major factor, min... | 0.9767 | -0.7071 |
| Do you think abortion should be legal or illegal in the situ... | 0.9808 | -0.7071 |
| Just to confirm, do you think there are any exceptions when ... | 0.9809 | -0.8165 |
| Do you think abortion should be legal or illegal in the situ... | 0.9867 | -0.7071 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
