# SynthBench Score Card

**Provider:** althing/openai/gpt-6-luna harness=codex
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 2172.2s

## SynthBench Parity Score (SPS)

**SPS: 0.7822 [0.7486, 0.8117]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6910 [0.6419, 0.7322] | ███████░░░ |
| P_rank  Rank-Order | 0.6835 [0.6207, 0.7376] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3090 |
| Median JSD | 0.2709 |
| Mean Kendall's tau | 0.3670 |
| Composite Parity (legacy) | 0.6873 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1253 | +22% |
| random-baseline | 0.6495 | +0.0378 | +6% |

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
| We are faced with many problems in this country, none of whi... | 0.0347 | 0.6667 |
| We are faced with many problems in this country, none of whi... | 0.0394 | 0.9129 |
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| I am going to name an institution in this country. As far as... | 0.0698 | 0.3333 |
| We are faced with many problems in this country, none of whi... | 0.0730 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think most people would try to take advantage of you ... | 0.7212 | -0.2357 |
| Which statement comes closest to expressing what you believe... | 0.7252 | -0.3944 |
| When a person has a disease that cannot be cured, do you thi... | 0.7928 | -0.3333 |
| If you were asked to use one of four names for your social c... | 0.8701 | -0.1195 |
| Compared with American families in general, would you say yo... | 0.8819 | -0.0861 |
