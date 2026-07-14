# SynthBench Score Card

**Provider:** synthpanel/openrouter/anthropic/claude-haiku-4-5
**Dataset:** subpop (200 questions)
**Samples per question:** 30
**Elapsed:** 1105.9s

## SynthBench Parity Score (SPS)

**SPS: 0.6942 [0.6712, 0.7157]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6559 [0.6300, 0.6790] | ███████░░░ |
| P_rank  Rank-Order | 0.7235 [0.7021, 0.7459] | ███████░░░ |
| P_refuse Refusal Cal. | 0.7031 [0.6567, 0.7432] | ███████░░░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3441 |
| Median JSD | 0.3143 |
| Mean Kendall's tau | 0.4470 |
| Composite Parity (legacy) | 0.6897 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1277 | +23% |
| random-baseline | 0.6495 | +0.0402 | +6% |

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
| Do you believe in Heaven?... | 0.0290 | 1.0000 |
| Have you heard of the social media site or app BitChute?... | 0.0383 | 0.8165 |
| When you see or hear news about terrible things happening to... | 0.0532 | 0.8367 |
| In recent years, several social media sites have emerged as ... | 0.0564 | 0.8165 |
| In the last month, did you attend religious services in pers... | 0.0605 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Thinking about policies around abortion in this country, in ... | 0.6930 | 0.1155 |
| How would you rate the job that your local elected officials... | 0.7079 | 0.1782 |
| How well does the explanation "Sometimes bad things just hap... | 0.7370 | -0.1195 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
