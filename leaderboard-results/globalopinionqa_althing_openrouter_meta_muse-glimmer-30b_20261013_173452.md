# SynthBench Score Card

**Provider:** althing/openrouter/meta/muse-glimmer-30b
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 1145.0s

## SynthBench Parity Score (SPS)

**SPS: 0.7616 [0.7272, 0.7929]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6364 [0.5911, 0.6765] | ██████░░░░ |
| P_rank  Rank-Order | 0.6721 [0.6076, 0.7262] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9762 [0.9647, 0.9839] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3636 |
| Median JSD | 0.3339 |
| Mean Kendall's tau | 0.3442 |
| Composite Parity (legacy) | 0.6543 |

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
| Do you know someone who went to the U.S., but returned to yo... | 0.0016 | 1.0000 |
| Do you think this change in the availability of modern medic... | 0.0163 | -1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| Do you think our country's efforts to reduce government spen... | 0.0323 | 1.0000 |
| (Now/And thinking about the American people...) Which of the... | 0.0524 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please tell me if you have a very favorable, somewhat favora... | 0.8297 | -0.3586 |
| Please tell me if you have a very favorable, somewhat favora... | 0.8484 | -0.3586 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.3162 |
