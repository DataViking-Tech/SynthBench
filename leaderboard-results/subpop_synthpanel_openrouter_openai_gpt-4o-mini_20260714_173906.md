# SynthBench Score Card

**Provider:** synthpanel/openrouter/openai/gpt-4o-mini
**Dataset:** subpop (100 questions)
**Samples per question:** 15
**Elapsed:** 2385.4s

## SynthBench Parity Score (SPS)

**SPS: 0.6542 [0.6419, 0.6671]** (from 5 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6100 [0.5733, 0.6457] | ██████░░░░ |
| P_rank  Rank-Order | 0.6890 [0.6548, 0.7220] | ███████░░░ |
| P_cond  Conditioning | 0.0305 | ░░░░░░░░░░ |
| P_sub   Subgroup | 0.9642 | ██████████ |
| P_refuse Refusal Cal. | 0.9775 [0.9339, 0.9890] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3900 |
| Median JSD | 0.4289 |
| Mean Kendall's tau | 0.3781 |
| Composite Parity (legacy) | 0.6495 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0875 | +16% |
| random-baseline | 0.6495 | +0.0000 | +0% |

## What These Scores Mean

- **SPS** (SynthBench Parity Score): The overall score — average of all metrics. 0 = random noise, 1 = indistinguishable from real humans.
- **P_dist** (Distributional Parity): How closely does the AI's answer distribution match real humans? If 60% of humans say 'yes' and the AI says 'yes' 60% of the time, that's a perfect match. 0 = completely different, 1 = identical distributions.
- **P_rank** (Rank-Order Parity): Does the AI get the preference ordering right? If humans prefer A > B > C, does the AI agree — even if the exact percentages differ? 0 = reversed ordering, 1 = perfect agreement.
- **P_refuse** (Refusal Calibration): Does the AI refuse to answer at appropriate rates? Humans sometimes decline sensitive questions. An AI that never refuses, or refuses too often, is miscalibrated. 0 = rates completely off, 1 = perfect match.
- **P_cond** (Conditioning Fidelity): When told 'respond as a 65-year-old conservative,' does the AI actually shift its answers? Higher = better demographic role-playing. (When available.)
- **P_sub** (Subgroup Consistency): Is the AI equally accurate across all demographics, or does it nail some groups and miss others? (When available.)

## Demographic Breakdown

### CREGION

Best: Northeast (P_dist=0.6302) / Worst: South (P_dist=0.6213)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Northeast | 0.6302 | 0.0428 | 100 |
| South | 0.6213 | 0.0622 | 100 |

### EDUCATION

Best: College graduate/some postgrad (P_dist=0.6405) / Worst: Less than high school (P_dist=0.5999)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| College graduate/some postgrad | 0.6405 | 0.0285 | 100 |
| Less than high school | 0.5999 | 0.0745 | 100 |

### INCOME

Best: $100,000 or more (P_dist=0.6336) / Worst: Less than $30,000 (P_dist=0.6183)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| $100,000 or more | 0.6336 | 0.0385 | 100 |
| Less than $30,000 | 0.6183 | 0.0755 | 100 |

### POLPARTY

Best: Republican (P_dist=0.6787) / Worst: Democrat (P_dist=0.6269)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Republican | 0.6787 | 0.1597 | 100 |
| Democrat | 0.6269 | 0.0264 | 100 |

### SEX

Best: Male (P_dist=0.6114) / Worst: Female (P_dist=0.5946)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Male | 0.6114 | 0.0251 | 100 |
| Female | 0.5946 | 0.0283 | 100 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think the United States’ decision to withdraw all tro... | 0.0109 | 1.0000 |
| Did you refuse to answer the previous question?... | 0.0149 | 0.8165 |
| Do you think whether a relative attended the school should b... | 0.0347 | 0.9129 |
| Do you think abortion should be legal or illegal in the situ... | 0.0860 | 0.9129 |
| Have your personal views about abortion changed in any way o... | 0.1270 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Regardless of whether you think abortion should be legal or ... | 0.6701 | -0.1155 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.6822 | -0.3162 |
| Do you think people have ever assumed that you benefited unf... | 0.6830 | -0.2357 |
| Do you think that you have ever been at an advantage in your... | 0.7174 | -0.2357 |
| Thinking now about how AI can be used in hiring, how much ha... | 0.7811 | -0.2357 |
