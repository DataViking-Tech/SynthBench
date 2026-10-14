# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-sonnet-4.6
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 332.8s

## SynthBench Parity Score (SPS)

**SPS: 0.7769 [0.7405, 0.8078]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6349 [0.5822, 0.6817] | ██████░░░░ |
| P_rank  Rank-Order | 0.7237 [0.6643, 0.7709] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3651 |
| Median JSD | 0.3122 |
| Mean Kendall's tau | 0.4475 |
| Composite Parity (legacy) | 0.6793 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1173 | +21% |
| random-baseline | 0.6495 | +0.0298 | +5% |

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
| Would you be for or against sex education in the public scho... | 0.0798 | 0.8165 |
| Please tell me whether or not you think it should be possibl... | 0.1067 | 0.8165 |
| I am going to name an institution in this country. As far as... | 0.1115 | 0.9129 |
| Consider somebody who is against all churches and religion. ... | 0.1190 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think the use of marijuana should be made legal or no... | 0.7644 | -0.8165 |
| I'm going to show you a seven-point scale on which the polit... | 0.8024 | 0.0524 |
| Do you favor or oppose the death penalty for persons convict... | 0.8903 | -0.8165 |
| Which statement comes closest to expressing what you believe... | 0.9802 | -0.5345 |
| Would you say your own health, in general, is excellent, goo... | 0.9958 | -0.6325 |
