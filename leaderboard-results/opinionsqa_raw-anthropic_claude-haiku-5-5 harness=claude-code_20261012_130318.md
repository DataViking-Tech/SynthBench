# SynthBench Score Card

**Provider:** raw-anthropic/claude-haiku-5-5 harness=claude-code
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 1827.5s

## SynthBench Parity Score (SPS)

**SPS: 0.8123 [0.7850, 0.8352]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7097 [0.6687, 0.7512] | ███████░░░ |
| P_rank  Rank-Order | 0.7331 [0.6923, 0.7695] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9939 [0.9926, 0.9947] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2903 |
| Median JSD | 0.2579 |
| Mean Kendall's tau | 0.4662 |
| Composite Parity (legacy) | 0.7214 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1594 | +28% |
| random-baseline | 0.6495 | +0.0719 | +11% |

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
| 2017 | 0.7081 | 0.7339 | 0.2919 | 99 |
| 2018 | 0.8702 | 0.6581 | 0.1298 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think the following are likely to happen as a result ... | 0.0052 | 1.0000 |
| Do you personally know anyone who has lost a job, or had the... | 0.0071 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Have you ever had your pay or hours reduced because your emp... | 0.0291 | 0.5477 |
| Not including in military combat or as part of your job, hav... | 0.0368 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How much of a problem was gun violence in the community wher... | 0.7887 | -0.3162 |
| Thinking about when you were growing up, as far as you know,... | 0.8239 | -0.2357 |
| In the last 12 months, how often did you talk with any of yo... | 0.8676 | -0.3563 |
| This next question is about friends and family you do not li... | 0.9546 | -0.3563 |
| How much do you agree or disagree with the following stateme... | 0.9722 | -0.6325 |
