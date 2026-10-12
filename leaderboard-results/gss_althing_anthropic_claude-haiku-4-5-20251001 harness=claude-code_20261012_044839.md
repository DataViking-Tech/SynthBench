# SynthBench Score Card

**Provider:** althing/anthropic/claude-haiku-4-5-20251001 harness=claude-code
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 3507.9s

## SynthBench Parity Score (SPS)

**SPS: 0.7659 [0.7360, 0.7950]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7029 [0.6681, 0.7355] | ███████░░░ |
| P_rank  Rank-Order | 0.7433 [0.6981, 0.7803] | ███████░░░ |
| P_refuse Refusal Cal. | 0.8514 [0.7950, 0.8953] | █████████░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2971 |
| Median JSD | 0.2787 |
| Mean Kendall's tau | 0.4866 |
| Composite Parity (legacy) | 0.7231 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1611 | +29% |
| random-baseline | 0.6495 | +0.0736 | +11% |

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
| Consider a person who believes that Black people are genetic... | 0.0350 | 1.0000 |
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| Would you be for or against sex education in the public scho... | 0.0798 | 0.8165 |
| Please tell me whether or not you think it should be possibl... | 0.1067 | 0.8165 |
| Please tell me whether or not you think it should be possibl... | 0.1148 | 0.3333 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Some people say that people get ahead by their own hard work... | 0.5687 | 0.2357 |
| Which statement comes closest to expressing what you believe... | 0.6099 | -0.0563 |
| Do you think most people would try to take advantage of you ... | 0.6386 | -0.1826 |
| Would you say that most of the time people try to be helpful... | 0.6583 | -0.2357 |
| Do you believe there is a life after death?... | 0.7016 | -0.8165 |
