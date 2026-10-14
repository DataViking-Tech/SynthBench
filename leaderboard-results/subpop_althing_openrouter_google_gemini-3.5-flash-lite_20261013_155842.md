# SynthBench Score Card

**Provider:** althing/openrouter/google/gemini-3.5-flash-lite
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 273.9s

## SynthBench Parity Score (SPS)

**SPS: 0.8107 [0.7898, 0.8277]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6837 [0.6538, 0.7118] | ███████░░░ |
| P_rank  Rank-Order | 0.7684 [0.7410, 0.7966] | ████████░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3163 |
| Median JSD | 0.3095 |
| Mean Kendall's tau | 0.5368 |
| Composite Parity (legacy) | 0.7261 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1641 | +29% |
| random-baseline | 0.6495 | +0.0765 | +12% |

## What These Scores Mean

- **SPS** (SynthBench Parity Score): The overall score — average of all metrics. 0 = random noise, 1 = indistinguishable from real humans.
- **P_dist** (Distributional Parity): How closely does the AI's answer distribution match real humans? If 60% of humans say 'yes' and the AI says 'yes' 60% of the time, that's a perfect match. 0 = completely different, 1 = identical distributions.
- **P_rank** (Rank-Order Parity): Does the AI get the preference ordering right? If humans prefer A > B > C, does the AI agree — even if the exact percentages differ? 0 = reversed ordering, 1 = perfect agreement.
- **P_refuse** (Refusal Calibration): Does the AI refuse to answer at appropriate rates? Humans sometimes decline sensitive questions. An AI that never refuses, or refuses too often, is miscalibrated. 0 = rates completely off, 1 = perfect match.
- **P_cond** (Conditioning Fidelity): When told 'respond as a 65-year-old conservative,' does the AI actually shift its answers? Higher = better demographic role-playing. (When available.)
- **P_sub** (Subgroup Consistency): Is the AI equally accurate across all demographics, or does it nail some groups and miss others? (When available.)

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think the United States’ decision to withdraw all tro... | 0.0143 | 1.0000 |
| If an abortion was carried out in a situation where it was i... | 0.0288 | 1.0000 |
| In the news you are receiving about the Biden administration... | 0.0553 | 0.8165 |
| Do you think race or ethnicity should be a major factor, min... | 0.0640 | 0.9129 |
| If an abortion was carried out in a situation where it was i... | 0.0697 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Regardless of whether you think abortion should be legal or ... | 0.5539 | 0.3464 |
| Regardless of whether you think abortion should be legal or ... | 0.5557 | 0.5774 |
| How much have you heard or read about medication abortion, w... | 0.5833 | 0.2357 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.5839 | 0.0000 |
| Regardless of whether you think abortion should be legal or ... | 0.6451 | -0.1155 |
