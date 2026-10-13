# SynthBench Score Card

**Provider:** raw-openai/gpt-6-luna harness=codex
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 3429.7s

## SynthBench Parity Score (SPS)

**SPS: 0.7430 [0.7060, 0.7715]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6238 [0.5732, 0.6651] | ██████░░░░ |
| P_rank  Rank-Order | 0.6252 [0.5723, 0.6739] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3762 |
| Median JSD | 0.3180 |
| Mean Kendall's tau | 0.2504 |
| Composite Parity (legacy) | 0.6245 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0625 | +11% |
| random-baseline | 0.6495 | -0.0250 | -4% |

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
| Do you think high school grades should be a major factor, mi... | 0.0452 | 0.9129 |
| How much, if anything, have you heard or read about thousand... | 0.0571 | 0.9129 |
| Do you think race or ethnicity should be a major factor, min... | 0.0640 | 0.9129 |
| Do you think artificial intelligence (AI) would do better, w... | 0.1098 | 0.7379 |
| Do you think gender should be a major factor, minor factor, ... | 0.1154 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please indicate if you have traveled more than 100 miles fro... | 0.9774 | -0.8165 |
| Please indicate if you have attended a concert over the past... | 0.9792 | -0.8165 |
| Please indicate if you have attended a sporting event over t... | 0.9835 | -0.8165 |
| Have there been times in the past 12 months when you did not... | 0.9861 | -0.7071 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
