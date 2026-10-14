# SynthBench Score Card

**Provider:** althing/openrouter/meta-llama/llama-3.3-70b-instruct
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 365.8s

## SynthBench Parity Score (SPS)

**SPS: 0.7757 [0.7556, 0.7945]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6235 [0.5926, 0.6543] | ██████░░░░ |
| P_rank  Rank-Order | 0.7238 [0.6909, 0.7537] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3765 |
| Median JSD | 0.4062 |
| Mean Kendall's tau | 0.4476 |
| Composite Parity (legacy) | 0.6736 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1116 | +20% |
| random-baseline | 0.6495 | +0.0241 | +4% |

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
| If an abortion was carried out in a situation where it was i... | 0.0176 | 0.3333 |
| Have your personal views about abortion changed in any way o... | 0.0783 | 0.9129 |
| Do you think gender should be a major factor, minor factor, ... | 0.1154 | 0.7071 |
| Do you think abortion should be legal or illegal in the situ... | 0.1278 | 0.7071 |
| Did you refuse to answer the previous question?... | 0.1401 | 0.3333 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think artificial intelligence (AI) would do better, w... | 0.6582 | 0.0000 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.6822 | -0.3162 |
| Do you think people have ever assumed that you benefited unf... | 0.6830 | -0.2357 |
| Regardless of whether you think abortion should be legal or ... | 0.6906 | -0.3464 |
| Have there been times in the past 12 months when you did not... | 0.7098 | -0.2357 |
