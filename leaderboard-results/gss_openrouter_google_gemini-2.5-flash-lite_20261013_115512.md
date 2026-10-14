# SynthBench Score Card

**Provider:** openrouter/google/gemini-2.5-flash-lite
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 102.1s

## SynthBench Parity Score (SPS)

**SPS: 0.8135 [0.7822, 0.8388]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7197 [0.6774, 0.7568] | ███████░░░ |
| P_rank  Rank-Order | 0.7492 [0.7002, 0.7878] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9716 [0.9642, 0.9770] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2803 |
| Median JSD | 0.2263 |
| Mean Kendall's tau | 0.4984 |
| Composite Parity (legacy) | 0.7344 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1725 | +31% |
| random-baseline | 0.6495 | +0.0849 | +13% |

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
| I am going to name an institution in this country. As far as... | 0.0073 | 1.0000 |
| I am going to name an institution in this country. As far as... | 0.0365 | 0.6667 |
| When a person has a disease that cannot be cured, do you thi... | 0.0424 | 1.0000 |
| Do you think most people would try to take advantage of you ... | 0.0521 | 0.6667 |
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please indicate whether you strongly agree, agree, disagree,... | 0.6247 | -0.3586 |
| Would you say your own health, in general, is excellent, goo... | 0.6251 | 0.0000 |
| Do you strongly agree, agree, disagree, or strongly disagree... | 0.6572 | -0.3162 |
| Do you believe there is a life after death?... | 0.7016 | -0.8165 |
| Do you agree strongly, agree somewhat, neither agree nor dis... | 0.7077 | -0.1155 |
