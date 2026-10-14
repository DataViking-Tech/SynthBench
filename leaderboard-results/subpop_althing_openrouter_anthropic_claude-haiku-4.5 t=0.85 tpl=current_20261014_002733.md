# SynthBench Score Card

**Provider:** althing/openrouter/anthropic/claude-haiku-4.5 t=0.85 tpl=current
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 349.0s

## SynthBench Parity Score (SPS)

**SPS: 0.7254 [0.6980, 0.7498]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6563 [0.6188, 0.6862] | ███████░░░ |
| P_rank  Rank-Order | 0.6284 [0.5806, 0.6683] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.8915 [0.8368, 0.9301] | █████████░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3437 |
| Median JSD | 0.3243 |
| Mean Kendall's tau | 0.2569 |
| Composite Parity (legacy) | 0.6423 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0804 | +14% |
| random-baseline | 0.6495 | -0.0072 | -1% |

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
| Did you refuse to answer the previous question?... | 0.0149 | 0.8165 |
| Do you think gender should be a major factor, minor factor, ... | 0.0335 | 0.9129 |
| Do you think abortion should be legal or illegal in the situ... | 0.0709 | 0.6667 |
| How much have you heard or read about medication abortion, w... | 0.1253 | 0.9129 |
| If a woman had an abortion in a situation where it was illeg... | 0.1327 | 0.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| As you may know, the Supreme Court’s decision found that the... | 0.6869 | -0.7746 |
| Regardless of whether you think abortion should be legal or ... | 0.6906 | -0.3464 |
| Do you personally know someone (such as a close friend, fami... | 0.8107 | -1.0000 |
| Still thinking about the area where you live, do you think t... | 0.9009 | -0.7071 |
| Thinking about policies around abortion in this country, in ... | 0.9509 | -0.5774 |
