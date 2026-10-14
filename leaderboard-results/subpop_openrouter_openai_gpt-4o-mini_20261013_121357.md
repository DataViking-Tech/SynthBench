# SynthBench Score Card

**Provider:** openrouter/openai/gpt-4o-mini
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 686.1s

## SynthBench Parity Score (SPS)

**SPS: 0.7739 [0.7427, 0.7959]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6333 [0.5938, 0.6702] | ██████░░░░ |
| P_rank  Rank-Order | 0.7085 [0.6694, 0.7449] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3667 |
| Median JSD | 0.3783 |
| Mean Kendall's tau | 0.4171 |
| Composite Parity (legacy) | 0.6709 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1089 | +19% |
| random-baseline | 0.6495 | +0.0214 | +3% |

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
| Please indicate if you have attended a concert over the past... | 0.0051 | 1.0000 |
| Have there been times in the past 12 months when you did not... | 0.0165 | 0.9129 |
| Have there been times in the past 12 months when you did not... | 0.0197 | 1.0000 |
| If an abortion was carried out in a situation where it was i... | 0.0321 | 1.0000 |
| Do you think whether a relative attended the school should b... | 0.0370 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Regardless of whether you think abortion should be legal or ... | 0.6701 | -0.1155 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.6822 | -0.3162 |
| How acceptable do you think it is for a smart speaker to ana... | 0.7683 | -0.3464 |
| Thinking now about how AI can be used in hiring, how much ha... | 0.7811 | -0.2357 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
