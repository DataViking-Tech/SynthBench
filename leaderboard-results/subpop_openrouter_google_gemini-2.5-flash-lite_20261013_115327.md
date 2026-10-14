# SynthBench Score Card

**Provider:** openrouter/google/gemini-2.5-flash-lite
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 143.4s

## SynthBench Parity Score (SPS)

**SPS: 0.7783 [0.7448, 0.8025]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6534 [0.6080, 0.6906] | ███████░░░ |
| P_rank  Rank-Order | 0.7016 [0.6615, 0.7366] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3466 |
| Median JSD | 0.3112 |
| Mean Kendall's tau | 0.4033 |
| Composite Parity (legacy) | 0.6775 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1155 | +21% |
| random-baseline | 0.6495 | +0.0280 | +4% |

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
| Do you think the use of artificial intelligence (AI) in heal... | 0.0062 | 0.9129 |
| Do you personally know someone (such as a close friend, fami... | 0.0080 | 1.0000 |
| Please choose the statement that comes closer to your own vi... | 0.0376 | 0.3333 |
| Which statement comes closer to your view, even if neither i... | 0.0488 | 1.0000 |
| If an abortion was carried out in a situation where it was i... | 0.0600 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Thinking now about how AI can be used in hiring, how much ha... | 0.7811 | -0.2357 |
| Do you think abortion should be...... | 0.9364 | -0.6325 |
| Do you think abortion should be...... | 0.9401 | -0.6325 |
| Do you think abortion should be...... | 0.9442 | -0.6325 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
