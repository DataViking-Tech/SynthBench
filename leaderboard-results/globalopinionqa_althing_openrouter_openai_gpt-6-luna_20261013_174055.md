# SynthBench Score Card

**Provider:** althing/openrouter/openai/gpt-6-luna
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 1430.3s

## SynthBench Parity Score (SPS)

**SPS: 0.7602 [0.7255, 0.7910]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6347 [0.5913, 0.6764] | ██████░░░░ |
| P_rank  Rank-Order | 0.6662 [0.6030, 0.7199] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9797 [0.9684, 0.9862] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3653 |
| Median JSD | 0.3689 |
| Mean Kendall's tau | 0.3323 |
| Composite Parity (legacy) | 0.6505 |

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
| For each of the following statements about the missile strik... | 0.0002 | 1.0000 |
| Do you think this change in the availability of modern medic... | 0.0020 | 1.0000 |
| As I read some specific policies of [American] President Geo... | 0.0023 | 1.0000 |
| Again, which one better describes George W. Bush...He makes ... | 0.0132 | 1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you personally believe that getting a divorce is morally ... | 0.7605 | -0.7071 |
| Do you personally believe that drinking alcohol is morally a... | 0.7823 | -0.5477 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.3162 |
