# SynthBench Score Card

**Provider:** althing/openrouter/anthropic/claude-haiku-5.5 tpl=structured
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 769.9s

## SynthBench Parity Score (SPS)

**SPS: 0.8344 [0.8174, 0.8500]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7182 [0.6881, 0.7476] | ███████░░░ |
| P_rank  Rank-Order | 0.7909 [0.7610, 0.8142] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2818 |
| Median JSD | 0.2611 |
| Mean Kendall's tau | 0.5818 |
| Composite Parity (legacy) | 0.7545 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1925 | +34% |
| random-baseline | 0.6495 | +0.1050 | +16% |

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
| 2017 | 0.7197 | 0.7922 | 0.2803 | 99 |
| 2018 | 0.5675 | 0.6581 | 0.4325 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Have you ever had your pay or hours reduced because your emp... | 0.0333 | 0.7071 |
| Not including in military combat or as part of your job, hav... | 0.0368 | 0.8165 |
| Do you think men and women are basically similar or basicall... | 0.0582 | 0.8165 |
| How often, if ever, do you visit websites about guns, huntin... | 0.0765 | 0.8367 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How much of a problem was gun violence in the community wher... | 0.5552 | 0.3162 |
| In the last 12 months, how often did you and your neighbors ... | 0.5608 | 0.3563 |
| How worried are you right now about not having enough to pay... | 0.5640 | 0.0000 |
| Regardless of whether or not you own a gun, have you ever fi... | 0.5721 | 0.0000 |
| How often, if ever, did you use air guns, such as paintball,... | 0.5850 | 0.0000 |
