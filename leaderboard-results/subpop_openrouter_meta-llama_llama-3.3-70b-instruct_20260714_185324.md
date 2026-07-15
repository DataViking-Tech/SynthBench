# SynthBench Score Card

**Provider:** openrouter/meta-llama/llama-3.3-70b-instruct
**Dataset:** subpop (100 questions)
**Samples per question:** 15
**Elapsed:** 2998.9s

## SynthBench Parity Score (SPS)

**SPS: 0.6704 [0.6505, 0.6820]** (from 5 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6503 [0.6114, 0.6814] | ███████░░░ |
| P_rank  Rank-Order | 0.7416 [0.7059, 0.7709] | ███████░░░ |
| P_cond  Conditioning | 0.0132 | ░░░░░░░░░░ |
| P_sub   Subgroup | 0.9671 | ██████████ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3497 |
| Median JSD | 0.3445 |
| Mean Kendall's tau | 0.4831 |
| Composite Parity (legacy) | 0.6959 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1340 | +24% |
| random-baseline | 0.6495 | +0.0464 | +7% |

## What These Scores Mean

- **SPS** (SynthBench Parity Score): The overall score — average of all metrics. 0 = random noise, 1 = indistinguishable from real humans.
- **P_dist** (Distributional Parity): How closely does the AI's answer distribution match real humans? If 60% of humans say 'yes' and the AI says 'yes' 60% of the time, that's a perfect match. 0 = completely different, 1 = identical distributions.
- **P_rank** (Rank-Order Parity): Does the AI get the preference ordering right? If humans prefer A > B > C, does the AI agree — even if the exact percentages differ? 0 = reversed ordering, 1 = perfect agreement.
- **P_refuse** (Refusal Calibration): Does the AI refuse to answer at appropriate rates? Humans sometimes decline sensitive questions. An AI that never refuses, or refuses too often, is miscalibrated. 0 = rates completely off, 1 = perfect match.
- **P_cond** (Conditioning Fidelity): When told 'respond as a 65-year-old conservative,' does the AI actually shift its answers? Higher = better demographic role-playing. (When available.)
- **P_sub** (Subgroup Consistency): Is the AI equally accurate across all demographics, or does it nail some groups and miss others? (When available.)

## Demographic Breakdown

### CREGION

Best: Northeast (P_dist=0.6387) / Worst: South (P_dist=0.6245)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Northeast | 0.6387 | 0.0325 | 100 |
| South | 0.6245 | 0.0486 | 100 |

### EDUCATION

Best: College graduate/some postgrad (P_dist=0.6530) / Worst: Less than high school (P_dist=0.6115)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| College graduate/some postgrad | 0.6530 | 0.0278 | 100 |
| Less than high school | 0.6115 | 0.0700 | 100 |

### INCOME

Best: $100,000 or more (P_dist=0.6431) / Worst: Less than $30,000 (P_dist=0.6314)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| $100,000 or more | 0.6431 | 0.0282 | 100 |
| Less than $30,000 | 0.6314 | 0.0566 | 100 |

### POLPARTY

Best: Republican (P_dist=0.6823) / Worst: Democrat (P_dist=0.6612)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Republican | 0.6823 | 0.1005 | 100 |
| Democrat | 0.6612 | 0.0397 | 100 |

### SEX

Best: Male (P_dist=0.6428) / Worst: Female (P_dist=0.6102)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Male | 0.6428 | 0.0314 | 100 |
| Female | 0.6102 | 0.0287 | 100 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think whether a relative attended the school should b... | 0.0319 | 0.9129 |
| Here’s a list of activities some people do and others do not... | 0.0343 | 0.3333 |
| If an abortion was carried out in a situation where it was i... | 0.0502 | 0.3333 |
| Do you think the use of artificial intelligence (AI) in heal... | 0.0795 | 0.9129 |
| Do you think gender should be a major factor, minor factor, ... | 0.1154 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Regardless of whether you think abortion should be legal or ... | 0.6701 | -0.1155 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.6822 | -0.3162 |
| How important is your religion in shaping your views about a... | 0.7067 | -0.1782 |
| If a woman had an abortion in a situation where it was illeg... | 0.9928 | -0.7071 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
