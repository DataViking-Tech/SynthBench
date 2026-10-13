# SynthBench Score Card

**Provider:** raw-anthropic/claude-haiku-4-5-20251001 harness=claude-code
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 6727.8s

## SynthBench Parity Score (SPS)

**SPS: 0.6665 [0.6291, 0.7023]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5683 [0.5191, 0.6137] | ██████░░░░ |
| P_rank  Rank-Order | 0.5526 [0.5046, 0.6002] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.8787 [0.8318, 0.9100] | █████████░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4317 |
| Median JSD | 0.3722 |
| Mean Kendall's tau | 0.1051 |
| Composite Parity (legacy) | 0.5604 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | -0.0015 | -0% |
| random-baseline | 0.6495 | -0.0891 | -14% |

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
| Would you favor or oppose employers’ use of artificial intel... | 0.0552 | 0.9129 |
| Still thinking about the area where you live, do you think t... | 0.0844 | 0.0000 |
| Thinking about the use of artificial intelligence (AI) in he... | 0.0855 | 0.8165 |
| Do you think people have ever assumed that you benefited unf... | 0.1181 | 0.6667 |
| If you were looking for work, would you want to apply for a ... | 0.1465 | 0.3333 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think abortion should be...... | 0.9401 | -0.6325 |
| Do you think abortion should be...... | 0.9442 | -0.6325 |
| How would you rate the job the Biden administration has done... | 0.9483 | -0.6325 |
| Do you think abortion should be…... | 0.9526 | -0.6325 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
