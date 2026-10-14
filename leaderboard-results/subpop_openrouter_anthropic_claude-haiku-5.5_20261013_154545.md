# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-haiku-5.5
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 407.9s

## SynthBench Parity Score (SPS)

**SPS: 0.7327 [0.6976, 0.7602]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6170 [0.5727, 0.6588] | ██████░░░░ |
| P_rank  Rank-Order | 0.6665 [0.6212, 0.7022] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9146 [0.8570, 0.9547] | █████████░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3830 |
| Median JSD | 0.3849 |
| Mean Kendall's tau | 0.3330 |
| Composite Parity (legacy) | 0.6417 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0797 | +14% |
| random-baseline | 0.6495 | -0.0078 | -1% |

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
| Do you think the United States’ decision to withdraw all tro... | 0.0152 | 1.0000 |
| Regardless of whether you think abortion should be legal or ... | 0.0702 | 0.0000 |
| Thinking about the area where you live, how easy or difficul... | 0.0706 | 0.0000 |
| Regardless of whether you think abortion should be legal or ... | 0.0900 | 0.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think abortion should be...... | 0.9364 | -0.6325 |
| Do you think abortion should be...... | 0.9401 | -0.6325 |
| As you may know, the Supreme Court’s decision found that the... | 0.9406 | -0.6325 |
| Do you think abortion should be...... | 0.9442 | -0.6325 |
| Do you think abortion should be…... | 0.9526 | -0.6325 |
