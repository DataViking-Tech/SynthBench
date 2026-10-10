# SynthBench Score Card

**Provider:** althing/openai/gpt-6-luna harness=codex
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 2072.8s

## SynthBench Parity Score (SPS)

**SPS: 0.7623 [0.7308, 0.7923]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6653 [0.6198, 0.7046] | ███████░░░ |
| P_rank  Rank-Order | 0.6418 [0.5797, 0.7002] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9797 [0.9684, 0.9862] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3347 |
| Median JSD | 0.3117 |
| Mean Kendall's tau | 0.2835 |
| Composite Parity (legacy) | 0.6535 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0915 | +16% |
| random-baseline | 0.6495 | +0.0040 | +1% |

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
| Do you think the U.S. should keep military troops in Iraq un... | 0.0170 | 1.0000 |
| Again, which one better describes George W. Bush...He makes ... | 0.0179 | 1.0000 |
| Do you think people should be able to say these types of thi... | 0.0188 | 1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| If robots and computers were able to do much of the work cur... | 0.0268 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you personally believe that getting a divorce is morally ... | 0.7605 | -0.7071 |
| Please tell me if you have a very favorable, somewhat favora... | 0.7656 | -0.1195 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.3162 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9290 | -0.6325 |
