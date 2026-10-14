# SynthBench Score Card

**Provider:** althing/openrouter/google/gemini-2.5-flash-lite
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 272.6s

## SynthBench Parity Score (SPS)

**SPS: 0.7714 [0.7376, 0.7988]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6812 [0.6406, 0.7192] | ███████░░░ |
| P_rank  Rank-Order | 0.6534 [0.5900, 0.7116] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9797 [0.9684, 0.9862] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3188 |
| Median JSD | 0.2738 |
| Mean Kendall's tau | 0.3068 |
| Composite Parity (legacy) | 0.6673 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1053 | +19% |
| random-baseline | 0.6495 | +0.0178 | +3% |

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
| Which of these characteristics do you associate with (the Ch... | 0.0053 | 1.0000 |
| Do you know someone who went to the U.S., but returned to yo... | 0.0055 | -1.0000 |
| Do you think this change in the working conditions for ordin... | 0.0132 | 0.0000 |
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| Do you think the U.S. should keep military troops in Iraq un... | 0.0301 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Which statement comes closer to your own views, even if neit... | 0.7544 | -0.1179 |
| Would you say that each of the following is doing a very goo... | 0.7558 | 0.0000 |
| Thinking about our relations with China, in your view, which... | 0.7563 | -0.5976 |
| Please tell me if you have a very favorable, somewhat favora... | 0.8181 | -0.1195 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9290 | -0.6325 |
