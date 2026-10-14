# SynthBench Score Card

**Provider:** openrouter/google/gemini-3.8-flash
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 1709.3s

## SynthBench Parity Score (SPS)

**SPS: 0.7013 [0.6643, 0.7355]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5387 [0.4774, 0.5987] | █████░░░░░ |
| P_rank  Rank-Order | 0.5710 [0.5114, 0.6262] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4613 |
| Median JSD | 0.3865 |
| Mean Kendall's tau | 0.1419 |
| Composite Parity (legacy) | 0.5548 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | -0.0072 | -1% |
| random-baseline | 0.6495 | -0.0947 | -15% |

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
| 2017 | 0.5440 | 0.5749 | 0.4560 | 99 |
| 2018 | 0.0175 | 0.1838 | 0.9825 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think the following are likely to happen as a result ... | 0.0053 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Have you ever had your pay or hours reduced because your emp... | 0.0333 | 0.7071 |
| Not including in military combat or as part of your job, hav... | 0.0368 | 0.8165 |
| How well, if at all, do the following words or phrases descr... | 0.0482 | 0.5976 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How much, if at all, do you think the ease with which people... | 0.9790 | -0.6325 |
| Thinking about when you were growing up, as far as you know,... | 0.9809 | -0.7071 |
| Please tell us whether you are satisfied or dissatisfied wit... | 0.9825 | -0.6325 |
| How much of a problem was gun violence in the community wher... | 0.9838 | -0.6325 |
| How safe, if at all, would you say your local community is f... | 0.9878 | -0.6325 |
