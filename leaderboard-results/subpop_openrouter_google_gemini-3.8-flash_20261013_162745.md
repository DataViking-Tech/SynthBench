# SynthBench Score Card

**Provider:** openrouter/google/gemini-3.8-flash
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 1614.3s

## SynthBench Parity Score (SPS)

**SPS: 0.6000 [0.5626, 0.6372]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.3795 [0.3226, 0.4312] | ████░░░░░░ |
| P_rank  Rank-Order | 0.4405 [0.3873, 0.4920] | ████░░░░░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.6205 |
| Median JSD | 0.5819 |
| Mean Kendall's tau | -0.1190 |
| Composite Parity (legacy) | 0.4100 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | -0.1520 | -27% |
| random-baseline | 0.6495 | -0.2395 | -37% |

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
| If you were looking for work, would you want to apply for a ... | 0.0512 | 1.0000 |
| Do you think the use of artificial intelligence (AI) in heal... | 0.1606 | 0.6667 |
| Thinking about health products, which of the following uses ... | 0.1850 | 0.5774 |
| Do you think the use of artificial intelligence (AI) in heal... | 0.1939 | 0.3333 |
| Please indicate if you have attended a concert over the past... | 0.1965 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think gender should be a major factor, minor factor, ... | 0.9764 | -0.7071 |
| Do you think race or ethnicity should be a major factor, min... | 0.9767 | -0.7071 |
| Just to confirm, do you think there are any exceptions when ... | 0.9809 | -0.8165 |
| Do you think abortion should be legal or illegal in the situ... | 0.9867 | -0.7071 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
