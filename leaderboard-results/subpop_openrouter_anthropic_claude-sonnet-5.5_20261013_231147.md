# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-sonnet-5.5
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 580.7s

## SynthBench Parity Score (SPS)

**SPS: 0.7361 [0.6972, 0.7642]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5690 [0.5204, 0.6110] | ██████░░░░ |
| P_rank  Rank-Order | 0.6721 [0.6274, 0.7124] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9674 [0.9309, 0.9827] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4310 |
| Median JSD | 0.4248 |
| Mean Kendall's tau | 0.3441 |
| Composite Parity (legacy) | 0.6205 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0585 | +10% |
| random-baseline | 0.6495 | -0.0290 | -4% |

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
| Please choose the statement that comes closer to your own vi... | 0.0057 | 1.0000 |
| Do you think abortion should be legal or illegal in the situ... | 0.0809 | 0.9129 |
| Do you think the use of artificial intelligence (AI) in heal... | 0.0988 | 0.9129 |
| Do you think gender should be a major factor, minor factor, ... | 0.1154 | 0.7071 |
| Have your personal views about abortion changed in any way o... | 0.1270 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Regardless of whether you think abortion should be legal or ... | 0.9490 | -0.5774 |
| Do you think abortion should be…... | 0.9526 | -0.6325 |
| Regardless of whether you think abortion should be legal or ... | 0.9542 | -0.5774 |
| Do you think race or ethnicity should be a major factor, min... | 0.9767 | -0.7071 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
