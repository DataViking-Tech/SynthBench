# SynthBench Score Card

**Provider:** althing/openrouter/anthropic/claude-haiku-5.5
**Dataset:** globalopinionqa (525 questions)
**Samples per question:** 30
**Elapsed:** 4960.6s

## SynthBench Parity Score (SPS)

**SPS: 0.7806 [0.7686, 0.7923]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6582 [0.6413, 0.6744] | ███████░░░ |
| P_rank  Rank-Order | 0.7099 [0.6853, 0.7322] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9737 [0.9656, 0.9787] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3418 |
| Median JSD | 0.3181 |
| Mean Kendall's tau | 0.4199 |
| Composite Parity (legacy) | 0.6841 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1221 | +22% |
| random-baseline | 0.6495 | +0.0346 | +5% |

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
| Do you think the Pakistani government provided intelligence ... | 0.0001 | 0.0000 |
| Which of these characteristics do you associate with people ... | 0.0020 | 0.0000 |
| On this list are various groups of people. Could you please ... | 0.0077 | 0.8367 |
| As a result of the earthquake and tsunami did you or members... | 0.0094 | 1.0000 |
| Now I will read a list of some things that have happened in ... | 0.0138 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Here are some different political and social actions that pe... | 0.8697 | -0.7071 |
| Do you think most Muslims in our country today want to adopt... | 0.8706 | -0.7071 |
| Do you personally believe that gambling is morally acceptabl... | 0.9064 | -0.7071 |
| Do you think of yourself first as your nationality or first ... | 0.9595 | -0.8165 |
| Which one of these comes closest to your opinion, number 1 o... | 0.9885 | -0.6325 |
