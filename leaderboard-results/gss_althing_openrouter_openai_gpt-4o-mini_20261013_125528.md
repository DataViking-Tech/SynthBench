# SynthBench Score Card

**Provider:** althing/openrouter/openai/gpt-4o-mini
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 348.2s

## SynthBench Parity Score (SPS)

**SPS: 0.8011 [0.7725, 0.8263]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6753 [0.6328, 0.7162] | ███████░░░ |
| P_rank  Rank-Order | 0.7559 [0.7107, 0.7922] | ████████░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3247 |
| Median JSD | 0.2810 |
| Mean Kendall's tau | 0.5118 |
| Composite Parity (legacy) | 0.7156 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1536 | +27% |
| random-baseline | 0.6495 | +0.0661 | +10% |

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
| We are faced with many problems in this country, none of whi... | 0.0451 | 1.0000 |
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| Would you be for or against sex education in the public scho... | 0.0798 | 0.8165 |
| I am going to name an institution in this country. As far as... | 0.0935 | 0.9129 |
| I am going to name an institution in this country. As far as... | 0.1055 | 0.5477 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you agree strongly, agree somewhat, neither agree nor dis... | 0.7077 | -0.1155 |
| Do you think most people would try to take advantage of you ... | 0.7212 | -0.2357 |
| If a man and a woman have sexual relations before marriage, ... | 0.7275 | 0.0000 |
| Generally speaking, would you say that most people can be tr... | 0.7427 | -0.2357 |
| Generally speaking, do you usually think of yourself as a Re... | 0.7506 | -0.2143 |
