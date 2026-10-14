# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-haiku-5.5
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 328.9s

## SynthBench Parity Score (SPS)

**SPS: 0.7303 [0.6882, 0.7696]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5981 [0.5429, 0.6518] | ██████░░░░ |
| P_rank  Rank-Order | 0.6441 [0.5806, 0.7013] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9486 [0.8991, 0.9674] | █████████░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4019 |
| Median JSD | 0.3489 |
| Mean Kendall's tau | 0.2882 |
| Composite Parity (legacy) | 0.6211 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0591 | +11% |
| random-baseline | 0.6495 | -0.0284 | -4% |

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
| In general, do you find life exciting, pretty routine, or du... | 0.0343 | 0.9129 |
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| Please tell me whether or not you think it should be possibl... | 0.1067 | 0.8165 |
| Consider somebody who is against all churches and religion. ... | 0.1190 | 0.8165 |
| Consider somebody who is against all churches and religion. ... | 0.1233 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you favor or oppose the death penalty for persons convict... | 0.8903 | -0.8165 |
| We are interested in how people are getting along financiall... | 0.8925 | -0.1826 |
| Compared with American families in general, would you say yo... | 0.9693 | -0.5774 |
| Which statement comes closest to expressing what you believe... | 0.9802 | -0.5345 |
| Would you say your own health, in general, is excellent, goo... | 0.9958 | -0.6325 |
