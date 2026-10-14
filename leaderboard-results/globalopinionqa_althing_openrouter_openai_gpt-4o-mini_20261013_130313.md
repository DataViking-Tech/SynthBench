# SynthBench Score Card

**Provider:** althing/openrouter/openai/gpt-4o-mini
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 461.4s

## SynthBench Parity Score (SPS)

**SPS: 0.7783 [0.7454, 0.8056]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6669 [0.6310, 0.7027] | ███████░░░ |
| P_rank  Rank-Order | 0.6929 [0.6290, 0.7469] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9752 [0.9639, 0.9825] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3331 |
| Median JSD | 0.2963 |
| Mean Kendall's tau | 0.3858 |
| Composite Parity (legacy) | 0.6799 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1179 | +21% |
| random-baseline | 0.6495 | +0.0304 | +5% |

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
| Do you think the U.S. should keep military troops in Iraq un... | 0.0071 | 1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| (Now/And thinking about the American people...) Which of the... | 0.0524 | 1.0000 |
| Thinking about some issues, do you approve or disapprove of ... | 0.0726 | 0.3333 |
| (Now I am going to read you a list of things that may be pro... | 0.0881 | 0.6325 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you personally believe that drinking alcohol is morally a... | 0.6554 | -0.5477 |
| Do you approve or disapprove of the U.S. military operation ... | 0.6983 | -1.0000 |
| Thinking about our relations with China, in your view, which... | 0.7233 | -0.3586 |
| Which statement comes closer to your own views, even if neit... | 0.7544 | -0.1179 |
| Do you personally believe that getting a divorce is morally ... | 0.7605 | -0.7071 |
