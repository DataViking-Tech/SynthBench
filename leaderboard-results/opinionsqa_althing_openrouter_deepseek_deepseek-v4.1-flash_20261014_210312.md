# SynthBench Score Card

**Provider:** althing/openrouter/deepseek/deepseek-v4.1-flash
**Dataset:** opinionsqa (684 questions)
**Samples per question:** 30
**Elapsed:** 12357.2s

## SynthBench Parity Score (SPS)

**SPS: 0.8385 [0.8319, 0.8445]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7248 [0.7149, 0.7349] | ███████░░░ |
| P_rank  Rank-Order | 0.8010 [0.7884, 0.8114] | ████████░░ |
| P_refuse Refusal Cal. | 0.9895 [0.9885, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2752 |
| Median JSD | 0.2751 |
| Mean Kendall's tau | 0.6021 |
| Composite Parity (legacy) | 0.7629 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.2009 | +36% |
| random-baseline | 0.6495 | +0.1134 | +17% |

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
| 2017 | 0.7183 | 0.7904 | 0.2817 | 99 |
| 2018 | 0.7388 | 0.7977 | 0.2612 | 124 |
| 2019 | 0.7282 | 0.8082 | 0.2718 | 218 |
| 2020 | 0.7443 | 0.8174 | 0.2557 | 101 |
| 2022 | 0.6982 | 0.7887 | 0.3018 | 142 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Which of the following, if any, do you restrict or limit eat... | 0.0005 | 1.0000 |
| Do you have other connected items in your home that you can ... | 0.0028 | 1.0000 |
| Do you use twitter?... | 0.0077 | 1.0000 |
| Which of the following, if any, do you restrict or limit eat... | 0.0092 | -1.0000 |
| How do you feel about your own ability to recognize the foll... | 0.0116 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Would you say China is doing a good or bad job dealing with ... | 0.6841 | 0.0000 |
| How much confidence do you have in chinese President Xi Jinp... | 0.7035 | -0.1195 |
| Do you think the government of China respects the personal f... | 0.7341 | -1.0000 |
| Compared to 50 years ago, do you think... | 0.7640 | -0.2357 |
| Who do you think has the most responsibility to reduce the a... | 0.7665 | -0.1155 |
