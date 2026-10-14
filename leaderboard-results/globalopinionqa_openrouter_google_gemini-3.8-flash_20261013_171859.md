# SynthBench Score Card

**Provider:** openrouter/google/gemini-3.8-flash
**Dataset:** globalopinionqa (100 questions)
**Samples per question:** 30
**Elapsed:** 1920.0s

## SynthBench Parity Score (SPS)

**SPS: 0.6943 [0.6552, 0.7323]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.5627 [0.5114, 0.6128] | ██████░░░░ |
| P_rank  Rank-Order | 0.5899 [0.5198, 0.6568] | ██████░░░░ |
| P_refuse Refusal Cal. | 0.9303 [0.9010, 0.9521] | █████████░ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.4373 |
| Median JSD | 0.4156 |
| Mean Kendall's tau | 0.1797 |
| Composite Parity (legacy) | 0.5763 |

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
| On another topic, had you heard that President Barack Obama'... | 0.0203 | 1.0000 |
| Thinking about possible war with Iraq, would you favor or op... | 0.0358 | 1.0000 |
| (Now/And thinking about the American people...) Which of the... | 0.0524 | 1.0000 |
| According to news reports, the American government has been ... | 0.0763 | 1.0000 |
| Do you think the U.S. should keep military troops in Iraq un... | 0.0767 | -1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.3162 |
| Do you approve or disapprove of the way President Nicolas Ma... | 0.9022 | -0.8165 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9290 | -0.6325 |
| Thinking about our relations with China, in your view, which... | 0.9331 | -0.6325 |
| How satisfied are you with the way democracy is working in o... | 1.0000 | -0.5774 |
