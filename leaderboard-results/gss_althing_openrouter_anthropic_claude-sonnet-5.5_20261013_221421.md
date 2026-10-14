# SynthBench Score Card

**Provider:** althing/openrouter/anthropic/claude-sonnet-5.5
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 449.6s

## SynthBench Parity Score (SPS)

**SPS: 0.7612 [0.7230, 0.7935]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6398 [0.5903, 0.6839] | ██████░░░░ |
| P_rank  Rank-Order | 0.6760 [0.6151, 0.7256] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9677 [0.9430, 0.9767] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3602 |
| Median JSD | 0.3094 |
| Mean Kendall's tau | 0.3521 |
| Composite Parity (legacy) | 0.6579 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0959 | +17% |
| random-baseline | 0.6495 | +0.0084 | +1% |

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
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| Do you consider the amount of federal income tax which you h... | 0.0695 | 0.5477 |
| Would you be for or against sex education in the public scho... | 0.0798 | 0.8165 |
| What is your opinion about a married person having sexual re... | 0.0822 | 0.8367 |
| Consider somebody who is against all churches and religion. ... | 0.1190 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think the use of marijuana should be made legal or no... | 0.7644 | -0.8165 |
| Please tell me whether or not you think it should be possibl... | 0.8723 | -0.8165 |
| Please tell me whether or not you think it should be possibl... | 0.8740 | -0.8165 |
| Please tell me whether or not you think it should be possibl... | 0.8901 | -0.8165 |
| Do you favor or oppose the death penalty for persons convict... | 0.8903 | -0.8165 |
