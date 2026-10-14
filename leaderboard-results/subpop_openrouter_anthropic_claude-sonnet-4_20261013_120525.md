# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-sonnet-4
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 486.9s

## SynthBench Parity Score (SPS)

**SPS: 0.6739 [0.6277, 0.7142]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5597 [0.5024, 0.6079] | ██████░░░░ |
| P_rank  Rank-Order | 0.6186 [0.5668, 0.6636] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.8433 [0.7763, 0.8970] | ████████░░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4403 |
| Median JSD | 0.4114 |
| Mean Kendall's tau | 0.2372 |
| Composite Parity (legacy) | 0.5891 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0271 | +5% |
| random-baseline | 0.6495 | -0.0604 | -9% |

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
| Do you think high school grades should be a major factor, mi... | 0.0499 | 0.9129 |
| Do you think race or ethnicity should be a major factor, min... | 0.0640 | 0.9129 |
| Thinking about the area where you live, how easy or difficul... | 0.0706 | 0.0000 |
| How confident, if at all, are you that the government is con... | 0.0895 | 0.0000 |
| Do you think gender should be a major factor, minor factor, ... | 0.1154 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think abortion should be…... | 0.9526 | -0.6325 |
| Please indicate if you have traveled more than 100 miles fro... | 0.9774 | -0.8165 |
| Please indicate if you have attended a concert over the past... | 0.9792 | -0.8165 |
| Just to confirm, do you think there are any exceptions when ... | 0.9809 | -0.8165 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
