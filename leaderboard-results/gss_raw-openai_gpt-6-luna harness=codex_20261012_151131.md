# SynthBench Score Card

**Provider:** raw-openai/gpt-6-luna harness=codex
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 2674.5s

## SynthBench Parity Score (SPS)

**SPS: 0.7103 [0.6737, 0.7431]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5880 [0.5257, 0.6418] | ██████░░░░ |
| P_rank  Rank-Order | 0.5708 [0.5194, 0.6246] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4120 |
| Median JSD | 0.3732 |
| Mean Kendall's tau | 0.1417 |
| Composite Parity (legacy) | 0.5794 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0174 | +3% |
| random-baseline | 0.6495 | -0.0701 | -11% |

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
| We are faced with many problems in this country, none of whi... | 0.1007 | 0.3333 |
| Please tell me whether or not you think it should be possibl... | 0.1067 | 0.8165 |
| What is your opinion about a married person having sexual re... | 0.1118 | 0.5270 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you happen to have in your home or garage any guns or rev... | 0.9449 | -0.5477 |
| If you were asked to use one of four names for your social c... | 0.9565 | -0.6325 |
| Compared with American families in general, would you say yo... | 0.9693 | -0.5774 |
| Which statement comes closest to expressing what you believe... | 0.9802 | -0.5345 |
| Would you say your own health, in general, is excellent, goo... | 0.9958 | -0.6325 |
