# SynthBench Score Card

**Provider:** openrouter/google/gemini-2.5-flash
**Dataset:** subpop (100 questions)
**Samples per question:** 15
**Elapsed:** 927.1s

## SynthBench Parity Score (SPS)

**SPS: 0.6731 [0.6556, 0.6882]** (from 5 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6510 [0.6080, 0.6872] | ███████░░░ |
| P_rank  Rank-Order | 0.6726 [0.6242, 0.7149] | ███████░░░ |
| P_cond  Conditioning | 0.0815 | █░░░░░░░░░ |
| P_sub   Subgroup | 0.9807 | ██████████ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3490 |
| Median JSD | 0.2976 |
| Mean Kendall's tau | 0.3452 |
| Composite Parity (legacy) | 0.6618 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0998 | +18% |
| random-baseline | 0.6495 | +0.0123 | +2% |

## What These Scores Mean

- **SPS** (SynthBench Parity Score): The overall score — average of all metrics. 0 = random noise, 1 = indistinguishable from real humans.
- **P_dist** (Distributional Parity): How closely does the AI's answer distribution match real humans? If 60% of humans say 'yes' and the AI says 'yes' 60% of the time, that's a perfect match. 0 = completely different, 1 = identical distributions.
- **P_rank** (Rank-Order Parity): Does the AI get the preference ordering right? If humans prefer A > B > C, does the AI agree — even if the exact percentages differ? 0 = reversed ordering, 1 = perfect agreement.
- **P_refuse** (Refusal Calibration): Does the AI refuse to answer at appropriate rates? Humans sometimes decline sensitive questions. An AI that never refuses, or refuses too often, is miscalibrated. 0 = rates completely off, 1 = perfect match.
- **P_cond** (Conditioning Fidelity): When told 'respond as a 65-year-old conservative,' does the AI actually shift its answers? Higher = better demographic role-playing. (When available.)
- **P_sub** (Subgroup Consistency): Is the AI equally accurate across all demographics, or does it nail some groups and miss others? (When available.)

## Demographic Breakdown

### CREGION

Best: Northeast (P_dist=0.7340) / Worst: South (P_dist=0.7101)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Northeast | 0.7340 | 0.1049 | 100 |
| South | 0.7101 | 0.0909 | 100 |

### EDUCATION

Best: College graduate/some postgrad (P_dist=0.7346) / Worst: Less than high school (P_dist=0.7298)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| College graduate/some postgrad | 0.7346 | 0.0916 | 100 |
| Less than high school | 0.7298 | 0.1608 | 100 |

### INCOME

Best: $100,000 or more (P_dist=0.7212) / Worst: Less than $30,000 (P_dist=0.6984)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| $100,000 or more | 0.7212 | 0.0951 | 100 |
| Less than $30,000 | 0.6984 | 0.1090 | 100 |

### POLPARTY

Best: Republican (P_dist=0.7369) / Worst: Democrat (P_dist=0.7086)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Republican | 0.7369 | 0.1393 | 100 |
| Democrat | 0.7086 | 0.1025 | 100 |

### SEX

Best: Female (P_dist=0.7404) / Worst: Male (P_dist=0.7378)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Female | 0.7404 | 0.1203 | 100 |
| Male | 0.7378 | 0.1022 | 100 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please indicate if you have attended a sporting event over t... | 0.0101 | 1.0000 |
| Would you favor or oppose employers’ use of artificial intel... | 0.0108 | 0.6667 |
| Please choose the statement that comes closer to your own vi... | 0.0496 | 0.3333 |
| Thinking about the use of artificial intelligence (AI) in he... | 0.0651 | 0.6000 |
| Have there been times in the past 12 months when you did not... | 0.1125 | 0.1826 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Thinking now about how AI can be used in hiring, how much ha... | 0.7811 | -0.2357 |
| Do you think abortion should be...... | 0.9364 | -0.6325 |
| Do you think abortion should be...... | 0.9401 | -0.6325 |
| Do you think abortion should be...... | 0.9442 | -0.6325 |
| Do you think abortion should be…... | 0.9526 | -0.6325 |
