# SynthBench Score Card

**Provider:** althing/anthropic/claude-haiku-5-5 harness=claude-code
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 1896.0s

## SynthBench Parity Score (SPS)

**SPS: 0.7421 [0.7081, 0.7752]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6613 [0.6171, 0.7034] | ███████░░░ |
| P_rank  Rank-Order | 0.6363 [0.5799, 0.6853] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9286 [0.8917, 0.9488] | █████████░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3387 |
| Median JSD | 0.3027 |
| Mean Kendall's tau | 0.2727 |
| Composite Parity (legacy) | 0.6488 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0868 | +15% |
| random-baseline | 0.6495 | -0.0007 | -0% |

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
| We are faced with many problems in this country, none of whi... | 0.0454 | 0.5477 |
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| I am going to name an institution in this country. As far as... | 0.0768 | 0.9129 |
| Would you be for or against sex education in the public scho... | 0.0915 | 0.3333 |
| Tell me if you agree or disagree with this statement: Most m... | 0.1008 | 0.3333 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| If you were asked to use one of four names for your social c... | 0.6966 | -0.1195 |
| Do you believe there is a life after death?... | 0.7016 | -0.8165 |
| Some people say that because of past discrimination, Black p... | 0.7049 | -0.1195 |
| Do you think most people would try to take advantage of you ... | 0.7212 | -0.2357 |
| Please tell me whether or not you think it should be possibl... | 0.8901 | -0.8165 |
