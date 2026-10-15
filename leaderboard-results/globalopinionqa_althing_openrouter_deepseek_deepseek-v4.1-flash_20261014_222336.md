# SynthBench Score Card

**Provider:** althing/openrouter/deepseek/deepseek-v4.1-flash
**Dataset:** globalopinionqa (525 questions)
**Samples per question:** 30
**Elapsed:** 5232.1s

## SynthBench Parity Score (SPS)

**SPS: 0.7917 [0.7782, 0.8025]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6768 [0.6614, 0.6927] | ███████░░░ |
| P_rank  Rank-Order | 0.7181 [0.6944, 0.7395] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9803 [0.9767, 0.9832] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3232 |
| Median JSD | 0.3070 |
| Mean Kendall's tau | 0.4362 |
| Composite Parity (legacy) | 0.6974 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1354 | +24% |
| random-baseline | 0.6495 | +0.0479 | +7% |

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
| Is there any area within a kilometer/mile of your home where... | 0.0000 | 1.0000 |
| Do you think the U.S. should keep military troops in Iraq un... | 0.0004 | 1.0000 |
| As a result of the earthquake and tsunami did you or members... | 0.0083 | 1.0000 |
| Now I will read a list of some things that have happened in ... | 0.0138 | 1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please tell me if you have a very favorable, somewhat favora... | 0.8560 | -0.3586 |
| Do you think most Muslims in our country today want to adopt... | 0.8706 | -0.7071 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
| Which one of these comes closest to your opinion, number 1 o... | 0.9068 | -0.3586 |
| Do you think of yourself first as your nationality or first ... | 0.9595 | -0.8165 |
