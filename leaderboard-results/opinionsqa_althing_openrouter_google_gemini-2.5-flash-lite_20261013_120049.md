# SynthBench Score Card

**Provider:** althing/openrouter/google/gemini-2.5-flash-lite
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 198.4s

## SynthBench Parity Score (SPS)

**SPS: 0.8312 [0.8119, 0.8496]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7234 [0.6917, 0.7560] | ███████░░░ |
| P_rank  Rank-Order | 0.7759 [0.7454, 0.8050] | ████████░░ |
| P_refuse Refusal Cal. | 0.9943 [0.9934, 0.9949] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2766 |
| Median JSD | 0.2648 |
| Mean Kendall's tau | 0.5518 |
| Composite Parity (legacy) | 0.7496 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1876 | +33% |
| random-baseline | 0.6495 | +0.1001 | +15% |

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
| 2017 | 0.7226 | 0.7745 | 0.2774 | 99 |
| 2018 | 0.8011 | 0.9183 | 0.1989 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have you ever taken any gun safety courses such as weapons t... | 0.0028 | 1.0000 |
| Do you think the following are likely to happen as a result ... | 0.0047 | 1.0000 |
| Has anyone ever used a gun to threaten or intimidate you or ... | 0.0049 | 1.0000 |
| If driverless vehicles become widespread, which of the follo... | 0.0056 | 1.0000 |
| Do you think men and women are basically similar or basicall... | 0.0057 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Would you favor or oppose the following? If people had the o... | 0.5373 | 0.3586 |
| Compared to 50 years ago, do you think... | 0.5416 | 0.1826 |
| How well, if at all, do the following words or phrases descr... | 0.5669 | 0.1195 |
| Do you personally know anyone who has lost a job, or had the... | 0.6144 | 0.0000 |
| On a different subject, would you say that society generally... | 0.6715 | -0.2357 |
