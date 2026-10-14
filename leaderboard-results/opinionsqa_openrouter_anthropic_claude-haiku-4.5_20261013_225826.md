# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-haiku-4.5
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 236.5s

## SynthBench Parity Score (SPS)

**SPS: 0.7654 [0.7311, 0.7930]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6705 [0.6336, 0.7068] | ███████░░░ |
| P_rank  Rank-Order | 0.7201 [0.6769, 0.7519] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9057 [0.8437, 0.9451] | █████████░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3295 |
| Median JSD | 0.3322 |
| Mean Kendall's tau | 0.4401 |
| Composite Parity (legacy) | 0.6953 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1333 | +24% |
| random-baseline | 0.6495 | +0.0458 | +7% |

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
| 2017 | 0.6703 | 0.7217 | 0.3297 | 99 |
| 2018 | 0.6862 | 0.5598 | 0.3138 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have you participated in any of these groups during the last... | 0.0049 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Have you ever had your pay or hours reduced because your emp... | 0.0333 | 0.7071 |
| Not including in military combat or as part of your job, hav... | 0.0368 | 0.8165 |
| How often, if ever, do you listen to gun-oriented podcasts o... | 0.0536 | 0.8367 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| The next question is about local elections, such as for mayo... | 0.6812 | -0.3162 |
| Thinking about when you were growing up, as far as you know,... | 0.7174 | -0.6667 |
| Compared to 50 years ago, do you think... | 0.7640 | -0.2357 |
| Do you feel that people in your local community tend to look... | 0.9279 | -0.8165 |
| How much do you agree or disagree with the following stateme... | 0.9744 | -0.6325 |
