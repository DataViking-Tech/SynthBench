# SynthBench Score Card

**Provider:** althing/openrouter/meta-llama/llama-3.3-70b-instruct
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 534.8s

## SynthBench Parity Score (SPS)

**SPS: 0.7639 [0.7324, 0.7914]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6309 [0.5953, 0.6694] | ██████░░░░ |
| P_rank  Rank-Order | 0.6809 [0.6176, 0.7366] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9797 [0.9684, 0.9862] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3691 |
| Median JSD | 0.3531 |
| Mean Kendall's tau | 0.3618 |
| Composite Parity (legacy) | 0.6559 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0939 | +17% |
| random-baseline | 0.6495 | +0.0064 | +1% |

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
| Again, which one better describes George W. Bush...He makes ... | 0.0010 | 1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| (Now/And thinking about the American people...) Which of the... | 0.0524 | 1.0000 |
| (Now I am going to read you a list of things that may be pro... | 0.0881 | 0.6325 |
| Please tell me which of the following is closest to your own... | 0.1038 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you approve or disapprove of the U.S. military operation ... | 0.6983 | -1.0000 |
| Which statement comes closer to your own views, even if neit... | 0.7544 | -0.1179 |
| Do you personally believe that getting a divorce is morally ... | 0.7605 | -0.7071 |
| Now I am going to read you a list of things that may be prob... | 0.7828 | -0.7071 |
| Please tell me if you have a very favorable, somewhat favora... | 0.8135 | 0.0000 |
