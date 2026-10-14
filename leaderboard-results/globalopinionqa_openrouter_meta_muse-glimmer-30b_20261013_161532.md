# SynthBench Score Card

**Provider:** openrouter/meta/muse-glimmer-30b
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 772.7s

## SynthBench Parity Score (SPS)

**SPS: 0.6554 [0.6182, 0.6918]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5648 [0.5109, 0.6138] | ██████░░░░ |
| P_rank  Rank-Order | 0.5372 [0.4701, 0.6057] | █████░░░░░ |
| P_refuse Refusal Cal. | 0.8641 [0.8200, 0.9008] | █████████░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4352 |
| Median JSD | 0.4032 |
| Mean Kendall's tau | 0.0744 |
| Composite Parity (legacy) | 0.5510 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | -0.0110 | -2% |
| random-baseline | 0.6495 | -0.0985 | -15% |

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
| Do you think this change in the availability of modern medic... | 0.0299 | 1.0000 |
| Do you think this change in the working conditions for ordin... | 0.0399 | -1.0000 |
| Now I am going to read you a list of things that may be prob... | 0.0429 | 0.9129 |
| (Now/And thinking about the American people...) Which of the... | 0.0524 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you approve or disapprove of the way President Nicolas Ma... | 0.9022 | -0.8165 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9290 | -0.6325 |
| Thinking about our relations with China, in your view, which... | 0.9331 | -0.6325 |
| (Now I am going to read you a list of things that may be pro... | 0.9361 | -0.3162 |
| How satisfied are you with the way democracy is working in o... | 1.0000 | -0.5774 |
