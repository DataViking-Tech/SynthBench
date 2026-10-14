# SynthBench Score Card

**Provider:** openrouter/deepseek/deepseek-v4.1-flash
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 365.6s

## SynthBench Parity Score (SPS)

**SPS: 0.7940 [0.7613, 0.8218]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7068 [0.6574, 0.7459] | ███████░░░ |
| P_rank  Rank-Order | 0.6954 [0.6278, 0.7503] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9797 [0.9684, 0.9862] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2932 |
| Median JSD | 0.2461 |
| Mean Kendall's tau | 0.3907 |
| Composite Parity (legacy) | 0.7011 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1391 | +25% |
| random-baseline | 0.6495 | +0.0516 | +8% |

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
| Thinking about possible war with Iraq, would you favor or op... | 0.0000 | 1.0000 |
| In your opinion, has the European Union provided too much fi... | 0.0002 | 1.0000 |
| Do you think the government of Ukraine respects the personal... | 0.0043 | 1.0000 |
| On the subject of Iraq, did your country make the right deci... | 0.0154 | -1.0000 |
| Please tell me if you approve or disapprove of the way Prime... | 0.0176 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please tell me if you have a very favorable, somewhat favora... | 0.8119 | -0.1195 |
| Please tell me if you have a very favorable, somewhat favora... | 0.8564 | -0.5976 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.3162 |
