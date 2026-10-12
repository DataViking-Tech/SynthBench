# SynthBench Score Card

**Provider:** althing/anthropic/claude-haiku-5-5 harness=claude-code
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 2602.6s

## SynthBench Parity Score (SPS)

**SPS: 0.7857 [0.7525, 0.8089]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7123 [0.6720, 0.7463] | ███████░░░ |
| P_rank  Rank-Order | 0.7494 [0.7098, 0.7844] | ███████░░░ |
| P_refuse Refusal Cal. | 0.8955 [0.8541, 0.9291] | █████████░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2877 |
| Median JSD | 0.2757 |
| Mean Kendall's tau | 0.4987 |
| Composite Parity (legacy) | 0.7309 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1689 | +30% |
| random-baseline | 0.6495 | +0.0813 | +13% |

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
| 2017 | 0.7127 | 0.7489 | 0.2873 | 99 |
| 2018 | 0.6733 | 0.7988 | 0.3267 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you personally know anyone who has lost a job, or had the... | 0.0040 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Do you think men and women are basically similar or basicall... | 0.0278 | 0.8165 |
| How much have you seen or heard about the effort to develop ... | 0.0280 | 0.5477 |
| Do you feel that people in your local community tend to look... | 0.0293 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Which statement comes closer to your views, even if neither ... | 0.7598 | -1.0000 |
| How much of a problem was gun violence in the community wher... | 0.8170 | -0.3586 |
| How well, if at all, do the following words or phrases descr... | 0.8690 | -0.3162 |
| How well, if at all, do the following words or phrases descr... | 0.9118 | -0.3162 |
| Which of the following statements comes closer to your feeli... | 0.9357 | -0.7071 |
