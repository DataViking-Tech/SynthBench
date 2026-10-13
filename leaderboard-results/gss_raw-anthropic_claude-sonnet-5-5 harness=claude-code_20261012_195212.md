# SynthBench Score Card

**Provider:** raw-anthropic/claude-sonnet-5-5 harness=claude-code
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 1937.2s

## SynthBench Parity Score (SPS)

**SPS: 0.6420 [0.5966, 0.6883]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.4608 [0.3922, 0.5282] | █████░░░░░ |
| P_rank  Rank-Order | 0.4932 [0.4241, 0.5629] | █████░░░░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.5392 |
| Median JSD | 0.5069 |
| Mean Kendall's tau | -0.0135 |
| Composite Parity (legacy) | 0.4770 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | -0.0850 | -15% |
| random-baseline | 0.6495 | -0.1725 | -27% |

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
| I am going to name an institution in this country. As far as... | 0.0436 | 0.5477 |
| I am going to name an institution in this country. As far as... | 0.0489 | 0.9129 |
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| Consider somebody who is against all churches and religion. ... | 0.1190 | 0.8165 |
| Consider somebody who is against all churches and religion. ... | 0.1233 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| We are faced with many problems in this country, none of whi... | 0.9297 | -0.7071 |
| Would you favor or oppose a law which would require a person... | 0.9388 | -0.8165 |
| If you were asked to use one of four names for your social c... | 0.9565 | -0.6325 |
| Compared with American families in general, would you say yo... | 0.9693 | -0.5774 |
| We are faced with many problems in this country, none of whi... | 0.9782 | -0.7071 |
