# SynthBench Score Card

**Provider:** althing/openrouter/qwen/qwen3.8-flash
**Dataset:** globalopinionqa (525 questions)
**Samples per question:** 30
**Elapsed:** 7463.0s

## SynthBench Parity Score (SPS)

**SPS: 0.8144 [0.8019, 0.8247]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7395 [0.7259, 0.7537] | ███████░░░ |
| P_rank  Rank-Order | 0.7242 [0.7001, 0.7478] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9793 [0.9755, 0.9822] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2605 |
| Median JSD | 0.2448 |
| Mean Kendall's tau | 0.4485 |
| Composite Parity (legacy) | 0.7319 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1699 | +30% |
| random-baseline | 0.6495 | +0.0824 | +13% |

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
| Do you have friends or relatives who live in another country... | 0.0001 | 1.0000 |
| Is there any area within a kilometer/mile of your home where... | 0.0005 | 1.0000 |
| As I read some proposed policies of President Donald Trump, ... | 0.0035 | 0.8165 |
| Do you think the U.S. should keep military troops in Iraq un... | 0.0039 | 1.0000 |
| Again, which one better describes George W. Bush...He makes ... | 0.0044 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think most Muslims in our country today want to adopt... | 0.8016 | -0.8165 |
| Which statement comes closer to your own views, even if neit... | 0.8324 | 0.0853 |
| Do you personally believe that gambling is morally acceptabl... | 0.8339 | -0.5477 |
| Do you think most Muslims in our country today want to adopt... | 0.8706 | -0.7071 |
| Which one of these comes closest to your opinion, number 1 o... | 0.9885 | -0.6325 |
