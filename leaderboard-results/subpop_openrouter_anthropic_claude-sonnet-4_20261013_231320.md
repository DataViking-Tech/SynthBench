# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-sonnet-4
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 577.6s

## SynthBench Parity Score (SPS)

**SPS: 0.6654 [0.6185, 0.7075]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5493 [0.4916, 0.5945] | █████░░░░░ |
| P_rank  Rank-Order | 0.6138 [0.5581, 0.6591] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.8331 [0.7683, 0.8880] | ████████░░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4507 |
| Median JSD | 0.4114 |
| Mean Kendall's tau | 0.2276 |
| Composite Parity (legacy) | 0.5816 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0196 | +3% |
| random-baseline | 0.6495 | -0.0680 | -10% |

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
| Would you favor or oppose employers’ use of artificial intel... | 0.0706 | 1.0000 |
| Thinking about the area where you live, how easy or difficul... | 0.0706 | 0.0000 |
| Do you think high school grades should be a major factor, mi... | 0.0834 | 0.5477 |
| Do you think race or ethnicity should be a major factor, min... | 0.1060 | 0.9129 |
| Do you think gender should be a major factor, minor factor, ... | 0.1154 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Here’s a list of activities some people do and others do not... | 0.9765 | -0.8165 |
| Please indicate if you have traveled more than 100 miles fro... | 0.9774 | -0.8165 |
| Please indicate if you have attended a concert over the past... | 0.9792 | -0.8165 |
| Just to confirm, do you think there are any exceptions when ... | 0.9809 | -0.8165 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
