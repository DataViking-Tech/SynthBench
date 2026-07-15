# SynthBench Score Card

**Provider:** synthpanel/openrouter/anthropic/claude-haiku-4-5
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 471.9s

## SynthBench Parity Score (SPS)

**SPS: 0.7093 [0.6668, 0.7474]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7319 [0.6800, 0.7735] | ███████░░░ |
| P_rank  Rank-Order | 0.7193 [0.6666, 0.7669] | ███████░░░ |
| P_refuse Refusal Cal. | 0.6765 [0.6039, 0.7408] | ███████░░░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2681 |
| Median JSD | 0.1963 |
| Mean Kendall's tau | 0.4387 |
| Composite Parity (legacy) | 0.7256 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1637 | +29% |
| random-baseline | 0.6495 | +0.0761 | +12% |

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
| I am going to name an institution in this country. As far as... | 0.0084 | 1.0000 |
| I am going to name an institution in this country. As far as... | 0.0132 | 0.6667 |
| I am going to name an institution in this country. As far as... | 0.0267 | 1.0000 |
| I am going to name an institution in this country. As far as... | 0.0281 | 0.9129 |
| Generally speaking, do you usually think of yourself as a Re... | 0.0496 | 0.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Should divorce in this country be easier or more difficult t... | 0.5806 | -0.2357 |
| Do you believe there is a life after death?... | 0.7016 | -0.8165 |
| Which statement comes closest to expressing what you believe... | 0.7956 | 0.0000 |
| Do you think a person has the right to end his or her own li... | 0.8751 | -0.8165 |
| When a person has a disease that cannot be cured, do you thi... | 0.8895 | -0.8165 |
