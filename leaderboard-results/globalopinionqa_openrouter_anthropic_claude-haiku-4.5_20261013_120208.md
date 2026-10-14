# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-haiku-4.5
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 193.7s

## SynthBench Parity Score (SPS)

**SPS: 0.6809 [0.6413, 0.7159]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6733 [0.6198, 0.7204] | ███████░░░ |
| P_rank  Rank-Order | 0.6207 [0.5621, 0.6791] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.7487 [0.6674, 0.8217] | ███████░░░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3267 |
| Median JSD | 0.2734 |
| Mean Kendall's tau | 0.2413 |
| Composite Parity (legacy) | 0.6470 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0850 | +15% |
| random-baseline | 0.6495 | -0.0025 | -0% |

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
| Overall, was the break-up of Czechoslovakia into two indepen... | 0.0000 | 0.0000 |
| In general, do you think our country is covered fairly or un... | 0.0001 | 0.0000 |
| Do you think our country's efforts to reduce government spen... | 0.0051 | 0.0000 |
| Has the Turkish parliament made the right decision not to al... | 0.0052 | 0.0000 |
| Do you think that the rise of nontraditional political parti... | 0.0058 | 0.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.3162 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9290 | -0.6325 |
