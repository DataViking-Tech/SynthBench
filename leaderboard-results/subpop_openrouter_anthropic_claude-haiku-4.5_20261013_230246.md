# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-haiku-4.5
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 256.2s

## SynthBench Parity Score (SPS)

**SPS: 0.7060 [0.6636, 0.7396]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6070 [0.5621, 0.6487] | ██████░░░░ |
| P_rank  Rank-Order | 0.6802 [0.6371, 0.7158] | ███████░░░ |
| P_refuse Refusal Cal. | 0.8308 [0.7550, 0.8891] | ████████░░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3930 |
| Median JSD | 0.3954 |
| Mean Kendall's tau | 0.3603 |
| Composite Parity (legacy) | 0.6436 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0816 | +15% |
| random-baseline | 0.6495 | -0.0059 | -1% |

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
| Thinking about the area where you live, how easy or difficul... | 0.0706 | 0.0000 |
| Still thinking about the area where you live, do you think t... | 0.0844 | 0.0000 |
| Please indicate if you have attended a concert over the past... | 0.0877 | 0.3333 |
| Please indicate if you have attended a sporting event over t... | 0.0966 | 0.3333 |
| As you may know, the Supreme Court’s decision found that the... | 0.1068 | 0.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think abortion should be...... | 0.9401 | -0.6325 |
| Do you think abortion should be...... | 0.9442 | -0.6325 |
| Do you think abortion should be…... | 0.9526 | -0.6325 |
| Do you personally know someone (such as a close friend, fami... | 0.9667 | -0.8165 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
