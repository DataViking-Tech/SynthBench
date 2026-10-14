# SynthBench Score Card

**Provider:** althing/openrouter/google/gemini-2.5-flash-lite
**Dataset:** subpop (100 questions)
**Samples per question:** 15
**Elapsed:** 1488.5s

## SynthBench Parity Score (SPS)

**SPS: 0.6822 [0.6707, 0.6928]** (from 5 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7012 [0.6695, 0.7303] | ███████░░░ |
| P_rank  Rank-Order | 0.7412 [0.7066, 0.7717] | ███████░░░ |
| P_cond  Conditioning | 0.0141 | ░░░░░░░░░░ |
| P_sub   Subgroup | 0.9745 | ██████████ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2988 |
| Median JSD | 0.2927 |
| Mean Kendall's tau | 0.4824 |
| Composite Parity (legacy) | 0.7212 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1592 | +28% |
| random-baseline | 0.6495 | +0.0717 | +11% |

## What These Scores Mean

- **SPS** (SynthBench Parity Score): The overall score — average of all metrics. 0 = random noise, 1 = indistinguishable from real humans.
- **P_dist** (Distributional Parity): How closely does the AI's answer distribution match real humans? If 60% of humans say 'yes' and the AI says 'yes' 60% of the time, that's a perfect match. 0 = completely different, 1 = identical distributions.
- **P_rank** (Rank-Order Parity): Does the AI get the preference ordering right? If humans prefer A > B > C, does the AI agree — even if the exact percentages differ? 0 = reversed ordering, 1 = perfect agreement.
- **P_refuse** (Refusal Calibration): Does the AI refuse to answer at appropriate rates? Humans sometimes decline sensitive questions. An AI that never refuses, or refuses too often, is miscalibrated. 0 = rates completely off, 1 = perfect match.
- **P_cond** (Conditioning Fidelity): When told 'respond as a 65-year-old conservative,' does the AI actually shift its answers? Higher = better demographic role-playing. (When available.)
- **P_sub** (Subgroup Consistency): Is the AI equally accurate across all demographics, or does it nail some groups and miss others? (When available.)

## Demographic Breakdown

### CREGION

Best: Northeast (P_dist=0.7190) / Worst: South (P_dist=0.6981)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Northeast | 0.7190 | 0.0496 | 100 |
| South | 0.6981 | 0.0497 | 100 |

### EDUCATION

Best: College graduate/some postgrad (P_dist=0.7382) / Worst: Less than high school (P_dist=0.6847)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| College graduate/some postgrad | 0.7382 | 0.0447 | 100 |
| Less than high school | 0.6847 | 0.0701 | 100 |

### INCOME

Best: $100,000 or more (P_dist=0.7296) / Worst: Less than $30,000 (P_dist=0.6888)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| $100,000 or more | 0.7296 | 0.0571 | 100 |
| Less than $30,000 | 0.6888 | 0.0666 | 100 |

### POLPARTY

Best: Republican (P_dist=0.6949) / Worst: Democrat (P_dist=0.6902)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Republican | 0.6949 | 0.0792 | 100 |
| Democrat | 0.6902 | 0.0478 | 100 |

### SEX

Best: Male (P_dist=0.7174) / Worst: Female (P_dist=0.6934)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Male | 0.7174 | 0.0485 | 100 |
| Female | 0.6934 | 0.0413 | 100 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you personally know someone (such as a close friend, fami... | 0.0045 | 1.0000 |
| Have there been times in the past 12 months when you did not... | 0.0138 | 1.0000 |
| Did you refuse to answer the previous question?... | 0.0149 | 0.8165 |
| If a doctor or provider performed an abortion in a situation... | 0.0153 | 0.6667 |
| Do you think whether a relative attended the school should b... | 0.0294 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have there been times in the past 12 months when you did not... | 0.5689 | 0.1826 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.5839 | 0.0000 |
| Thinking now about how AI can be used in hiring, how much ha... | 0.5869 | -0.1826 |
| Do you think being the first person in the family to go to c... | 0.6147 | -0.2357 |
| As you may know, the Supreme Court’s decision found that the... | 0.6494 | -0.5976 |
