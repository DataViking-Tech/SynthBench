# SynthBench Score Card

**Provider:** random-baseline
**Dataset:** globalopinionqa (525 questions)
**Samples per question:** 30
**Elapsed:** 0.5s

## SynthBench Parity Score (SPS)

**SPS: 0.7793 [0.7693, 0.7888]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.8681 [0.8592, 0.8763] | █████████░ |
| P_rank  Rank-Order | 0.4896 [0.4644, 0.5143] | █████░░░░░ |
| P_refuse Refusal Cal. | 0.9803 [0.9767, 0.9832] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.1319 |
| Median JSD | 0.1128 |
| Mean Kendall's tau | -0.0209 |
| Composite Parity (legacy) | 0.6788 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1168 | +21% |
| random-baseline | 0.6495 | +0.0293 | +5% |

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
| In your opinion, are there any serious threats to Islam toda... | 0.0000 | 1.0000 |
| Overall, was the break-up of Czechoslovakia into two indepen... | 0.0000 | 0.0000 |
| Do you approve or disapprove of the way Prime Minister Tayyi... | 0.0002 | 0.0000 |
| According to news reports, the American government has been ... | 0.0003 | 1.0000 |
| Do you know someone who went to the U.S., but returned to yo... | 0.0003 | 0.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| I am going to read you a list of things that might be import... | 0.4424 | -0.1168 |
| (Now I am going to read you a list of things that may be pro... | 0.4462 | -0.3162 |
| (Now I am going to read you a list of things that may be pro... | 0.4534 | -0.4000 |
| Do you think...rising prices are a very big problem, a moder... | 0.4556 | 0.1054 |
| Some people say the following things are important to them. ... | 0.4579 | 0.0000 |
