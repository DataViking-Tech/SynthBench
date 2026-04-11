# SynthBench Score Card

**Provider:** synthpanel/claude-haiku-4-5-20251001
**Dataset:** subpop (200 questions)
**Samples per question:** 30
**Elapsed:** 203.5s

## SynthBench Parity Score (SPS)

**SPS: 0.7732 [0.6658, 0.6893]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.8042 [0.7848, 0.8189] | ████████░░ |
| P_rank  Rank-Order | 0.5513 [0.5337, 0.5708] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9642 [0.9375, 0.9786] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.1958 |
| Median JSD | 0.1663 |
| Mean Kendall's tau | 0.1026 |
| Composite Parity (legacy) | 0.6777 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1157 | +21% |
| random-baseline | 0.6495 | +0.0282 | +4% |

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
| Do you believe that some things happen in life that can’t re... | 0.0249 | 1.0000 |
| Did you refuse to answer the previous question?... | 0.0293 | 0.0000 |
| All in all, do you think that allegations of voter fraud in ... | 0.0297 | 1.0000 |
| When you see or hear news about terrible things happening to... | 0.0326 | 0.8367 |
| Regardless of whether you think abortion should be legal or ... | 0.0549 | 0.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| In general, how often do you attend religious services in pe... | 0.5588 | 0.3563 |
| In their coverage of the Biden administration, which of thes... | 0.6061 | 0.3464 |
| How much have you heard about the boycott, divestment, and s... | 0.6387 | -0.1195 |
| Thinking of some of the early issues that the Biden administ... | 0.6406 | -0.2357 |
| Thinking of some of the early issues that the Biden administ... | 1.0000 | 0.0000 |
