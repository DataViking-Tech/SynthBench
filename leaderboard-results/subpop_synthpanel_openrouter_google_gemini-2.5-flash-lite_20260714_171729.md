# SynthBench Score Card

**Provider:** synthpanel/openrouter/google/gemini-2.5-flash-lite
**Dataset:** subpop (100 questions)
**Samples per question:** 15
**Elapsed:** 1088.8s

## SynthBench Parity Score (SPS)

**SPS: 0.6873 [0.6751, 0.6993]** (from 5 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7200 [0.6907, 0.7482] | ███████░░░ |
| P_rank  Rank-Order | 0.7523 [0.7148, 0.7849] | ████████░░ |
| P_cond  Conditioning | 0.0137 | ░░░░░░░░░░ |
| P_sub   Subgroup | 0.9718 | ██████████ |
| P_refuse Refusal Cal. | 0.9787 [0.9388, 0.9893] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2800 |
| Median JSD | 0.2754 |
| Mean Kendall's tau | 0.5046 |
| Composite Parity (legacy) | 0.7362 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1742 | +31% |
| random-baseline | 0.6495 | +0.0867 | +13% |

## What These Scores Mean

- **SPS** (SynthBench Parity Score): The overall score — average of all metrics. 0 = random noise, 1 = indistinguishable from real humans.
- **P_dist** (Distributional Parity): How closely does the AI's answer distribution match real humans? If 60% of humans say 'yes' and the AI says 'yes' 60% of the time, that's a perfect match. 0 = completely different, 1 = identical distributions.
- **P_rank** (Rank-Order Parity): Does the AI get the preference ordering right? If humans prefer A > B > C, does the AI agree — even if the exact percentages differ? 0 = reversed ordering, 1 = perfect agreement.
- **P_refuse** (Refusal Calibration): Does the AI refuse to answer at appropriate rates? Humans sometimes decline sensitive questions. An AI that never refuses, or refuses too often, is miscalibrated. 0 = rates completely off, 1 = perfect match.
- **P_cond** (Conditioning Fidelity): When told 'respond as a 65-year-old conservative,' does the AI actually shift its answers? Higher = better demographic role-playing. (When available.)
- **P_sub** (Subgroup Consistency): Is the AI equally accurate across all demographics, or does it nail some groups and miss others? (When available.)

## Demographic Breakdown

### CREGION

Best: Northeast (P_dist=0.7402) / Worst: South (P_dist=0.7158)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Northeast | 0.7402 | 0.0548 | 100 |
| South | 0.7158 | 0.0506 | 100 |

### EDUCATION

Best: College graduate/some postgrad (P_dist=0.7525) / Worst: Less than high school (P_dist=0.6913)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| College graduate/some postgrad | 0.7525 | 0.0492 | 100 |
| Less than high school | 0.6913 | 0.0663 | 100 |

### INCOME

Best: $100,000 or more (P_dist=0.7478) / Worst: Less than $30,000 (P_dist=0.7084)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| $100,000 or more | 0.7478 | 0.0600 | 100 |
| Less than $30,000 | 0.7084 | 0.0645 | 100 |

### POLPARTY

Best: Democrat (P_dist=0.7118) / Worst: Republican (P_dist=0.7032)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Democrat | 0.7118 | 0.0499 | 100 |
| Republican | 0.7032 | 0.0736 | 100 |

### SEX

Best: Male (P_dist=0.7477) / Worst: Female (P_dist=0.7227)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Male | 0.7477 | 0.0544 | 100 |
| Female | 0.7227 | 0.0500 | 100 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| If an abortion was carried out in a situation where it was i... | 0.0103 | 1.0000 |
| If a doctor or provider performed an abortion in a situation... | 0.0215 | 0.7071 |
| Do you personally know someone (such as a close friend, fami... | 0.0223 | 0.8165 |
| Do you think people have ever assumed that you benefited unf... | 0.0246 | 1.0000 |
| If you were looking for work, would you want to apply for a ... | 0.0299 | 0.3333 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Which country in Africa is known for having the largest popu... | 0.5123 | 0.3464 |
| Just to confirm, do you think there are any exceptions when ... | 0.5494 | 0.0000 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.5839 | 0.0000 |
| Thinking now about how AI can be used in hiring, how much ha... | 0.5869 | -0.1826 |
| As you may know, the Supreme Court’s decision found that the... | 0.6451 | -0.5976 |
