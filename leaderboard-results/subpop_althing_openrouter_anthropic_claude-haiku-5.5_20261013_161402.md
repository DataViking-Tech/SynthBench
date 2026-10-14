# SynthBench Score Card

**Provider:** althing/openrouter/anthropic/claude-haiku-5.5
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 431.0s

## SynthBench Parity Score (SPS)

**SPS: 0.7834 [0.7620, 0.8022]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6453 [0.6135, 0.6775] | ██████░░░░ |
| P_rank  Rank-Order | 0.7309 [0.6962, 0.7620] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9739 [0.9341, 0.9888] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3547 |
| Median JSD | 0.3726 |
| Mean Kendall's tau | 0.4617 |
| Composite Parity (legacy) | 0.6881 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1261 | +22% |
| random-baseline | 0.6495 | +0.0386 | +6% |

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
| Do you think whether a relative attended the school should b... | 0.0370 | 0.9129 |
| Please indicate if you have attended a concert over the past... | 0.0521 | 0.3333 |
| Did you refuse to answer the previous question?... | 0.0676 | 0.3333 |
| Do you personally know someone (such as a close friend, fami... | 0.0692 | 1.0000 |
| Have your personal views about abortion changed in any way o... | 0.0783 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think race or ethnicity should be a major factor, min... | 0.6062 | 0.2357 |
| Regardless of whether you think abortion should be legal or ... | 0.6451 | -0.1155 |
| As you may know, the Supreme Court’s decision found that the... | 0.6653 | 0.0000 |
| If an abortion was carried out in a situation where it was i... | 0.8475 | -0.3333 |
| If an abortion was carried out in a situation where it was i... | 0.9276 | -0.8165 |
