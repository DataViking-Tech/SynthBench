# SynthBench Score Card

**Provider:** openrouter/google/gemini-2.5-flash
**Dataset:** subpop (100 questions)
**Samples per question:** 15
**Elapsed:** 2025.3s

## SynthBench Parity Score (SPS)

**SPS: 0.6717 [0.6541, 0.6861]** (from 5 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6674 [0.6252, 0.7013] | ███████░░░ |
| P_rank  Rank-Order | 0.6839 [0.6408, 0.7208] | ███████░░░ |
| P_cond  Conditioning | 0.0597 | █░░░░░░░░░ |
| P_sub   Subgroup | 0.9676 | ██████████ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3326 |
| Median JSD | 0.2774 |
| Mean Kendall's tau | 0.3679 |
| Composite Parity (legacy) | 0.6757 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1137 | +20% |
| random-baseline | 0.6495 | +0.0262 | +4% |

## What These Scores Mean

- **SPS** (SynthBench Parity Score): The overall score — average of all metrics. 0 = random noise, 1 = indistinguishable from real humans.
- **P_dist** (Distributional Parity): How closely does the AI's answer distribution match real humans? If 60% of humans say 'yes' and the AI says 'yes' 60% of the time, that's a perfect match. 0 = completely different, 1 = identical distributions.
- **P_rank** (Rank-Order Parity): Does the AI get the preference ordering right? If humans prefer A > B > C, does the AI agree — even if the exact percentages differ? 0 = reversed ordering, 1 = perfect agreement.
- **P_refuse** (Refusal Calibration): Does the AI refuse to answer at appropriate rates? Humans sometimes decline sensitive questions. An AI that never refuses, or refuses too often, is miscalibrated. 0 = rates completely off, 1 = perfect match.
- **P_cond** (Conditioning Fidelity): When told 'respond as a 65-year-old conservative,' does the AI actually shift its answers? Higher = better demographic role-playing. (When available.)
- **P_sub** (Subgroup Consistency): Is the AI equally accurate across all demographics, or does it nail some groups and miss others? (When available.)

## Demographic Breakdown

### CREGION

Best: Northeast (P_dist=0.7486) / Worst: South (P_dist=0.7202)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Northeast | 0.7486 | 0.1059 | 100 |
| South | 0.7202 | 0.0930 | 100 |

### EDUCATION

Best: College graduate/some postgrad (P_dist=0.7170) / Worst: Less than high school (P_dist=0.6979)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| College graduate/some postgrad | 0.7170 | 0.0712 | 100 |
| Less than high school | 0.6979 | 0.1273 | 100 |

### INCOME

Best: $100,000 or more (P_dist=0.7136) / Worst: Less than $30,000 (P_dist=0.6848)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| $100,000 or more | 0.7136 | 0.0785 | 100 |
| Less than $30,000 | 0.6848 | 0.0894 | 100 |

### POLPARTY

Best: Republican (P_dist=0.7113) / Worst: Democrat (P_dist=0.7026)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Republican | 0.7113 | 0.1154 | 100 |
| Democrat | 0.7026 | 0.0839 | 100 |

### SEX

Best: Male (P_dist=0.7669) / Worst: Female (P_dist=0.7359)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Male | 0.7669 | 0.1061 | 100 |
| Female | 0.7359 | 0.1004 | 100 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think artificial intelligence (AI) would do better, w... | 0.0231 | 0.8000 |
| Please indicate if you have traveled more than 100 miles fro... | 0.0246 | 1.0000 |
| Do you think that you have ever been at a disadvantage in yo... | 0.0553 | 0.6667 |
| Have there been times in the past 12 months when you did not... | 0.0759 | 0.5477 |
| Do you think that you have ever been at an advantage in your... | 0.0835 | 0.6667 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How confident, if at all, are you that the government is con... | 0.7230 | -0.3586 |
| Do you think abortion should be...... | 0.8173 | -0.3586 |
| Do you think abortion should be...... | 0.9401 | -0.6325 |
| Do you think abortion should be...... | 0.9442 | -0.6325 |
| Do you think abortion should be…... | 0.9526 | -0.6325 |
