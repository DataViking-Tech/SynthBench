# SynthBench Score Card

**Provider:** openrouter/openai/gpt-4o
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 391.9s

## SynthBench Parity Score (SPS)

**SPS: 0.7647 [0.7288, 0.7955]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6864 [0.6429, 0.7252] | ███████░░░ |
| P_rank  Rank-Order | 0.6292 [0.5559, 0.6913] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9783 [0.9670, 0.9849] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3136 |
| Median JSD | 0.2471 |
| Mean Kendall's tau | 0.2585 |
| Composite Parity (legacy) | 0.6578 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0958 | +17% |
| random-baseline | 0.6495 | +0.0083 | +1% |

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
| Do you think our country's efforts to reduce government spen... | 0.0186 | 1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| I am going to read you the same list.  Does...you can openly... | 0.0322 | 0.6667 |
| As I read a list of groups and organizations, for each, plea... | 0.0336 | 1.0000 |
| (Now/And thinking about the American people...) Which of the... | 0.0524 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| (Now I'd like to ask you about some political parties.) Plea... | 0.7290 | -0.5976 |
| Thinking about our relations with China, in your view, which... | 0.7336 | -0.9487 |
| Which statement comes closer to your own views, even if neit... | 0.7544 | -0.1179 |
| Please tell me if you have a very favorable, somewhat favora... | 0.8399 | -0.6708 |
| Please tell me if you have a very favorable, somewhat favora... | 0.8979 | -0.8367 |
