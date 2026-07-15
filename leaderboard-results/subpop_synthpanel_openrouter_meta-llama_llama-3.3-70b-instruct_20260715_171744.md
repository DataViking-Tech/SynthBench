# SynthBench Score Card

**Provider:** synthpanel/openrouter/meta-llama/llama-3.3-70b-instruct
**Dataset:** subpop (100 questions)
**Samples per question:** 15
**Elapsed:** 187.9s

## SynthBench Parity Score (SPS)

**SPS: 0.7761 [0.7539, 0.7961]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6374 [0.6081, 0.6693] | ██████░░░░ |
| P_rank  Rank-Order | 0.7352 [0.7014, 0.7643] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9558 [0.9101, 0.9734] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3626 |
| Median JSD | 0.3724 |
| Mean Kendall's tau | 0.4703 |
| Composite Parity (legacy) | 0.6863 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1243 | +22% |
| random-baseline | 0.6495 | +0.0368 | +6% |

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
| If an abortion was carried out in a situation where it was i... | 0.0321 | 1.0000 |
| Do you think abortion should be legal or illegal in the situ... | 0.0787 | 0.9129 |
| Would you favor or oppose employers’ use of artificial intel... | 0.0848 | 0.9129 |
| Have your personal views about abortion changed in any way o... | 0.0859 | 0.9129 |
| Do you think gender should be a major factor, minor factor, ... | 0.1154 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Thinking about the use of artificial intelligence (AI) in th... | 0.6221 | 0.0000 |
| Regardless of whether you think abortion should be legal or ... | 0.6451 | -0.1155 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.6822 | -0.3162 |
| Regardless of whether you think abortion should be legal or ... | 0.6906 | -0.3464 |
| Have there been times in the past 12 months when you did not... | 0.7098 | -0.2357 |
