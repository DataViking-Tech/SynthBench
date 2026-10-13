# SynthBench Score Card

**Provider:** raw-anthropic/claude-haiku-5-5 harness=claude-code
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 2588.4s

## SynthBench Parity Score (SPS)

**SPS: 0.7015 [0.6614, 0.7378]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6590 [0.6052, 0.7064] | ███████░░░ |
| P_rank  Rank-Order | 0.6031 [0.5318, 0.6661] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.8423 [0.7746, 0.8976] | ████████░░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3410 |
| Median JSD | 0.2734 |
| Mean Kendall's tau | 0.2061 |
| Composite Parity (legacy) | 0.6311 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0691 | +12% |
| random-baseline | 0.6495 | -0.0185 | -3% |

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
| Do you think this change in the availability of modern medic... | 0.0002 | 1.0000 |
| On the subject of Iraq, did your country make the right deci... | 0.0015 | 0.0000 |
| Which of these characteristics do you associate with people ... | 0.0020 | 0.0000 |
| Now I'd like to ask your views about some additional politic... | 0.0058 | 0.0000 |
| (Now/And thinking about the American people...) Which of the... | 0.0138 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.3162 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9290 | -0.6325 |
