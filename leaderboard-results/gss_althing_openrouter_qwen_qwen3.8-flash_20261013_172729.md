# SynthBench Score Card

**Provider:** althing/openrouter/qwen/qwen3.8-flash
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 978.3s

## SynthBench Parity Score (SPS)

**SPS: 0.8444 [0.8178, 0.8659]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7769 [0.7472, 0.8049] | ████████░░ |
| P_rank  Rank-Order | 0.7843 [0.7386, 0.8228] | ████████░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2231 |
| Median JSD | 0.2123 |
| Mean Kendall's tau | 0.5686 |
| Composite Parity (legacy) | 0.7806 |

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
| We are faced with many problems in this country, none of whi... | 0.0115 | 1.0000 |
| We are faced with many problems in this country, none of whi... | 0.0135 | 0.5477 |
| We are faced with many problems in this country, none of whi... | 0.0321 | 1.0000 |
| Do you favor or oppose the death penalty for persons convict... | 0.0323 | 1.0000 |
| We are faced with many problems in this country, none of whi... | 0.0332 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| I'm going to show you a seven-point scale on which the polit... | 0.4359 | 0.5000 |
| Would you say that most of the time people try to be helpful... | 0.4643 | -0.1826 |
| Should divorce in this country be easier or more difficult t... | 0.4674 | -0.5477 |
| Generally speaking, do you usually think of yourself as a Re... | 0.5088 | 0.1572 |
| Do you believe there is a life after death?... | 0.7016 | -0.8165 |
