# SynthBench Score Card

**Provider:** openrouter/deepseek/deepseek-v4.1-flash
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 265.9s

## SynthBench Parity Score (SPS)

**SPS: 0.8337 [0.8082, 0.8523]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7309 [0.6986, 0.7616] | ███████░░░ |
| P_rank  Rank-Order | 0.7980 [0.7574, 0.8275] | ████████░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2691 |
| Median JSD | 0.2521 |
| Mean Kendall's tau | 0.5961 |
| Composite Parity (legacy) | 0.7645 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.2025 | +36% |
| random-baseline | 0.6495 | +0.1150 | +18% |

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
| In general, do you find life exciting, pretty routine, or du... | 0.0400 | 0.9129 |
| We are faced with many problems in this country, none of whi... | 0.0467 | 0.6667 |
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| Would you be for or against sex education in the public scho... | 0.0798 | 0.8165 |
| Generally speaking, would you say that most people can be tr... | 0.0962 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Some people say that people get ahead by their own hard work... | 0.4783 | 0.5477 |
| How often do you attend religious services?... | 0.4990 | 0.4714 |
| Do you believe there is a life after death?... | 0.7016 | -0.8165 |
| Do you agree strongly, agree somewhat, neither agree nor dis... | 0.7077 | -0.1155 |
| Which statement comes closest to expressing what you believe... | 0.7373 | -0.0658 |
