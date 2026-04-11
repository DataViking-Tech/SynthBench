# SynthBench Score Card

**Provider:** random-baseline
**Dataset:** opinionsqa (429 questions)
**Samples per question:** 10
**Elapsed:** 0.1s

## SynthBench Parity Score (SPS)

**SPS: 0.7463 [0.6074, 0.6413]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7605 [0.7477, 0.7729] | ████████░░ |
| P_rank  Rank-Order | 0.4884 [0.4636, 0.5127] | █████░░░░░ |
| P_refuse Refusal Cal. | 0.9899 [0.9890, 0.9907] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2395 |
| Median JSD | 0.2130 |
| Mean Kendall's tau | -0.0232 |
| Composite Parity (legacy) | 0.6245 |

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
| Which of the following, if any, do you restrict or limit eat... | 0.0005 | 1.0000 |
| Which of the following, if any, do you restrict or limit eat... | 0.0008 | 1.0000 |
| Have you participated in any of these groups during the last... | 0.0053 | 1.0000 |
| Have you, or has anyone in your immediate family, ever had a... | 0.0055 | 0.9129 |
| How do you feel about the average American's ability to reco... | 0.0091 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Thinking again about race and race relations in the U.S. in ... | 0.5985 | -0.3581 |
| How much do you trust the accuracy of the news and informati... | 0.6237 | -0.8000 |
| Please compare the US to other developed nations in a few di... | 0.6265 | -0.6445 |
| Please choose the statement that comes closer to your own vi... | 0.6368 | -1.0000 |
| Do you think of yourself as... | 0.7838 | -0.0772 |
