# SynthBench Score Card

**Provider:** openrouter/qwen/qwen3.8-flash
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 804.9s

## SynthBench Parity Score (SPS)

**SPS: 0.8343 [0.8085, 0.8537]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7504 [0.7189, 0.7772] | ████████░░ |
| P_rank  Rank-Order | 0.7805 [0.7380, 0.8136] | ████████░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2496 |
| Median JSD | 0.2315 |
| Mean Kendall's tau | 0.5610 |
| Composite Parity (legacy) | 0.7654 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.2035 | +36% |
| random-baseline | 0.6495 | +0.1159 | +18% |

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
| In general, do you find life exciting, pretty routine, or du... | 0.0343 | 0.9129 |
| Which of these statements comes closest to your feelings abo... | 0.0573 | 0.9129 |
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| Generally speaking, would you say that most people can be tr... | 0.0642 | 0.9129 |
| Would you be for or against sex education in the public scho... | 0.0798 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Generally speaking, do you usually think of yourself as a Re... | 0.4288 | 0.2621 |
| Should divorce in this country be easier or more difficult t... | 0.4451 | 0.1826 |
| Please indicate whether you strongly agree, agree, disagree,... | 0.4752 | 0.3162 |
| Do you agree strongly, agree somewhat, neither agree nor dis... | 0.5907 | -0.2582 |
| Do you believe there is a life after death?... | 0.7016 | -0.8165 |
