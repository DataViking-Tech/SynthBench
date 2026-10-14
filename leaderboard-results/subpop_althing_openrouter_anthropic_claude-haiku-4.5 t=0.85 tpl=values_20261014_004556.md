# SynthBench Score Card

**Provider:** althing/openrouter/anthropic/claude-haiku-4.5 t=0.85 tpl=values
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 350.3s

## SynthBench Parity Score (SPS)

**SPS: 0.6374 [0.6022, 0.6697]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6323 [0.5840, 0.6733] | ██████░░░░ |
| P_rank  Rank-Order | 0.6096 [0.5610, 0.6529] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.6703 [0.6055, 0.7379] | ███████░░░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3677 |
| Median JSD | 0.3066 |
| Mean Kendall's tau | 0.2192 |
| Composite Parity (legacy) | 0.6210 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0590 | +10% |
| random-baseline | 0.6495 | -0.0285 | -4% |

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
| Did you refuse to answer the previous question?... | 0.0002 | 1.0000 |
| Regardless of whether you think abortion should be legal or ... | 0.0549 | 0.0000 |
| Regardless of whether you think abortion should be legal or ... | 0.0584 | 0.0000 |
| Regardless of whether you think abortion should be legal or ... | 0.0649 | 0.0000 |
| Do you think there are situations when abortion should be le... | 0.0769 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| In the news you are receiving about the Biden administration... | 0.9102 | -0.8165 |
| Regardless of whether you think abortion should be legal or ... | 0.9490 | -0.5774 |
| Please choose the statement that comes closer to your own vi... | 0.9582 | -0.8165 |
| Which statement comes closer to your view, even if neither i... | 0.9648 | -0.8165 |
| Before taking this survey, how much thought would you say yo... | 0.9691 | -0.6325 |
