# SynthBench Score Card

**Provider:** synthpanel/openrouter/anthropic/claude-haiku-4-5
**Dataset:** subpop (200 questions)
**Samples per question:** 30
**Elapsed:** 917.4s

## SynthBench Parity Score (SPS)

**SPS: 0.7873 [0.7680, 0.8017]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6629 [0.6377, 0.6862] | ███████░░░ |
| P_rank  Rank-Order | 0.7235 [0.7020, 0.7459] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9755 [0.9539, 0.9862] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3371 |
| Median JSD | 0.3236 |
| Mean Kendall's tau | 0.4469 |
| Composite Parity (legacy) | 0.6932 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1312 | +23% |
| random-baseline | 0.6495 | +0.0437 | +7% |

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
| Do you think medication abortion should be legal or illegal ... | 0.0051 | 1.0000 |
| Have you heard of the social media site or app BitChute?... | 0.0383 | 0.8165 |
| In recent years, several social media sites have emerged as ... | 0.0564 | 0.8165 |
| In the last month, did you attend religious services in pers... | 0.0605 | 0.8165 |
| Have you heard of the social media site or app Gab?... | 0.0622 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| When you see or hear news about terrible things happening to... | 0.6630 | 0.0000 |
| Thinking about policies around abortion in this country, in ... | 0.6930 | 0.1155 |
| How well does the explanation "Sometimes bad things just hap... | 0.7718 | 0.0000 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
