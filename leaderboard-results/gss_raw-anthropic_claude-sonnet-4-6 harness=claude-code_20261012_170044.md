# SynthBench Score Card

**Provider:** raw-anthropic/claude-sonnet-4-6 harness=claude-code
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 2652.1s

## SynthBench Parity Score (SPS)

**SPS: 0.7670 [0.7304, 0.8008]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6222 [0.5597, 0.6701] | ██████░░░░ |
| P_rank  Rank-Order | 0.7068 [0.6488, 0.7546] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3778 |
| Median JSD | 0.3007 |
| Mean Kendall's tau | 0.4137 |
| Composite Parity (legacy) | 0.6645 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1025 | +18% |
| random-baseline | 0.6495 | +0.0150 | +2% |

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
| I am going to name an institution in this country. As far as... | 0.0489 | 0.9129 |
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| I am going to name an institution in this country. As far as... | 0.0665 | 0.9129 |
| Would you be for or against sex education in the public scho... | 0.0798 | 0.8165 |
| Please tell me whether or not you think it should be possibl... | 0.1067 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| I'm going to show you a seven-point scale on which the polit... | 0.8837 | -0.3571 |
| Which of these statements comes closest to describing your f... | 0.8919 | -0.6325 |
| Do you happen to have in your home or garage any guns or rev... | 0.9495 | -0.2357 |
| Compared with American families in general, would you say yo... | 0.9693 | -0.5774 |
| Would you say your own health, in general, is excellent, goo... | 0.9958 | -0.6325 |
