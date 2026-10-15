# SynthBench Score Card

**Provider:** althing/openrouter/meta-llama/llama-3.3-70b-instruct
**Dataset:** subpop (525 questions)
**Samples per question:** 30
**Elapsed:** 9857.1s

## SynthBench Parity Score (SPS)

**SPS: 0.7927 [0.7843, 0.8004]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6431 [0.6304, 0.6569] | ██████░░░░ |
| P_rank  Rank-Order | 0.7510 [0.7390, 0.7632] | ████████░░ |
| P_refuse Refusal Cal. | 0.9839 [0.9751, 0.9884] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3569 |
| Median JSD | 0.3516 |
| Mean Kendall's tau | 0.5020 |
| Composite Parity (legacy) | 0.6970 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1350 | +24% |
| random-baseline | 0.6495 | +0.0475 | +7% |

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
| In the last month, did you attend religious services in pers... | 0.0038 | 1.0000 |
| Which of the following statements comes closest to your view... | 0.0103 | 0.3333 |
| In the last month, did you attend religious services in pers... | 0.0153 | 1.0000 |
| Thinking about our economic and trade policy toward China, w... | 0.0220 | 0.3333 |
| Have your personal views about abortion changed in any way o... | 0.0486 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How would you rate the job that your local elected officials... | 0.7141 | 0.0000 |
| Have you heard of the social media site or app Gab?... | 0.7439 | 0.0000 |
| In recent years, several social media sites have emerged as ... | 0.7570 | 0.0000 |
| Have you ever moved out of where you were living, either per... | 0.7766 | 0.2357 |
| Have you heard of the social media site or app BitChute?... | 0.8196 | 0.0000 |
