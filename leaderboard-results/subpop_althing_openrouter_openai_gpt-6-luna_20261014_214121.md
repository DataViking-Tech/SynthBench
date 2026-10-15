# SynthBench Score Card

**Provider:** althing/openrouter/openai/gpt-6-luna
**Dataset:** subpop (525 questions)
**Samples per question:** 30
**Elapsed:** 13393.4s

## SynthBench Parity Score (SPS)

**SPS: 0.8082 [0.7995, 0.8163]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6726 [0.6599, 0.6860] | ███████░░░ |
| P_rank  Rank-Order | 0.7683 [0.7548, 0.7808] | ████████░░ |
| P_refuse Refusal Cal. | 0.9839 [0.9751, 0.9884] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3274 |
| Median JSD | 0.3257 |
| Mean Kendall's tau | 0.5366 |
| Composite Parity (legacy) | 0.7204 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1584 | +28% |
| random-baseline | 0.6495 | +0.0709 | +11% |

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
| Overall, would you favor or oppose the U.S. expanding natura... | 0.0094 | 1.0000 |
| Do you think travelers on airplanes and public transportatio... | 0.0166 | 0.8165 |
| Please choose the statement that comes closer to your own vi... | 0.0197 | 0.3333 |
| Do you believe that some things happen in life that can’t re... | 0.0249 | 1.0000 |
| Do you favor or oppose employers’ use of artificial intellig... | 0.0306 | 0.6667 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| In the past month, how often, if ever, have you worn a mask ... | 0.7644 | 0.2981 |
| Have you heard of the social media site or app BitChute?... | 0.8196 | 0.0000 |
| Is the national unemployment rate as reported by the governm... | 0.9673 | -0.3563 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
| Did you refuse to answer the previous question?... | 1.0000 | -0.8165 |
