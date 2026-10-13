# SynthBench Score Card

**Provider:** raw-anthropic/claude-haiku-4-5-20251001 harness=claude-code
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 6722.6s

## SynthBench Parity Score (SPS)

**SPS: 0.6133 [0.5727, 0.6536]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6507 [0.5914, 0.7023] | ███████░░░ |
| P_rank  Rank-Order | 0.5905 [0.5259, 0.6514] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.5988 [0.5246, 0.6707] | ██████░░░░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3493 |
| Median JSD | 0.2873 |
| Mean Kendall's tau | 0.1810 |
| Composite Parity (legacy) | 0.6206 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0586 | +10% |
| random-baseline | 0.6495 | -0.0289 | -4% |

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
| Again, which one better describes George W. Bush...He makes ... | 0.0001 | 1.0000 |
| Do you think people should be able to say these types of thi... | 0.0026 | 1.0000 |
| Do you think our country's efforts to reduce government spen... | 0.0051 | 0.0000 |
| Please tell me if you approve or disapprove of the way Presi... | 0.0097 | 0.0000 |
| Do you think the upcoming parliamentary elections will impro... | 0.0116 | 0.8165 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.3162 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9290 | -0.6325 |
| How satisfied are you with the way democracy is working in o... | 1.0000 | -0.5774 |
