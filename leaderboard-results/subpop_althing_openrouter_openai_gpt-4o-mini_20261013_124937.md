# SynthBench Score Card

**Provider:** althing/openrouter/openai/gpt-4o-mini
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 474.1s

## SynthBench Parity Score (SPS)

**SPS: 0.7601 [0.7399, 0.7809]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6125 [0.5766, 0.6480] | ██████░░░░ |
| P_rank  Rank-Order | 0.6879 [0.6546, 0.7207] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3875 |
| Median JSD | 0.4085 |
| Mean Kendall's tau | 0.3759 |
| Composite Parity (legacy) | 0.6502 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0882 | +16% |
| random-baseline | 0.6495 | +0.0007 | +0% |

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
| Did you refuse to answer the previous question?... | 0.0149 | 0.8165 |
| Do you think whether a relative attended the school should b... | 0.0347 | 0.9129 |
| Do you think the United States’ decision to withdraw all tro... | 0.0474 | 0.3333 |
| Have there been times in the past 12 months when you did not... | 0.0912 | 0.5477 |
| Have your personal views about abortion changed in any way o... | 0.1270 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Regardless of whether you think abortion should be legal or ... | 0.6701 | -0.1155 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.6822 | -0.3162 |
| Do you think people have ever assumed that you benefited unf... | 0.6830 | -0.2357 |
| Do you think that you have ever been at an advantage in your... | 0.7174 | -0.2357 |
| Thinking now about how AI can be used in hiring, how much ha... | 0.7811 | -0.2357 |
