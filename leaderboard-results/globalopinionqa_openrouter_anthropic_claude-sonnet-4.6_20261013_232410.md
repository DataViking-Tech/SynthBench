# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-sonnet-4.6
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 419.8s

## SynthBench Parity Score (SPS)

**SPS: 0.7284 [0.6903, 0.7634]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5706 [0.5256, 0.6197] | ██████░░░░ |
| P_rank  Rank-Order | 0.6347 [0.5632, 0.6958] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9797 [0.9684, 0.9862] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4294 |
| Median JSD | 0.4105 |
| Mean Kendall's tau | 0.2695 |
| Composite Parity (legacy) | 0.6027 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0407 | +7% |
| random-baseline | 0.6495 | -0.0468 | -7% |

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
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| Now I am going to read you a list of things that may be prob... | 0.0482 | 0.9129 |
| (Now/And thinking about the American people...) Which of the... | 0.0524 | 1.0000 |
| Which of these characteristics do you associate with (the Ch... | 0.0834 | 1.0000 |
| (Now I am going to read you a list of things that may be pro... | 0.0881 | 0.6325 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.3162 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9290 | -0.6325 |
| How satisfied are you with the way democracy is working in o... | 1.0000 | -0.5774 |
