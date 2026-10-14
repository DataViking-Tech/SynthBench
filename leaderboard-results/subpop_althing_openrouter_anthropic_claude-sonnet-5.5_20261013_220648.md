# SynthBench Score Card

**Provider:** althing/openrouter/anthropic/claude-sonnet-5.5
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 711.2s

## SynthBench Parity Score (SPS)

**SPS: 0.7227 [0.6865, 0.7536]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5555 [0.5056, 0.6004] | ██████░░░░ |
| P_rank  Rank-Order | 0.6328 [0.5815, 0.6803] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9902] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4445 |
| Median JSD | 0.4206 |
| Mean Kendall's tau | 0.2656 |
| Composite Parity (legacy) | 0.5941 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0321 | +6% |
| random-baseline | 0.6495 | -0.0554 | -9% |

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
| In the news you are receiving about the Biden administration... | 0.0220 | 1.0000 |
| Do you think that you have ever been at an advantage in your... | 0.1056 | 0.9129 |
| Have your personal views about abortion changed in any way o... | 0.1270 | 0.7071 |
| How much, if anything, have you heard or read about thousand... | 0.1276 | 0.5477 |
| Do you think abortion should be legal or illegal in the situ... | 0.1278 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think abortion should be...... | 0.9442 | -0.6325 |
| Regardless of whether you think abortion should be legal or ... | 0.9490 | -0.5774 |
| Do you think abortion should be…... | 0.9526 | -0.6325 |
| Do you think medication abortion should be legal or illegal ... | 0.9663 | -0.7071 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
