# SynthBench Score Card

**Provider:** openrouter/openai/gpt-4o-mini
**Dataset:** subpop (100 questions)
**Samples per question:** 15
**Elapsed:** 5173.3s

## SynthBench Parity Score (SPS)

**SPS: 0.6580 [0.6397, 0.6707]** (from 5 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6255 [0.5866, 0.6625] | ██████░░░░ |
| P_rank  Rank-Order | 0.6964 [0.6585, 0.7317] | ███████░░░ |
| P_cond  Conditioning | 0.0154 | ░░░░░░░░░░ |
| P_sub   Subgroup | 0.9727 | ██████████ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3745 |
| Median JSD | 0.3861 |
| Mean Kendall's tau | 0.3927 |
| Composite Parity (legacy) | 0.6609 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0990 | +18% |
| random-baseline | 0.6495 | +0.0114 | +2% |

## What These Scores Mean

- **SPS** (SynthBench Parity Score): The overall score — average of all metrics. 0 = random noise, 1 = indistinguishable from real humans.
- **P_dist** (Distributional Parity): How closely does the AI's answer distribution match real humans? If 60% of humans say 'yes' and the AI says 'yes' 60% of the time, that's a perfect match. 0 = completely different, 1 = identical distributions.
- **P_rank** (Rank-Order Parity): Does the AI get the preference ordering right? If humans prefer A > B > C, does the AI agree — even if the exact percentages differ? 0 = reversed ordering, 1 = perfect agreement.
- **P_refuse** (Refusal Calibration): Does the AI refuse to answer at appropriate rates? Humans sometimes decline sensitive questions. An AI that never refuses, or refuses too often, is miscalibrated. 0 = rates completely off, 1 = perfect match.
- **P_cond** (Conditioning Fidelity): When told 'respond as a 65-year-old conservative,' does the AI actually shift its answers? Higher = better demographic role-playing. (When available.)
- **P_sub** (Subgroup Consistency): Is the AI equally accurate across all demographics, or does it nail some groups and miss others? (When available.)

## Demographic Breakdown

### CREGION

Best: Northeast (P_dist=0.6008) / Worst: South (P_dist=0.5978)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Northeast | 0.6008 | 0.0320 | 100 |
| South | 0.5978 | 0.0507 | 100 |

### EDUCATION

Best: College graduate/some postgrad (P_dist=0.6308) / Worst: Less than high school (P_dist=0.6221)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| College graduate/some postgrad | 0.6308 | 0.0214 | 100 |
| Less than high school | 0.6221 | 0.0847 | 100 |

### INCOME

Best: Less than $30,000 (P_dist=0.6095) / Worst: $100,000 or more (P_dist=0.6090)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Less than $30,000 | 0.6095 | 0.0723 | 100 |
| $100,000 or more | 0.6090 | 0.0146 | 100 |

### POLPARTY

Best: Republican (P_dist=0.6486) / Worst: Democrat (P_dist=0.6205)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Republican | 0.6486 | 0.1251 | 100 |
| Democrat | 0.6205 | 0.0380 | 100 |

### SEX

Best: Male (P_dist=0.6086) / Worst: Female (P_dist=0.5874)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Male | 0.6086 | 0.0198 | 100 |
| Female | 0.5874 | 0.0337 | 100 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Have there been times in the past 12 months when you did not... | 0.0165 | 0.9129 |
| Do you think the United States’ decision to withdraw all tro... | 0.0189 | 1.0000 |
| Please indicate if you have attended a concert over the past... | 0.0200 | 1.0000 |
| Do you think whether a relative attended the school should b... | 0.0319 | 0.9129 |
| Have there been times in the past 12 months when you did not... | 0.0466 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Regardless of whether you think abortion should be legal or ... | 0.6701 | -0.1155 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.6822 | -0.3162 |
| Do you think the use of artificial intelligence (AI) in heal... | 0.6939 | -0.2357 |
| Thinking now about how AI can be used in hiring, how much ha... | 0.7811 | -0.2357 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
