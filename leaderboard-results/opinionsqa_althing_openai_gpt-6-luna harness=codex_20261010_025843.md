# SynthBench Score Card

**Provider:** althing/openai/gpt-6-luna harness=codex
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 2038.2s

## SynthBench Parity Score (SPS)

**SPS: 0.8328 [0.8158, 0.8496]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7458 [0.7181, 0.7730] | ███████░░░ |
| P_rank  Rank-Order | 0.7582 [0.7285, 0.7864] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2542 |
| Median JSD | 0.2523 |
| Mean Kendall's tau | 0.5164 |
| Composite Parity (legacy) | 0.7520 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1900 | +34% |
| random-baseline | 0.6495 | +0.1025 | +16% |

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
| 2017 | 0.7463 | 0.7578 | 0.2537 | 99 |
| 2018 | 0.7002 | 0.7988 | 0.2998 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Compared to 50 years ago, do you think... | 0.0058 | 1.0000 |
| If driverless vehicles become widespread, which of the follo... | 0.0102 | 1.0000 |
| Do you feel that society in general tends to look at most gu... | 0.0126 | 0.8165 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| How much have you seen or heard about the effort to develop ... | 0.0236 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Thinking about when you were growing up, as far as you know,... | 0.4832 | -0.1826 |
| How enthusiastic are you, if at all, about the development o... | 0.4992 | 0.3162 |
| The next question is about local elections, such as for mayo... | 0.5062 | 0.3162 |
| How likely is it that, at some point in your life, you will ... | 0.5318 | 0.3464 |
| Have you ever been told by a doctor or other health professi... | 0.7367 | -0.3333 |
