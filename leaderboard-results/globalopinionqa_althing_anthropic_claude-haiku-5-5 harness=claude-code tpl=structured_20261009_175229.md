# SynthBench Score Card

**Provider:** althing/anthropic/claude-haiku-5-5 harness=claude-code tpl=structured
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 2318.0s

## SynthBench Parity Score (SPS)

**SPS: 0.7425 [0.7071, 0.7769]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6223 [0.5744, 0.6647] | ██████░░░░ |
| P_rank  Rank-Order | 0.6253 [0.5550, 0.6861] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9797 [0.9684, 0.9862] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3777 |
| Median JSD | 0.3456 |
| Mean Kendall's tau | 0.2506 |
| Composite Parity (legacy) | 0.6238 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0618 | +11% |
| random-baseline | 0.6495 | -0.0257 | -4% |

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
| (Now/And thinking about the American people...) Which of the... | 0.0138 | 1.0000 |
| Which of these characteristics do you associate with people ... | 0.0158 | -1.0000 |
| Please tell me if you approve or disapprove of the way Presi... | 0.0195 | 1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| I am going to read you a list of things that the government ... | 0.0289 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Thinking about our relations with China, in your view, which... | 0.7658 | 0.0000 |
| Do you personally believe that drinking alcohol is morally a... | 0.8564 | -0.7071 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.3162 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9290 | -0.6325 |
