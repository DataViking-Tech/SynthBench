# SynthBench Score Card

**Provider:** althing/openrouter/qwen/qwen3.8-flash
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 1163.5s

## SynthBench Parity Score (SPS)

**SPS: 0.8491 [0.8237, 0.8684]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7822 [0.7531, 0.8106] | ████████░░ |
| P_rank  Rank-Order | 0.7929 [0.7519, 0.8258] | ████████░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2178 |
| Median JSD | 0.1982 |
| Mean Kendall's tau | 0.5858 |
| Composite Parity (legacy) | 0.7876 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.2256 | +40% |
| random-baseline | 0.6495 | +0.1380 | +21% |

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
| Do you favor or oppose the death penalty for persons convict... | 0.0244 | 1.0000 |
| Consider a person who believes that Black people are genetic... | 0.0303 | 0.3333 |
| I am going to name an institution in this country. As far as... | 0.0342 | 0.9129 |
| We are faced with many problems in this country, none of whi... | 0.0528 | 0.6667 |
| We are faced with many problems in this country, none of whi... | 0.0572 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Should divorce in this country be easier or more difficult t... | 0.4302 | 0.1826 |
| I'm going to show you a seven-point scale on which the polit... | 0.4359 | 0.5000 |
| Generally speaking, do you usually think of yourself as a Re... | 0.4368 | 0.2621 |
| Do you agree strongly, agree somewhat, neither agree nor dis... | 0.4685 | -0.1491 |
| Do you believe there is a life after death?... | 0.7016 | -0.8165 |
