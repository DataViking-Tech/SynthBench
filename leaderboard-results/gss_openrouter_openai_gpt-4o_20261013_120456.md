# SynthBench Score Card

**Provider:** openrouter/openai/gpt-4o
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 270.7s

## SynthBench Parity Score (SPS)

**SPS: 0.8024 [0.7712, 0.8308]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7049 [0.6588, 0.7478] | ███████░░░ |
| P_rank  Rank-Order | 0.7302 [0.6769, 0.7752] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2951 |
| Median JSD | 0.2334 |
| Mean Kendall's tau | 0.4604 |
| Composite Parity (legacy) | 0.7175 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1555 | +28% |
| random-baseline | 0.6495 | +0.0680 | +10% |

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
| I am going to name an institution in this country. As far as... | 0.0124 | 1.0000 |
| I am going to name an institution in this country. As far as... | 0.0489 | 0.9129 |
| I am going to name an institution in this country. As far as... | 0.0511 | 0.9129 |
| I am going to name an institution in this country. As far as... | 0.0537 | 1.0000 |
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please indicate whether you strongly agree, agree, disagree,... | 0.6379 | 0.0000 |
| Do you think most people would try to take advantage of you ... | 0.6386 | -0.1826 |
| Do you believe there is a life after death?... | 0.7016 | -0.8165 |
| Generally speaking, would you say that most people can be tr... | 0.7427 | -0.2357 |
| Do you happen to have in your home or garage any guns or rev... | 0.7429 | 0.1826 |
