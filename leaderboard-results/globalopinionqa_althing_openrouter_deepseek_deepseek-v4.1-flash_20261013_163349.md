# SynthBench Score Card

**Provider:** althing/openrouter/deepseek/deepseek-v4.1-flash
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 715.4s

## SynthBench Parity Score (SPS)

**SPS: 0.7782 [0.7443, 0.8068]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6609 [0.6199, 0.6988] | ███████░░░ |
| P_rank  Rank-Order | 0.6941 [0.6244, 0.7469] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9797 [0.9684, 0.9862] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3391 |
| Median JSD | 0.2926 |
| Mean Kendall's tau | 0.3882 |
| Composite Parity (legacy) | 0.6775 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1155 | +21% |
| random-baseline | 0.6495 | +0.0280 | +4% |

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
| Do you think the U.S. should keep military troops in Iraq un... | 0.0030 | 1.0000 |
| As I read some specific policies of [American] President Geo... | 0.0187 | 1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| (Now/And thinking about the American people...) Which of the... | 0.0524 | 1.0000 |
| I’d like your opinion about some possible international conc... | 0.0713 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please tell me if you have a very favorable, somewhat favora... | 0.7314 | -0.3586 |
| Which statement comes closer to your own views, even if neit... | 0.7544 | -0.1179 |
| Please tell me if you have a very favorable, somewhat favora... | 0.7656 | -0.1195 |
| Please tell me if you have a very favorable, somewhat favora... | 0.8209 | -0.1195 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
