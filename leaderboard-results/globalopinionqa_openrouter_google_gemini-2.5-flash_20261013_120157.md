# SynthBench Score Card

**Provider:** openrouter/google/gemini-2.5-flash
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 277.9s

## SynthBench Parity Score (SPS)

**SPS: 0.7653 [0.7310, 0.7949]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6737 [0.6321, 0.7094] | ███████░░░ |
| P_rank  Rank-Order | 0.6425 [0.5745, 0.6986] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9797 [0.9684, 0.9862] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3263 |
| Median JSD | 0.3105 |
| Mean Kendall's tau | 0.2850 |
| Composite Parity (legacy) | 0.6581 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0961 | +17% |
| random-baseline | 0.6495 | +0.0086 | +1% |

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
| Which of these characteristics do you associate with (the Ch... | 0.0152 | 1.0000 |
| Which of these characteristics do you associate with people ... | 0.0169 | -1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| Do you think this change in the working conditions for ordin... | 0.0248 | 1.0000 |
| For each of the following statements about the missile strik... | 0.0345 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you approve or disapprove of the U.S. military operation ... | 0.6983 | -1.0000 |
| Would you say that each of the following is doing a very goo... | 0.7558 | 0.0000 |
| Thinking about our relations with China, in your view, which... | 0.7658 | 0.0000 |
| Please tell me if you have a very favorable, somewhat favora... | 0.8280 | -0.8367 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9290 | -0.6325 |
