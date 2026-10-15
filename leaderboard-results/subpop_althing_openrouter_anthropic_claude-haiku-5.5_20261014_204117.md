# SynthBench Score Card

**Provider:** althing/openrouter/anthropic/claude-haiku-5.5
**Dataset:** subpop (525 questions)
**Samples per question:** 30
**Elapsed:** 9788.7s

## SynthBench Parity Score (SPS)

**SPS: 0.7999 [0.7914, 0.8076]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6605 [0.6477, 0.6747] | ███████░░░ |
| P_rank  Rank-Order | 0.7565 [0.7441, 0.7692] | ████████░░ |
| P_refuse Refusal Cal. | 0.9827 [0.9736, 0.9872] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3395 |
| Median JSD | 0.3363 |
| Mean Kendall's tau | 0.5129 |
| Composite Parity (legacy) | 0.7085 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1465 | +26% |
| random-baseline | 0.6495 | +0.0590 | +9% |

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
| Do you think travelers on airplanes and public transportatio... | 0.0042 | 1.0000 |
| Overall, do you think the Biden administration’s policies on... | 0.0112 | 0.3333 |
| How much of a threat, if any, is the coronavirus outbreak fo... | 0.0128 | 0.9129 |
| How much of a threat, if any, is the coronavirus outbreak fo... | 0.0170 | 0.9129 |
| How much of a threat, if any, is the coronavirus outbreak fo... | 0.0213 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| If an abortion was carried out in a situation where it was i... | 0.7856 | -0.3333 |
| Is the national unemployment rate as reported by the governm... | 0.8459 | -0.0658 |
| In the past month, how often, if ever, have you worn a mask ... | 0.8655 | 0.0861 |
| In the past month, how often, if ever, have you worn a mask ... | 0.8669 | -0.0861 |
| In the past month, how often, if ever, have you worn a mask ... | 0.8804 | -0.0861 |
