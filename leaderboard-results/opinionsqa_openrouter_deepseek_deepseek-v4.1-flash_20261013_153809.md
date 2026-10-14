# SynthBench Score Card

**Provider:** openrouter/deepseek/deepseek-v4.1-flash
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 353.5s

## SynthBench Parity Score (SPS)

**SPS: 0.8718 [0.8585, 0.8843]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7897 [0.7697, 0.8110] | ████████░░ |
| P_rank  Rank-Order | 0.8313 [0.8067, 0.8528] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2103 |
| Median JSD | 0.2029 |
| Mean Kendall's tau | 0.6626 |
| Composite Parity (legacy) | 0.8105 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.2485 | +44% |
| random-baseline | 0.6495 | +0.1610 | +25% |

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
| 2017 | 0.7888 | 0.8304 | 0.2112 | 99 |
| 2018 | 0.8726 | 0.9183 | 0.1274 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think men and women are basically similar or basicall... | 0.0044 | 1.0000 |
| Have you ever had your pay or hours reduced because your emp... | 0.0144 | 0.9129 |
| Do you think the following are likely to happen as a result ... | 0.0195 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| How often, if ever, do you participate in online discussion ... | 0.0308 | 0.8367 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think it is very likely, somewhat likely, not very li... | 0.4011 | 0.6325 |
| How enthusiastic are you, if at all, about the development o... | 0.4216 | 0.5976 |
| On a different subject, would you say that society generally... | 0.4528 | 0.3333 |
| How worried are you right now about not having enough to pay... | 0.4698 | 0.6325 |
| How much, if at all, do you think the ease with which people... | 0.4785 | 0.6325 |
