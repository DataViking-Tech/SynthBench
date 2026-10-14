# SynthBench Score Card

**Provider:** althing/openrouter/google/gemini-2.5-flash-lite
**Dataset:** gss (75 questions)
**Samples per question:** 30
**Elapsed:** 178.2s

## SynthBench Parity Score (SPS)

**SPS: 0.8184 [0.7901, 0.8427]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.7168 [0.6792, 0.7523] | ███████░░░ |
| P_rank  Rank-Order | 0.7662 [0.7141, 0.8041] | ████████░░ |
| P_refuse Refusal Cal. | 0.9721 [0.9645, 0.9775] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.2832 |
| Median JSD | 0.2679 |
| Mean Kendall's tau | 0.5325 |
| Composite Parity (legacy) | 0.7415 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1795 | +32% |
| random-baseline | 0.6495 | +0.0920 | +14% |

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
| Consider a person who believes that Black people are genetic... | 0.0101 | 1.0000 |
| Would you favor or oppose a law which would require a person... | 0.0107 | 1.0000 |
| When a person has a disease that cannot be cured, do you thi... | 0.0576 | 1.0000 |
| Please tell me whether or not you think it should be possibl... | 0.0579 | 0.8165 |
| Would you be for or against sex education in the public scho... | 0.0798 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Some people say that people get ahead by their own hard work... | 0.5687 | 0.2357 |
| Would you say that most of the time people try to be helpful... | 0.5746 | 0.1826 |
| Which statement comes closest to expressing what you believe... | 0.6706 | 0.3563 |
| Do you believe there is a life after death?... | 0.7016 | -0.8165 |
| Do you think most people would try to take advantage of you ... | 0.7212 | -0.2357 |
