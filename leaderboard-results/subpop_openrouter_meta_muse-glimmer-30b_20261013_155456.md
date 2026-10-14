# SynthBench Score Card

**Provider:** openrouter/meta/muse-glimmer-30b
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 707.3s

## SynthBench Parity Score (SPS)

**SPS: 0.6321 [0.5993, 0.6644]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.4639 [0.4149, 0.5084] | █████░░░░░ |
| P_rank  Rank-Order | 0.4674 [0.4218, 0.5148] | █████░░░░░ |
| P_refuse Refusal Cal. | 0.9651 [0.9241, 0.9784] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.5361 |
| Median JSD | 0.5084 |
| Mean Kendall's tau | -0.0651 |
| Composite Parity (legacy) | 0.4656 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | -0.0963 | -17% |
| random-baseline | 0.6495 | -0.1839 | -28% |

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
| Do you think that you have ever been at an advantage in your... | 0.0751 | 0.9129 |
| Do you think artificial intelligence (AI) would do better, w... | 0.1093 | 0.6708 |
| Over the next 20 years, how much impact do you think the use... | 0.1319 | 0.5976 |
| How much, if anything, have you heard or read about thousand... | 0.1383 | 0.1826 |
| Over the next 20 years, how much impact do you think the use... | 0.1596 | 0.5976 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| As you may know, the Supreme Court’s decision found that the... | 0.9406 | -0.6325 |
| How confident, if at all, are you that the government is con... | 0.9474 | -0.6325 |
| How would you rate the job the Biden administration has done... | 0.9483 | -0.6325 |
| Just to confirm, do you think there are any exceptions when ... | 0.9809 | -0.8165 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
