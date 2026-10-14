# SynthBench Score Card

**Provider:** althing/openrouter/anthropic/claude-haiku-4.5
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 525.2s

## SynthBench Parity Score (SPS)

**SPS: 0.7701 [0.7425, 0.7877]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6335 [0.5985, 0.6633] | ██████░░░░ |
| P_rank  Rank-Order | 0.7109 [0.6806, 0.7381] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9659 [0.9232, 0.9831] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3665 |
| Median JSD | 0.3772 |
| Mean Kendall's tau | 0.4218 |
| Composite Parity (legacy) | 0.6722 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1102 | +20% |
| random-baseline | 0.6495 | +0.0227 | +3% |

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
| Which statement comes closer to your view, even if neither i... | 0.0126 | 0.3333 |
| Please choose the statement that comes closer to your own vi... | 0.0310 | 0.3333 |
| How much, if anything, have you heard or read about thousand... | 0.0602 | 0.5477 |
| Do you think medication abortion should be legal or illegal ... | 0.1183 | 0.9129 |
| Have your personal views about abortion changed in any way o... | 0.1270 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Thinking about the use of artificial intelligence (AI) in th... | 0.6221 | 0.0000 |
| How important is your religion in shaping your views about a... | 0.6375 | 0.1782 |
| Do you think gender should be a major factor, minor factor, ... | 0.6621 | 0.2357 |
| Thinking about policies around abortion in this country, in ... | 0.6930 | 0.1155 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
