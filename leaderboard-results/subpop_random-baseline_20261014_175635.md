# SynthBench Score Card

**Provider:** random-baseline
**Dataset:** subpop (525 questions)
**Samples per question:** 30
**Elapsed:** 0.4s

## SynthBench Parity Score (SPS)

**SPS: 0.7683 [0.7595, 0.7764]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.8197 [0.8130, 0.8267] | ████████░░ |
| P_rank  Rank-Order | 0.5013 [0.4793, 0.5231] | █████░░░░░ |
| P_refuse Refusal Cal. | 0.9839 [0.9751, 0.9884] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.1803 |
| Median JSD | 0.1681 |
| Mean Kendall's tau | 0.0026 |
| Composite Parity (legacy) | 0.6605 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0985 | +18% |
| random-baseline | 0.6495 | +0.0110 | +2% |

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
| Do you think abortion should be...... | 0.0238 | 0.6000 |
| Did you refuse to answer the previous question?... | 0.0293 | 0.0000 |
| Which president would you name as the second-best president ... | 0.0377 | 0.4226 |
| Is the lack of access to adequate health care a reason why b... | 0.0394 | 1.0000 |
| Thinking about the situation at the U.S. border with Mexico,... | 0.0420 | 0.5270 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| How many people in the community where you live would you sa... | 0.4091 | -0.6025 |
| Have there been times in the past 12 months when you did not... | 0.4094 | -0.6667 |
| How often, if ever, do you think friends, family, and acquai... | 0.4133 | -0.8281 |
| In the past month, how often, if ever, have you worn a mask ... | 0.4266 | -0.0861 |
| Have you turned to family or friends for help with bills, ho... | 0.5000 | -1.0000 |
