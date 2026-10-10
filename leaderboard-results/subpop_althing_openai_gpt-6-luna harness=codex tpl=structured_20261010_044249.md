# SynthBench Score Card

**Provider:** althing/openai/gpt-6-luna harness=codex tpl=structured
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 2085.1s

## SynthBench Parity Score (SPS)

**SPS: 0.7910 [0.7608, 0.8121]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6661 [0.6300, 0.6992] | ███████░░░ |
| P_rank  Rank-Order | 0.7270 [0.6893, 0.7595] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3339 |
| Median JSD | 0.3291 |
| Mean Kendall's tau | 0.4539 |
| Composite Parity (legacy) | 0.6965 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1345 | +24% |
| random-baseline | 0.6495 | +0.0470 | +7% |

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
| If you were looking for work, would you want to apply for a ... | 0.0129 | 1.0000 |
| Please choose the statement that comes closer to your own vi... | 0.0136 | 0.3333 |
| If an abortion was carried out in a situation where it was i... | 0.0304 | 0.3333 |
| In the news you are receiving about the Biden administration... | 0.0676 | 1.0000 |
| Which statement comes closer to your view, even if neither i... | 0.0702 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Regardless of whether you think abortion should be legal or ... | 0.6451 | -0.1155 |
| Have there been times in the past 12 months when you did not... | 0.6506 | 0.1826 |
| Have there been times in the past 12 months when you did not... | 0.6829 | -0.3333 |
| As you may know, the Supreme Court’s decision found that the... | 0.8176 | -0.8367 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
