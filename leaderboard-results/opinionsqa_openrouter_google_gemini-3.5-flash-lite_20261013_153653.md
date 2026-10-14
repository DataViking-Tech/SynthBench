# SynthBench Score Card

**Provider:** openrouter/google/gemini-3.5-flash-lite
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 276.6s

## SynthBench Parity Score (SPS)

**SPS: 0.8361 [0.8170, 0.8533]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7295 [0.7006, 0.7598] | ███████░░░ |
| P_rank  Rank-Order | 0.7844 [0.7541, 0.8126] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2705 |
| Median JSD | 0.2590 |
| Mean Kendall's tau | 0.5688 |
| Composite Parity (legacy) | 0.7570 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1950 | +35% |
| random-baseline | 0.6495 | +0.1074 | +17% |

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
| 2017 | 0.7299 | 0.7841 | 0.2701 | 99 |
| 2018 | 0.6876 | 0.8162 | 0.3124 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have you ever taken any gun safety courses such as weapons t... | 0.0079 | 1.0000 |
| Have you ever personally experienced discrimination or been ... | 0.0210 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Have you ever had your pay or hours reduced because your emp... | 0.0333 | 0.7071 |
| Not including in military combat or as part of your job, hav... | 0.0368 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How much do you agree or disagree with the following stateme... | 0.4906 | -0.1054 |
| Please consider the following scenario - in the future, robo... | 0.5261 | 0.2357 |
| How worried are you right now about not having enough money ... | 0.5726 | 0.0000 |
| Do you feel that people in your local community tend to look... | 0.7195 | -0.3333 |
| Compared to 50 years ago, do you think... | 0.7640 | -0.2357 |
