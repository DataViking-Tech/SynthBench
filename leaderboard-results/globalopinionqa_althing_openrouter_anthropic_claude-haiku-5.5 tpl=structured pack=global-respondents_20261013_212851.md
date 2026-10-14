# SynthBench Score Card

**Provider:** althing/openrouter/anthropic/claude-haiku-5.5 tpl=structured pack=global-respondents
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 772.4s

## SynthBench Parity Score (SPS)

**SPS: 0.8107 [0.7845, 0.8347]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7260 [0.6891, 0.7602] | ███████░░░ |
| P_rank  Rank-Order | 0.7264 [0.6716, 0.7754] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9797 [0.9684, 0.9862] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2740 |
| Median JSD | 0.2416 |
| Mean Kendall's tau | 0.4527 |
| Composite Parity (legacy) | 0.7262 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1642 | +29% |
| random-baseline | 0.6495 | +0.0767 | +12% |

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
| As I read some specific policies of [American] President Geo... | 0.0026 | 1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| Do you think the U.S. should keep military troops in Iraq un... | 0.0301 | 1.0000 |
| In your opinion, has the European Union provided too much fi... | 0.0330 | -0.3333 |
| Do you think this change in the availability of modern medic... | 0.0339 | -1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| And thinking about some political leaders and organizations ... | 0.6404 | -0.5164 |
| Here is a list of three dangers in the world today.  In your... | 0.6620 | -0.8165 |
| And thinking about some political leaders and organizations ... | 0.6625 | -0.2357 |
| Thinking about our relations with China, in your view, which... | 0.7037 | -0.1195 |
| Which statement comes closer to your own views, even if neit... | 0.7544 | -0.1179 |
