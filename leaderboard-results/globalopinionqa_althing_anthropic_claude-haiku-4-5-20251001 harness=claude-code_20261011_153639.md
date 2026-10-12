# SynthBench Score Card

**Provider:** althing/anthropic/claude-haiku-4-5-20251001 harness=claude-code
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 5141.3s

## SynthBench Parity Score (SPS)

**SPS: 0.7425 [0.7070, 0.7730]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6792 [0.6405, 0.7140] | ███████░░░ |
| P_rank  Rank-Order | 0.6866 [0.6259, 0.7403] | ███████░░░ |
| P_refuse Refusal Cal. | 0.8617 [0.8156, 0.8950] | █████████░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3208 |
| Median JSD | 0.3007 |
| Mean Kendall's tau | 0.3733 |
| Composite Parity (legacy) | 0.6829 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1209 | +22% |
| random-baseline | 0.6495 | +0.0334 | +5% |

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
| Which of these characteristics do you associate with (the Ch... | 0.0003 | 1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| For each of the following statements about the missile strik... | 0.0345 | 1.0000 |
| Now I am going to read you a list of things that may be prob... | 0.0365 | 0.9129 |
| Thinking about the future of your country, please tell me wh... | 0.0520 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you approve or disapprove of the U.S. military operation ... | 0.6983 | -1.0000 |
| Please tell me if you have a very favorable, somewhat favora... | 0.7097 | -0.3586 |
| Which statement comes closer to your own views, even if neit... | 0.7544 | -0.1179 |
| Do you personally believe that getting a divorce is morally ... | 0.7605 | -0.7071 |
| Do you personally believe that drinking alcohol is morally a... | 0.8564 | -0.7071 |
