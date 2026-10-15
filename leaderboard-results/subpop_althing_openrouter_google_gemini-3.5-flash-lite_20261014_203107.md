# SynthBench Score Card

**Provider:** althing/openrouter/google/gemini-3.5-flash-lite
**Dataset:** subpop (525 questions)
**Samples per question:** 30
**Elapsed:** 9179.5s

## SynthBench Parity Score (SPS)

**SPS: 0.8114 [0.8030, 0.8195]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6780 [0.6655, 0.6923] | ███████░░░ |
| P_rank  Rank-Order | 0.7724 [0.7604, 0.7849] | ████████░░ |
| P_refuse Refusal Cal. | 0.9838 [0.9751, 0.9883] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3220 |
| Median JSD | 0.3149 |
| Mean Kendall's tau | 0.5447 |
| Composite Parity (legacy) | 0.7252 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1632 | +29% |
| random-baseline | 0.6495 | +0.0757 | +12% |

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
| Since the coronavirus outbreak began in February 2020, have ... | 0.0108 | 1.0000 |
| Would you say that the news coverage you have seen of the Bi... | 0.0121 | 1.0000 |
| If an abortion was carried out in a situation where it was i... | 0.0139 | 1.0000 |
| Do you think the United States’ decision to withdraw all tro... | 0.0189 | 1.0000 |
| In the last month, have you watched religious services onlin... | 0.0283 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have you ever moved out of where you were living, either per... | 0.7766 | 0.2357 |
| In the past month, how often, if ever, have you worn a mask ... | 0.7837 | 0.2582 |
| In the past month, how often, if ever, have you worn a mask ... | 0.7902 | 0.2582 |
| In the past month, how often, if ever, have you worn a mask ... | 0.7947 | 0.2582 |
| Have you heard of the social media site or app BitChute?... | 0.8196 | 0.0000 |
