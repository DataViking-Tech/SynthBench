# SynthBench Score Card

**Provider:** althing/openrouter/anthropic/claude-sonnet-4
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 661.5s

## SynthBench Parity Score (SPS)

**SPS: 0.8033 [0.7755, 0.8221]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6662 [0.6321, 0.6972] | ███████░░░ |
| P_rank  Rank-Order | 0.7638 [0.7326, 0.7924] | ████████░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3338 |
| Median JSD | 0.3311 |
| Mean Kendall's tau | 0.5276 |
| Composite Parity (legacy) | 0.7150 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1530 | +27% |
| random-baseline | 0.6495 | +0.0655 | +10% |

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
| Please indicate if you have attended a concert over the past... | 0.0035 | 1.0000 |
| Do you personally know someone (such as a close friend, fami... | 0.0126 | 1.0000 |
| Would you favor or oppose employers’ use of artificial intel... | 0.0242 | 0.6667 |
| Do you think gender should be a major factor, minor factor, ... | 0.0303 | 0.9129 |
| Do you think whether a relative attended the school should b... | 0.1061 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think race or ethnicity should be a major factor, min... | 0.6062 | 0.2357 |
| Regardless of whether you think abortion should be legal or ... | 0.6171 | 0.1155 |
| How important is your religion in shaping your views about a... | 0.6375 | 0.1782 |
| As you may know, the Supreme Court’s decision found that the... | 0.6671 | -0.3162 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
