# SynthBench Score Card

**Provider:** althing/openrouter/anthropic/claude-sonnet-4.6
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 778.9s

## SynthBench Parity Score (SPS)

**SPS: 0.7586 [0.7282, 0.7868]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6228 [0.5825, 0.6617] | ██████░░░░ |
| P_rank  Rank-Order | 0.6734 [0.6054, 0.7239] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9797 [0.9684, 0.9862] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3772 |
| Median JSD | 0.3925 |
| Mean Kendall's tau | 0.3468 |
| Composite Parity (legacy) | 0.6481 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0861 | +15% |
| random-baseline | 0.6495 | -0.0014 | -0% |

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
| Do you think the U.S. should keep military troops in Iraq un... | 0.0495 | 1.0000 |
| (Now/And thinking about the American people...) Which of the... | 0.0524 | 1.0000 |
| Thinking about the future of your country, please tell me wh... | 0.0530 | 0.9129 |
| Which of these characteristics do you associate with people ... | 0.0619 | -1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you personally believe that drinking alcohol is morally a... | 0.7176 | -0.9129 |
| Which statement comes closer to your own views, even if neit... | 0.7544 | -0.1179 |
| Do you personally believe that getting a divorce is morally ... | 0.7605 | -0.7071 |
| Thinking about our relations with China, in your view, which... | 0.7658 | 0.0000 |
| Please tell me if you have a very favorable, somewhat favora... | 0.7866 | -0.3586 |
