# SynthBench Score Card

**Provider:** althing/anthropic/claude-sonnet-4-6 harness=claude-code
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 3419.6s

## SynthBench Parity Score (SPS)

**SPS: 0.7696 [0.7407, 0.7976]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6503 [0.6120, 0.6885] | ███████░░░ |
| P_rank  Rank-Order | 0.6787 [0.6126, 0.7344] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9797 [0.9684, 0.9862] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3497 |
| Median JSD | 0.3409 |
| Mean Kendall's tau | 0.3574 |
| Composite Parity (legacy) | 0.6645 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1025 | +18% |
| random-baseline | 0.6495 | +0.0150 | +2% |

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
| Which of these characteristics do you associate with (the Ch... | 0.0053 | 1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| Do you think this change in the availability of modern medic... | 0.0339 | -1.0000 |
| As I read some specific policies of [American] President Geo... | 0.0479 | 1.0000 |
| (Now/And thinking about the American people...) Which of the... | 0.0524 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Now I am going to read you a list of things that may be prob... | 0.6490 | -0.5477 |
| And thinking about some political leaders and organizations ... | 0.6625 | -0.2357 |
| Do you approve or disapprove of the U.S. military operation ... | 0.6983 | -1.0000 |
| Which statement comes closer to your own views, even if neit... | 0.7544 | -0.1179 |
| Thinking about our relations with China, in your view, which... | 0.7658 | 0.0000 |
