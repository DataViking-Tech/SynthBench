# SynthBench Score Card

**Provider:** random-baseline
**Dataset:** ntia (Nov 2023) (79 questions)
**Samples per question:** 30
**Elapsed:** 0.1s

## SynthBench Parity Score (SPS)

**SPS: 0.7882 [0.7523, 0.8239]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.8898 [0.8683, 0.9084] | █████████░ |
| P_rank  Rank-Order | 0.4747 [0.3544, 0.5633] | █████░░░░░ |
| P_refuse Refusal Cal. | 1.0000 [1.0000, 1.0000] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.1102 |
| Median JSD | 0.0948 |
| Mean Kendall's tau | -0.0506 |
| Composite Parity (legacy) | 0.6822 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1202 | +21% |
| random-baseline | 0.6495 | +0.0327 | +5% |

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
| Uses a Laptop Computer (among persons ages 3+)?... | 0.0000 | 1.0000 |
| Household Subscribes to Cable or Satellite TV Service (among... | 0.0000 | 0.0000 |
| Streams or Downloads Music, Radio, Podcasts, etc. (among adu... | 0.0001 | 1.0000 |
| Uses the Internet While Traveling Between Places (among adul... | 0.0006 | 1.0000 |
| Uses a Smart TV or Connected Device (among persons ages 3+)?... | 0.0034 | -1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Main Reason for Household Not Online at Home: Can Use Elsewh... | 0.2901 | 0.0000 |
| Household Used to Go Online from Home (among householders)?... | 0.2936 | -1.0000 |
| Main Reason for Household Not Online at Home: Privacy or Sec... | 0.3378 | -1.0000 |
| Anyone in Household Uses Internet at Home (among households ... | 0.3382 | -1.0000 |
| Anyone in Household Uses Internet From Any Location (among h... | 0.4267 | -1.0000 |
