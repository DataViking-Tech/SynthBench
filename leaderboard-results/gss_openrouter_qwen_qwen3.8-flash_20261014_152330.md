# SynthBench Score Card

**Provider:** openrouter/qwen/qwen3.8-flash
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 414.6s

## SynthBench Parity Score (SPS)

**SPS: 0.8360 [0.8107, 0.8541]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7571 [0.7258, 0.7842] | ████████░░ |
| P_rank  Rank-Order | 0.7789 [0.7396, 0.8116] | ████████░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2429 |
| Median JSD | 0.2128 |
| Mean Kendall's tau | 0.5578 |
| Composite Parity (legacy) | 0.7680 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.2060 | +37% |
| random-baseline | 0.6495 | +0.1185 | +18% |

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
| Generally speaking, would you say that most people can be tr... | 0.0201 | 1.0000 |
| Do you consider the amount of federal income tax which you h... | 0.0306 | 0.9129 |
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| Would you be for or against sex education in the public scho... | 0.0798 | 0.8165 |
| I am going to name an institution in this country. As far as... | 0.0930 | 0.5477 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| I'm going to show you a seven-point scale on which the polit... | 0.4359 | 0.5000 |
| Please indicate whether you strongly agree, agree, disagree,... | 0.4752 | 0.3162 |
| Should divorce in this country be easier or more difficult t... | 0.4969 | 0.1826 |
| Do you agree strongly, agree somewhat, neither agree nor dis... | 0.5455 | -0.2582 |
| Do you believe there is a life after death?... | 0.7016 | -0.8165 |
