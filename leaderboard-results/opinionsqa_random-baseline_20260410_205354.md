# SynthBench Score Card

**Provider:** random-baseline
**Dataset:** opinionsqa (175 questions)
**Samples per question:** 10
**Elapsed:** 0.0s

## SynthBench Parity Score (SPS)

**SPS: 0.7416 [0.5904, 0.6430]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7533 [0.7322, 0.7725] | ████████░░ |
| P_rank  Rank-Order | 0.4836 [0.4461, 0.5220] | █████░░░░░ |
| P_refuse Refusal Cal. | 0.9880 [0.9850, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2467 |
| Median JSD | 0.2309 |
| Mean Kendall's tau | -0.0328 |
| Composite Parity (legacy) | 0.6185 |

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
| Now thinking about when you were growing up, how would you d... | 0.0030 | 1.0000 |
| How often, if ever, do you worry about the cost of health ca... | 0.0085 | 0.8944 |
| Would you say China has done a good or bad job dealing with ... | 0.0175 | 0.8367 |
| Still thinking ahead 30 years, which do you think is more li... | 0.0279 | 0.3333 |
| How much, if at all, do you think what happens to white peop... | 0.0315 | 0.4472 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have you ever had your pay or hours reduced because your emp... | 0.5943 | 0.0000 |
| Thinking about children growing up in this country these day... | 0.6231 | -0.5270 |
| If driverless vehicles become widespread, which of the follo... | 0.6677 | -1.0000 |
| Do you think science has had a mostly positive or mostly neg... | 0.6922 | -1.0000 |
| How much power and influence do you think politicians have o... | 0.7134 | -0.6667 |
