# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-haiku-5.5
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 385.8s

## SynthBench Parity Score (SPS)

**SPS: 0.6561 [0.6123, 0.6963]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6099 [0.5588, 0.6607] | ██████░░░░ |
| P_rank  Rank-Order | 0.5813 [0.5161, 0.6404] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.7770 [0.6992, 0.8455] | ████████░░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3901 |
| Median JSD | 0.3999 |
| Mean Kendall's tau | 0.1626 |
| Composite Parity (legacy) | 0.5956 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0336 | +6% |
| random-baseline | 0.6495 | -0.0539 | -8% |

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
| In general, do you think our country is covered fairly or un... | 0.0001 | 0.0000 |
| Do you know someone who went to the U.S., but returned to yo... | 0.0003 | 0.0000 |
| Do you think this change in the availability of modern medic... | 0.0020 | 1.0000 |
| Please tell me if you approve or disapprove of the way Presi... | 0.0097 | 0.0000 |
| Which of these characteristics do you associate with people ... | 0.0112 | -1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.3162 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9290 | -0.6325 |
