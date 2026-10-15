# SynthBench Score Card

**Provider:** althing/openrouter/meta-llama/llama-3.3-70b-instruct
**Dataset:** globalopinionqa (525 questions)
**Samples per question:** 30
**Elapsed:** 5093.1s

## SynthBench Parity Score (SPS)

**SPS: 0.7758 [0.7631, 0.7868]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6465 [0.6312, 0.6618] | ██████░░░░ |
| P_rank  Rank-Order | 0.7006 [0.6763, 0.7248] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9802 [0.9766, 0.9831] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3535 |
| Median JSD | 0.3432 |
| Mean Kendall's tau | 0.4012 |
| Composite Parity (legacy) | 0.6735 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1115 | +20% |
| random-baseline | 0.6495 | +0.0240 | +4% |

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
| Do you think...rising prices are a very big problem, a moder... | 0.0102 | 0.8819 |
| Now I will read a list of some things that have happened in ... | 0.0138 | 1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| Do you approve or disapprove of the way President Rodrigo Du... | 0.0212 | 1.0000 |
| Do you think media organizations should be able to publish i... | 0.0263 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please tell me if you have a very favorable, somewhat favora... | 0.8135 | 0.0000 |
| (How much of a role do you think Islam plays in the politica... | 0.8148 | -0.8165 |
| Which statement comes closer to your own views, even if neit... | 0.8324 | 0.0853 |
| Here are some different political and social actions that pe... | 0.8697 | -0.7071 |
| Which one of these comes closest to your opinion, number 1 o... | 0.9885 | -0.6325 |
