# SynthBench Score Card

**Provider:** althing/openrouter/openai/gpt-6-luna
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 1317.9s

## SynthBench Parity Score (SPS)

**SPS: 0.7983 [0.7711, 0.8164]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6654 [0.6303, 0.6938] | ███████░░░ |
| P_rank  Rank-Order | 0.7496 [0.7167, 0.7752] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3346 |
| Median JSD | 0.3235 |
| Mean Kendall's tau | 0.4992 |
| Composite Parity (legacy) | 0.7075 |

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
| Please choose the statement that comes closer to your own vi... | 0.0197 | 0.3333 |
| Please indicate if you have attended a concert over the past... | 0.0649 | 1.0000 |
| Which statement comes closer to your view, even if neither i... | 0.0825 | 1.0000 |
| Please indicate if you have attended a sporting event over t... | 0.1050 | 1.0000 |
| Do you think gender should be a major factor, minor factor, ... | 0.1154 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| As you may know, the Supreme Court’s decision found that the... | 0.5831 | 0.1195 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.5839 | 0.0000 |
| Regardless of whether you think abortion should be legal or ... | 0.6451 | -0.1155 |
| Do you think that you have ever been at an advantage in your... | 0.6579 | 0.2357 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
