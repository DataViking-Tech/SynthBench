# SynthBench Score Card

**Provider:** random-baseline
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 5
**Elapsed:** 0.0s

## SynthBench Parity Score (SPS)

**SPS: 0.7311 [0.5562, 0.6378]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6842 [0.6439, 0.7224] | ███████░░░ |
| P_rank  Rank-Order | 0.5150 [0.4627, 0.5687] | █████░░░░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3158 |
| Median JSD | 0.2884 |
| Mean Kendall's tau | 0.0300 |
| Composite Parity (legacy) | 0.5996 |

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
| Do you feel that society in general tends to look at most gu... | 0.0092 | 1.0000 |
| Do you feel that people in your local community tend to look... | 0.0114 | 1.0000 |
| How worried are you right now about not having enough money ... | 0.0268 | 0.5976 |
| Do you think the following are likely to happen as a result ... | 0.0280 | 0.3333 |
| In general, thinking about job opportunities where you live,... | 0.0289 | 0.3333 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Has anyone ever used a gun to threaten or intimidate you or ... | 0.6948 | -1.0000 |
| Do you personally own any guns (not including air guns, such... | 0.7011 | -1.0000 |
| Please tell us whether you are satisfied or dissatisfied wit... | 0.7015 | -0.1195 |
| Do you think it is very likely, somewhat likely, not very li... | 0.7563 | -0.5976 |
| How much, if at all, do you think the ease with which people... | 0.8285 | -0.5976 |
