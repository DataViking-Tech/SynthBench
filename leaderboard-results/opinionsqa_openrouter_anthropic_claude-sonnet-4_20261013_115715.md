# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-sonnet-4
**Dataset:** opinionsqa (100 questions)
**Samples per question:** 30
**Elapsed:** 500.6s

## SynthBench Parity Score (SPS)

**SPS: 0.7196 [0.6748, 0.7604]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6201 [0.5639, 0.6717] | ██████░░░░ |
| P_rank  Rank-Order | 0.6620 [0.6094, 0.7078] | ███████░░░ |
| P_refuse Refusal Cal. | 0.8766 [0.8065, 0.9207] | █████████░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3799 |
| Median JSD | 0.3120 |
| Mean Kendall's tau | 0.3241 |
| Composite Parity (legacy) | 0.6410 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0791 | +14% |
| random-baseline | 0.6495 | -0.0085 | -1% |

## What These Scores Mean

- **SPS** (SynthBench Parity Score): The overall score — average of all metrics. 0 = random noise, 1 = indistinguishable from real humans.
- **P_dist** (Distributional Parity): How closely does the AI's answer distribution match real humans? If 60% of humans say 'yes' and the AI says 'yes' 60% of the time, that's a perfect match. 0 = completely different, 1 = identical distributions.
- **P_rank** (Rank-Order Parity): Does the AI get the preference ordering right? If humans prefer A > B > C, does the AI agree — even if the exact percentages differ? 0 = reversed ordering, 1 = perfect agreement.
- **P_refuse** (Refusal Calibration): Does the AI refuse to answer at appropriate rates? Humans sometimes decline sensitive questions. An AI that never refuses, or refuses too often, is miscalibrated. 0 = rates completely off, 1 = perfect match.
- **P_cond** (Conditioning Fidelity): When told 'respond as a 65-year-old conservative,' does the AI actually shift its answers? Higher = better demographic role-playing. (When available.)
- **P_sub** (Subgroup Consistency): Is the AI equally accurate across all demographics, or does it nail some groups and miss others? (When available.)

## Temporal Breakdown (by Survey Year)

Scores stratified by Pew ATP survey wave year. Rising P_dist in recent years may indicate training-data contamination.

| Year | P_dist | P_rank | Mean JSD | Questions |
|------|--------|--------|----------|-----------|
| 2017 | 0.6262 | 0.6669 | 0.3738 | 99 |
| 2018 | 0.0175 | 0.1838 | 0.9825 | 1 |

## Best Matches (lowest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you think the following are likely to happen as a result ... | 0.0047 | 1.0000 |
| If driverless vehicles become widespread, which of the follo... | 0.0135 | 1.0000 |
| Have you yourself ever lost a job because your employer repl... | 0.0220 | 0.7071 |
| How well, if at all, do the following words or phrases descr... | 0.0408 | 0.9487 |
| Do you think men and women are basically similar or basicall... | 0.0582 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please tell us whether you are satisfied or dissatisfied wit... | 0.9825 | -0.6325 |
| Thinking about the people you know, including yourself, do y... | 0.9832 | -0.8165 |
| How worried are you right now about not having enough money ... | 0.9849 | -0.6325 |
| Regardless of whether or not you own a gun, have you ever fi... | 0.9858 | -0.8165 |
| How safe, if at all, would you say your local community is f... | 0.9878 | -0.6325 |
