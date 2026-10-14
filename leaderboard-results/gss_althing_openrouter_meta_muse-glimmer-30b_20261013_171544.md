# SynthBench Score Card

**Provider:** althing/openrouter/meta/muse-glimmer-30b
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 1356.0s

## SynthBench Parity Score (SPS)

**SPS: 0.8050 [0.7791, 0.8262]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6962 [0.6606, 0.7255] | ███████░░░ |
| P_rank  Rank-Order | 0.7472 [0.7017, 0.7839] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9717 [0.9642, 0.9771] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3038 |
| Median JSD | 0.2810 |
| Mean Kendall's tau | 0.4943 |
| Composite Parity (legacy) | 0.7217 |

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
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| Would you be for or against sex education in the public scho... | 0.0798 | 0.8165 |
| Please tell me whether or not you think it should be possibl... | 0.1067 | 0.8165 |
| Consider somebody who is against all churches and religion. ... | 0.1190 | 0.8165 |
| Consider somebody who is against all churches and religion. ... | 0.1233 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you agree strongly, agree somewhat, neither agree nor dis... | 0.5503 | -0.4303 |
| What is your opinion about a married person having sexual re... | 0.5913 | 0.3586 |
| Would you say that most of the time people try to be helpful... | 0.6583 | -0.2357 |
| Do you believe there is a life after death?... | 0.7016 | -0.8165 |
| Do you think most people would try to take advantage of you ... | 0.7212 | -0.2357 |
