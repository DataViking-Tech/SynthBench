# SynthBench Score Card

**Provider:** althing/anthropic/claude-haiku-5-5 harness=claude-code
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 1613.3s

## SynthBench Parity Score (SPS)

**SPS: 0.6710 [0.6268, 0.7099]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5795 [0.5324, 0.6207] | ██████░░░░ |
| P_rank  Rank-Order | 0.6116 [0.5555, 0.6588] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.8219 [0.7620, 0.8692] | ████████░░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4205 |
| Median JSD | 0.4085 |
| Mean Kendall's tau | 0.2232 |
| Composite Parity (legacy) | 0.5956 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0336 | +6% |
| random-baseline | 0.6495 | -0.0539 | -8% |

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
| Please indicate if you have attended a concert over the past... | 0.0283 | 1.0000 |
| Regardless of whether you think abortion should be legal or ... | 0.0549 | 0.0000 |
| Here’s a list of activities some people do and others do not... | 0.0716 | 1.0000 |
| Do you think gender should be a major factor, minor factor, ... | 0.0978 | 0.3333 |
| If you were looking for work, would you want to apply for a ... | 0.1113 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Thinking about abortion policies around the country, which i... | 0.9202 | -0.8165 |
| Have there been times in the past 12 months when you did not... | 0.9213 | -0.9129 |
| Regardless of whether you think abortion should be legal or ... | 0.9453 | -0.5774 |
| Regardless of whether you think abortion should be legal or ... | 0.9542 | -0.5774 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
