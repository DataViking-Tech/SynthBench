# SynthBench Score Card

**Provider:** althing/openrouter/anthropic/claude-haiku-5.5
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 325.9s

## SynthBench Parity Score (SPS)

**SPS: 0.8029 [0.7730, 0.8291]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6917 [0.6487, 0.7260] | ███████░░░ |
| P_rank  Rank-Order | 0.7491 [0.6957, 0.7902] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9681 [0.9550, 0.9755] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3083 |
| Median JSD | 0.2810 |
| Mean Kendall's tau | 0.4981 |
| Composite Parity (legacy) | 0.7204 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1584 | +28% |
| random-baseline | 0.6495 | +0.0709 | +11% |

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
| I am going to name an institution in this country. As far as... | 0.0789 | 0.8165 |
| Would you be for or against sex education in the public scho... | 0.0798 | 0.8165 |
| Please tell me whether or not you think it should be possibl... | 0.1067 | 0.8165 |
| Consider somebody who is against all churches and religion. ... | 0.1190 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Would you say that most of the time people try to be helpful... | 0.6583 | -0.2357 |
| Do you believe there is a life after death?... | 0.7016 | -0.8165 |
| Do you think most people would try to take advantage of you ... | 0.7212 | -0.2357 |
| Generally speaking, would you say that most people can be tr... | 0.7427 | -0.2357 |
| Please tell me whether or not you think it should be possibl... | 0.8901 | -0.8165 |
