# SynthBench Score Card

**Provider:** openrouter/qwen/qwen3.8-flash
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 852.2s

## SynthBench Parity Score (SPS)

**SPS: 0.7980 [0.7695, 0.8216]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7364 [0.7065, 0.7639] | ███████░░░ |
| P_rank  Rank-Order | 0.6783 [0.6126, 0.7345] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9794 [0.9681, 0.9858] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2636 |
| Median JSD | 0.2459 |
| Mean Kendall's tau | 0.3566 |
| Composite Parity (legacy) | 0.7073 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1453 | +26% |
| random-baseline | 0.6495 | +0.0578 | +9% |

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
| On the subject of Iraq, did your country make the right deci... | 0.0022 | 1.0000 |
| Again, which one better describes George W. Bush...He makes ... | 0.0051 | 1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| Do you think people should be able to say these types of thi... | 0.0326 | 1.0000 |
| Please tell me if you approve or disapprove of the way Prime... | 0.0422 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think that using military force against countries tha... | 0.5264 | 0.2357 |
| Do you think the government of Ukraine respects the personal... | 0.5751 | -1.0000 |
| For each statement, please tell me whether you completely ag... | 0.6100 | -0.5477 |
| Do you approve or disapprove of the U.S. military operation ... | 0.6983 | -1.0000 |
| Which statement comes closer to your own views, even if neit... | 0.7544 | -0.1179 |
