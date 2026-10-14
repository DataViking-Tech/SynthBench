# SynthBench Score Card

**Provider:** althing/openrouter/openai/gpt-4o-mini t=0.7
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 645.0s

## SynthBench Parity Score (SPS)

**SPS: 0.8018 [0.7824, 0.8212]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6679 [0.6353, 0.7030] | ███████░░░ |
| P_rank  Rank-Order | 0.7431 [0.7112, 0.7755] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3321 |
| Median JSD | 0.3341 |
| Mean Kendall's tau | 0.4862 |
| Composite Parity (legacy) | 0.7055 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1435 | +26% |
| random-baseline | 0.6495 | +0.0560 | +9% |

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
| 2017 | 0.6670 | 0.7413 | 0.3330 | 99 |
| 2018 | 0.7602 | 0.9183 | 0.2398 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| In the last 12 months, that is since September 2016, have yo... | 0.0162 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Have you ever had your pay or hours reduced because your emp... | 0.0333 | 0.7071 |
| Not including in military combat or as part of your job, hav... | 0.0368 | 0.8165 |
| How well, if at all, do the following words or phrases descr... | 0.0811 | 0.8367 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How much do you agree or disagree with the following stateme... | 0.6761 | 0.0000 |
| How often, if ever, do you attend gun shows... | 0.6877 | 0.3162 |
| How often, if ever, do you participate in online discussion ... | 0.6910 | 0.3586 |
| How often, if ever, do you listen to gun-oriented podcasts o... | 0.7285 | 0.3162 |
| How much of a problem was gun violence in the community wher... | 0.7736 | -0.1195 |
