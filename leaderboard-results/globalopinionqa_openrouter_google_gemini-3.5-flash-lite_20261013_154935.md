# SynthBench Score Card

**Provider:** openrouter/google/gemini-3.5-flash-lite
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 280.5s

## SynthBench Parity Score (SPS)

**SPS: 0.7700 [0.7354, 0.8010]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6632 [0.6161, 0.7030] | ███████░░░ |
| P_rank  Rank-Order | 0.6851 [0.6225, 0.7405] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9617 [0.9216, 0.9762] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3368 |
| Median JSD | 0.2831 |
| Mean Kendall's tau | 0.3702 |
| Composite Parity (legacy) | 0.6741 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1121 | +20% |
| random-baseline | 0.6495 | +0.0246 | +4% |

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
| As I read some specific policies of [American] President Geo... | 0.0003 | 1.0000 |
| Do you think this change in the working conditions for ordin... | 0.0008 | 1.0000 |
| Please tell me if you approve or disapprove of the way Presi... | 0.0030 | 1.0000 |
| Do you think the U.S. should keep military troops in Iraq un... | 0.0176 | 1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.3162 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9290 | -0.6325 |
