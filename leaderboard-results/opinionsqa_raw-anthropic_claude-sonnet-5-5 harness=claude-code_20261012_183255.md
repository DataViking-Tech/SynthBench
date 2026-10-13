# SynthBench Score Card

**Provider:** raw-anthropic/claude-sonnet-5-5 harness=claude-code
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 2272.5s

## SynthBench Parity Score (SPS)

**SPS: 0.7707 [0.7357, 0.7986]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6288 [0.5749, 0.6766] | ██████░░░░ |
| P_rank  Rank-Order | 0.6891 [0.6377, 0.7356] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3712 |
| Median JSD | 0.3198 |
| Mean Kendall's tau | 0.3781 |
| Composite Parity (legacy) | 0.6589 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0969 | +17% |
| random-baseline | 0.6495 | +0.0094 | +1% |

## What These Scores Mean

- **SPS** (SynthBench Parity Score): The overall score — average of all metrics. 0 = random noise, 1 = indistinguishable from real humans.
- **P_dist** (Distributional Parity): How closely does the AI's answer distribution match real humans? If 60% of humans say 'yes' and the AI says 'yes' 60% of the time, that's a perfect match. 0 = completely different, 1 = identical distributions.
- **P_rank** (Rank-Order Parity): Does the AI get the preference ordering right? If humans prefer A > B > C, does the AI agree — even if the exact percentages differ? 0 = reversed ordering, 1 = perfect agreement.
- **P_refuse** (Refusal Calibration): Does the AI refuse to answer at appropriate rates? Humans sometimes decline sensitive questions. An AI that never refuses, or refuses too often, is miscalibrated. 0 = rates completely off, 1 = perfect match.
- **P_cond** (Conditioning Fidelity): When told 'respond as a 65-year-old conservative,' does the AI actually shift its answers? Higher = better demographic role-playing. (When available.)
- **P_sub** (Subgroup Consistency): Is the AI equally accurate across all demographics, or does it nail some groups and miss others? (When available.)

## Temporal Breakdown (by Survey Year)

Scores stratified by Pew ATP survey wave year. Rising P_dist in recent years may indicate training-data contamination.

| Year | P_dist | P_rank | Mean JSD | Questions |
|------|--------|--------|----------|-----------|
| 2017 | 0.6350 | 0.6942 | 0.3650 | 99 |
| 2018 | 0.0175 | 0.1838 | 0.9825 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How well, if at all, do the following words or phrases descr... | 0.0191 | 0.5976 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Have you ever had your pay or hours reduced because your emp... | 0.0333 | 0.7071 |
| Not including in military combat or as part of your job, hav... | 0.0368 | 0.8165 |
| Do you think the following are likely to happen as a result ... | 0.0542 | 0.3333 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Which statement comes closer to your views, even if neither ... | 0.9443 | -0.8165 |
| Which of the following statements best describes how you fee... | 0.9497 | -0.8165 |
| Which of the following statements best describes how you fee... | 0.9582 | -0.8165 |
| How much, if at all, do you think the ease with which people... | 0.9790 | -0.6325 |
| Please tell us whether you are satisfied or dissatisfied wit... | 0.9825 | -0.6325 |
