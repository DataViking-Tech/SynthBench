# SynthBench Score Card

**Provider:** majority-baseline
**Dataset:** ntia (Nov 2023) (79 questions)
**Samples per question:** 30
**Elapsed:** 0.1s

## SynthBench Parity Score (SPS)

**SPS: 0.6650 [0.6080, 0.7251]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5646 [0.4959, 0.6401] | ██████░░░░ |
| P_rank  Rank-Order | 0.4304 [0.3165, 0.5316] | ████░░░░░░ |
| P_refuse Refusal Cal. | 1.0000 [1.0000, 1.0000] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4354 |
| Median JSD | 0.4492 |
| Mean Kendall's tau | -0.1392 |
| Composite Parity (legacy) | 0.4975 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | -0.0645 | -11% |
| random-baseline | 0.6495 | -0.1520 | -23% |

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
| Anyone in Household Uses Internet From Any Location (among h... | 0.0000 | 1.0000 |
| Anyone in Household Uses Internet From Any Location (among h... | 0.0000 | 1.0000 |
| Anyone in Household Uses Internet at Home (among households ... | 0.0000 | 1.0000 |
| Anyone in Household Uses Internet at Home (among households ... | 0.0147 | 1.0000 |
| Uses Text Messaging or Instant Messaging (among adult intern... | 0.0251 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Main Reason for Household Not Online at Home: Too Expensive ... | 0.9195 | -1.0000 |
| Main Reason for Household Not Online at Home: Privacy or Sec... | 0.9660 | -1.0000 |
| Main Reason for Household Not Online at Home: Can Use Elsewh... | 0.9742 | -1.0000 |
| Main Reason for Household Not Online at Home: No/Inadequate ... | 0.9779 | -1.0000 |
| Main Reason for Household Not Online at Home: Not Available ... | 0.9800 | -1.0000 |
