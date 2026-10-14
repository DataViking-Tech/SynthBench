# SynthBench Score Card

**Provider:** openrouter/google/gemini-3.5-flash-lite
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 268.1s

## SynthBench Parity Score (SPS)

**SPS: 0.8005 [0.7782, 0.8194]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6656 [0.6305, 0.6987] | ███████░░░ |
| P_rank  Rank-Order | 0.7558 [0.7189, 0.7859] | ████████░░ |
| P_refuse Refusal Cal. | 0.9802 [0.9400, 0.9905] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3344 |
| Median JSD | 0.3363 |
| Mean Kendall's tau | 0.5116 |
| Composite Parity (legacy) | 0.7107 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1487 | +26% |
| random-baseline | 0.6495 | +0.0612 | +9% |

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
| Please indicate if you have attended a concert over the past... | 0.0035 | 1.0000 |
| In the news you are receiving about the Biden administration... | 0.0142 | 1.0000 |
| Did you refuse to answer the previous question?... | 0.0149 | 0.8165 |
| If an abortion was carried out in a situation where it was i... | 0.0568 | 0.3333 |
| Please indicate if you have attended a sporting event over t... | 0.1050 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How acceptable do you think it is to use computer programs, ... | 0.6049 | 0.1155 |
| Do you think people have ever assumed that you benefited unf... | 0.6071 | 0.2357 |
| Regardless of whether you think abortion should be legal or ... | 0.7599 | -0.4303 |
| Thinking now about how AI can be used in hiring, how much ha... | 0.7811 | -0.2357 |
| Regardless of whether you think abortion should be legal or ... | 0.8798 | -0.6025 |
