# SynthBench Score Card

**Provider:** openrouter/openai/gpt-4o-mini
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 15
**Elapsed:** 146.6s

## SynthBench Parity Score (SPS)

**SPS: 0.7493 [0.5912, 0.6834]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6335 [0.5925, 0.6725] | ██████░░░░ |
| P_rank  Rank-Order | 0.6479 [0.5793, 0.7049] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9664 [0.9330, 0.9797] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3665 |
| Median JSD | 0.3226 |
| Mean Kendall's tau | 0.2959 |
| Composite Parity (legacy) | 0.6407 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0787 | +14% |
| random-baseline | 0.6495 | -0.0088 | -1% |

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
| Thinking about possible war with Iraq, would you favor or op... | 0.0225 | 1.0000 |
| (Now/And thinking about the American people...) Which of the... | 0.0524 | 1.0000 |
| (Now I am going to read you a list of things that may be pro... | 0.0881 | 0.6325 |
| Do you think the U.S. should keep military troops in Iraq un... | 0.0905 | -1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| (Now I'd like to ask you about some political parties.) Plea... | 0.7583 | -0.3162 |
| Do you personally believe that getting a divorce is morally ... | 0.7605 | -0.7071 |
| Please tell me if you have a very favorable, somewhat favora... | 0.8135 | 0.0000 |
| Thinking about our relations with China, in your view, which... | 0.8777 | -0.3162 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
