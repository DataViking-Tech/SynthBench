# SynthBench Score Card

**Provider:** openrouter/google/gemini-2.5-flash-lite
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 132.0s

## SynthBench Parity Score (SPS)

**SPS: 0.7613 [0.7300, 0.7906]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6786 [0.6343, 0.7211] | ███████░░░ |
| P_rank  Rank-Order | 0.6265 [0.5626, 0.6876] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9790 [0.9679, 0.9856] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3214 |
| Median JSD | 0.2529 |
| Mean Kendall's tau | 0.2530 |
| Composite Parity (legacy) | 0.6525 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0905 | +16% |
| random-baseline | 0.6495 | +0.0030 | +0% |

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
| For each of the following statements about the missile strik... | 0.0003 | 1.0000 |
| Which of these characteristics do you associate with (the Ch... | 0.0008 | 1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| (Now/And thinking about the American people...) Which of the... | 0.0524 | 1.0000 |
| Please tell me how worried you are about each of the followi... | 0.0538 | 0.3333 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Which statement comes closer to your own views, even if neit... | 0.7544 | -0.1179 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.3162 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9290 | -0.6325 |
