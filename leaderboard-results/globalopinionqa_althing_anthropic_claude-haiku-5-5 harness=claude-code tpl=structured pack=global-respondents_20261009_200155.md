# SynthBench Score Card

**Provider:** althing/anthropic/claude-haiku-5-5 harness=claude-code tpl=structured pack=global-respondents
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 1312.8s

## SynthBench Parity Score (SPS)

**SPS: 0.8154 [0.7871, 0.8428]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7607 [0.7210, 0.7931] | ████████░░ |
| P_rank  Rank-Order | 0.7058 [0.6450, 0.7584] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9797 [0.9684, 0.9862] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2393 |
| Median JSD | 0.1949 |
| Mean Kendall's tau | 0.4116 |
| Composite Parity (legacy) | 0.7332 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1713 | +30% |
| random-baseline | 0.6495 | +0.0837 | +13% |

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
| Which of these characteristics do you associate with (the Ch... | 0.0001 | 1.0000 |
| As I read some specific policies of [American] President Geo... | 0.0003 | 1.0000 |
| In your opinion, has the European Union provided too much fi... | 0.0029 | 1.0000 |
| Thinking about possible war with Iraq, would you favor or op... | 0.0089 | 1.0000 |
| I am going to read you the same list.  Does...you can openly... | 0.0103 | 0.5477 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How concerned, if at all, are you about Hindu extremism in o... | 0.6100 | -0.2357 |
| And thinking about some political leaders and organizations ... | 0.6625 | -0.2357 |
| Please tell me if you approve or disapprove of the way Prime... | 0.6937 | -0.8165 |
| Thinking about our relations with China, in your view, which... | 0.7023 | -0.1195 |
| Which statement comes closer to your own views, even if neit... | 0.7544 | -0.1179 |
