# SynthBench Score Card

**Provider:** random-baseline
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 0.0s

## SynthBench Parity Score (SPS)

**SPS: 0.7575 [0.6080, 0.6693]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7871 [0.7724, 0.8028] | ████████░░ |
| P_rank  Rank-Order | 0.4911 [0.4393, 0.5363] | █████░░░░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2129 |
| Median JSD | 0.2166 |
| Mean Kendall's tau | -0.0177 |
| Composite Parity (legacy) | 0.6391 |

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
| On a different subject, would you say that society generally... | 0.0432 | 0.9129 |
| How worried are you right now about not having enough money ... | 0.0526 | 0.1054 |
| Would you favor or oppose the following? If the federal gove... | 0.0583 | 0.5270 |
| How likely is it that, at some point in your life, you will ... | 0.0779 | 0.7877 |
| Do you think it is very likely, somewhat likely, not very li... | 0.0840 | 0.5270 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have you yourself ever lost a job because your employer repl... | 0.3569 | 0.9129 |
| Do you personally know anyone who has lost a job, or had the... | 0.3839 | -1.0000 |
| Have you participated in any of these groups during the last... | 0.3886 | -0.3333 |
| Have you ever had your pay or hours reduced because your emp... | 0.3910 | 0.0000 |
| Do you think it is very likely, somewhat likely, not very li... | 0.3947 | -0.9487 |
