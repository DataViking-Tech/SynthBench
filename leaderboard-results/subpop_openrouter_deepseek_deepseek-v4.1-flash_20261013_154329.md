# SynthBench Score Card

**Provider:** openrouter/deepseek/deepseek-v4.1-flash
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 316.4s

## SynthBench Parity Score (SPS)

**SPS: 0.8373 [0.8138, 0.8542]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7387 [0.7113, 0.7665] | ███████░░░ |
| P_rank  Rank-Order | 0.7934 [0.7659, 0.8180] | ████████░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2613 |
| Median JSD | 0.2548 |
| Mean Kendall's tau | 0.5867 |
| Composite Parity (legacy) | 0.7660 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.2040 | +36% |
| random-baseline | 0.6495 | +0.1165 | +18% |

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
| Please indicate if you have attended a sporting event over t... | 0.0026 | 1.0000 |
| Please choose the statement that comes closer to your own vi... | 0.0057 | 1.0000 |
| Which statement comes closer to your view, even if neither i... | 0.0091 | 0.3333 |
| In the news you are receiving about the Biden administration... | 0.0146 | 1.0000 |
| If you were looking for work, would you want to apply for a ... | 0.0339 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Which country in Africa is known for having the largest popu... | 0.5123 | 0.3464 |
| Regardless of whether you think abortion should be legal or ... | 0.5222 | 0.6025 |
| How important is your religion in shaping your views about a... | 0.5574 | 0.5345 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.5839 | 0.0000 |
| Did you refuse to answer the previous question?... | 0.6139 | -0.3333 |
