# SynthBench Score Card

**Provider:** openrouter/qwen/qwen3.8-flash
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 948.9s

## SynthBench Parity Score (SPS)

**SPS: 0.7937 [0.7635, 0.8180]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7274 [0.6931, 0.7560] | ███████░░░ |
| P_rank  Rank-Order | 0.6739 [0.6058, 0.7305] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9797 [0.9684, 0.9862] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2726 |
| Median JSD | 0.2458 |
| Mean Kendall's tau | 0.3477 |
| Composite Parity (legacy) | 0.7006 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1386 | +25% |
| random-baseline | 0.6495 | +0.0511 | +8% |

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
| In general, do you think our country is covered fairly or un... | 0.0004 | 1.0000 |
| On the subject of Iraq, did your country make the right deci... | 0.0111 | 1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| Again, which one better describes George W. Bush...He makes ... | 0.0272 | 1.0000 |
| Do you think people should be able to say these types of thi... | 0.0326 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you personally believe that getting a divorce is morally ... | 0.6303 | -0.1826 |
| For each statement, please tell me whether you completely ag... | 0.6802 | -0.7071 |
| Do you approve or disapprove of the U.S. military operation ... | 0.6983 | -1.0000 |
| Thinking about our relations with China, in your view, which... | 0.7315 | -0.1195 |
| Which statement comes closer to your own views, even if neit... | 0.7544 | -0.1179 |
