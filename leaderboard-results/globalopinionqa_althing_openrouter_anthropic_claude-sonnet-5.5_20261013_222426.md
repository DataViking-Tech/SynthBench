# SynthBench Score Card

**Provider:** althing/openrouter/anthropic/claude-sonnet-5.5
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 601.7s

## SynthBench Parity Score (SPS)

**SPS: 0.7654 [0.7335, 0.7936]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6434 [0.6033, 0.6824] | ██████░░░░ |
| P_rank  Rank-Order | 0.6797 [0.6139, 0.7350] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9731 [0.9594, 0.9821] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3566 |
| Median JSD | 0.3496 |
| Mean Kendall's tau | 0.3594 |
| Composite Parity (legacy) | 0.6615 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0995 | +18% |
| random-baseline | 0.6495 | +0.0120 | +2% |

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
| Do you think this change in the working conditions for ordin... | 0.0034 | 1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| Do you think the U.S. should keep military troops in Iraq un... | 0.0234 | 1.0000 |
| Do you know someone who went to the U.S., but returned to yo... | 0.0353 | 1.0000 |
| Do you think this change in the availability of modern medic... | 0.0453 | -1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| And thinking about some political leaders and organizations ... | 0.6625 | -0.2357 |
| Do you approve or disapprove of the U.S. military operation ... | 0.6983 | -1.0000 |
| Which statement comes closer to your own views, even if neit... | 0.7544 | -0.1179 |
| Thinking about our relations with China, in your view, which... | 0.7658 | 0.0000 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
