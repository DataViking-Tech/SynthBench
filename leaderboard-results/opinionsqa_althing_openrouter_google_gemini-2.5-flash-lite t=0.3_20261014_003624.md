# SynthBench Score Card

**Provider:** althing/openrouter/google/gemini-2.5-flash-lite t=0.3
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 875.8s

## SynthBench Parity Score (SPS)

**SPS: 0.7957 [0.7754, 0.8157]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6547 [0.6188, 0.6924] | ███████░░░ |
| P_rank  Rank-Order | 0.7382 [0.7060, 0.7679] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3453 |
| Median JSD | 0.3500 |
| Mean Kendall's tau | 0.4763 |
| Composite Parity (legacy) | 0.6964 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1344 | +24% |
| random-baseline | 0.6495 | +0.0469 | +7% |

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
| 2017 | 0.6543 | 0.7374 | 0.3457 | 99 |
| 2018 | 0.6876 | 0.8162 | 0.3124 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| If driverless vehicles become widespread, which of the follo... | 0.0056 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| Do you think men and women are basically similar or basicall... | 0.0278 | 0.8165 |
| Have you ever had your pay or hours reduced because your emp... | 0.0333 | 0.7071 |
| Not including in military combat or as part of your job, hav... | 0.0368 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How often, if ever, do you attend gun shows... | 0.6877 | 0.3162 |
| How well, if at all, do the following words or phrases descr... | 0.6889 | 0.0000 |
| Do you think it is very likely, somewhat likely, not very li... | 0.6929 | 0.0000 |
| How often, if ever, do you participate in online discussion ... | 0.7219 | 0.3162 |
| How often, if ever, do you listen to gun-oriented podcasts o... | 0.7285 | 0.3162 |
