# SynthBench Score Card

**Provider:** althing/openrouter/openai/gpt-6-luna
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 1280.1s

## SynthBench Parity Score (SPS)

**SPS: 0.8294 [0.8098, 0.8459]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7208 [0.6920, 0.7533] | ███████░░░ |
| P_rank  Rank-Order | 0.7730 [0.7405, 0.8002] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2792 |
| Median JSD | 0.2729 |
| Mean Kendall's tau | 0.5460 |
| Composite Parity (legacy) | 0.7469 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1849 | +33% |
| random-baseline | 0.6495 | +0.0974 | +15% |

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
| 2017 | 0.7224 | 0.7742 | 0.2776 | 99 |
| 2018 | 0.5675 | 0.6581 | 0.4325 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think the following are likely to happen as a result ... | 0.0053 | 1.0000 |
| If driverless vehicles become widespread, which of the follo... | 0.0135 | 1.0000 |
| Thinking about the people you know, including yourself, do y... | 0.0152 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| How often, if ever, do you listen to gun-oriented podcasts o... | 0.0331 | 0.8367 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have you ever personally experienced discrimination or been ... | 0.5345 | -0.3333 |
| Do you think men and women are basically similar or basicall... | 0.5796 | 0.3333 |
| Regardless of whether or not you own a gun, have you ever fi... | 0.5942 | -0.3333 |
| On a different subject, would you say that society generally... | 0.6715 | -0.2357 |
| Thinking about when you were growing up, as far as you know,... | 0.7398 | -0.1826 |
