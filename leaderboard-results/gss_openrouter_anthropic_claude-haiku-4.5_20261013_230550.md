# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-haiku-4.5
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 180.2s

## SynthBench Parity Score (SPS)

**SPS: 0.7344 [0.6916, 0.7718]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6071 [0.5537, 0.6576] | ██████░░░░ |
| P_rank  Rank-Order | 0.6773 [0.6187, 0.7277] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9188 [0.8586, 0.9517] | █████████░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3929 |
| Median JSD | 0.3489 |
| Mean Kendall's tau | 0.3545 |
| Composite Parity (legacy) | 0.6422 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0802 | +14% |
| random-baseline | 0.6495 | -0.0073 | -1% |

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
| Consider somebody who is against all churches and religion. ... | 0.1190 | 0.8165 |
| Consider somebody who is against all churches and religion. ... | 0.1233 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think a person has the right to end his or her own li... | 0.8751 | -0.8165 |
| When a person has a disease that cannot be cured, do you thi... | 0.8895 | -0.8165 |
| Do you consider the amount of federal income tax which you h... | 0.9111 | -0.2357 |
| If you were asked to use one of four names for your social c... | 0.9565 | -0.6325 |
| Would you say your own health, in general, is excellent, goo... | 0.9958 | -0.6325 |
