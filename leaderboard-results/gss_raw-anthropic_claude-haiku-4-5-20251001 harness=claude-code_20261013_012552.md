# SynthBench Score Card

**Provider:** raw-anthropic/claude-haiku-4-5-20251001 harness=claude-code
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 4483.8s

## SynthBench Parity Score (SPS)

**SPS: 0.6327 [0.5900, 0.6724]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5444 [0.4880, 0.5994] | █████░░░░░ |
| P_rank  Rank-Order | 0.4990 [0.4464, 0.5544] | █████░░░░░ |
| P_refuse Refusal Cal. | 0.8547 [0.8079, 0.8884] | █████████░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4556 |
| Median JSD | 0.4536 |
| Mean Kendall's tau | -0.0021 |
| Composite Parity (legacy) | 0.5217 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | -0.0403 | -7% |
| random-baseline | 0.6495 | -0.1278 | -20% |

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
| Consider a person who believes that Black people are genetic... | 0.0239 | 0.3333 |
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| Please tell me whether or not you think it should be possibl... | 0.0998 | 0.3333 |
| I am going to name an institution in this country. As far as... | 0.1146 | 0.6667 |
| I am going to name an institution in this country. As far as... | 0.1169 | 0.5477 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you consider the amount of federal income tax which you h... | 0.9111 | -0.2357 |
| If you were asked to use one of four names for your social c... | 0.9565 | -0.6325 |
| Compared with American families in general, would you say yo... | 0.9693 | -0.5774 |
| We are interested in how people are getting along financiall... | 0.9806 | -0.7071 |
| Would you say your own health, in general, is excellent, goo... | 0.9958 | -0.6325 |
