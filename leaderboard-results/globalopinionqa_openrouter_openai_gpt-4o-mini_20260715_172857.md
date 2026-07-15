# SynthBench Score Card

**Provider:** openrouter/openai/gpt-4o-mini
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 15
**Elapsed:** 262.7s

## SynthBench Parity Score (SPS)

**SPS: 0.7588 [0.7250, 0.7870]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6355 [0.5947, 0.6726] | ██████░░░░ |
| P_rank  Rank-Order | 0.6612 [0.5975, 0.7188] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9797 [0.9684, 0.9862] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3645 |
| Median JSD | 0.3271 |
| Mean Kendall's tau | 0.3225 |
| Composite Parity (legacy) | 0.6483 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0864 | +15% |
| random-baseline | 0.6495 | -0.0012 | -0% |

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
| Do you think the U.S. should keep military troops in Iraq un... | 0.0359 | 1.0000 |
| (Now/And thinking about the American people...) Which of the... | 0.0524 | 1.0000 |
| (Now I am going to read you a list of things that may be pro... | 0.0881 | 0.6325 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Which statement comes closer to your own views, even if neit... | 0.7544 | -0.1179 |
| (Now I'd like to ask you about some political parties.) Plea... | 0.7583 | -0.3162 |
| Please tell me if you have a very favorable, somewhat favora... | 0.8135 | 0.0000 |
| Thinking about our relations with China, in your view, which... | 0.8777 | -0.3162 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
