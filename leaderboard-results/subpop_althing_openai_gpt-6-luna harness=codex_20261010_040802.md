# SynthBench Score Card

**Provider:** althing/openai/gpt-6-luna harness=codex
**Dataset:** subpop (100 questions)
**Samples per question:** 30
**Elapsed:** 2090.7s

## SynthBench Parity Score (SPS)

**SPS: 0.8020 [0.7783, 0.8208]** (from 3 metrics)

| Metric | Score | |
|--------|------:|---|
| P_dist  Distributional | 0.6960 [0.6687, 0.7239] | ███████░░░ |
| P_rank  Rank-Order | 0.7301 [0.6905, 0.7614] | ███████░░░ |
| P_refuse Refusal Cal. | 0.9799 [0.9394, 0.9903] | ██████████ |

## Raw Metrics

| Metric | Value |
|--------|-------|
| Mean JSD | 0.3040 |
| Median JSD | 0.3078 |
| Mean Kendall's tau | 0.4601 |
| Composite Parity (legacy) | 0.7130 |

## vs Baselines

| Baseline | Score | Delta | % |
|----------|------:|------:|--:|
| majority-baseline | 0.5620 | +0.1510 | +27% |
| random-baseline | 0.6495 | +0.0635 | +10% |

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
| Which statement comes closer to your view, even if neither i... | 0.0042 | 1.0000 |
| Just to confirm, do you think there are any exceptions when ... | 0.0292 | 1.0000 |
| Do you think whether a relative attended the school should b... | 0.0370 | 0.9129 |
| Would you favor or oppose employers’ use of artificial intel... | 0.0594 | 0.3333 |
| Do you think gender should be a major factor, minor factor, ... | 0.0652 | 0.9129 |

## Worst Matches (highest JSD)

| Question | JSD | tau |
|----------|-----|-----|
| Regardless of whether you think abortion should be legal or ... | 0.5272 | 0.2582 |
| Regardless of whether you think abortion should be legal or ... | 0.5333 | 0.0861 |
| Regardless of whether you think abortion should be legal or ... | 0.5344 | -0.4472 |
| How important is your religion in shaping your views about a... | 0.5574 | 0.5345 |
| Did you refuse to answer the previous question?... | 0.7066 | -0.3333 |
