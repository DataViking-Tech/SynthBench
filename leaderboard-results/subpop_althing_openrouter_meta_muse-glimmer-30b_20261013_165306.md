# SynthBench Score Card

**Provider:** althing/openrouter/meta/muse-glimmer-30b
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 1062.3s

## SynthBench Parity Score (SPS)

**SPS: 0.8092 [0.7808, 0.8280]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6782 [0.6434, 0.7071] | ███████░░░ |
| P_rank  Rank-Order | 0.7694 [0.7383, 0.7965] | ████████░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3218 |
| Median JSD | 0.3428 |
| Mean Kendall's tau | 0.5389 |
| Composite Parity (legacy) | 0.7238 |

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
| Please indicate if you have attended a concert over the past... | 0.0023 | 1.0000 |
| If you were looking for work, would you want to apply for a ... | 0.0227 | 0.8165 |
| Do you think the United States’ decision to withdraw all tro... | 0.0242 | 0.8165 |
| Do you think whether a relative attended the school should b... | 0.0548 | 0.9129 |
| Do you think the use of artificial intelligence (AI) in heal... | 0.0864 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Just to confirm, do you think there are any exceptions when ... | 0.5494 | 0.0000 |
| Regardless of whether you think abortion should be legal or ... | 0.5557 | 0.5774 |
| How acceptable do you think it is for a smart speaker to ana... | 0.6048 | 0.1155 |
| How acceptable do you think it is to use computer programs, ... | 0.6049 | 0.1155 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
