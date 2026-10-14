# SynthBench Score Card

**Provider:** openrouter/anthropic/claude-sonnet-4
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 642.5s

## SynthBench Parity Score (SPS)

**SPS: 0.6311 [0.5928, 0.6696]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6886 [0.6322, 0.7393] | ███████░░░ |
| P_rank  Rank-Order | 0.5951 [0.5359, 0.6503] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.6094 [0.5223, 0.6984] | ██████░░░░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3114 |
| Median JSD | 0.2324 |
| Mean Kendall's tau | 0.1902 |
| Composite Parity (legacy) | 0.6419 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0799 | +14% |
| random-baseline | 0.6495 | -0.0077 | -1% |

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
| In general, do you think our country is covered fairly or un... | 0.0001 | 0.0000 |
| On the subject of Iraq, did your country make the right deci... | 0.0015 | 0.0000 |
| How much of a threat, if any, does Islamic extremism pose to... | 0.0015 | 0.0000 |
| Do you think our country's efforts to reduce government spen... | 0.0051 | 0.0000 |
| Now I'd like to ask your views about some additional politic... | 0.0058 | 0.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.3162 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9290 | -0.6325 |
| How satisfied are you with the way democracy is working in o... | 1.0000 | -0.5774 |
