# SynthBench Score Card

**Provider:** althing/anthropic/claude-sonnet-5-5 harness=claude-code
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 2850.3s

## SynthBench Parity Score (SPS)

**SPS: 0.8046 [0.7778, 0.8263]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6713 [0.6289, 0.7108] | ███████░░░ |
| P_rank  Rank-Order | 0.7482 [0.7082, 0.7820] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3287 |
| Median JSD | 0.3043 |
| Mean Kendall's tau | 0.4964 |
| Composite Parity (legacy) | 0.7098 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1478 | +26% |
| random-baseline | 0.6495 | +0.0602 | +9% |

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
| 2017 | 0.6723 | 0.7491 | 0.3277 | 99 |
| 2018 | 0.5675 | 0.6581 | 0.4325 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think the following are likely to happen as a result ... | 0.0060 | 1.0000 |
| Thinking about the people you know, including yourself, do y... | 0.0143 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Which of the following statements best describes how you fee... | 0.0251 | 0.3333 |
| Have you ever had your pay or hours reduced because your emp... | 0.0333 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think men and women are basically similar or basicall... | 0.7490 | 0.0000 |
| Thinking about when you were growing up, as far as you know,... | 0.8239 | -0.2357 |
| How well, if at all, do the following words or phrases descr... | 0.8690 | -0.3162 |
| Which of the following statements comes closer to your feeli... | 0.9357 | -0.7071 |
| Which statement comes closer to your views, even if neither ... | 0.9443 | -0.8165 |
