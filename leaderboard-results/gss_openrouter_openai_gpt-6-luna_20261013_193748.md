# SynthBench Score Card

**Provider:** openrouter/openai/gpt-6-luna
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 1473.9s

## SynthBench Parity Score (SPS)

**SPS: 0.7241 [0.6817, 0.7633]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5856 [0.5213, 0.6483] | ██████░░░░ |
| P_rank  Rank-Order | 0.6146 [0.5481, 0.6723] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4144 |
| Median JSD | 0.3123 |
| Mean Kendall's tau | 0.2292 |
| Composite Parity (legacy) | 0.6001 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0381 | +7% |
| random-baseline | 0.6495 | -0.0494 | -8% |

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
| I am going to name an institution in this country. As far as... | 0.0759 | 0.9129 |
| Would you be for or against sex education in the public scho... | 0.0798 | 0.8165 |
| What is your opinion about a married person having sexual re... | 0.0927 | 0.8367 |
| Please tell me whether or not you think it should be possibl... | 0.1067 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| I am going to name an institution in this country. As far as... | 0.9675 | -0.7071 |
| Compared with American families in general, would you say yo... | 0.9693 | -0.5774 |
| Which statement comes closest to expressing what you believe... | 0.9802 | -0.5345 |
| We are interested in how people are getting along financiall... | 0.9806 | -0.7071 |
| Would you say your own health, in general, is excellent, goo... | 0.9958 | -0.6325 |
