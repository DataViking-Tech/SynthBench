# SynthBench Score Card

**Provider:** althing/openai/gpt-6-luna harness=codex tpl=structured
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 2274.4s

## SynthBench Parity Score (SPS)

**SPS: 0.7648 [0.7300, 0.7956]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6539 [0.6084, 0.6958] | ███████░░░ |
| P_rank  Rank-Order | 0.6606 [0.5975, 0.7197] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9797 [0.9684, 0.9862] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3461 |
| Median JSD | 0.3195 |
| Mean Kendall's tau | 0.3213 |
| Composite Parity (legacy) | 0.6573 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.0953 | +17% |
| random-baseline | 0.6495 | +0.0077 | +1% |

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
| As I read some specific policies of [American] President Geo... | 0.0116 | 1.0000 |
| Do you think this change in the availability of modern medic... | 0.0193 | 1.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| Do you think that the rise of nontraditional political parti... | 0.0262 | 1.0000 |
| Which of these characteristics do you associate with (the Ch... | 0.0346 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please tell me if you have a very favorable, somewhat favora... | 0.7656 | -0.1195 |
| Please tell me if you have a very favorable, somewhat favora... | 0.7758 | -0.4472 |
| How satisfied are you with the way democracy is working in o... | 0.8756 | -0.2582 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.3162 |
