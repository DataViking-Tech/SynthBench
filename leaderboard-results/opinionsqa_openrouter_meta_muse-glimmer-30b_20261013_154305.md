# SynthBench Score Card

**Provider:** openrouter/meta/muse-glimmer-30b
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 649.2s

## SynthBench Parity Score (SPS)

**SPS: 0.6890 [0.6566, 0.7199]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5769 [0.5249, 0.6250] | ██████░░░░ |
| P_rank  Rank-Order | 0.5212 [0.4738, 0.5636] | █████░░░░░ |
| P_refuse Refusal Cal. | 0.9690 [0.9396, 0.9816] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4231 |
| Median JSD | 0.3843 |
| Mean Kendall's tau | 0.0424 |
| Composite Parity (legacy) | 0.5490 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | -0.0130 | -2% |
| random-baseline | 0.6495 | -0.1005 | -15% |

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
| 2017 | 0.5791 | 0.5219 | 0.4209 | 99 |
| 2018 | 0.3585 | 0.4473 | 0.6415 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Have you ever had your pay or hours reduced because your emp... | 0.0522 | 0.1826 |
| How often, if ever, do you listen to gun-oriented podcasts o... | 0.0552 | 0.4472 |
| If driverless vehicles become widespread, which of the follo... | 0.0786 | 0.3333 |
| Do you think the following are likely to happen as a result ... | 0.0791 | 0.3333 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Would you favor or oppose the following? If the federal gove... | 0.9429 | -0.6325 |
| Does anyone else in your household own any guns (not includi... | 0.9440 | -0.8165 |
| This next question is about friends and family you do not li... | 0.9560 | -0.7237 |
| How well, if at all, do the following words or phrases descr... | 0.9722 | -0.6325 |
| How much of a problem was gun violence in the community wher... | 0.9838 | -0.6325 |
