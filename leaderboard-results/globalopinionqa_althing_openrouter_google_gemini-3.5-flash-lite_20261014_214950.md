# SynthBench Score Card

**Provider:** althing/openrouter/google/gemini-3.5-flash-lite
**Dataset:** globalopinionqa (525 questions)
**Samples per question:** 30
**Elapsed:** 4704.5s

## SynthBench Parity Score (SPS)

**SPS: 0.7802 [0.7676, 0.7921]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6611 [0.6439, 0.6778] | ███████░░░ |
| P_rank  Rank-Order | 0.6995 [0.6740, 0.7214] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9763, 0.9828] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3389 |
| Median JSD | 0.3059 |
| Mean Kendall's tau | 0.3990 |
| Composite Parity (legacy) | 0.6803 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1183 | +21% |
| random-baseline | 0.6495 | +0.0308 | +5% |

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
| Do you think this change in the working conditions for ordin... | 0.0008 | 1.0000 |
| Which of these characteristics do you associate with Muslims... | 0.0013 | 1.0000 |
| Do you think the government of Ukraine respects the personal... | 0.0020 | 1.0000 |
| Which of the following phrases comes closer to your view?  I... | 0.0020 | 0.0000 |
| Do you think this change in the availability of modern medic... | 0.0050 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Here are some different political and social actions that pe... | 0.8697 | -0.7071 |
| Do you think most Muslims in our country today want to adopt... | 0.8706 | -0.7071 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9014 | -0.6325 |
| Please tell me if you have a very favorable, somewhat favora... | 0.9022 | -0.6325 |
| Now I am going to read you a list of things that may be prob... | 0.9108 | -0.7071 |
