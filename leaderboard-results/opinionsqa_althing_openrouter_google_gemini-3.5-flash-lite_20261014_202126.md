# SynthBench Score Card

**Provider:** althing/openrouter/google/gemini-3.5-flash-lite
**Dataset:** opinionsqa (684 questions)
**Samples per question:** 30
**Elapsed:** 9847.3s

## SynthBench Parity Score (SPS)

**SPS: 0.8323 [0.8255, 0.8385]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7176 [0.7063, 0.7277] | ███████░░░ |
| P_rank  Rank-Order | 0.7898 [0.7779, 0.7999] | ████████░░ |
| P_refuse Refusal Cal. | 0.9895 [0.9885, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2824 |
| Median JSD | 0.2870 |
| Mean Kendall's tau | 0.5796 |
| Composite Parity (legacy) | 0.7537 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1917 | +34% |
| random-baseline | 0.6495 | +0.1042 | +16% |

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
| 2017 | 0.7369 | 0.7850 | 0.2631 | 99 |
| 2018 | 0.7221 | 0.7894 | 0.2779 | 124 |
| 2019 | 0.7319 | 0.8053 | 0.2681 | 218 |
| 2020 | 0.7149 | 0.7822 | 0.2851 | 101 |
| 2022 | 0.6802 | 0.7750 | 0.3199 | 142 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| If driverless vehicles become widespread, which of the follo... | 0.0029 | 1.0000 |
| Do you think an adequate standard of living is something the... | 0.0041 | 1.0000 |
| Please choose the statement that comes closer to your own vi... | 0.0046 | 1.0000 |
| Has the issue of made-up news and information led you to red... | 0.0065 | 1.0000 |
| Do you think genetic engineering of aquarium fish to change ... | 0.0067 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| What do you think is the ideal situation for men with young ... | 0.6606 | 0.2357 |
| On a different subject, would you say that society generally... | 0.6715 | -0.2357 |
| Do you think greater social acceptance of people who are tra... | 0.6718 | -0.1155 |
| Please compare the US to other developed nations in a few di... | 0.6796 | 0.1155 |
| How much do you think to be funny is a reason why made-up ne... | 0.7501 | -0.2357 |
