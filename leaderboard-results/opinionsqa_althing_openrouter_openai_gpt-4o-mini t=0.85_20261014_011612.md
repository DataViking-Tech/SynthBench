# SynthBench Score Card

**Provider:** althing/openrouter/openai/gpt-4o-mini t=0.85
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 643.7s

## SynthBench Parity Score (SPS)

**SPS: 0.8031 [0.7834, 0.8224]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6723 [0.6409, 0.7078] | ███████░░░ |
| P_rank  Rank-Order | 0.7427 [0.7106, 0.7764] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3277 |
| Median JSD | 0.3341 |
| Mean Kendall's tau | 0.4854 |
| Composite Parity (legacy) | 0.7075 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1455 | +26% |
| random-baseline | 0.6495 | +0.0580 | +9% |

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
| 2017 | 0.6710 | 0.7409 | 0.3290 | 99 |
| 2018 | 0.8011 | 0.9183 | 0.1989 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| In the last 12 months, that is since September 2016, have yo... | 0.0087 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Have you ever had your pay or hours reduced because your emp... | 0.0333 | 0.7071 |
| Not including in military combat or as part of your job, hav... | 0.0368 | 0.8165 |
| Have you participated in any of these groups during the last... | 0.0869 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How much do you agree or disagree with the following stateme... | 0.6761 | 0.0000 |
| How often, if ever, do you participate in online discussion ... | 0.6811 | 0.3586 |
| How often, if ever, do you attend gun shows... | 0.6877 | 0.3162 |
| How often, if ever, do you listen to gun-oriented podcasts o... | 0.7285 | 0.3162 |
| How much of a problem was gun violence in the community wher... | 0.7722 | -0.1195 |
