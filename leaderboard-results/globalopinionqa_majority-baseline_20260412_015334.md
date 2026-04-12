# SynthBench Score Card

**Provider:** majority-baseline
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 0.2s

## SynthBench Parity Score (SPS)

**SPS: 0.6896 [0.4930, 0.5924]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5342 [0.4868, 0.5792] | █████░░░░░ |
| P_rank  Rank-Order | 0.5547 [0.4929, 0.6236] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9797 [0.9684, 0.9862] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4658 |
| Median JSD | 0.4772 |
| Mean Kendall's tau | 0.1094 |
| Composite Parity (legacy) | 0.5445 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | -0.0175 | -3% |
| random-baseline | 0.6495 | -0.1050 | -16% |

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
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| (Now/And thinking about the American people...) Which of the... | 0.0524 | 1.0000 |
| (Now I am going to read you a list of things that may be pro... | 0.0881 | 0.6325 |
| Please tell me which of the following is closest to your own... | 0.1038 | 1.0000 |
| Again, which one better describes George W. Bush...He makes ... | 0.1052 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.3162 |
| Here is the 'ladder of life.'  Let's suppose the top of the ... | 0.9525 | -0.4264 |
| As I read a list of groups and organizations, please tell me... | 0.9585 | -0.7071 |
| As I read a list of groups and organizations, please tell me... | 0.9589 | -0.7071 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9595 | -0.6325 |
