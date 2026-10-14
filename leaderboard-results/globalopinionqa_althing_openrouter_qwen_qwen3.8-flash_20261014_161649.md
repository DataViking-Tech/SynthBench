# SynthBench Score Card

**Provider:** althing/openrouter/qwen/qwen3.8-flash
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 1509.0s

## SynthBench Parity Score (SPS)

**SPS: 0.7995 [0.7714, 0.8251]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7299 [0.6954, 0.7607] | ███████░░░ |
| P_rank  Rank-Order | 0.6900 [0.6239, 0.7459] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9784 [0.9673, 0.9849] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2701 |
| Median JSD | 0.2471 |
| Mean Kendall's tau | 0.3800 |
| Composite Parity (legacy) | 0.7100 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1480 | +26% |
| random-baseline | 0.6495 | +0.0605 | +9% |

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
| Thinking about possible war with Iraq, would you favor or op... | 0.0006 | 1.0000 |
| Which of these characteristics do you associate with (the Ch... | 0.0023 | 1.0000 |
| Again, which one better describes George W. Bush...He makes ... | 0.0035 | 1.0000 |
| Do you think this change in the working conditions for ordin... | 0.0083 | 1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How serious of a threat is the Taliban to our country? Is it... | 0.5705 | 0.1195 |
| Do you approve or disapprove of the U.S. military operation ... | 0.6983 | -1.0000 |
| Thinking about our relations with China, in your view, which... | 0.7068 | -0.4472 |
| Which statement comes closer to your own views, even if neit... | 0.7544 | -0.1179 |
| Do you personally believe that getting a divorce is morally ... | 0.7605 | -0.7071 |
