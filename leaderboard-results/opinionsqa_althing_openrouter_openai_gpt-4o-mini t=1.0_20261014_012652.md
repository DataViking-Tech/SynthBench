# SynthBench Score Card

**Provider:** althing/openrouter/openai/gpt-4o-mini t=1.0
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 636.0s

## SynthBench Parity Score (SPS)

**SPS: 0.8073 [0.7876, 0.8272]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6773 [0.6466, 0.7120] | ███████░░░ |
| P_rank  Rank-Order | 0.7502 [0.7179, 0.7829] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3227 |
| Median JSD | 0.3258 |
| Mean Kendall's tau | 0.5003 |
| Composite Parity (legacy) | 0.7138 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1518 | +27% |
| random-baseline | 0.6495 | +0.0642 | +10% |

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
| 2017 | 0.6765 | 0.7485 | 0.3235 | 99 |
| 2018 | 0.7602 | 0.9183 | 0.2398 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| In the last 12 months, that is since September 2016, have yo... | 0.0272 | 1.0000 |
| Have you ever had your pay or hours reduced because your emp... | 0.0333 | 0.7071 |
| Not including in military combat or as part of your job, hav... | 0.0368 | 0.8165 |
| Do you think men and women are basically similar or basicall... | 0.0727 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| On a different subject, would you say that society generally... | 0.6715 | -0.2357 |
| How often, if ever, do you participate in online discussion ... | 0.6758 | 0.3586 |
| How much do you agree or disagree with the following stateme... | 0.6761 | 0.0000 |
| How often, if ever, do you listen to gun-oriented podcasts o... | 0.7285 | 0.3162 |
| How much of a problem was gun violence in the community wher... | 0.7709 | -0.1195 |
