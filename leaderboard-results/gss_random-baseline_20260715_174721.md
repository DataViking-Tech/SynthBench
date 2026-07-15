# SynthBench Score Card

**Provider:** random-baseline
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 0.0s

## SynthBench Parity Score (SPS)

**SPS: 0.7354 [0.7155, 0.7556]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.8169 [0.7972, 0.8337] | ████████░░ |
| P_rank  Rank-Order | 0.4172 [0.3607, 0.4643] | ████░░░░░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.1831 |
| Median JSD | 0.1909 |
| Mean Kendall's tau | -0.1656 |
| Composite Parity (legacy) | 0.6170 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0551 | +10% |
| random-baseline | 0.6495 | -0.0325 | -5% |

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
| Would you say that most of the time people try to be helpful... | 0.0118 | 1.0000 |
| We are faced with many problems in this country, none of whi... | 0.0488 | 0.5477 |
| In general, do you think the courts in this area deal too ha... | 0.0555 | 0.1826 |
| I am going to name an institution in this country. As far as... | 0.0709 | 1.0000 |
| How often do you attend religious services?... | 0.0736 | 0.1497 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| We are faced with many problems in this country, none of whi... | 0.2853 | 0.1826 |
| Some people say that people get ahead by their own hard work... | 0.3102 | -0.6667 |
| When a person has a disease that cannot be cured, do you thi... | 0.3170 | -1.0000 |
| What is your opinion about a married person having sexual re... | 0.3291 | -0.3162 |
| Do you happen to have in your home or garage any guns or rev... | 0.5236 | -0.6667 |
