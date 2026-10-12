# SynthBench Score Card

**Provider:** althing/anthropic/claude-sonnet-5-5 harness=claude-code
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 2959.3s

## SynthBench Parity Score (SPS)

**SPS: 0.6954 [0.6571, 0.7318]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5223 [0.4620, 0.5773] | █████░░░░░ |
| P_rank  Rank-Order | 0.5845 [0.5272, 0.6357] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9795 [0.9392, 0.9898] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4777 |
| Median JSD | 0.4276 |
| Mean Kendall's tau | 0.1690 |
| Composite Parity (legacy) | 0.5534 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | -0.0086 | -2% |
| random-baseline | 0.6495 | -0.0961 | -15% |

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
| Please indicate if you have attended a concert over the past... | 0.0029 | 1.0000 |
| Please indicate if you have traveled more than 100 miles fro... | 0.0040 | 1.0000 |
| Please indicate if you have attended a sporting event over t... | 0.0171 | 1.0000 |
| Which statement comes closer to your view, even if neither i... | 0.0728 | 0.3333 |
| Do you think people have ever assumed that you benefited unf... | 0.0804 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think medication abortion should be legal or illegal ... | 0.9663 | -0.7071 |
| Do you think race or ethnicity should be a major factor, min... | 0.9767 | -0.7071 |
| Just to confirm, do you think there are any exceptions when ... | 0.9809 | -0.8165 |
| Do you think abortion should be legal or illegal in the situ... | 0.9867 | -0.7071 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
