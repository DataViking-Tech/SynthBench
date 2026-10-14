# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-haiku-5.5
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 323.3s

## SynthBench Parity Score (SPS)

**SPS: 0.7404 [0.7008, 0.7772]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6033 [0.5502, 0.6532] | ██████░░░░ |
| P_rank  Rank-Order | 0.6545 [0.5933, 0.7117] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9633 [0.9275, 0.9750] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3967 |
| Median JSD | 0.3539 |
| Mean Kendall's tau | 0.3091 |
| Composite Parity (legacy) | 0.6289 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0669 | +12% |
| random-baseline | 0.6495 | -0.0206 | -3% |

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
| In general, do you find life exciting, pretty routine, or du... | 0.0337 | 0.9129 |
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| Please tell me whether or not you think it should be possibl... | 0.1067 | 0.8165 |
| Consider somebody who is against all churches and religion. ... | 0.1190 | 0.8165 |
| Consider somebody who is against all churches and religion. ... | 0.1233 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please tell me whether or not you think it should be possibl... | 0.8901 | -0.8165 |
| Do you favor or oppose the death penalty for persons convict... | 0.8903 | -0.8165 |
| Do you happen to have in your home or garage any guns or rev... | 0.8962 | -0.1826 |
| Compared with American families in general, would you say yo... | 0.9693 | -0.5774 |
| Would you say your own health, in general, is excellent, goo... | 0.9958 | -0.6325 |
