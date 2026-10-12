# SynthBench Score Card

**Provider:** althing/anthropic/claude-haiku-5-5 harness=claude-code
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 2867.0s

## SynthBench Parity Score (SPS)

**SPS: 0.6608 [0.6142, 0.7022]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5616 [0.5104, 0.6068] | ██████░░░░ |
| P_rank  Rank-Order | 0.5994 [0.5475, 0.6467] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.8213 [0.7648, 0.8673] | ████████░░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4384 |
| Median JSD | 0.4088 |
| Mean Kendall's tau | 0.1988 |
| Composite Parity (legacy) | 0.5805 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0185 | +3% |
| random-baseline | 0.6495 | -0.0690 | -11% |

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
| Do you think the use of artificial intelligence (AI) in heal... | 0.0696 | 0.6667 |
| Please indicate if you have traveled more than 100 miles fro... | 0.1174 | 0.3333 |
| Please indicate if you have attended a sporting event over t... | 0.1228 | 1.0000 |
| How much have you heard or read about medication abortion, w... | 0.1238 | 0.9129 |
| Here’s a list of activities some people do and others do not... | 0.1431 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Regardless of whether you think abortion should be legal or ... | 0.9453 | -0.5774 |
| Regardless of whether you think abortion should be legal or ... | 0.9490 | -0.5774 |
| Do you think abortion should be…... | 0.9526 | -0.6325 |
| Regardless of whether you think abortion should be legal or ... | 0.9542 | -0.5774 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
