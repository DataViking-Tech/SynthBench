# SynthBench Score Card

**Provider:** althing/openrouter/anthropic/claude-haiku-4.5 t=0.85 tpl=minimal
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 375.3s

## SynthBench Parity Score (SPS)

**SPS: 0.6482 [0.6133, 0.6828]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6391 [0.5867, 0.6795] | ██████░░░░ |
| P_rank  Rank-Order | 0.6038 [0.5537, 0.6455] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.7016 [0.6304, 0.7687] | ███████░░░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3609 |
| Median JSD | 0.2976 |
| Mean Kendall's tau | 0.2075 |
| Composite Parity (legacy) | 0.6214 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0594 | +11% |
| random-baseline | 0.6495 | -0.0281 | -4% |

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
| Do you think abortion should be legal or illegal in the situ... | 0.0499 | 0.9129 |
| Did you refuse to answer the previous question?... | 0.0502 | 1.0000 |
| Regardless of whether you think abortion should be legal or ... | 0.0549 | 0.0000 |
| Regardless of whether you think abortion should be legal or ... | 0.0584 | 0.0000 |
| Regardless of whether you think abortion should be legal or ... | 0.0649 | 0.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think the United States’ decision to withdraw all tro... | 0.9246 | -0.8165 |
| All in all, do you favor or oppose the United States admitti... | 0.9452 | -0.6325 |
| Thinking about policies around abortion in this country, in ... | 0.9509 | -0.5774 |
| Please choose the statement that comes closer to your own vi... | 0.9582 | -0.8165 |
| Please indicate if you have attended a concert over the past... | 0.9792 | -0.8165 |
