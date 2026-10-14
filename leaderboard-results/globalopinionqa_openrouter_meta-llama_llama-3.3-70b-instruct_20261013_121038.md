# SynthBench Score Card

**Provider:** openrouter/meta-llama/llama-3.3-70b-instruct
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 314.8s

## SynthBench Parity Score (SPS)

**SPS: 0.7701 [0.7379, 0.7991]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6388 [0.5959, 0.6793] | ██████░░░░ |
| P_rank  Rank-Order | 0.6916 [0.6269, 0.7439] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9797 [0.9684, 0.9862] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3612 |
| Median JSD | 0.3249 |
| Mean Kendall's tau | 0.3832 |
| Composite Parity (legacy) | 0.6652 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1032 | +18% |
| random-baseline | 0.6495 | +0.0157 | +2% |

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
| As I read some specific policies of [American] President Geo... | 0.0023 | 1.0000 |
| Do you think the U.S. should keep military troops in Iraq un... | 0.0108 | 1.0000 |
| For each of the following statements about the missile strik... | 0.0179 | 1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| (Now/And thinking about the American people...) Which of the... | 0.0524 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| (Now I'd like to ask you about some political parties.) Plea... | 0.7583 | -0.3162 |
| Thinking about our relations with China, in your view, which... | 0.7658 | 0.0000 |
| Please tell me if you have a very favorable, somewhat favora... | 0.7737 | -0.1195 |
| Now I am going to read you a list of things that may be prob... | 0.7828 | -0.7071 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
