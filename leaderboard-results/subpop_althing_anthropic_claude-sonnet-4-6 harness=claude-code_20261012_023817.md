# SynthBench Score Card

**Provider:** althing/anthropic/claude-sonnet-4-6 harness=claude-code
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 3161.3s

## SynthBench Parity Score (SPS)

**SPS: 0.7828 [0.7525, 0.8019]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6339 [0.5991, 0.6652] | ██████░░░░ |
| P_rank  Rank-Order | 0.7346 [0.7001, 0.7627] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3661 |
| Median JSD | 0.3900 |
| Mean Kendall's tau | 0.4692 |
| Composite Parity (legacy) | 0.6842 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1223 | +22% |
| random-baseline | 0.6495 | +0.0347 | +5% |

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
| In the news you are receiving about the Biden administration... | 0.0136 | 1.0000 |
| Which statement comes closer to your view, even if neither i... | 0.1130 | 0.3333 |
| Do you think gender should be a major factor, minor factor, ... | 0.1154 | 0.7071 |
| Have your personal views about abortion changed in any way o... | 0.1270 | 0.7071 |
| Do you think abortion should be legal or illegal in the situ... | 0.1278 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Thinking about the use of artificial intelligence (AI) in th... | 0.6221 | 0.0000 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.6822 | -0.3162 |
| Do you think people have ever assumed that you benefited unf... | 0.6830 | -0.2357 |
| How important is your religion in shaping your views about a... | 0.7534 | -0.3563 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
