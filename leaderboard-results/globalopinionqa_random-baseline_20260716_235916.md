# SynthBench Score Card

**Provider:** random-baseline
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 0.1s

## SynthBench Parity Score (SPS)

**SPS: 0.7740 [0.7530, 0.7958]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.8904 [0.8704, 0.9078] | █████████░ |
| P_rank  Rank-Order | 0.4519 [0.3954, 0.5047] | █████░░░░░ |
| P_refuse Refusal Cal. | 0.9797 [0.9684, 0.9862] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.1096 |
| Median JSD | 0.0845 |
| Mean Kendall's tau | -0.0962 |
| Composite Parity (legacy) | 0.6712 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1092 | +19% |
| random-baseline | 0.6495 | +0.0216 | +3% |

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
| Overall, was the break-up of Czechoslovakia into two indepen... | 0.0000 | 0.0000 |
| Do you know someone who went to the U.S., but returned to yo... | 0.0003 | 0.0000 |
| Which of these characteristics do you associate with people ... | 0.0016 | 0.0000 |
| In your opinion, has the European Union provided too much fi... | 0.0021 | 0.8165 |
| I am going to read you the same list.  Does...you can openly... | 0.0041 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| On another topic, had you heard that President Barack Obama'... | 0.3264 | -1.0000 |
| Please tell me if you have a very favorable, somewhat favora... | 0.3340 | -0.5270 |
| I'm going to read you a list of issues that human rights org... | 0.3359 | -0.3162 |
| How important is it to have the following things in our coun... | 0.3717 | -0.3162 |
| (Now I am going to read you a list of things that may be pro... | 0.4534 | -0.4000 |
