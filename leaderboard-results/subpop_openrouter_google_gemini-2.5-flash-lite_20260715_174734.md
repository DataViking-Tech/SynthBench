# SynthBench Score Card

**Provider:** openrouter/google/gemini-2.5-flash-lite
**Dataset:** subpop (100 questions)
**Samples per question:** 15
**Elapsed:** 61.1s

## SynthBench Parity Score (SPS)

**SPS: 0.7763 [0.7441, 0.8008]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6530 [0.6091, 0.6921] | ███████░░░ |
| P_rank  Rank-Order | 0.6967 [0.6569, 0.7328] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9793 [0.9388, 0.9897] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3470 |
| Median JSD | 0.2974 |
| Mean Kendall's tau | 0.3934 |
| Composite Parity (legacy) | 0.6748 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1128 | +20% |
| random-baseline | 0.6495 | +0.0253 | +4% |

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
| Which statement comes closer to your view, even if neither i... | 0.0181 | 1.0000 |
| Do you think the use of artificial intelligence (AI) in heal... | 0.0481 | 0.9129 |
| Do you think athletic ability should be a major factor, mino... | 0.0484 | 0.6667 |
| Have there been times in the past 12 months when you did not... | 0.0505 | 0.9129 |
| If an abortion was carried out in a situation where it was i... | 0.0600 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think abortion should be…... | 0.8199 | -0.1195 |
| Do you think abortion should be...... | 0.9364 | -0.6325 |
| Do you think abortion should be...... | 0.9401 | -0.6325 |
| Do you think abortion should be...... | 0.9442 | -0.6325 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
