# SynthBench Score Card

**Provider:** althing/anthropic/claude-haiku-5-5 harness=claude-code
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 3229.8s

## SynthBench Parity Score (SPS)

**SPS: 0.7027 [0.6616, 0.7378]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6897 [0.6458, 0.7304] | ███████░░░ |
| P_rank  Rank-Order | 0.6468 [0.5835, 0.7041] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.7716 [0.7048, 0.8295] | ████████░░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3103 |
| Median JSD | 0.3104 |
| Mean Kendall's tau | 0.2936 |
| Composite Parity (legacy) | 0.6682 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1062 | +19% |
| random-baseline | 0.6495 | +0.0187 | +3% |

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
| Now I'd like to ask your views about some additional politic... | 0.0058 | 0.0000 |
| Again, which one better describes George W. Bush...He makes ... | 0.0065 | 1.0000 |
| And thinking about some political leaders and organizations ... | 0.0174 | 0.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| Which of these characteristics do you associate with (the Ch... | 0.0317 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| (Now I'd like to ask you about some political parties.) Plea... | 0.7583 | -0.3162 |
| Do you personally believe that getting a divorce is morally ... | 0.7605 | -0.7071 |
| Please tell me if you have a very favorable, somewhat favora... | 0.7782 | -0.1195 |
| Do you personally believe that drinking alcohol is morally a... | 0.8564 | -0.7071 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
