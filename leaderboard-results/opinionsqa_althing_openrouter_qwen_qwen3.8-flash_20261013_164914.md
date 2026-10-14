# SynthBench Score Card

**Provider:** althing/openrouter/qwen/qwen3.8-flash
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 1064.7s

## SynthBench Parity Score (SPS)

**SPS: 0.8702 [0.8539, 0.8838]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7882 [0.7650, 0.8140] | ████████░░ |
| P_rank  Rank-Order | 0.8281 [0.8023, 0.8521] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2118 |
| Median JSD | 0.1904 |
| Mean Kendall's tau | 0.6562 |
| Composite Parity (legacy) | 0.8081 |

## What These Scores Mean

- **SPS** (SynthBench Parity Score): The overall score — average of all metrics. 0 = random noise, 1 = indistinguishable from real humans.
- **P_dist** (Distributional Parity): How closely does the AI's answer distribution match real humans? If 60% of humans say 'yes' and the AI says 'yes' 60% of the time, that's a perfect match. 0 = completely different, 1 = identical distributions.
- **P_rank** (Rank-Order Parity): Does the AI get the preference ordering right? If humans prefer A > B > C, does the AI agree — even if the exact percentages differ? 0 = reversed ordering, 1 = perfect agreement.
- **P_refuse** (Refusal Calibration): Does the AI refuse to answer at appropriate rates? Humans sometimes decline sensitive questions. An AI that never refuses, or refuses too often, is miscalibrated. 0 = rates completely off, 1 = perfect match.
- **P_cond** (Conditioning Fidelity): When told 'respond as a 65-year-old conservative,' does the AI actually shift its answers? Higher = better demographic role-playing. (When available.)
- **P_sub** (Subgroup Consistency): Is the AI equally accurate across all demographics, or does it nail some groups and miss others? (When available.)

## Temporal Breakdown (by Survey Year)

Scores stratified by Pew ATP survey wave year. Rising P_dist in recent years may indicate training-data contamination.

| Year | P_dist | P_rank | Mean JSD | Questions |
|------|--------|--------|----------|-----------|
| 2017 | 0.7879 | 0.8284 | 0.2121 | 99 |
| 2018 | 0.8205 | 0.7988 | 0.1795 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Thinking about the people you know, including yourself, do y... | 0.0031 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Have you ever had your pay or hours reduced because your emp... | 0.0333 | 0.7071 |
| Not including in military combat or as part of your job, hav... | 0.0368 | 0.8165 |
| Regardless of whether or not you own a gun, have you ever fi... | 0.0386 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Which of the following statements comes closer to your feeli... | 0.4565 | 0.1826 |
| On a different subject, would you say that society generally... | 0.4881 | -0.1826 |
| How enthusiastic are you, if at all, about the development o... | 0.4992 | 0.3162 |
| How often, if ever, do you visit websites about guns, huntin... | 0.5046 | 0.6708 |
| The next question is about local elections, such as for mayo... | 0.5062 | 0.3162 |
