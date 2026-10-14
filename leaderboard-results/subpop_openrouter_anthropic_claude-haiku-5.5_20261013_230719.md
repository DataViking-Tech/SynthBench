# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-haiku-5.5
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 365.2s

## SynthBench Parity Score (SPS)

**SPS: 0.6951 [0.6459, 0.7354]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5708 [0.5148, 0.6164] | ██████░░░░ |
| P_rank  Rank-Order | 0.6535 [0.5996, 0.6971] | ███████░░░ |
| P_refuse Refusal Cal. | 0.8611 [0.7926, 0.9137] | █████████░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4292 |
| Median JSD | 0.4308 |
| Mean Kendall's tau | 0.3069 |
| Composite Parity (legacy) | 0.6121 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0501 | +9% |
| random-baseline | 0.6495 | -0.0374 | -6% |

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
| Do you think the United States’ decision to withdraw all tro... | 0.0109 | 1.0000 |
| Did you refuse to answer the previous question?... | 0.0149 | 0.8165 |
| If an abortion was carried out in a situation where it was i... | 0.0198 | 1.0000 |
| If an abortion was carried out in a situation where it was i... | 0.0239 | 1.0000 |
| Do you think abortion should be legal or illegal in the situ... | 0.0501 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think abortion should be…... | 0.9526 | -0.6325 |
| Here’s a list of activities some people do and others do not... | 0.9765 | -0.8165 |
| Please indicate if you have traveled more than 100 miles fro... | 0.9774 | -0.8165 |
| Please indicate if you have attended a concert over the past... | 0.9792 | -0.8165 |
| Please indicate if you have attended a sporting event over t... | 0.9835 | -0.8165 |
