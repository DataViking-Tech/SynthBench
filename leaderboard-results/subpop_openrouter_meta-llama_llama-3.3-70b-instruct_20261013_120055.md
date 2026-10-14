# SynthBench Score Card

**Provider:** openrouter/meta-llama/llama-3.3-70b-instruct
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 314.2s

## SynthBench Parity Score (SPS)

**SPS: 0.7883 [0.7554, 0.8086]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6453 [0.6092, 0.6759] | ██████░░░░ |
| P_rank  Rank-Order | 0.7396 [0.7007, 0.7703] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3547 |
| Median JSD | 0.3525 |
| Mean Kendall's tau | 0.4793 |
| Composite Parity (legacy) | 0.6925 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1305 | +23% |
| random-baseline | 0.6495 | +0.0430 | +7% |

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
| Here’s a list of activities some people do and others do not... | 0.0092 | 1.0000 |
| If an abortion was carried out in a situation where it was i... | 0.0103 | 1.0000 |
| Please indicate if you have traveled more than 100 miles fro... | 0.0392 | 1.0000 |
| Do you think the use of artificial intelligence (AI) in heal... | 0.0845 | 0.9129 |
| Do you think whether a relative attended the school should b... | 0.0881 | 0.5477 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Thinking about the use of artificial intelligence (AI) in th... | 0.6221 | 0.0000 |
| Regardless of whether you think abortion should be legal or ... | 0.6701 | -0.1155 |
| How important is your religion in shaping your views about a... | 0.7067 | -0.1782 |
| If a woman had an abortion in a situation where it was illeg... | 0.9928 | -0.7071 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
