# SynthBench Score Card

**Provider:** openrouter/google/gemini-2.5-flash
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 137.2s

## SynthBench Parity Score (SPS)

**SPS: 0.7895 [0.7578, 0.8179]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6924 [0.6491, 0.7324] | ███████░░░ |
| P_rank  Rank-Order | 0.7040 [0.6458, 0.7482] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3076 |
| Median JSD | 0.2418 |
| Mean Kendall's tau | 0.4080 |
| Composite Parity (legacy) | 0.6982 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1362 | +24% |
| random-baseline | 0.6495 | +0.0487 | +7% |

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
| In general, do you find life exciting, pretty routine, or du... | 0.0360 | 0.9129 |
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| Consider a person who believes that Black people are genetic... | 0.0779 | 0.3333 |
| Would you be for or against sex education in the public scho... | 0.0798 | 0.8165 |
| Which of these statements comes closest to describing your f... | 0.0877 | 0.7379 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Would you say your own health, in general, is excellent, goo... | 0.6251 | 0.0000 |
| Do you strongly agree, agree, disagree, or strongly disagree... | 0.6572 | -0.3162 |
| Do you believe there is a life after death?... | 0.7016 | -0.8165 |
| Which statement comes closest to expressing what you believe... | 0.7449 | -0.2646 |
| Please indicate whether you strongly agree, agree, disagree,... | 0.8098 | -0.1195 |
