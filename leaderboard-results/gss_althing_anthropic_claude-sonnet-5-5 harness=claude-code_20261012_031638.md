# SynthBench Score Card

**Provider:** althing/anthropic/claude-sonnet-5-5 harness=claude-code
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 2257.6s

## SynthBench Parity Score (SPS)

**SPS: 0.7214 [0.6795, 0.7588]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5787 [0.5177, 0.6344] | ██████░░░░ |
| P_rank  Rank-Order | 0.6128 [0.5414, 0.6741] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9726 [0.9650, 0.9782] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4213 |
| Median JSD | 0.3401 |
| Mean Kendall's tau | 0.2257 |
| Composite Parity (legacy) | 0.5958 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0338 | +6% |
| random-baseline | 0.6495 | -0.0538 | -8% |

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
| Please tell me whether or not you think it should be possibl... | 0.0420 | 0.3333 |
| I am going to name an institution in this country. As far as... | 0.0641 | 0.8165 |
| Consider somebody who is against all churches and religion. ... | 0.1190 | 0.8165 |
| Consider somebody who is against all churches and religion. ... | 0.1233 | 0.8165 |
| Suppose there is a community-wide vote on the general housin... | 0.1280 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please tell me whether or not you think it should be possibl... | 0.8740 | -0.8165 |
| Please tell me whether or not you think it should be possibl... | 0.8823 | -0.8165 |
| Please tell me whether or not you think it should be possibl... | 0.8901 | -0.8165 |
| Do you favor or oppose the death penalty for persons convict... | 0.8903 | -0.8165 |
| Would you favor or oppose a law which would require a person... | 0.9388 | -0.8165 |
