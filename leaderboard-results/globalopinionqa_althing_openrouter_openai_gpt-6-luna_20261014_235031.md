# SynthBench Score Card

**Provider:** althing/openrouter/openai/gpt-6-luna
**Dataset:** globalopinionqa (525 questions)
**Samples per question:** 30
**Elapsed:** 7732.3s

## SynthBench Parity Score (SPS)

**SPS: 0.7737 [0.7608, 0.7858]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6580 [0.6414, 0.6749] | ███████░░░ |
| P_rank  Rank-Order | 0.6846 [0.6603, 0.7080] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9784 [0.9716, 0.9820] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3420 |
| Median JSD | 0.3264 |
| Mean Kendall's tau | 0.3692 |
| Composite Parity (legacy) | 0.6713 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1093 | +19% |
| random-baseline | 0.6495 | +0.0218 | +3% |

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
| Again, which one better describes George W. Bush...He makes ... | 0.0010 | 1.0000 |
| Do you approve or disapprove of the way President Dilma Rous... | 0.0057 | 1.0000 |
| Do you think this change in the availability of modern medic... | 0.0114 | 1.0000 |
| In the last five years have you traveled to another country ... | 0.0114 | 1.0000 |
| Now I will read a list of some things that have happened in ... | 0.0138 | 1.0000 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Do you personally believe that gambling is morally acceptabl... | 0.9064 | -0.7071 |
| And now thinking about the future, overall, today are you op... | 0.9130 | -0.1826 |
| Does this statement describe your country very well, somewha... | 0.9178 | -0.6325 |
| Do you think of yourself first as your nationality or first ... | 0.9595 | -0.8165 |
| Which one of these comes closest to your opinion, number 1 o... | 0.9885 | -0.6325 |
