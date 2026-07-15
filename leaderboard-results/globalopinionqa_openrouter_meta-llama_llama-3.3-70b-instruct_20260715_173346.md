# SynthBench Score Card

**Provider:** openrouter/meta-llama/llama-3.3-70b-instruct
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 15
**Elapsed:** 287.2s

## SynthBench Parity Score (SPS)

**SPS: 0.7696 [0.7371, 0.7980]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6428 [0.6002, 0.6829] | ██████░░░░ |
| P_rank  Rank-Order | 0.6861 [0.6202, 0.7372] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9797 [0.9684, 0.9862] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3572 |
| Median JSD | 0.3238 |
| Mean Kendall's tau | 0.3723 |
| Composite Parity (legacy) | 0.6645 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1025 | +18% |
| random-baseline | 0.6495 | +0.0150 | +2% |

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
| For each of the following statements about the missile strik... | 0.0059 | 1.0000 |
| As I read some specific policies of [American] President Geo... | 0.0061 | 1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| Thinking about the future of your country, please tell me wh... | 0.0518 | 0.9129 |
| (Now/And thinking about the American people...) Which of the... | 0.0524 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| (Now I'd like to ask you about some political parties.) Plea... | 0.7583 | -0.3162 |
| Thinking about our relations with China, in your view, which... | 0.7658 | 0.0000 |
| Please tell me if you have a very favorable, somewhat favora... | 0.7737 | -0.1195 |
| Now I am going to read you a list of things that may be prob... | 0.7828 | -0.7071 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
