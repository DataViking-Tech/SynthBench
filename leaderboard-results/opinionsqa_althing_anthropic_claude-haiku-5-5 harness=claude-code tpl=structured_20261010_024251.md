# SynthBench Score Card

**Provider:** althing/anthropic/claude-haiku-5-5 harness=claude-code tpl=structured
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 1084.4s

## SynthBench Parity Score (SPS)

**SPS: 0.7912 [0.7673, 0.8116]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6798 [0.6463, 0.7132] | ███████░░░ |
| P_rank  Rank-Order | 0.6994 [0.6539, 0.7361] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3202 |
| Median JSD | 0.3078 |
| Mean Kendall's tau | 0.3988 |
| Composite Parity (legacy) | 0.6896 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1276 | +23% |
| random-baseline | 0.6495 | +0.0401 | +6% |

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
| 2017 | 0.6809 | 0.7020 | 0.3191 | 99 |
| 2018 | 0.5687 | 0.4402 | 0.4313 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think men and women are basically similar or basicall... | 0.0198 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| How often, if ever, do you listen to gun-oriented podcasts o... | 0.0536 | 0.8367 |
| How often, if ever, do you attend gun shows... | 0.0758 | 0.8367 |
| How often, if ever, do you participate in online discussion ... | 0.0893 | 0.6325 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Which of the following statements best describes how you fee... | 0.6116 | -1.0000 |
| Does anyone else in your household own any guns (not includi... | 0.6386 | -0.3333 |
| How well, if at all, do the following words or phrases descr... | 0.7539 | 0.1195 |
| Thinking about when you were growing up, as far as you know,... | 0.8161 | -0.5477 |
| How much of a problem was gun violence in the community wher... | 0.8180 | -0.3586 |
