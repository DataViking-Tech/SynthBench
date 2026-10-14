# SynthBench Score Card

**Provider:** openrouter/meta-llama/llama-3.3-70b-instruct
**Dataset:** subpop (100 questions)
**Samples per question:** 15
**Elapsed:** 1943.2s

## SynthBench Parity Score (SPS)

**SPS: 0.6701 [0.6507, 0.6821]** (from 5 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6504 [0.6123, 0.6817] | ███████░░░ |
| P_rank  Rank-Order | 0.7424 [0.7041, 0.7713] | ███████░░░ |
| P_cond  Conditioning | 0.0116 | ░░░░░░░░░░ |
| P_sub   Subgroup | 0.9664 | ██████████ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3496 |
| Median JSD | 0.3380 |
| Mean Kendall's tau | 0.4847 |
| Composite Parity (legacy) | 0.6964 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1344 | +24% |
| random-baseline | 0.6495 | +0.0469 | +7% |

## What These Scores Mean

- **SPS** (SynthBench Parity Score): The overall score — average of all metrics. 0 = random noise, 1 = indistinguishable from real humans.
- **P_dist** (Distributional Parity): How closely does the AI's answer distribution match real humans? If 60% of humans say 'yes' and the AI says 'yes' 60% of the time, that's a perfect match. 0 = completely different, 1 = identical distributions.
- **P_rank** (Rank-Order Parity): Does the AI get the preference ordering right? If humans prefer A > B > C, does the AI agree — even if the exact percentages differ? 0 = reversed ordering, 1 = perfect agreement.
- **P_refuse** (Refusal Calibration): Does the AI refuse to answer at appropriate rates? Humans sometimes decline sensitive questions. An AI that never refuses, or refuses too often, is miscalibrated. 0 = rates completely off, 1 = perfect match.
- **P_cond** (Conditioning Fidelity): When told 'respond as a 65-year-old conservative,' does the AI actually shift its answers? Higher = better demographic role-playing. (When available.)
- **P_sub** (Subgroup Consistency): Is the AI equally accurate across all demographics, or does it nail some groups and miss others? (When available.)

## Demographic Breakdown

### CREGION

Best: Northeast (P_dist=0.6397) / Worst: South (P_dist=0.6177)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Northeast | 0.6397 | 0.0362 | 100 |
| South | 0.6177 | 0.0461 | 100 |

### EDUCATION

Best: College graduate/some postgrad (P_dist=0.6499) / Worst: Less than high school (P_dist=0.6048)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| College graduate/some postgrad | 0.6499 | 0.0243 | 100 |
| Less than high school | 0.6048 | 0.0653 | 100 |

### INCOME

Best: $100,000 or more (P_dist=0.6407) / Worst: Less than $30,000 (P_dist=0.6264)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| $100,000 or more | 0.6407 | 0.0270 | 100 |
| Less than $30,000 | 0.6264 | 0.0558 | 100 |

### POLPARTY

Best: Republican (P_dist=0.6791) / Worst: Democrat (P_dist=0.6559)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Republican | 0.6791 | 0.1015 | 100 |
| Democrat | 0.6559 | 0.0376 | 100 |

### SEX

Best: Male (P_dist=0.6387) / Worst: Female (P_dist=0.6097)

| Group | P_dist | P_cond | Questions |
|-------|--------|--------|-----------|
| Male | 0.6387 | 0.0323 | 100 |
| Female | 0.6097 | 0.0303 | 100 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Here’s a list of activities some people do and others do not... | 0.0068 | 1.0000 |
| Do you think whether a relative attended the school should b... | 0.0319 | 0.9129 |
| If an abortion was carried out in a situation where it was i... | 0.0502 | 0.3333 |
| Please indicate if you have traveled more than 100 miles fro... | 0.0603 | 1.0000 |
| Do you think gender should be a major factor, minor factor, ... | 0.1154 | 0.7071 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Regardless of whether you think abortion should be legal or ... | 0.6701 | -0.1155 |
| Thinking about the use of artificial intelligence (AI) in th... | 0.6822 | -0.3162 |
| How important is your religion in shaping your views about a... | 0.7067 | -0.1782 |
| If a woman had an abortion in a situation where it was illeg... | 0.9928 | -0.7071 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
