# SynthBench Score Card

**Provider:** openrouter/openai/gpt-4o-mini
**Dataset:** subpop (100 questions)
**Samples per question:** 15
**Elapsed:** 1566.5s

## SynthBench Parity Score (SPS)

**SPS: 0.6601 [0.6412, 0.6747]** (from 5 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6324 [0.5914, 0.6698] | ██████░░░░ |
| P_rank  Rank-Order | 0.7031 [0.6629, 0.7414] | ███████░░░ |
| P_cond  Conditioning | 0.0139 | ░░░░░░░░░░ |
| P_sub   Subgroup | 0.9710 | ██████████ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3676 |
| Median JSD | 0.3628 |
| Mean Kendall's tau | 0.4061 |
| Composite Parity (legacy) | 0.6677 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1057 | +19% |
| random-baseline | 0.6495 | +0.0182 | +3% |

## What These Scores Mean

- **SPS** (SynthBench Parity Score): The overall score — average of all metrics. 0 = random noise, 1 = indistinguishable from real humans.
- **P_dist** (Distributional Parity): How closely does the AI's answer distribution match real humans? If 60% of humans say 'yes' and the AI says 'yes' 60% of the time, that's a perfect match. 0 = completely different, 1 = identical distributions.
- **P_rank** (Rank-Order Parity): Does the AI get the preference ordering right? If humans prefer A > B > C, does the AI agree — even if the exact percentages differ? 0 = reversed ordering, 1 = perfect agreement.
- **P_refuse** (Refusal Calibration): Does the AI refuse to answer at appropriate rates? Humans sometimes decline sensitive questions. An AI that never refuses, or refuses too often, is miscalibrated. 0 = rates completely off, 1 = perfect match.
- **P_cond** (Conditioning Fidelity): When told 'respond as a 65-year-old conservative,' does the AI actually shift its answers? Higher = better demographic role-playing. (When available.)
- **P_sub** (Subgroup Consistency): Is the AI equally accurate across all demographics, or does it nail some groups and miss others? (When available.)

## Demographic Breakdown

### CREGION

Best: South (P_dist=0.6012) / Worst: Northeast (P_dist=0.5980)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| South | 0.6012 | 0.0522 | 100 |
| Northeast | 0.5980 | 0.0383 | 100 |

### EDUCATION

Best: College graduate/some postgrad (P_dist=0.6327) / Worst: Less than high school (P_dist=0.6217)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| College graduate/some postgrad | 0.6327 | 0.0180 | 100 |
| Less than high school | 0.6217 | 0.0780 | 100 |

### INCOME

Best: $100,000 or more (P_dist=0.6163) / Worst: Less than $30,000 (P_dist=0.6120)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| $100,000 or more | 0.6163 | 0.0173 | 100 |
| Less than $30,000 | 0.6120 | 0.0705 | 100 |

### POLPARTY

Best: Republican (P_dist=0.6502) / Worst: Democrat (P_dist=0.6246)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Republican | 0.6502 | 0.1300 | 100 |
| Democrat | 0.6246 | 0.0395 | 100 |

### SEX

Best: Male (P_dist=0.6052) / Worst: Female (P_dist=0.5849)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Male | 0.6052 | 0.0176 | 100 |
| Female | 0.5849 | 0.0390 | 100 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please indicate if you have attended a concert over the past... | 0.0023 | 1.0000 |
| If an abortion was carried out in a situation where it was i... | 0.0112 | 1.0000 |
| Have there been times in the past 12 months when you did not... | 0.0253 | 1.0000 |
| Have there been times in the past 12 months when you did not... | 0.0295 | 0.9129 |
| Do you think whether a relative attended the school should b... | 0.0453 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Thinking about the use of artificial intelligence (AI) in th... | 0.6822 | -0.3162 |
| Do you think the use of artificial intelligence (AI) in heal... | 0.6939 | -0.2357 |
| Thinking now about how AI can be used in hiring, how much ha... | 0.7811 | -0.2357 |
| How acceptable do you think it is for social media companies... | 0.8398 | -0.3464 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
