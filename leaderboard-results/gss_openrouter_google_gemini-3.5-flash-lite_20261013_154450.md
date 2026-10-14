# SynthBench Score Card

**Provider:** openrouter/google/gemini-3.5-flash-lite
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 201.8s

## SynthBench Parity Score (SPS)

**SPS: 0.8074 [0.7800, 0.8293]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7016 [0.6640, 0.7364] | ███████░░░ |
| P_rank  Rank-Order | 0.7487 [0.6993, 0.7840] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2984 |
| Median JSD | 0.2647 |
| Mean Kendall's tau | 0.4974 |
| Composite Parity (legacy) | 0.7251 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1631 | +29% |
| random-baseline | 0.6495 | +0.0756 | +12% |

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
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| I am going to name an institution in this country. As far as... | 0.0696 | 0.8165 |
| Would you be for or against sex education in the public scho... | 0.0798 | 0.8165 |
| In general, do you find life exciting, pretty routine, or du... | 0.0964 | 0.9129 |
| Please tell me whether or not you think it should be possibl... | 0.1067 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Some people say that people get ahead by their own hard work... | 0.5687 | 0.2357 |
| Should divorce in this country be easier or more difficult t... | 0.5806 | -0.2357 |
| Would you say that most of the time people try to be helpful... | 0.6583 | -0.2357 |
| Do you believe there is a life after death?... | 0.7016 | -0.8165 |
| I'm going to show you a seven-point scale on which the polit... | 0.8837 | -0.3571 |
