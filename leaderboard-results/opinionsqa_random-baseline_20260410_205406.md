# SynthBench Score Card

**Provider:** random-baseline
**Dataset:** opinionsqa (80 questions)
**Samples per question:** 10
**Elapsed:** 0.0s

## SynthBench Parity Score (SPS)

**SPS: 0.7578 [0.5964, 0.6784]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7493 [0.7071, 0.7798] | ███████░░░ |
| P_rank  Rank-Order | 0.5332 [0.4804, 0.5854] | █████░░░░░ |
| P_refuse Refusal Cal. | 0.9909 [0.9889, 0.9922] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2507 |
| Median JSD | 0.2055 |
| Mean Kendall's tau | 0.0664 |
| Composite Parity (legacy) | 0.6412 |

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
| Do you think a college education is something the federal go... | 0.0263 | 0.8165 |
| Thinking about Joe Biden's ability to handle a number of thi... | 0.0422 | 0.8944 |
| Do you think adequate income in retirement is something the ... | 0.0455 | 0.3333 |
| Thinking about Joe Biden's ability to handle a number of thi... | 0.0501 | 0.6708 |
| Thinking about how the federal government spends money, do y... | 0.0656 | 0.4082 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have you ever taken any gun safety courses such as weapons t... | 0.5602 | -0.3333 |
| Do you think the government of China respects the personal f... | 0.5907 | -0.3333 |
| How often, if ever, do you attend gun shows... | 0.6064 | -0.2000 |
| Thinking about elections in the country, how important, if a... | 0.7935 | -0.8367 |
| Have you or anyone in your household received unemployment b... | 0.8763 | -1.0000 |
